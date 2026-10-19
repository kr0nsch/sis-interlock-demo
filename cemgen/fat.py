"""Протокол испытаний в стиле FAT (DESIGN.md, 12.7): шаги, автотесты и отчёт по прогону.

Шаги строятся по матрице и эталонной модели; один и тот же список используется для
``docs/FAT_protocol.md`` (графа «Результат» пустая) и для ``docs/FAT_REPORT.md`` (``cemgen fat-report``:
шаг «соответствует», если у каждого шаблона автотестов есть результаты и все они пройдены).

Автотест шага — точное имя теста coUnit или шаблон с ``*`` (``fnmatch``). Шаги таблиц истинности
ссылаются на оба независимых набора: ``VoteTruth_*`` (эталонная модель cemgen) и ``VoteTable_*``
(модель ``tools_project/vote_model.py``, A-10 в ``docs/ASSUMPTIONS.md``).
"""

from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass, field
from pathlib import Path

from cemgen import DISCLAIMER, __version__
from cemgen.model import Cause, Matrix, Signal, format_dec
from cemgen.refmodel import Harness, arch_channels, channel_demand, channel_invalid
from cemgen.sisdefs import ARCH_TEXT, POLICIES, SAFE_STATE_RU, VOTING_ARCHS, st_member
from cemgen.values import format_duration_ru, format_float_ru

RESULT_PASS = "соответствует"
RESULT_FAIL = "не соответствует"
RESULT_NONE = "не выполнялся"
COLUMNS = ("Шаг", "Проверка", "Воздействие", "Ожидаемый результат", "Автотест", "Результат", "Отметка")
TRUTH_KINDS = 2
"""Виды входа в таблицах ``FB_Voting`` (DI и AI, DESIGN.md 12.2)."""
TRUTH_STEP_BASE = 90
"""Шаги таблиц истинности в разделе 4: ``FAT-04-91`` … ``FAT-04-94`` по схемам."""


@dataclass(frozen=True)
class Step:
    """Шаг протокола."""

    id: str
    check: str
    action: str
    expected: str
    autotests: tuple[str, ...] = ()


@dataclass
class Section:
    """Раздел протокола."""

    no: int
    title: str
    intro: str
    steps: list[Step] = field(default_factory=list)


def _stimulus(cause: Cause) -> str:
    if cause.signal is Signal.AI and cause.analog is not None:
        a = cause.analog
        return (
            f"{', '.join(cause.sources)}: {format_float_ru(a.demand_ma)} мА "
            f"({format_dec(a.demand_value)} {a.units}; уставка {'≥' if a.high else '≤'} "
            f"{format_dec(a.setpoint)} {a.units})"
        )
    level = "1" if cause.trip_on == 1 else "0 (размыкание)"
    return f"{', '.join(cause.sources)}: {level}"


def _effects_words(matrix: Matrix, cause: Cause) -> str:
    parts = [f"{matrix.effect(j).tag} — {SAFE_STATE_RU[matrix.effect(j).safe_state]}" for j in sorted(cause.effects)]
    others = [e.tag for e in matrix.effects if e.no not in cause.effects]
    text = "; ".join(parts)
    if others:
        text += f"; {', '.join(others)} — под напряжением"
    return text


def _channel_invalid_expected(matrix: Matrix, cause: Cause) -> str:
    """Ожидаемое при обрыве канала 1 и требовании канала 2 — по эталонной модели."""
    h = Harness(matrix)
    h.arm()
    name, value = channel_invalid(cause, 1)
    h.io[name] = value
    h.cycle()
    h.run(cause.delay_ms, matrix.header.test_step_ms)
    vs = h.app.vote_sts[cause.no - 1]
    arch = ARCH_TEXT[vs.arch_eff]
    if h.app.cem_sts.latched & cause.bit:
        return f"действующая схема {arch}; срабатывание {cause.tag} через {format_duration_ru(cause.delay_ms)}"
    text = f"действующая схема {arch}, срабатывания нет"
    if cause.channels >= 2:
        name, value = channel_demand(cause, 2)
        h.io[name] = value
        h.cycle()
        h.run(cause.delay_ms, matrix.header.test_step_ms)
        tripped = bool(h.app.cem_sts.latched & cause.bit)
        text += f"; требование {cause.sources[1]} → " + (
            f"срабатывание {cause.tag}" if tripped else "срабатывания нет (нужен ещё один голос)"
        )
    return text


