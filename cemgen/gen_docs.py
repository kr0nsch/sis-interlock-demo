"""Документы по матрице: ``docs/cause_effect_matrix.md`` и ``.html``, ``docs/truth_tables/VOTING.md``,
``docs/FAT_protocol.md``.

Матрица в документации и в коде строится из одной модели (критерий готовности спецификации):
маски, CRC, схемы и уставки здесь — те же значения, что в ``GVL_SisCfg``.
"""

from __future__ import annotations

from cemgen import DISCLAIMER, fat
from cemgen.describe import bypass_text, degradation_text, override_text, setpoint_text
from cemgen.gen_html import cem_html
from cemgen.gen_truth import KIND_SHORT, tables
from cemgen.model import Matrix, Signal, format_dec
from cemgen.refmodel import arch_channels, degradation, eval_row_states, vote_eval
from cemgen.sisdefs import (
    ARCH_NM,
    ARCH_TEXT,
    POLICIES,
    POLICY_TEXT,
    SAFE_STATE_RU,
    VOTING_ARCHS,
    ChannelState,
    Policy,
    VoteArch,
    st_member,
)
from cemgen.stfmt import HeaderInfo
from cemgen.values import format_duration_ru, format_float_ru

Files = dict[str, str]

CEM_MD = "docs/cause_effect_matrix.md"
CEM_HTML = "docs/cause_effect_matrix.html"
FAT_MD = "docs/FAT_protocol.md"

POLICY_RU = {
    Policy.VOTE_TRIP: "VoteTrip — недостоверный канал голосует «на останов»",
    Policy.DEGRADE_SAFE: "DegradeSafe — недостоверный исключается, голосов нужно меньше",
    Policy.DEGRADE_AVAILABLE: "DegradeAvailable — недостоверный исключается, голосов нужно столько же",
}
STATE_SHORT = {
    ChannelState.NORMAL: "норма",
    ChannelState.DEMAND: "требование",
    ChannelState.INVALID: "недостов.",
    ChannelState.BYPASSED: "байпас",
}


def md_header(info: HeaderInfo) -> str:
    lines = info.generated_lines()
    return "<!-- " + "\n     ".join(lines) + " -->\n"


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _disclaimer() -> str:
    return f"> **Внимание.** {DISCLAIMER[0].upper()}{DISCLAIMER[1:]}"


