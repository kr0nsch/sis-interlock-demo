"""Раздел «Функции безопасности» в ``docs/SRS.md`` — по матрице причин и следствий.

``docs/SRS.md`` пишется вручную: структура спецификации, общие требования, ссылки. Генератор ведёт
в нём только блок между маркерами :data:`BEGIN` и :data:`END` — сводку и по подразделу на каждую
причину матрицы (SIF): описание, инициирующая причина, голосование, безопасное состояние, байпасы и
обходы, сброс, время реакции, режим работы, интервал проверочных испытаний, SIL, проверки. Так
описание функций в SRS берётся из того же источника, что код и тесты, а ``generate --check``
находит устаревший блок.

Чего нет в матрице (время безопасности процесса, частота запросов, SIL, интервал проверочных
испытаний), генератор не придумывает: эти поля — явные заглушки «вне рамок демо».
"""

from __future__ import annotations

from pathlib import Path

from cemgen.describe import degradation_text, override_text, setpoint_text
from cemgen.fat import build_sections
from cemgen.model import Cause, Matrix, Signal, format_dec
from cemgen.sisdefs import ARCH_NM, SAFE_STATE_RU, Policy
from cemgen.stfmt import GenerationError
from cemgen.values import format_duration_ru

Files = dict[str, str]

SRS_PATH = "docs/SRS.md"
BEGIN = "<!-- cemgen:sif:begin -->"
END = "<!-- cemgen:sif:end -->"

SIL_TEXT = "определяется анализом рисков (LOPA) — вне рамок демо"
DEMAND_MODE_TEXT = (
    "предварительно — режим с низкой частотой запросов; подтверждается анализом опасностей и рисков "
    "(частота запросов в демо не оценивалась)"
)
PROOF_TEST_TEXT = (
    "_не задан_ — определяется при проектировании расчётом средней вероятности отказа по запросу "
    "(PFDavg) для выбранной аппаратуры; вне рамок демо"
)
RESPONSE_TARGET_TEXT = (
    "_не задано_ — выводится из времени безопасности процесса по результатам анализа опасностей; вне рамок демо"
)
EVENTS_TEXT = "по результатам анализа опасностей (HAZOP) — вне рамок демо"
POLICY_WORDS = {
    Policy.VOTE_TRIP: "VoteTrip — недостоверный канал голосует «на останов»",
    Policy.DEGRADE_SAFE: "DegradeSafe — недостоверный канал исключается, голосов нужно меньше",
    Policy.DEGRADE_AVAILABLE: "DegradeAvailable — недостоверный канал исключается, голосов нужно столько же",
}


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _lower_first(text: str) -> str:
    return text[:1].lower() + text[1:]


def _vote_words(cause: Cause) -> str:
    """«2 из 3 каналов» для голосования, «внешний сигнал» для ext."""
    if cause.vote is None:
        return "внешний сигнал"
    n, m = ARCH_NM[cause.vote]
    return f"{m} из {n} {'канала' if n == 1 else 'каналов'}"


def _condition(cause: Cause) -> str:
    """Условие требования словами."""
    sources = ", ".join(cause.sources)
    if cause.signal is Signal.AI and cause.analog is not None:
        return f"значение {setpoint_text(cause)} по {_vote_words(cause)} ({sources})"
    if cause.signal is Signal.DI:
        return f"сигнал {setpoint_text(cause)} по {_vote_words(cause)} ({sources})"
    return f"внешний сигнал {sources}: {setpoint_text(cause)}"


def _effects_words(matrix: Matrix, cause: Cause) -> str:
    return "; ".join(
        f"{matrix.effect(j).tag} ({_lower_first(matrix.effect(j).description)}) — "
        f"{SAFE_STATE_RU[matrix.effect(j).safe_state]}"
        for j in sorted(cause.effects)
    )


def _effects_short(matrix: Matrix, cause: Cause) -> str:
    return "; ".join(
        f"{matrix.effect(j).tag} — {SAFE_STATE_RU[matrix.effect(j).safe_state]}" for j in sorted(cause.effects)
    )