def _truth_steps() -> list[Step]:
    """Таблицы истинности по схемам: оба независимых набора (``VoteTruth_*`` и ``VoteTable_*``)."""
    steps: list[Step] = []
    for no, arch in enumerate(VOTING_ARCHS, TRUTH_STEP_BASE + 1):
        name = ARCH_TEXT[arch]
        n = arch_channels(arch)
        eval_rows = len(POLICIES) * 4**n
        fb_rows = len(POLICIES) * TRUTH_KINDS * 8**n
        steps.append(
            Step(
                f"FAT-04-{no:02d}",
                f"Таблица истинности {name}",
                f"все сочетания состояний {n} кан. (F_VoteEval: 3 политики × {4**n} строк) и входов "
                f"«требование × достоверность × запрос байпаса» (FB_Voting: 3 политики × DI/AI × {8**n} строк)",
                f"строк {eval_rows + fb_rows}; результат совпадает с эталонной моделью cemgen и с независимой "
                "моделью tools_project/vote_model.py",
                (f"VoteTruth_*{name}*", f"VoteTable_*{name}*"),
            )
        )
    return steps


def build_sections(matrix: Matrix) -> list[Section]:
    h = matrix.header
    enabled = matrix.enabled_causes
    s1 = Section(1, "Объект, состав, конфигурация, условия", "Проверяются по документам и сборке, без автотестов.")
    s1.steps = [
        Step(
            "FAT-01-01",
            "Документ и ревизия матрицы",
            "сверка с документом",
            f"{h.document}, ревизия {h.revision} от {h.date}",
        ),
        Step(
            "FAT-01-02",
            "Состав",
            "сверка с матрицей",
            f"{len(matrix.causes)} причин ({len(enabled)} включено), {len(matrix.effects)} следствий",
        ),
        Step(
            "FAT-01-03", "Контрольная сумма матрицы", "CEM_CFG.wMatrixCrc", f"16#{matrix.crc:04X} (CRC-16/CCITT-FALSE)"
        ),
        Step(
            "FAT-01-04",
            "Версия ПО и условия",
            "сборка и прогон",
            f"cemgen {__version__}; CODESYS 3.5.17.30, CODESYS Control Win V3, coUnit 1.2.0.0; время — "
            "PL.FB_FakeTime (подменное)",
        ),
    ]
    s2 = Section(2, "Предварительные проверки", "Старт ПЛК и целостность конфигурации.")
    s2.steps = [
        Step(
            "FAT-02-01",
            "Старт в сработавшем состоянии" if h.start_tripped else "Старт без срабатывания",
            "первый цикл с нормальными входами, затем сброс",
            "все следствия обесточены, первопричина SIS_FIRST_OUT_START; после сброса — под напряжением"
            if h.start_tripped
            else "все следствия под напряжением с первого цикла",
            ("Matrix_Start_*",),
        ),
        Step(
            "FAT-02-02",
            "Целостность конфигурации",
            "F_CemCrc, F_CemCheckCfg; конфигурация по умолчанию; искажённая CRC",
            f"CRC 16#{matrix.crc:04X}, ошибок нет; умолчания и несовпадение CRC — срабатывание всех следствий",
            ("Matrix_GeneratedCfg_PassesChecks", "Cem_DefaultCfg_*", "Cem_CrcMismatch_*"),
        ),
    ]
    s3 = Section(3, "Причины и следствия", "Для каждой причины: требование на всех каналах после взвода стенда.")
    for c in enabled:
        demand_tests = [f"Matrix_{c.tag}Demand_*"]
        if c.delay_ms:
            demand_tests.append(f"Matrix_{c.tag}Delay_*")
        s3.steps.append(
            Step(
                f"FAT-03-{c.no:02d}",
                f"{c.tag} — {c.description}",
                _stimulus(c),
                f"через {format_duration_ru(c.delay_ms)}: {_effects_words(matrix, c)}; первопричина {c.tag}",
                tuple(demand_tests),
            )
        )
    s4 = Section(4, "Голосование и отказ каналов", "Обрыв канала 1, затем требование канала 2; таблицы истинности.")
    for c in enabled:
        if not c.is_voting:
            continue
        policy = st_member(c.policy) if c.policy is not None else ""
        s4.steps.append(
            Step(
                f"FAT-04-{c.no:02d}",
                f"{c.tag}: {c.vote_text}, {policy}",
                f"{c.sources[0]} — {'2,0 мА (обрыв)' if c.signal is Signal.AI else 'контроль линии FALSE'}"
                + (f", затем требование {c.sources[1]}" if c.channels >= 2 else ""),
                _channel_invalid_expected(matrix, c),
                (f"Matrix_{c.tag}ChannelInvalid_*",),
            )
        )
    s4.steps += _truth_steps()
    s5 = Section(5, "Байпасы и пусковые обходы", "Ключи разрешения, сроки и журнал.")
    for c in enabled:
        tests: list[str] = []
        parts: list[str] = []
        expected: list[str] = []
        if c.is_voting:
            tests.append(f"Matrix_{c.tag}Bypass_*")
            if c.bypass_max > 0:
                parts.append(f"байпас {c.sources[0]} на {format_duration_ru(c.bypass_time_ms)}")
                expected.append(
                    f"байпас действует до t0 + {format_duration_ru(c.bypass_time_ms)}, затем истекает (BypassExpired)"
                )
            else:
                parts.append(f"запрос байпаса {c.sources[0]}")
                expected.append("байпас запрещён: Denied, BypassDenied")
        tests.append(f"Matrix_{c.tag}Override_*")
        if c.override:
            clear = format_duration_ru(c.override_clear_ms)
            parts.append(
                f"пусковой обход на {format_duration_ru(c.override_time_ms)} при требовании; норма; "
                "требование снова во время подтверждения нормы"
            )
            expected.append(
                f"обход действует до t0 + {format_duration_ru(c.override_time_ms)}, "
                "затем OverrideExpired и срабатывание; "
                f"при норме обход снимается через {clear} (OverrideCleared), требование во время подтверждения "
                "перезапускает его, срок остаётся верхней границей"
                + (
                    f"; после снятия новое требование — срабатывание через {format_duration_ru(c.delay_ms)}"
                    if c.delay_ms
                    else ""
                )
            )
        else:
            parts.append("запрос пускового обхода")
            expected.append("обход запрещён: OverrideDenied")
        s5.steps.append(Step(f"FAT-05-{c.no:02d}", c.tag, "; ".join(parts), "; ".join(expected), tuple(tests)))
    s5.steps.append(
        Step(
            "FAT-05-99",
            "Логика байпасов и обходов",
            "граничные случаи ФБ",
            "сроки ровно, пределы числа, снятие ключом, повторные запросы, автоснятие обхода при норме и дребезг",
            ("Voting_Bypass_*", "Cem_Override_*"),
        )
    )
    s6 = Section(6, "Первопричина и сброс", "Сброс — только вручную и только при снятых причинах.")
    for index, c in enumerate(enabled):
        nxt = enabled[(index + 1) % len(enabled)]
        tests = [f"Matrix_{c.tag}Reset_*"]
        if nxt.no != c.no:
            tests.append(f"Matrix_FirstOut{c.tag}Then{nxt.tag}_*")
        s6.steps.append(
            Step(
                f"FAT-06-{c.no:02d}",
                f"{c.tag}: сброс и первопричина",
                "сброс при требовании; норма; сброс" + (f"; затем требование {nxt.tag}" if nxt.no != c.no else ""),
                f"сброс отклонён (ResetDenied, блокирует {c.tag}); следствия обесточены до сброса; после сброса — "
                f"под напряжением"
                + (f"; первопричина {c.tag}, {nxt.tag} — среди зафиксированных" if nxt.no != c.no else ""),
                tuple(tests),
            )
        )
    s6.steps.append(
        Step(
            "FAT-06-99",
            "Одновременные причины, логика сброса",
            "две причины фиксируются в одном вызове; граничные случаи ФБ",
            "первопричина — младшая, в маске обе; сброс по фронту кнопки и команде HMI",
            ("Matrix_FirstOutSimultaneous_*", "Cem_Reset*", "Cem_FirstOut_*"),
        )
    )
    s7 = Section(7, "Логика ФБ", "Сводка по наборам граничных тестов (DESIGN.md, 12.3).")
    for no, (pattern, title) in enumerate(
        (
            ("Vote_*", "F_VoteEval и функции схем"),
            ("Voting_*", "FB_Voting: уставки, гистерезис, NaN, байпасы, рассогласование"),
            ("Cem_*", "FB_CauseEffect: задержки, фиксация, обходы, сброс, события"),
            ("Log_*", "FB_SisEventLog: кольцо, номера, очистка"),
            ("Unit_*", "FB_SisUnit: источники требования, время, порядок событий"),
            ("Sis_*", "функции: CRC, биты, NE 43, масштабирование"),
            ("Common_*", "размеры и умолчания типов"),
        ),
        1,
    ):
        s7.steps.append(Step(f"FAT-07-{no:02d}", title, "набор тестов coUnit", "все тесты пройдены", (pattern,)))
    s8 = Section(8, "Замечания и подписи", "")
    return [s1, s2, s3, s4, s5, s6, s7, s8]


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _tests_cell(step: Step) -> str:
    return "<br>".join(f"`{t}`" for t in step.autotests) if step.autotests else "—"