# --- cause_effect_matrix.md ---------------------------------------------------------------------------------
def cem_md(matrix: Matrix, info: HeaderInfo) -> str:
    h = matrix.header
    out = [md_header(info).rstrip("\n"), "", f"# {h.title}", "", _disclaimer(), ""]
    keys = "; ".join(f"{tag} — {purpose}" for tag, purpose in matrix.key_tags) or "не заданы"
    out += [
        "| | |",
        "|---|---|",
        f"| Документ | {_cell(h.document)}, ревизия {_cell(h.revision)} от {h.date} |",
        f"| Объект | {_cell(h.object)} — {_cell(h.object_name)} |",
        f"| Автор | {_cell(h.author)} |",
        f"| Источник | матрица формата `{h.format}` (CSV или XLSX), SHA-256 сетки `{matrix.grid_digest}` |",
        f"| CRC матрицы | `16#{matrix.crc:04X}` (CRC-16/CCITT-FALSE, DESIGN.md 6.8) |",
        f"| Старт ПЛК | {'все следствия сработали до сброса оператором' if h.start_tripped else 'без срабатывания'} |",
        f"| Ключи и кнопка | {_cell(keys)} |",
        f"| Шаг испытаний | {format_duration_ru(h.test_step_ms)} |",
        "| HTML-представление | [cause_effect_matrix.html](cause_effect_matrix.html) — для печати на A3 и просмотра |",
        "",
        "## Легенда",
        "",
        "- **X** — причина отключает следствие: выход ПАЗ — разрешение (TRUE — под напряжением), "
        "срабатывание — обесточивание (решение D-15).",
        "- Уставки включительны: «≥» — требование при значении не меньше уставки, «≤» — не больше; "
        "снятие требования — за полосой гистерезиса (DESIGN.md, 5.6).",
        "- Схемы MooN: требование, когда M из N достоверных каналов в требовании; при отказе и байпасе "
        "каналов — деградация по политике (таблицы — [VOTING.md](truth_tables/VOTING.md)).",
        "- Задержка — от появления требования до фиксации; фиксация держится до ручного сброса при снятых "
        "причинах; пусковой обход маскирует только фиксацию.",
        "- Пусковой обход: срок — верхняя граница; обход снимается сам, когда требования причины нет "
        "непрерывно время подтверждения нормы (DESIGN.md, 6.4).",
        "",
        "## Матрица",
        "",
    ]
    head = ["№", "Причина", "Описание", "Схема", "Уставка", "Задержка"]
    head += [f"{e.no}<br>{e.tag}" for e in matrix.effects]
    out.append("| " + " | ".join(head) + " |")
    out.append("|" + "---|" * 6 + ":---:|" * len(matrix.effects))
    for c in matrix.causes:
        name = c.tag if c.enable else f"~~{c.tag}~~ (выкл.)"
        row = [
            str(c.no),
            f"**{name}**",
            _cell(c.description),
            c.vote_text,
            setpoint_text(c),
            format_duration_ru(c.delay_ms),
        ]
        row += ["**X**" if e.no in c.effects else "" for e in matrix.effects]
        out.append("| " + " | ".join(row) + " |")
    out.append(
        "| | | Безопасное состояние | | | | " + " | ".join(SAFE_STATE_RU[e.safe_state] for e in matrix.effects) + " |"
    )
    out.append(
        "| | | Маска `wCauseMask` | | | | "
        + " | ".join(f"`16#{matrix.effect_mask(e.no):04X}`" for e in matrix.effects)
        + " |"
    )
    out += ["", "## Причины", ""]
    out.append(
        "| № | Тег | Описание | Вход | Каналы | Схема | Политика | Уставка | Гистерезис | Шкала датчиков | "
        "Норма | Задержка | Вкл. |"
    )
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in matrix.causes:
        if c.analog is not None:
            a = c.analog
            hyst = f"{format_dec(a.hyst)} {a.units}"
            scale = f"{format_dec(a.range_lo)}…{format_dec(a.range_hi)} {a.units}"
            normal = f"{format_dec(a.normal)} {a.units} ({format_float_ru(a.normal_ma)} мА)"
        else:
            hyst, scale = "—", "—"
            normal = "1" if c.trip_on == 0 else "0"
        policy = POLICY_TEXT[c.policy] if c.policy is not None else "—"
        out.append(
            f"| {c.no} | {c.tag} | {_cell(c.description)} | {c.signal.value} | {', '.join(c.sources)} | "
            f"{c.vote_text} | "
            f"{policy} | {setpoint_text(c)} | {hyst} | {scale} | {normal} | {format_duration_ru(c.delay_ms)} | "
            f"{'да' if c.enable else 'нет'} |"
        )
    out += ["", "## Следствия", ""]
    out.append(
        "| № | Тег | Следствие | Исполнительный механизм | Безопасное состояние | Причины | Маска | Примечание |"
    )
    out.append("|---|---|---|---|---|---|---|---|")
    for e in matrix.effects:
        causes = ", ".join(f"{c.no} {c.tag}" for c in matrix.effect_causes(e.no))
        out.append(
            f"| {e.no} | {e.tag} | {_cell(e.description)} | {_cell(e.actuator)} | {SAFE_STATE_RU[e.safe_state]} | "
            f"{causes} | `16#{matrix.effect_mask(e.no):04X}` | {_cell(e.notes)} |"
        )
    out += ["", "## Голосование, байпасы и пусковые обходы", ""]
    out.append(
        "| № | Тег | Схема | Политика | Деградация (по эталонной модели) | Рассогласование | Байпас | Пусковой обход |"
    )
    out.append("|---|---|---|---|---|---|---|---|")
    for c in matrix.causes:
        if c.analog is not None and c.analog.discrepancy > 0 and c.channels > 1:
            disc = (
                f"> {format_dec(c.analog.discrepancy)} {c.analog.units}, "
                f"{format_duration_ru(c.analog.discrepancy_delay_ms)}"
            )
        else:
            disc = "—"
        policy = st_member(c.policy) if c.policy is not None else "—"
        out.append(
            f"| {c.no} | {c.tag} | {c.vote_text} | {policy} | {degradation_text(c)} | {disc} | {bypass_text(c)} | "
            f"{override_text(c)} |"
        )
    out += ["", "## Каналы", ""]
    out.append("| Канал | Вход | Шкала, норма | Поле `ST_SisIo` | Причины |")
    out.append("|---|---|---|---|---|")
    for ch in matrix.channels:
        if ch.analog is not None:
            a = ch.analog
            scale = (
                f"{format_dec(a.range_lo)}…{format_dec(a.range_hi)} {a.units}, норма {format_dec(a.normal)} "
                f"({format_float_ru(a.normal_ma)} мА)"
            )
            fields = f"`r{ch.tag}_mA`"
        elif ch.signal is Signal.DI:
            scale = f"норма {'1' if ch.trip_on == 0 else '0'}, контроль линии"
            fields = f"`x{ch.tag}`, `x{ch.tag}_Ok`"
        else:
            scale = f"норма {'1' if ch.trip_on == 0 else '0'}"
            fields = f"`x{ch.tag}`"
        causes = ", ".join(f"{no} {matrix.cause(no).tag}" for no in ch.causes)
        out.append(f"| {ch.tag} | {ch.signal.value} | {scale} | {fields} | {causes} |")
    notes = [c for c in matrix.causes if c.notes]
    effect_notes = [e for e in matrix.effects if e.notes]
    if notes or effect_notes:
        out += ["", "## Примечания", ""]
        out += [f"- **{c.tag}**: {c.notes}" for c in notes]
        out += [f"- **{e.tag}**: {e.notes}" for e in effect_notes]
    out += [
        "",
        "## Контрольная сумма",
        "",
        f"CRC-16/CCITT-FALSE (полином `16#1021`, начальное `16#FFFF`) по 36 байтам: число причин "
        f"({len(matrix.causes)}), число следствий ({len(matrix.effects)}) и маски 16 следствий, младший байт "
        f"первым — **`16#{matrix.crc:04X}`**. ПЛК пересчитывает её (`F_CemCrc`) и при расхождении с "
        "`CEM_CFG.wMatrixCrc` обесточивает все следствия (решения D-02, D-10).",
    ]
    return "\n".join(out) + "\n"