def _signals(cause: Cause) -> str:
    sources = ", ".join(cause.sources)
    if cause.signal is Signal.AI and cause.analog is not None:
        a = cause.analog
        inputs = "аналоговый вход" if len(cause.sources) == 1 else "аналоговые входы"
        return (
            f"{sources} — {inputs} 4–20 мА, шкала {format_dec(a.range_lo)}…{format_dec(a.range_hi)} {a.units}, "
            f"достоверность по NAMUR NE 43; уставка {setpoint_text(cause)} (включительно), гистерезис "
            f"{format_dec(a.hyst)} {a.units}"
        )
    if cause.signal is Signal.DI:
        inputs = "дискретный вход" if len(cause.sources) == 1 else "дискретные входы"
        return f"{sources} — {inputs} с контролем линии; требование — {setpoint_text(cause)}"
    return f"{sources} — внешний дискретный сигнал без голосования; требование — {setpoint_text(cause)}"


def _voting(cause: Cause) -> str:
    if cause.vote is None or cause.policy is None:
        return "нет: внешняя причина без голосования"
    n, _m = ARCH_NM[cause.vote]
    text = (
        f"{cause.vote_text} ({_vote_words(cause)}); политика деградации {POLICY_WORDS[cause.policy]}; "
        f"{degradation_text(cause)}"
    )
    if n > 1 and cause.analog is not None and cause.analog.discrepancy > 0:
        a = cause.analog
        text += (
            f"; рассогласование каналов > {format_dec(a.discrepancy)} {a.units} дольше "
            f"{format_duration_ru(a.discrepancy_delay_ms)} — сигнализация, на срабатывание не влияет"
        )
    return text


def _bypass(matrix: Matrix, cause: Cause) -> str:
    if not cause.is_voting:
        return "нет (внешняя причина)"
    if cause.bypass_max == 0:
        return "запрещён"
    key = matrix.header.bypass_permit_tag
    permit = f"при ключе {key}" if key else "при разрешении оператора"
    return (
        f"одновременно не больше {cause.bypass_max} кан., срок {format_duration_ru(cause.bypass_time_ms)}, {permit}; "
        "включение, снятие и истечение — в журнале событий"
    )


def _override(matrix: Matrix, cause: Cause) -> str:
    if not cause.override:
        return "не предусмотрен"
    key = matrix.header.override_permit_tag
    permit = f"при ключе {key}" if key else "по разрешению оператора"
    return (
        f"до {override_text(cause)} {permit}: маскирует только фиксацию срабатывания, по истечении — срабатывание, "
        "если требование есть; повторный запрос действующего обхода не продлевает его"
    )


def _reset(matrix: Matrix) -> str:
    key = matrix.header.reset_tag
    how = f"кнопкой {key} или командой оператора" if key else "командой оператора"
    return f"только вручную ({how}) и только при снятом требовании; до сброса следствия остаются в безопасном состоянии"


def _fat_steps(matrix: Matrix) -> dict[int, list[str]]:
    """Номер причины → шаги протокола FAT (разделы 3–6), в которых она проверяется."""
    steps: dict[int, list[str]] = {c.no: [] for c in matrix.causes}
    for section in build_sections(matrix):
        if section.no not in (3, 4, 5, 6):
            continue
        for step in section.steps:
            no = int(step.id.rsplit("-", 1)[1])
            if no in steps:
                steps[no].append(step.id)
    return steps


def _summary(matrix: Matrix) -> list[str]:
    out = [
        "| SIF | Причина | Схема | Уставка | Задержка | Безопасное состояние | Пусковой обход |",
        "|---|---|---|---|---|---|---|",
    ]
    for c in matrix.causes:
        name = f"{c.tag} — {_cell(c.description)}" + ("" if c.enable else " (выключена)")
        out.append(
            f"| SIF-{c.no:02d} | {name} | {c.vote_text} | {setpoint_text(c)} | {format_duration_ru(c.delay_ms)} | "
            f"{_effects_short(matrix, c)} | {override_text(c)} |"
        )
    return out