def render(matrix: Matrix, header_comment: str, results: dict[str, tuple[str, str]] | None = None) -> str:
    """``docs/FAT_protocol.md`` (``results`` = None) или ``docs/FAT_REPORT.md``."""
    h = matrix.header
    report = results is not None
    lines = [header_comment.rstrip("\n"), ""]
    title = "Отчёт об испытаниях" if report else "Протокол испытаний"
    lines.append(f"# {title} ПАЗ {h.object} в стиле FAT")
    lines.append("")
    lines.append(f"> **Внимание.** {DISCLAIMER[0].upper()}{DISCLAIMER[1:]}")
    lines.append("")
    lines += [
        "| | |",
        "|---|---|",
        f"| Объект | {_cell(h.object)} — {_cell(h.object_name)} |",
        f"| Матрица | {_cell(h.document)}, ревизия {_cell(h.revision)} от {h.date}, CRC `16#{matrix.crc:04X}` |",
        "| Состав протокола | DESIGN.md, раздел 12.7; автотесты — наборы coUnit (`cds.py test`) |",
    ]
    if not report:
        lines.append(
            "| Как заполнять | графы «Результат» и «Отметка» — после прогона; отчёт по результатам — "
            "`python -m cemgen fat-report` → `docs/FAT_REPORT.md` |"
        )
    lines.append("")
    if report:
        assert results is not None
        counts = {RESULT_PASS: 0, RESULT_FAIL: 0, RESULT_NONE: 0}
        for section in build_sections(matrix):
            for step in section.steps:
                if step.autotests:
                    counts[results.get(step.id, (RESULT_NONE, ""))[0]] += 1
        lines += [
            "## Итог",
            "",
            "| Результат | Шагов |",
            "|---|---|",
            *(f"| {name} | {count} |" for name, count in counts.items()),
            "",
        ]
    for section in build_sections(matrix):
        lines.append(f"## {section.no}. {section.title}")
        lines.append("")
        if section.intro:
            lines += [section.intro, ""]
        if section.no == 8:
            lines += [
                "| № | Замечание | Шаг | Решение | Ответственный | Срок |",
                "|---|---|---|---|---|---|",
                "| | | | | | |",
                "",
                "| Роль | Организация | ФИО | Подпись | Дата |",
                "|---|---|---|---|---|",
                "| Испытания провёл | | | | |",
                "| Заказчик | | | | |",
                "",
            ]
            continue
        lines.append("| " + " | ".join(COLUMNS) + " |")
        lines.append("|" + "---|" * len(COLUMNS))
        for step in section.steps:
            result, note = ("", "")
            if report and step.autotests:
                assert results is not None
                result, note = results.get(step.id, (RESULT_NONE, ""))
            elif report:
                result = "—"
            lines.append(
                f"| {step.id} | {_cell(step.check)} | {_cell(step.action)} | {_cell(step.expected)} | "
                f"{_tests_cell(step)} | {_cell(result)} | {_cell(note)} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


# --- fat-report --------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class CaseResult:
    name: str
    status: str
    message: str


def results_started(path: Path) -> str:
    """Время начала прогона из ``test-results.json`` (поле ``started``) или пусто."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return str(data.get("started") or "")


def load_results(path: Path) -> list[CaseResult]:
    """Результаты ``cds.py test``: ``suites[].cases[].name``, ``status`` (PASS, FAIL, SKIP), ``message``."""
    data = json.loads(path.read_text(encoding="utf-8"))
    cases: list[CaseResult] = []
    for suite in data.get("suites", []):
        for case in suite.get("cases", []):
            cases.append(
                CaseResult(str(case.get("name", "")), str(case.get("status", "")), str(case.get("message") or ""))
            )
    return cases


def step_results(matrix: Matrix, cases: list[CaseResult]) -> dict[str, tuple[str, str]]:
    """Шаг → (результат, отметка): «соответствует», «не соответствует» (сообщение) или «не выполнялся».

    «Соответствует» — только если у каждого шаблона автотестов шага есть результаты и все они PASS:
    шаблон без единого теста (набор не собран или переименован) даёт «не выполнялся» с этим шаблоном.
    """
    out: dict[str, tuple[str, str]] = {}
    for section in build_sections(matrix):
        for step in section.steps:
            if not step.autotests:
                continue
            matched = [c for c in cases if any(fnmatch.fnmatchcase(c.name, pattern) for pattern in step.autotests)]
            missing = [p for p in step.autotests if not any(fnmatch.fnmatchcase(c.name, p) for c in cases)]
            failed = [c for c in matched if c.status == "FAIL"]
            passed = [c for c in matched if c.status == "PASS"]
            if failed:
                first = failed[0]
                out[step.id] = (RESULT_FAIL, f"{first.name}: {first.message}".strip(": "))
            elif missing:
                out[step.id] = (RESULT_NONE, "нет результатов: " + ", ".join(missing))
            elif len(passed) == len(matched):
                out[step.id] = (RESULT_PASS, f"тестов {len(passed)}")
            else:
                out[step.id] = (RESULT_NONE, "")
    return out