# --- VOTING.md ---------------------------------------------------------------------------------------------------
def _arch_name(arch: VoteArch) -> str:
    return ARCH_TEXT[arch]


def voting_md(matrix: Matrix, info: HeaderInfo) -> str:
    out = [md_header(info).rstrip("\n"), "", "# Таблицы истинности голосования MooN", "", _disclaimer(), ""]
    all_tables = tables()
    level1 = [t for t in all_tables if t.level == 1]
    level2 = [t for t in all_tables if t.level == 2]
    out += [
        "Таблицы считает эталонная модель `cemgen` (перенос псевдокода DESIGN.md, 5.2 на Python); те же байты "
        "записаны в `tests/GVLs/Generated/GVL_VoteTruthTable.gvl.st` и проверяются набором "
        "`FB_VoteTruth_Test` на настоящих `F_VoteEval` и `FB_Voting`.",
        "",
        f"- Уровень 1 — `F_VoteEval`: {len(level1)} таблиц, {sum(len(t.values) for t in level1)} строк.",
        f"- Уровень 2 — `FB_Voting`: {len(level2)} таблиц, {sum(len(t.values) for t in level2)} строк "
        "(сочетания «требование × достоверность × запрос байпаса» по каждому каналу).",
        "- Байт результата: бит 0 — `xTrip`, бит 1 — `xDegraded`, биты 2–4 — `eArchEff` (0 None, 1 1oo1, "
        "2 1oo2, 3 2oo2, 4 2oo3, 5 ForcedTrip), биты 5–7 — байпас каналов 1–3 `Active` (уровень 2).",
        "",
        "Политики деградации (`E_DegradePolicy`):",
        "",
        *(f"- {POLICY_RU[p]}" for p in POLICIES),
        "",
        "## 1. Деградация схем (DESIGN.md, 5.3)",
        "",
        "Действующая схема по числу байпасированных (B) и недостоверных (F) каналов. `ForcedTrip` — "
        "требование срабатывания при любых остальных каналах.",
        "",
    ]
    for arch in reversed(VOTING_ARCHS):
        n = ARCH_NM[arch][0]
        out += [
            f"### {_arch_name(arch)}",
            "",
            "| B | F | VoteTrip | DegradeSafe | DegradeAvailable |",
            "|---|---|---|---|---|",
        ]
        for b in range(n + 1):
            for f in range(n + 1 - b):
                cells = [_arch_name(degradation(arch, p, b, f)) for p in POLICIES]
                out.append(f"| {b} | {f} | " + " | ".join(cells) + " |")
        out.append("")
    out += [
        "## 2. Полные таблицы `F_VoteEval`",
        "",
        "Строка — состояния каналов; результат каждой политики: «С» — требование срабатывания (`xTrip`), "
        "«Д» — деградация (`xDegraded`), затем действующая схема. Байт — константа `TT_EVAL_<схема>_<политика>`.",
        "",
    ]
    for arch in VOTING_ARCHS:
        n = arch_channels(arch)
        out.append(f"### {_arch_name(arch)} ({4**n} строк)")
        out.append("")
        head = ["r"] + [f"канал {k + 1}" for k in range(n)] + [st_member(p) for p in POLICIES]
        out.append("| " + " | ".join(head) + " |")
        out.append("|" + "---|" * len(head))
        for row in range(4**n):
            states = eval_row_states(row, n)
            cells = [str(row)] + [STATE_SHORT[states[k]] for k in range(n)]
            for policy in POLICIES:
                res = vote_eval(arch, policy, states)
                flags = ("С" if res.trip else "—") + (" Д" if res.degraded else "")
                cells.append(f"{flags} {_arch_name(res.arch_eff)}")
            out.append("| " + " | ".join(cells) + " |")
        out.append("")
    out += [
        "## 3. Таблицы `FB_Voting` (уровень 2)",
        "",
        "Конфигурация теста: уставка 50.0 (High), гистерезис 0, рассогласование выключено, `tBypassMax = T#1H`, "
        "`uiMaxBypass = MIN(1, N − 1)`, ключ байпасов включён, время не меняется. Строка `r`: для канала k биты "
        "3(k − 1) — требование (DI: `axDi := FALSE`, AI: 60.0 вместо 40.0), +1 — достоверность, +2 — запрос "
        "байпаса. На строку — два вызова одного экземпляра: без запросов байпаса и с полной строкой.",
        "",
        "| Константа | Схема | Политика | Вход | Строк | Тест |",
        "|---|---|---|---|---|---|",
    ]
    for t in level2:
        assert t.kind is not None
        out.append(
            f"| `{t.const}` | {_arch_name(t.arch)} | {st_member(t.policy)} | {KIND_SHORT[t.kind]} | {len(t.values)} | "
            f"`{t.test_name}` |"
        )
    out += ["", "Тесты уровня 1:", ""]
    out += [f"- `{t.test_name}` — `{t.const}`, {len(t.values)} строк" for t in level1]
    return "\n".join(out) + "\n"


def generate_docs(matrix: Matrix) -> Files:
    info = HeaderInfo.of(matrix)
    return {
        CEM_MD: cem_md(matrix, info),
        CEM_HTML: cem_html(matrix, info),
        "docs/truth_tables/VOTING.md": voting_md(matrix, info),
        FAT_MD: fat.render(matrix, md_header(info)),
    }
