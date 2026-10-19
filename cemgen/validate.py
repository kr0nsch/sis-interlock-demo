"""Проверка матрицы ``cem/1`` и построение модели (DESIGN.md, 9.2–9.4).

:func:`parse_grid` проходит разделы ``[header]`` и ``[matrix]``, проверяет каждую ячейку и
связи между ними и возвращает модель (:class:`cemgen.model.Matrix`) — только если ошибок нет.
Сообщения собираются все сразу (без остановки на первой ошибке), но без каскадов: правило,
которому нужна неверная ячейка, для этой строки пропускается.

Коды правил — таблица 9.4. Предупреждения CEM-W002 (стимул одной причины вызывает другую)
считает эталонная модель (:mod:`cemgen.refmodel`) на уже построенной модели.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

from cemgen import limits
from cemgen.diagnostics import Diagnostic, MatrixFileError, sort_key
from cemgen.grid import Grid, GridRow, read_grid
from cemgen.model import Analog, Cause, Effect, Header, Matrix, Signal
from cemgen.refmodel import cross_demands
from cemgen.sisdefs import ARCH_NM, ARCH_TEXT, POLICY_TEXT, SAFE_STATE_WORDS, Policy, SafeState, VoteArch
from cemgen.values import (
    DurationError,
    is_ascii_text,
    is_iso_date,
    is_tag,
    matrix_mark,
    parse_bool,
    parse_duration_ms,
    parse_int_number,
    parse_number,
    parse_uint,
)

# --- раздел [header] (9.2) -----------------------------------------------------------------
HEADER_KEYS: dict[str, bool] = {
    "format": True,
    "object": True,
    "object_name": True,
    "title": True,
    "document": True,
    "revision": True,
    "date": True,
    "author": True,
    "start_tripped": False,
    "test_step": False,
    "reset_tag": False,
    "bypass_permit_tag": False,
    "override_permit_tag": False,
}
FORMAT_ID = "cem/1"

# --- раздел [matrix] ------------------------------------------------------------------------
LABEL_MARK = ">>"
HEADER_FIRST = "no"
EFFECT_LABELS: dict[str, bool] = {
    "effect_no": True,
    "effect_tag": True,
    "effect_description": True,
    "actuator": True,
    "safe_state": True,
    "effect_notes": False,
}
CAUSE_COLUMNS: tuple[str, ...] = (
    "no",
    "tag",
    "description",
    "signal",
    "source",
    "vote",
    "policy",
    "trip_on",
    "setpoint",
    "hyst",
    "units",
    "range_lo",
    "range_hi",
    "normal",
    "discrepancy",
    "discrepancy_delay",
    "delay",
    "bypass_max",
    "bypass_time",
    "override",
    "override_time",
    "enable",
    "notes",
)
REQUIRED_COLUMNS = ("no", "tag", "description", "signal", "source", "vote", "trip_on", "delay")
AI_REQUIRED_COLUMNS = ("setpoint", "units", "range_lo", "range_hi", "normal")
AI_ONLY_COLUMNS = ("setpoint", "hyst", "units", "range_lo", "range_hi", "normal", "discrepancy", "discrepancy_delay")

_ARCH_BY_TEXT = {text: arch for arch, text in ARCH_TEXT.items() if arch in ARCH_NM}
_POLICY_BY_TEXT = {text: policy for policy, text in POLICY_TEXT.items()}
_SAFE_BY_WORD = {word: state for state, words in SAFE_STATE_WORDS.items() for word in words}
RESERVED_TAGS = frozenset({"COUNT"})  # CAUSE_COUNT, EFFECT_COUNT


@dataclass
class _Ctx:
    """Сообщения проверки."""

    diags: list[Diagnostic] = field(default_factory=list)

    def error(self, code: str, row: int | None, col: int | None, message: str, hint: str) -> None:
        self.diags.append(Diagnostic(code, message, hint, row, col))

    def warn(self, code: str, row: int | None, col: int | None, message: str, hint: str) -> None:
        self.diags.append(Diagnostic(code, message, hint, row, col))

    @property
    def count(self) -> int:
        return len([d for d in self.diags if d.is_error])


@dataclass
class _Draft:
    """Причина в процессе разбора: значения ячеек и признак ошибок в строке."""

    row: GridRow
    cols: dict[str, int]
    ok: bool = True

    def text(self, name: str) -> str:
        col = self.cols.get(name)
        return self.row.cell(col) if col is not None else ""

    def col(self, name: str) -> int | None:
        return self.cols.get(name)


@dataclass(frozen=True)
class Result:
    """Итог проверки: модель (если нет ошибок) и сообщения в порядке строк файла."""

    matrix: Matrix | None
    diagnostics: tuple[Diagnostic, ...]

    @property
    def errors(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.is_error]

    @property
    def warnings(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if not d.is_error]


def load(path: Path) -> Result:
    """Прочитать и проверить файл матрицы. Нечитаемый файл — одно сообщение CEM-E001/E009."""
    try:
        grid = read_grid(path)
    except MatrixFileError as exc:
        return Result(None, (exc.diagnostic,))
    return parse_grid(grid)


# --- разделы ---------------------------------------------------------------------------------
def parse_grid(grid: Grid) -> Result:
    """Проверить сетку и построить модель."""
    ctx = _Ctx()
    sections = _split_sections(grid, ctx)
    if sections is None:
        return Result(None, tuple(sorted(ctx.diags, key=sort_key)))
    header_mark, header_rows, matrix_mark_row, matrix_rows = sections
    header = _parse_header(header_mark, header_rows, ctx)
    test_step = header.test_step_ms if header is not None else limits.DEFAULT_TEST_STEP_MS
    parsed = _parse_matrix(matrix_mark_row, matrix_rows, test_step, ctx)
    matrix: Matrix | None = None
    if parsed is not None and header is not None and ctx.count == 0:
        causes, effects, effect_cols, hdr_row = parsed
        _check_cross(header, causes, effects, effect_cols, hdr_row, header_mark, ctx)
        if ctx.count == 0:
            matrix = Matrix(header, tuple(causes), tuple(effects), grid.digest())
            _check_stimuli_overlap(matrix, ctx)
    return Result(matrix if ctx.count == 0 else None, tuple(sorted(ctx.diags, key=sort_key)))


def _split_sections(grid: Grid, ctx: _Ctx) -> tuple[GridRow, list[GridRow], GridRow, list[GridRow]] | None:
    header_mark: GridRow | None = None
    matrix_mark_row: GridRow | None = None
    header_rows: list[GridRow] = []
    matrix_rows: list[GridRow] = []
    for row in grid.rows:
        marker = row.first.casefold()
        if marker == "[header]":
            if header_mark is not None:
                ctx.error("CEM-E002", row.line, 1, "раздел [header] повторяется", "оставьте один раздел [header]")
            elif matrix_mark_row is not None:
                ctx.error(
                    "CEM-E002", row.line, 1, "раздел [header] после [matrix]", "перенесите [header] в начало файла"
                )
            else:
                header_mark = row
            continue
        if marker == "[matrix]":
            if matrix_mark_row is not None:
                ctx.error("CEM-E002", row.line, 1, "раздел [matrix] повторяется", "оставьте один раздел [matrix]")
            else:
                matrix_mark_row = row
            continue
        if matrix_mark_row is not None:
            matrix_rows.append(row)
        elif header_mark is not None:
            header_rows.append(row)
        else:
            ctx.error(
                "CEM-E002",
                row.line,
                1,
                "строка до раздела [header]",
                "начните файл строкой [header]; пояснения оформляйте комментариями (# в первой ячейке)",
            )
    if header_mark is None:
        ctx.error("CEM-E002", None, None, "нет раздела [header]", "добавьте строку [header] и ключи шапки (9.2)")
    if matrix_mark_row is None:
        ctx.error("CEM-E002", None, None, "нет раздела [matrix]", "добавьте строку [matrix] после шапки")
    if header_mark is None or matrix_mark_row is None:
        return None
    return header_mark, header_rows, matrix_mark_row, matrix_rows


def _parse_header(mark: GridRow, rows: list[GridRow], ctx: _Ctx) -> Header | None:
    values: dict[str, tuple[str, GridRow]] = {}
    errors_before = ctx.count
    for row in rows:
        key = row.first
        if len(row.cells) > 2:
            ctx.error(
                "CEM-E003",
                row.line,
                3,
                f"лишние ячейки в строке ключа «{key}»",
                "в [header] — только две ячейки: ключ и значение",
            )
        if key not in HEADER_KEYS:
            ctx.error(
                "CEM-E003",
                row.line,
                1,
                f"неизвестный ключ «{key}»",
                "допустимые ключи: " + ", ".join(HEADER_KEYS),
            )
            continue
        if key in values:
            ctx.error(
                "CEM-E003",
                row.line,
                1,
                f"ключ «{key}» повторяется (первый — строка {values[key][1].line})",
                "оставьте одну строку ключа",
            )
            continue
        values[key] = (row.cell(2), row)
    for key, required in HEADER_KEYS.items():
        if required and key not in values:
            ctx.error("CEM-E003", mark.line, 1, f"нет обязательного ключа «{key}»", f"добавьте строку {key};<значение>")
        elif required and not values[key][0]:
            ctx.error("CEM-E014", values[key][1].line, 2, f"пустое значение ключа «{key}»", "заполните значение")

    def get(key: str) -> tuple[str, int | None]:
        if key in values:
            return values[key][0], values[key][1].line
        return "", None

    fmt, line = get("format")
    if fmt and fmt != FORMAT_ID:
        ctx.error("CEM-E004", line, 2, f"формат «{fmt}» не поддерживается", f"укажите format;{FORMAT_ID}")
    date, line = get("date")
    if date and not is_iso_date(date):
        ctx.error("CEM-E004", line, 2, f"дата «{date}» не в формате ГГГГ-ММ-ДД", "запишите дату как 2026-10-16")
    for key in ("object", "document", "revision"):
        text, line = get(key)
        if text and not is_ascii_text(text):
            ctx.error(
                "CEM-E004",
                line,
                2,
                f"«{key}» не ASCII: «{text}»",
                "используйте латиницу, цифры и знаки ASCII (значение попадает в заголовки ST)",
            )
    start_tripped = True
    text, line = get("start_tripped")
    if text:
        parsed = parse_bool(text)
        if parsed is None:
            ctx.error("CEM-E029", line, 2, f"start_tripped: «{text}» — не логическое значение", _BOOL_HINT)
        else:
            start_tripped = parsed
    test_step = limits.DEFAULT_TEST_STEP_MS
    text, line = get("test_step")
    if text:
        try:
            test_step = parse_duration_ms(text)
        except DurationError as exc:
            ctx.error("CEM-E021", line, 2, f"test_step: {exc}", _DURATION_HINT)
            test_step = limits.DEFAULT_TEST_STEP_MS
        else:
            if test_step <= 0:
                ctx.error("CEM-E021", line, 2, "test_step должен быть больше 0", "укажите шаг, например 100ms")
                test_step = limits.DEFAULT_TEST_STEP_MS
    tags: dict[str, str | None] = {}
    for key in ("reset_tag", "bypass_permit_tag", "override_permit_tag"):
        text, line = get(key)
        if text and not is_tag(text):
            ctx.error("CEM-E012", line, 2, f"{key}: тег «{text}» не по правилу 9.3", _TAG_HINT)
            tags[key] = None
        else:
            tags[key] = text or None
    if ctx.count > errors_before:
        return None
    return Header(
        format=get("format")[0],
        object=get("object")[0],
        object_name=get("object_name")[0],
        title=get("title")[0],
        document=get("document")[0],
        revision=get("revision")[0],
        date=get("date")[0],
        author=get("author")[0],
        start_tripped=start_tripped,
        test_step_ms=test_step,
        reset_tag=tags["reset_tag"],
        bypass_permit_tag=tags["bypass_permit_tag"],
        override_permit_tag=tags["override_permit_tag"],
    )


_BOOL_HINT = "запишите yes/no, да/нет, 1/0 или true/false"
_DURATION_HINT = "запишите длительность как 500ms, 2s, 1.5s, 15m или 8h (без пробела)"
_TAG_HINT = "тег — заглавные латинские буквы и цифры, первая — буква, до 24 символов, без «-», «_» и пробелов"


# --- раздел [matrix] ---------------------------------------------------------------------------
def _parse_matrix(
    mark: GridRow, rows: list[GridRow], test_step: int, ctx: _Ctx
) -> tuple[list[Cause], list[Effect], dict[int, int], GridRow] | None:
    hdr_index = next((i for i, row in enumerate(rows) if row.first == HEADER_FIRST), None)
    if hdr_index is None:
        ctx.error(
            "CEM-E005",
            mark.line,
            1,
            "в [matrix] нет строки заголовков причин (первая ячейка «no»)",
            "добавьте строку с именами колонок причин, начиная с no, и ячейкой >>",
        )
        return None
    hdr = rows[hdr_index]
    marks = [col for col, value in enumerate(hdr.cells, 1) if value == LABEL_MARK]
    if not marks:
        ctx.error(
            "CEM-E005",
            hdr.line,
            len(hdr.cells) + 1,
            "в строке заголовков нет ячейки >>",
            "поставьте >> после последней колонки причин: её колонка — колонка меток",
        )
        return None
    if len(marks) > 1:
        ctx.error("CEM-E005", hdr.line, marks[1], "ячеек >> в строке заголовков несколько", "оставьте одну ячейку >>")
        return None
    label_col = marks[0]
    cols = _parse_cause_columns(hdr, label_col, ctx)
    for col in range(label_col + 1, len(hdr.cells) + 1):
        if hdr.cell(col):
            ctx.error(
                "CEM-E007",
                hdr.line,
                col,
                "значение правее колонки меток в строке заголовков",
                "строка заголовков заканчивается ячейкой >>",
            )
    attr_rows = rows[:hdr_index]
    cause_rows = rows[hdr_index + 1 :]
    effects, effect_cols = _parse_effects(mark, hdr, attr_rows, label_col, ctx)
    last_col = label_col + len(effect_cols)
    for row in [*attr_rows, *cause_rows]:
        for col in range(last_col + 1, len(row.cells) + 1):
            if row.cell(col):
                ctx.error(
                    "CEM-E007",
                    row.line,
                    col,
                    "значение правее последнего следствия",
                    "последнее следствие — последняя колонка с effect_tag; уберите лишние значения",
                )
                break
    if cols is None:
        return None
    causes = _parse_causes(cause_rows, cols, label_col, effect_cols, test_step, ctx)
    if not cause_rows:
        ctx.error(
            "CEM-E010", hdr.line, 1, "в матрице нет ни одной причины", "добавьте строки причин после строки заголовков"
        )
    return causes, effects, effect_cols, hdr


def _parse_cause_columns(hdr: GridRow, label_col: int, ctx: _Ctx) -> dict[str, int] | None:
    cols: dict[str, int] = {}
    ok = True
    for col in range(1, label_col):
        name = hdr.cell(col)
        if not name:
            continue
        if name not in CAUSE_COLUMNS:
            ctx.error(
                "CEM-E008",
                hdr.line,
                col,
                f"неизвестная колонка причин «{name}»",
                "имена колонок — строчными, из таблицы 9.2: " + ", ".join(CAUSE_COLUMNS),
            )
            ok = False
        elif name in cols:
            ctx.error("CEM-E008", hdr.line, col, f"колонка «{name}» повторяется", "оставьте одну колонку")
            ok = False
        else:
            cols[name] = col
    for name in REQUIRED_COLUMNS:
        if name not in cols:
            ctx.error("CEM-E008", hdr.line, label_col, f"нет обязательной колонки «{name}»", "добавьте колонку")
            ok = False
    return cols if ok else None


def _parse_effects(
    mark: GridRow, hdr: GridRow, attr_rows: list[GridRow], label_col: int, ctx: _Ctx
) -> tuple[list[Effect], dict[int, int]]:
    labels: dict[str, GridRow] = {}
    for row in attr_rows:
        for col in range(1, label_col):
            if row.cell(col):
                ctx.error(
                    "CEM-E007",
                    row.line,
                    col,
                    "непустая ячейка левее колонки меток в строке атрибута следствий",
                    "в строках атрибутов левее колонки меток ячейки пусты",
                )
                break
        label = row.cell(label_col)
        if label not in EFFECT_LABELS:
            shown = f"«{label}»" if label else "пустая"
            ctx.error(
                "CEM-E006",
                row.line,
                label_col,
                f"неизвестная метка атрибута следствий: {shown}",
                "метки: " + ", ".join(EFFECT_LABELS),
            )
            continue
        if label in labels:
            ctx.error(
                "CEM-E006",
                row.line,
                label_col,
                f"метка «{label}» повторяется (первая — строка {labels[label].line})",
                "оставьте одну строку атрибута",
            )
            continue
        labels[label] = row
    missing = [label for label, required in EFFECT_LABELS.items() if required and label not in labels]
    for label in missing:
        ctx.error(
            "CEM-E006",
            hdr.line,
            label_col,
            f"нет строки атрибута следствий «{label}»",
            f"добавьте строку с меткой {label} в колонке меток выше строки заголовков",
        )
    tag_row = labels.get("effect_tag")
    if tag_row is None:
        return [], {}
    last = max((col for col in range(label_col + 1, len(tag_row.cells) + 1) if tag_row.cell(col)), default=label_col)
    count = last - label_col
    if count == 0:
        ctx.error(
            "CEM-E011",
            tag_row.line,
            label_col + 1,
            "в матрице нет ни одного следствия",
            "впишите теги следствий в строку effect_tag правее колонки меток",
        )
        return [], {}
    if count > limits.SIS_EFFECTS_MAX:
        ctx.error(
            "CEM-E011",
            tag_row.line,
            label_col + limits.SIS_EFFECTS_MAX + 1,
            f"следствий {count} — больше {limits.SIS_EFFECTS_MAX}",
            f"оставьте не больше {limits.SIS_EFFECTS_MAX} следствий (маски WORD)",
        )
        return [], {}
    effects: list[Effect] = []
    effect_cols: dict[int, int] = {}
    for j in range(1, count + 1):
        col = label_col + j
        effect_cols[j] = col

        def attr(label: str, col: int = col) -> tuple[str, int | None]:
            row = labels.get(label)
            return (row.cell(col), row.line) if row is not None else ("", None)

        ok = True
        no_text, line = attr("effect_no")
        no = parse_int_number(no_text) if no_text else None
        if line is not None and not no_text:
            ctx.error("CEM-E014", line, col, f"пустой effect_no следствия {j}", f"впишите {j}")
            ok = False
        elif line is not None and no != j:
            ctx.error(
                "CEM-E011",
                line,
                col,
                f"effect_no «{no_text}»: ожидается {j} — номера по порядку колонок, подряд с 1",
                f"впишите {j}",
            )
            ok = False
        tag, line = attr("effect_tag")
        if not tag:
            ctx.error("CEM-E014", line, col, f"пустой effect_tag следствия {j}", "впишите тег следствия")
            ok = False
        elif not is_tag(tag):
            ctx.error("CEM-E012", line, col, f"тег следствия «{tag}» не по правилу 9.3", _TAG_HINT)
            ok = False
        values: dict[str, str] = {}
        for label in ("effect_description", "actuator"):
            text, line = attr(label)
            if line is not None and not text:
                ctx.error("CEM-E014", line, col, f"пустой {label} следствия {j}", "заполните значение")
                ok = False
            values[label] = text
        state_text, line = attr("safe_state")
        state: SafeState | None = None
        if line is not None and not state_text:
            ctx.error("CEM-E014", line, col, f"пустой safe_state следствия {j}", "заполните значение")
            ok = False
        elif line is not None:
            state = _SAFE_BY_WORD.get(state_text.casefold())
            if state is None:
                ctx.error(
                    "CEM-E028",
                    line,
                    col,
                    f"safe_state «{state_text}» неизвестно",
                    "допустимо: closed/закрыт, open/открыт, stopped/остановлен, off/отключён, alarm/сигнал",
                )
                ok = False
        notes, _ = attr("effect_notes")
        if ok and state is not None and not missing:
            effects.append(Effect(j, tag, values["effect_description"], values["actuator"], state, notes))
    return effects, effect_cols


def _parse_causes(
    rows: list[GridRow],
    cols: dict[str, int],
    label_col: int,
    effect_cols: dict[int, int],
    test_step: int,
    ctx: _Ctx,
) -> list[Cause]:
    causes: list[Cause] = []
    expected_no = 1
    for row in rows:
        label = row.cell(label_col)
        if label:
            expected_no += 1  # строка причины с ошибкой: следующий номер — всё равно следующий
            if label in EFFECT_LABELS:
                ctx.error(
                    "CEM-E006",
                    row.line,
                    label_col,
                    f"строка атрибута «{label}» после строки заголовков причин",
                    "перенесите строки атрибутов следствий выше строки заголовков",
                )
            else:
                ctx.error(
                    "CEM-E007",
                    row.line,
                    label_col,
                    "непустая ячейка в колонке меток в строке причины",
                    "в строках причин колонка меток пуста",
                )
            continue
        named = set(cols.values())
        for col in range(1, label_col):
            if col not in named and row.cell(col):
                ctx.error(
                    "CEM-E008",
                    row.line,
                    col,
                    "значение в колонке без имени",
                    "дайте колонке имя из таблицы 9.2 в строке заголовков или очистите ячейку",
                )
        draft = _Draft(row, cols)
        cause = _parse_cause(draft, expected_no, label_col, effect_cols, test_step, ctx)
        expected_no += 1
        if cause is not None:
            causes.append(cause)
    return causes


def _parse_cause(
    d: _Draft, expected_no: int, label_col: int, effect_cols: dict[int, int], test_step: int, ctx: _Ctx
) -> Cause | None:
    line = d.row.line
    errors_before = ctx.count

    def err(code: str, name: str, message: str, hint: str) -> None:
        ctx.error(code, line, d.col(name), message, hint)

    # no
    no_text = d.text("no")
    no = parse_int_number(no_text) if no_text else None
    if not no_text:
        err("CEM-E014", "no", "пустой номер причины", f"впишите {expected_no}")
    elif no is None:
        err("CEM-E010", "no", f"номер «{no_text}» не целое число", f"впишите {expected_no}")
    elif not 1 <= no <= limits.SIS_CAUSES_MAX:
        err(
            "CEM-E010",
            "no",
            f"номер {no} вне 1..{limits.SIS_CAUSES_MAX}",
            f"оставьте не больше {limits.SIS_CAUSES_MAX} причин (маски WORD)",
        )
    elif no != expected_no:
        err(
            "CEM-E010",
            "no",
            f"номер {no}: ожидается {expected_no} — номера подряд с 1, по возрастанию",
            f"впишите {expected_no}",
        )
    # tag, description
    tag = d.text("tag")
    if not tag:
        err("CEM-E014", "tag", "пустой тег причины", "впишите тег функции ПАЗ, например PSHH101")
    elif not is_tag(tag):
        err("CEM-E012", "tag", f"тег причины «{tag}» не по правилу 9.3", _TAG_HINT)
    description = d.text("description")
    if not description:
        err("CEM-E014", "description", "пустое описание причины", "опишите причину")
    # signal
    signal_text = d.text("signal").casefold()
    signal: Signal | None = None
    if not signal_text:
        err("CEM-E014", "signal", "пустой signal", "впишите ai, di или ext")
    else:
        signal = {"ai": Signal.AI, "di": Signal.DI, "ext": Signal.EXT}.get(signal_text)
        if signal is None:
            err("CEM-E015", "signal", f"signal «{d.text('signal')}» не ai/di/ext", "впишите ai, di или ext")
    # vote, source
    vote: VoteArch | None = None
    vote_text = d.text("vote")
    if signal is Signal.EXT:
        if vote_text != "-":
            err("CEM-E016", "vote", f"для ext vote «{vote_text}» — ожидается «-»", "впишите - (без голосования)")
    elif signal is not None:
        if not vote_text:
            err("CEM-E014", "vote", "пустой vote", "впишите 1oo1, 1oo2, 2oo2 или 2oo3")
        else:
            vote = _ARCH_BY_TEXT.get(vote_text.casefold())
            if vote is None:
                err("CEM-E016", "vote", f"vote «{vote_text}» не из списка", "впишите 1oo1, 1oo2, 2oo2 или 2oo3")
    source_text = d.text("source")
    sources: tuple[str, ...] = ()
    if not source_text:
        err("CEM-E014", "source", "пустой source", "впишите теги каналов через запятую")
    else:
        sources = tuple(part.strip() for part in source_text.split(","))
        bad = [t for t in sources if not is_tag(t)]
        if bad:
            shown = ", ".join(f"«{t}»" for t in bad)
            err("CEM-E012", "source", f"тег канала {shown} не по правилу 9.3", _TAG_HINT)
        seen: set[str] = set()
        for t in sources:
            if t.casefold() in seen:
                err("CEM-E013", "source", f"канал «{t}» указан дважды", "у каждого канала группы свой тег")
            seen.add(t.casefold())
        if signal is Signal.EXT and len(sources) != 1:
            err("CEM-E016", "source", f"для ext тегов {len(sources)}, нужен один", "оставьте один тег входа")
        elif vote is not None and len(sources) != ARCH_NM[vote][0]:
            err(
                "CEM-E016",
                "source",
                f"тегов каналов {len(sources)}, схеме {ARCH_TEXT[vote]} нужно {ARCH_NM[vote][0]}",
                "число тегов в source равно N схемы",
            )
    # policy
    policy: Policy | None = None
    policy_text = d.text("policy")
    if signal is Signal.EXT:
        if policy_text:
            err("CEM-E017", "policy", "policy задана для ext", "оставьте ячейку пустой: у ext нет голосования")
    elif signal is not None:
        policy = _POLICY_BY_TEXT.get(policy_text.casefold()) if policy_text else Policy.VOTE_TRIP
        if policy is None:
            err(
                "CEM-E017",
                "policy",
                f"policy «{policy_text}» неизвестна",
                "впишите vote_trip, degrade_safe или degrade_available (пусто — vote_trip)",
            )
    # trip_on
    trip_text = d.text("trip_on").casefold()
    trip_on: int | None = None
    high: bool | None = None
    if not trip_text:
        err("CEM-E014", "trip_on", "пустой trip_on", "ai — high/low, di/ext — 0/1")
    elif signal is Signal.AI:
        if trip_text in ("high", "low"):
            high = trip_text == "high"
        else:
            err("CEM-E018", "trip_on", f"trip_on «{d.text('trip_on')}» для ai", "для ai впишите high или low")
    elif signal is not None:
        if trip_text in ("0", "1"):
            trip_on = int(trip_text)
        else:
            err(
                "CEM-E018",
                "trip_on",
                f"trip_on «{d.text('trip_on')}» для {signal.value}",
                "для di и ext впишите 0 (требование при 0, норма 1) или 1",
            )
    # поля ai
    analog: Analog | None = None
    if signal is Signal.AI:
        analog = _parse_analog(d, high, test_step, ctx)
    elif signal is not None:
        for name in AI_ONLY_COLUMNS:
            if d.text(name):
                err("CEM-E020", name, f"{signal.value}: заполнено поле ai «{name}»", "очистите ячейку")
    # delay
    delay = _duration(d, "delay", test_step, limits.SIS_DELAY_MAX_MS, ctx, required=True)
    # bypass
    n = ARCH_NM[vote][0] if vote is not None else 1
    bypass_text = d.text("bypass_max")
    bypass_max = parse_uint(bypass_text) if bypass_text else 0
    if bypass_max is None:
        err("CEM-E023", "bypass_max", f"bypass_max «{bypass_text}» не целое ≥ 0", "впишите 0..N-1")
    elif signal is Signal.EXT and bypass_max != 0:
        err("CEM-E023", "bypass_max", "для ext bypass_max должен быть 0", "впишите 0: у ext нет каналов голосования")
    elif vote is not None and bypass_max > n - 1:
        err(
            "CEM-E023",
            "bypass_max",
            f"bypass_max {bypass_max} больше N − 1 = {n - 1}",
            "хотя бы один канал группы всегда голосует",
        )
    bypass_time = _duration(d, "bypass_time", test_step, limits.SIS_BYPASS_MAX_MS, ctx, default=0)
    if signal is Signal.EXT and bypass_time not in (None, 0):
        err("CEM-E023", "bypass_time", "для ext bypass_time должен быть 0s", "впишите 0s")
    elif bypass_max and bypass_time == 0:
        err(
            "CEM-E023",
            "bypass_time",
            f"bypass_max {bypass_max} при bypass_time 0s",
            "задайте bypass_time > 0 или bypass_max 0 (байпас запрещён)",
        )
    # override
    override_text = d.text("override")
    override = parse_bool(override_text) if override_text else False
    if override is None:
        err("CEM-E029", "override", f"override «{override_text}» — не логическое значение", _BOOL_HINT)
    override_time_text = d.text("override_time")
    override_time: int | None = 0
    if override:
        if not override_time_text:
            err("CEM-E022", "override_time", "override = yes без override_time", "задайте длительность обхода > 0")
            override_time = None
        else:
            override_time = _duration(d, "override_time", test_step, limits.SIS_OVERRIDE_MAX_MS, ctx)
            if override_time == 0:
                err("CEM-E022", "override_time", "override_time 0 при override = yes", "задайте длительность > 0")
    elif override is False and override_time_text:
        err("CEM-E022", "override_time", "override_time при override = no", "очистите ячейку или разрешите обход")
    # enable
    enable_text = d.text("enable")
    enable = parse_bool(enable_text) if enable_text else True
    if enable is None:
        err("CEM-E029", "enable", f"enable «{enable_text}» — не логическое значение", _BOOL_HINT)
    # ячейки матрицы
    effects: set[int] = set()
    for j, col in effect_cols.items():
        mark = matrix_mark(d.row.cell(col))
        if mark is None:
            ctx.error(
                "CEM-E025",
                line,
                col,
                f"ячейка матрицы «{d.row.cell(col)}»",
                "впишите X (латиница или кириллица) или оставьте пустой",
            )
        elif mark:
            effects.add(j)
    if ctx.count > errors_before:
        return None
    assert no is not None and signal is not None and delay is not None and bypass_max is not None
    assert bypass_time is not None and override is not None and override_time is not None and enable is not None
    if override_time and delay is not None and override_time < delay:
        ctx.warn(
            "CEM-W003",
            line,
            d.col("override_time"),
            f"override_time {override_time_text} меньше задержки {d.text('delay')}: обход истечёт раньше задержки",
            "проверьте длительность пускового обхода",
        )
    if analog is not None and analog.discrepancy > 0 and n == 1:
        ctx.warn(
            "CEM-W004",
            line,
            d.col("discrepancy"),
            "discrepancy задан для схемы с одним каналом — не действует",
            "очистите ячейку или выберите схему с двумя-тремя каналами",
        )
    if signal is Signal.DI and trip_on == 1:
        ctx.warn(
            "CEM-W006",
            line,
            d.col("trip_on"),
            "di: требование при 1 — вход срабатывает под напряжением: обрыв цепи без контроля линии даёт «норму»",
            "для ПАЗ впишите trip_on = 0 (нормально замкнутый контакт, срабатывание на обесточивание) "
            "или обоснуйте требование при 1 и подтвердите контроль линии (_Ok)",
        )
    return Cause(
        no=no,
        tag=tag,
        description=description,
        signal=signal,
        sources=sources,
        vote=vote,
        policy=policy,
        trip_on=trip_on,
        analog=analog,
        delay_ms=delay,
        bypass_max=bypass_max,
        bypass_time_ms=bypass_time,
        override=override,
        override_time_ms=override_time,
        enable=enable,
        notes=d.text("notes"),
        effects=frozenset(effects),
        row=line,
    )


def _duration(
    d: _Draft,
    name: str,
    test_step: int,
    maximum: int,
    ctx: _Ctx,
    *,
    required: bool = False,
    default: int | None = None,
) -> int | None:
    text = d.text(name)
    line = d.row.line
    if not text:
        if required:
            ctx.error("CEM-E014", line, d.col(name), f"пустой {name}", _DURATION_HINT)
            return None
        return default
    try:
        value = parse_duration_ms(text)
    except DurationError as exc:
        ctx.error("CEM-E021", line, d.col(name), f"{name}: {exc}", _DURATION_HINT)
        return None
    if value < 0:
        ctx.error("CEM-E021", line, d.col(name), f"{name} «{text}» отрицательная", "длительность ≥ 0")
        return None
    if value > maximum:
        ctx.error(
            "CEM-E021",
            line,
            d.col(name),
            f"{name} «{text}» больше предела {_limit_text(maximum)}",
            f"уменьшите до {_limit_text(maximum)} или меньше",
        )
        return None
    if value % test_step:
        ctx.error(
            "CEM-E021",
            line,
            d.col(name),
            f"{name} «{text}» не кратна test_step ({test_step} мс)",
            "сделайте длительность кратной шагу испытаний или уменьшите test_step",
        )
        return None
    return value


def _limit_text(ms: int) -> str:
    return {
        limits.SIS_DELAY_MAX_MS: "10m",
        limits.SIS_OVERRIDE_MAX_MS: "2h",
        limits.SIS_BYPASS_MAX_MS: "12h",
    }.get(ms, f"{ms}ms")


def _parse_analog(d: _Draft, high: bool | None, test_step: int, ctx: _Ctx) -> Analog | None:
    line = d.row.line
    errors_before = ctx.count
    numbers: dict[str, Decimal] = {}
    for name in ("setpoint", "range_lo", "range_hi", "normal"):
        text = d.text(name)
        if name not in d.cols:
            ctx.error("CEM-E008", line, None, f"нет колонки «{name}», обязательной для ai", "добавьте колонку")
            continue
        if not text:
            ctx.error("CEM-E014", line, d.col(name), f"ai: пустой {name}", "впишите число")
            continue
        value = parse_number(text)
        if value is None:
            ctx.error("CEM-E019", line, d.col(name), f"ai: {name} «{text}» не число", "число с точкой или запятой")
            continue
        numbers[name] = value
    for name in ("hyst", "discrepancy"):
        text = d.text(name)
        if not text:
            numbers[name] = Decimal(0)
            continue
        value = parse_number(text)
        if value is None:
            ctx.error("CEM-E019", line, d.col(name), f"ai: {name} «{text}» не число", "число с точкой или запятой")
        elif value < 0:
            ctx.error("CEM-E020", line, d.col(name), f"ai: {name} {text} < 0", "значение ≥ 0")
        else:
            numbers[name] = value
    units = d.text("units")
    if not units:
        ctx.error("CEM-E020", line, d.col("units") or d.col("signal"), "ai: нет units", "впишите единицы измерения")
    disc_delay = _duration(
        d, "discrepancy_delay", test_step, limits.SIS_DELAY_MAX_MS, ctx, default=limits.DEFAULT_DISCREPANCY_DELAY_MS
    )
    if ctx.count > errors_before or high is None or disc_delay is None:
        return None
    lo, hi = numbers["range_lo"], numbers["range_hi"]
    sp, normal, hyst = numbers["setpoint"], numbers["normal"], numbers["hyst"]
    if lo >= hi:
        ctx.error("CEM-E019", line, d.col("range_hi"), f"range_lo {lo} ≥ range_hi {hi}", "range_lo < range_hi")
        return None
    if not lo <= sp <= hi:
        ctx.error("CEM-E019", line, d.col("setpoint"), f"уставка {sp} вне шкалы {lo}…{hi}", "уставка внутри шкалы")
    if not lo <= normal <= hi:
        ctx.error("CEM-E019", line, d.col("normal"), f"normal {normal} вне шкалы {lo}…{hi}", "normal внутри шкалы")
    elif high and not normal < sp - hyst:
        ctx.error(
            "CEM-E019",
            line,
            d.col("normal"),
            f"normal {normal} не на стороне нормы: для high нужно normal < setpoint − hyst = {sp - hyst}",
            "нормальное значение — ниже уставки за полосой гистерезиса",
        )
    elif not high and not normal > sp + hyst:
        ctx.error(
            "CEM-E019",
            line,
            d.col("normal"),
            f"normal {normal} не на стороне нормы: для low нужно normal > setpoint + hyst = {sp + hyst}",
            "нормальное значение — выше уставки за полосой гистерезиса",
        )
    if ctx.count > errors_before:
        return None
    analog = Analog(
        high=high,
        setpoint=sp,
        hyst=hyst,
        units=units,
        range_lo=lo,
        range_hi=hi,
        normal=normal,
        discrepancy=numbers["discrepancy"],
        discrepancy_delay_ms=disc_delay,
    )
    stim = analog.demand_ma
    if not limits.NE43_MEAS_LOW_MA <= stim <= limits.NE43_MEAS_HIGH_MA:
        ctx.error(
            "CEM-E030",
            line,
            d.col("setpoint"),
            f"стимул требования {stim:.2f} мА вне {limits.NE43_MEAS_LOW_MA}…{limits.NE43_MEAS_HIGH_MA} мА",
            "уставка слишком близко к краю шкалы: сдвиньте уставку или расширьте шкалу",
        )
        return None
    return analog


# --- связи между строками и колонками ----------------------------------------------------------
def _check_cross(
    header: Header,
    causes: list[Cause],
    effects: list[Effect],
    effect_cols: dict[int, int],
    hdr_row: GridRow,
    header_mark: GridRow,
    ctx: _Ctx,
) -> None:
    # E013: теги причин, следствий и зарезервированные имена
    seen_cause: dict[str, Cause] = {}
    for cause in causes:
        key = cause.tag.casefold()
        if key in seen_cause:
            ctx.error(
                "CEM-E013",
                cause.row,
                None,
                f"тег причины {cause.tag} повторяется (причина {seen_cause[key].no})",
                "теги причин уникальны без учёта регистра",
            )
        seen_cause[key] = cause
        if cause.tag in RESERVED_TAGS:
            ctx.error(
                "CEM-E013",
                cause.row,
                None,
                f"тег {cause.tag} совпадает с именем CAUSE_COUNT",
                "выберите другой тег",
            )
    seen_effect: dict[str, Effect] = {}
    for effect in effects:
        key = effect.tag.casefold()
        col = effect_cols[effect.no]
        if key in seen_effect:
            ctx.error(
                "CEM-E013",
                hdr_row.line,
                col,
                f"тег следствия {effect.tag} повторяется (следствие {seen_effect[key].no})",
                "теги следствий уникальны без учёта регистра",
            )
        seen_effect[key] = effect
        if key in seen_cause:
            ctx.error(
                "CEM-E013",
                hdr_row.line,
                col,
                f"тег следствия {effect.tag} совпадает с тегом причины {seen_cause[key].no}",
                "теги причин и следствий различаются",
            )
        if effect.tag in RESERVED_TAGS:
            ctx.error("CEM-E013", hdr_row.line, col, f"тег {effect.tag} совпадает с EFFECT_COUNT", "другой тег")
    # E024: общий канал нескольких причин — одинаковые параметры
    first_use: dict[str, Cause] = {}
    for cause in causes:
        for tag in cause.sources:
            key = tag.casefold()
            if key not in first_use:
                first_use[key] = cause
                continue
            other = first_use[key]
            diff = _channel_diff(other, cause)
            if diff:
                ctx.error(
                    "CEM-E024",
                    cause.row,
                    None,
                    f"канал {tag} у причин {other.no} и {cause.no} различается: {diff}",
                    "у общего канала одинаковые signal, units, шкала, normal и (di) trip_on",
                )
    # E013: поля ST_SisIo
    names: dict[str, str] = {}

    def claim(name: str, owner: str, row: int | None, col: int | None) -> None:
        key = name.casefold()
        if key in names and names[key] != owner:
            ctx.error(
                "CEM-E013",
                row,
                col,
                f"поле ST_SisIo {name} получается дважды: {names[key]} и {owner}",
                "переименуйте тег: поля образа ввода-вывода не совпадают",
            )
        names.setdefault(key, owner)

    for cause in causes:
        for tag in cause.sources:
            owner = f"канал {tag}"
            if cause.signal is Signal.AI:
                claim(f"r{tag}_mA", owner, cause.row, None)
            else:
                claim(f"x{tag}", owner, cause.row, None)
                if cause.signal is Signal.DI:
                    claim(f"x{tag}_Ok", owner, cause.row, None)
    for key_name in ("reset_tag", "bypass_permit_tag", "override_permit_tag"):
        tag = getattr(header, key_name)
        if tag:
            claim(f"x{tag}", f"ключ {key_name}", header_mark.line, None)
    for effect in effects:
        claim(effect.io_field, f"следствие {effect.tag}", hdr_row.line, effect_cols[effect.no])
    # E026, E027, W001
    for cause in causes:
        if cause.enable and not cause.effects:
            ctx.error(
                "CEM-E026",
                cause.row,
                None,
                f"включённая причина {cause.tag} без «X»",
                "отметьте следствия причины или выключите её (enable = no)",
            )
        if not cause.enable and cause.effects:
            ctx.warn(
                "CEM-W001",
                cause.row,
                None,
                f"выключенная причина {cause.tag} с «X»: в конфигурацию попадёт, но не сработает",
                "очистите отметки или включите причину",
            )
    for effect in effects:
        if not any(effect.no in cause.effects and cause.enable for cause in causes):
            ctx.error(
                "CEM-E027",
                hdr_row.line,
                effect_cols[effect.no],
                f"следствие {effect.tag} без «X» включённых причин",
                "отметьте причины следствия или удалите колонку",
            )
    # W005
    if not header.bypass_permit_tag and any(cause.bypass_max > 0 for cause in causes):
        ctx.warn(
            "CEM-W005",
            header_mark.line,
            None,
            "нет bypass_permit_tag при разрешённых байпасах: разрешение — только командой HMI",
            "добавьте в [header] ключ bypass_permit_tag",
        )
    if not header.override_permit_tag and any(cause.override for cause in causes):
        ctx.warn(
            "CEM-W005",
            header_mark.line,
            None,
            "нет override_permit_tag при разрешённых обходах: разрешение — только командой HMI",
            "добавьте в [header] ключ override_permit_tag",
        )


def _channel_diff(a: Cause, b: Cause) -> str:
    if a.signal is not b.signal:
        return f"signal {a.signal.value} и {b.signal.value}"
    if a.analog is not None and b.analog is not None:
        pairs: list[tuple[str, object, object]] = [
            ("units", a.analog.units, b.analog.units),
            ("range_lo", a.analog.range_lo, b.analog.range_lo),
            ("range_hi", a.analog.range_hi, b.analog.range_hi),
            ("normal", a.analog.normal, b.analog.normal),
        ]
        for name, left, right in pairs:
            if left != right:
                return f"{name} {left} и {right}"
    if a.signal is Signal.DI and a.trip_on != b.trip_on:
        return f"trip_on {a.trip_on} и {b.trip_on}"
    return ""


def _check_stimuli_overlap(matrix: Matrix, ctx: _Ctx) -> None:
    """CEM-W002: стимул требования причины вызывает требование и других причин."""
    for cause, others in cross_demands(matrix):
        tags = ", ".join(other.tag for other in others)
        ctx.warn(
            "CEM-W002",
            cause.row,
            None,
            f"стимул требования {cause.tag} вызывает и {tags} (общие каналы)",
            f"тест Matrix_{cause.tag}Demand_TripsOwnEffects ожидает срабатывание всех — по эталонной модели",
        )