def _sif(matrix: Matrix, cause: Cause, fat_steps: list[str]) -> list[str]:
    delay = format_duration_ru(cause.delay_ms)
    description = (
        f"{cause.description}. Требование — {_condition(cause)}; через {delay} после появления требования "
        f"ПАЗ переводит процесс в безопасное состояние и держит его до ручного сброса."
    )
    if not cause.enable:
        description += " **В матрице функция выключена (`enable = no`) и не действует.**"
    rows = [
        ("Описание", description),
        ("Инициирующая причина", _signals(cause)),
        ("Инициирующие события", EVENTS_TEXT),
        ("Голосование", _voting(cause)),
        (
            "Безопасное состояние",
            f"{_effects_words(matrix, cause)}. Выходы ПАЗ — разрешения: срабатывание обесточивает выход",
        ),
        ("Байпас канала", _bypass(matrix, cause)),
        ("Пусковой обход", _override(matrix, cause)),
        ("Сброс", _reset(matrix)),
        (
            "Время реакции логики",
            f"задержка {delay} плюс цикл задачи ПЛК и обновление входов и выходов; время срабатывания датчиков и "
            "исполнительных механизмов не учтено",
        ),
        ("Целевое время реакции", RESPONSE_TARGET_TEXT),
        ("Режим работы", DEMAND_MODE_TEXT),
        ("Интервал проверочных испытаний", PROOF_TEST_TEXT),
        ("Целевой SIL", SIL_TEXT),
        (
            "Проверка",
            f"автотесты `Matrix_{cause.tag}*`; протокол FAT — {', '.join(fat_steps) if fat_steps else 'нет шагов'}",
        ),
    ]
    if cause.notes:
        rows.insert(1, ("Примечание матрицы", cause.notes))
    out = [f"### SIF-{cause.no:02d}. {cause.tag} — {_cell(cause.description)}", ""]
    out += ["| Параметр | Значение |", "|---|---|"]
    out += [f"| {name} | {_cell(value)} |" for name, value in rows]
    return out


def sif_block(matrix: Matrix) -> str:
    """Текст между маркерами: сводка функций и подраздел на каждую причину."""
    h = matrix.header
    out = [
        f"<!-- Блок ведёт cemgen по матрице {h.document}, ревизия {h.revision} от {h.date} "
        f"(SHA-256 сетки {matrix.grid_digest}):",
        "     ручные правки перезапишет python -m cemgen generate. -->",
        "",
        f"Функций: {len(matrix.causes)} (включено {len(matrix.enabled_causes)}), следствий: {len(matrix.effects)}, "
        f"CRC матрицы `16#{matrix.crc:04X}`.",
        "",
        *_summary(matrix),
    ]
    fat_steps = _fat_steps(matrix)
    for cause in matrix.causes:
        out += ["", *_sif(matrix, cause, fat_steps[cause.no])]
    return "\n".join(out) + "\n"


def splice(text: str, block: str, path: str = SRS_PATH) -> str:
    """Заменить текст между маркерами на ``block``; маркеров должно быть ровно по одному, по порядку."""
    if text.count(BEGIN) != 1 or text.count(END) != 1 or text.index(BEGIN) > text.index(END):
        raise GenerationError(f"{path}: нужно ровно по одному маркеру {BEGIN} и {END}, в этом порядке")
    head, rest = text.split(BEGIN, 1)
    _old, tail = rest.split(END, 1)
    return f"{head}{BEGIN}\n{block}{END}{tail}"


def spliced_docs(root: Path, matrix: Matrix) -> Files:
    """``docs/SRS.md`` с обновлённым блоком функций; пусто, если файла нет (например, в чужом каталоге)."""
    path = root / SRS_PATH
    if not path.is_file():
        return {}
    return {SRS_PATH: splice(path.read_bytes().decode("utf-8"), sif_block(matrix))}
