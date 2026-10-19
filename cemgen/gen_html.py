"""HTML-представление матрицы: ``docs/cause_effect_matrix.html`` (DESIGN.md, 10.2).

Одна самодостаточная страница: встроенные CSS и небольшой скрипт подсветки строки и столбца,
без внешних шрифтов, картинок и библиотек. Светлая и тёмная схемы (``prefers-color-scheme``),
печать на A3 альбомно, повёрнутые заголовки следствий, закреплённые заголовки таблицы,
дисклеймер вверху. Значения — из той же модели, что ``GVL_SisCfg`` и ``cause_effect_matrix.md``.
"""

from __future__ import annotations

from html import escape

from cemgen import DISCLAIMER, __version__
from cemgen.describe import bypass_text, degradation_text, override_text
from cemgen.model import Cause, Matrix, Signal, format_dec
from cemgen.sisdefs import POLICY_SHORT, SAFE_STATE_RU, SafeState, st_member
from cemgen.stfmt import HeaderInfo
from cemgen.values import format_duration_ru, format_float_ru

SAFE_CLASS = {
    SafeState.CLOSED: "closed",
    SafeState.OPEN: "open",
    SafeState.STOPPED: "stopped",
    SafeState.OFF: "off",
    SafeState.ALARM: "alarm",
}

CSS = """
:root {
  color-scheme: light;
  --paper: #ffffff;
  --page: #e9edf2;
  --ink: #17202b;
  --ink-2: #4a5666;
  --ink-3: #7b8796;
  --line: #c6cfda;
  --line-strong: #8d9aab;
  --band: #1f2a37;
  --band-ink: #f4f7fb;
  --band-2: #314155;
  --head: #f2f5f9;
  --zebra: #f8fafc;
  --hl: #fff3c4;
  --hl-x: #ffe28a;
  --x-bg: #c62828;
  --x-ink: #ffffff;
  --x-off: #b9a3a3;
  --warn-bg: #fff4e5;
  --warn-ink: #7a4100;
  --warn-line: #f0b25c;
  --vote-bg: #e7ecf6;
  --vote-ink: #23395d;
  --mono: "Cascadia Mono", Consolas, "SFMono-Regular", Menlo, "Liberation Mono", monospace;
  --sans: "Segoe UI", "Inter", Roboto, "Helvetica Neue", Arial, sans-serif;
  --ss-closed: #1e5aa8;
  --ss-open: #b86e00;
  --ss-stopped: #2f6f62;
  --ss-off: #5d6673;
  --ss-alarm: #b3261e;
}
@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: dark;
    --paper: #151b23;
    --page: #0d1117;
    --ink: #e6edf3;
    --ink-2: #b0bccb;
    --ink-3: #7d8a9b;
    --line: #2c3746;
    --line-strong: #4b5a6e;
    --band: #0b1220;
    --band-ink: #e6edf3;
    --band-2: #1c2a3d;
    --head: #1b2330;
    --zebra: #18202a;
    --hl: #3a3417;
    --hl-x: #5a4a12;
    --x-bg: #e5534b;
    --x-ink: #1a0b0a;
    --x-off: #6e5555;
    --warn-bg: #2b2011;
    --warn-ink: #f0c27a;
    --warn-line: #8a5a1c;
    --vote-bg: #1e2b40;
    --vote-ink: #b8cdf0;
    --ss-closed: #5b9cf0;
    --ss-open: #e0a03a;
    --ss-stopped: #4fb3a0;
    --ss-off: #97a3b3;
    --ss-alarm: #f0726a;
  }
}
* { box-sizing: border-box; }
html { background: var(--page); }
body {
  margin: 0; padding: 18px; background: var(--page); color: var(--ink);
  font: 13px/1.35 var(--sans); -webkit-font-smoothing: antialiased;
}
.sheet {
  max-width: 1680px; margin: 0 auto; background: var(--paper);
  border: 1px solid var(--line-strong); box-shadow: 0 2px 14px rgba(15, 23, 42, .12);
  padding: 18px 20px 14px;
}
/* --- штамп ------------------------------------------------------------------------- */
.titleblock { display: grid; grid-template-columns: 1fr auto; gap: 18px; align-items: stretch;
  border: 2px solid var(--ink); }
.tb-main { padding: 12px 16px; display: flex; flex-direction: column; justify-content: center; gap: 4px; }
.tb-kicker { font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: var(--ink-3); font-weight: 600; }
.tb-main h1 { margin: 0; font-size: 22px; line-height: 1.2; font-weight: 700; }
.tb-sub { color: var(--ink-2); font-size: 14px; }
.tb-stamp { border-collapse: collapse; border-left: 2px solid var(--ink); font-size: 12px; min-width: 440px; }
.tb-stamp th, .tb-stamp td { border-bottom: 1px solid var(--line); padding: 4px 10px; text-align: left;
  white-space: nowrap; }
.tb-stamp tr:last-child th, .tb-stamp tr:last-child td { border-bottom: 0; }
.tb-stamp th { color: var(--ink-3); font-weight: 600; width: 1%; border-right: 1px solid var(--line); }
.tb-stamp td { font-weight: 600; }
.tb-stamp .mono { font-family: var(--mono); font-weight: 600; }
.disclaimer { margin: 12px 0 10px; padding: 8px 12px; border: 1px solid var(--warn-line); border-left-width: 5px;
  background: var(--warn-bg); color: var(--warn-ink); font-size: 12.5px; }
.disclaimer b { letter-spacing: .04em; }
.facts { display: flex; flex-wrap: wrap; gap: 6px 18px; margin: 0 0 10px; color: var(--ink-2); font-size: 12.5px; }
.facts b { color: var(--ink); font-variant-numeric: tabular-nums; }
/* --- матрица ------------------------------------------------------------------------- */
.matrix-scroll { overflow: auto; max-height: calc(100vh - 24px); border: 2px solid var(--ink); }
table.cem { border-collapse: separate; border-spacing: 0; width: 100%; font-variant-numeric: tabular-nums; }
.cem th, .cem td { border-right: 1px solid var(--line); border-bottom: 1px solid var(--line); padding: 5px 7px;
  background: var(--paper); vertical-align: middle; }
.cem thead th { position: sticky; z-index: 3; background: var(--head); }
.cem tr.band th { top: 0; height: 30px; background: var(--band); color: var(--band-ink); font-size: 11.5px;
  letter-spacing: .16em; text-transform: uppercase; font-weight: 700; border-color: var(--band-2); }
.cem tr.band th.band-effects { background: var(--band-2); }
.cem tr.heads th { top: 30px; height: 236px; font-size: 11.5px; color: var(--ink-2); font-weight: 600;
  text-align: left; vertical-align: bottom; }
.cem tr.safe th { top: 266px; height: 28px; font-size: 11px; }
.cem th.sticky-1, .cem td.sticky-1 { position: sticky; left: 0; z-index: 2; }
.cem th.sticky-2, .cem td.sticky-2 { position: sticky; left: 38px; z-index: 2; box-shadow: 1px 0 0 var(--line-strong); }
.cem thead th.sticky-1, .cem thead th.sticky-2 { z-index: 4; }
.c-no { width: 38px; min-width: 38px; text-align: center; color: var(--ink-3); font-weight: 600; }
.c-tag { width: 96px; min-width: 96px; }
.c-tag b { font-family: var(--mono); font-size: 13px; letter-spacing: .01em; }
.c-desc { min-width: 230px; max-width: 320px; }
.c-ch { min-width: 110px; font-family: var(--mono); font-size: 11.5px; color: var(--ink-2); line-height: 1.3; }
.c-vote { min-width: 74px; white-space: nowrap; }
.c-sp { min-width: 104px; white-space: nowrap; font-weight: 600; }
.c-sp small, .c-dly small { font-weight: 400; color: var(--ink-3); }
.c-dly, .c-byp, .c-ovr { white-space: nowrap; text-align: center; }
.c-sum { width: 56px; text-align: center; font-weight: 700; color: var(--ink-2); }
.sig { display: inline-block; margin-top: 3px; padding: 0 5px; border-radius: 3px; font: 600 10px/16px var(--sans);
  letter-spacing: .06em; text-transform: uppercase; color: var(--ink-3); border: 1px solid var(--line); }
.vote { display: inline-block; padding: 1px 7px; border-radius: 10px; background: var(--vote-bg);
  color: var(--vote-ink);
  font: 700 12px/18px var(--mono); }
.pol { display: block; margin-top: 3px; font-size: 10.5px; color: var(--ink-3); letter-spacing: .04em; }
.cem tbody tr:nth-child(even) td { background: var(--zebra); }
.cem td.cell { text-align: center; width: 60px; min-width: 60px; padding: 4px; }
.cem .sep { border-left: 2px solid var(--line-strong); }
.cem th.eff { width: 60px; min-width: 60px; padding: 8px 4px; text-align: center; vertical-align: bottom;
  border-top: 4px solid var(--ss); }
.rot { writing-mode: vertical-rl; transform: rotate(180deg); display: inline-flex; flex-direction: column;
  align-items: flex-start; gap: 2px; max-height: 216px; text-align: left; white-space: normal; line-height: 1.2; }
.rot .eno { color: var(--ink-3); font-size: 10.5px; font-weight: 600; }
.rot b { font: 700 13px/1.1 var(--mono); color: var(--ink); }
.rot .edesc { font-size: 11px; color: var(--ink-2); font-weight: 500; }
.ss { color: #fff; background: var(--ss); border-radius: 3px; padding: 1px 4px; font-weight: 700; font-size: 10.5px;
  white-space: nowrap; display: inline-block; }
.ss-closed { --ss: var(--ss-closed); } .ss-open { --ss: var(--ss-open); } .ss-stopped { --ss: var(--ss-stopped); }
.ss-off { --ss: var(--ss-off); } .ss-alarm { --ss: var(--ss-alarm); }
.cem tr.safe th.safe-label { text-align: right; color: var(--ink-3); font-weight: 600; letter-spacing: .02em; }
.x { display: inline-grid; place-items: center; width: 24px; height: 24px; border-radius: 4px; background: var(--x-bg);
  color: var(--x-ink); font: 800 13px/1 var(--mono); box-shadow: inset 0 -2px 0 rgba(0, 0, 0, .18); }
tr.off td { color: var(--ink-3); }
tr.off .x { background: var(--x-off); }
tr.off .c-tag b { text-decoration: line-through; }
.badge-off { display: inline-block; margin-left: 4px; font-size: 10px; color: var(--ink-3);
  border: 1px solid var(--line);
  border-radius: 3px; padding: 0 4px; }
.cem tfoot td { background: var(--head); font-weight: 700; text-align: center; color: var(--ink-2); }
.cem tfoot td.f-label { text-align: right; font-weight: 600; color: var(--ink-3); }
.cem tfoot .mono { font: 600 11px/1.2 var(--mono); }
.cem .hl-row td, .cem td.hl-col, .cem th.hl-col { background: var(--hl) !important; }
.cem td.hl-col.hl-cross { background: var(--hl-x) !important; }
/* --- под матрицей ---------------------------------------------------------------------- */
.below { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.25fr); gap: 16px; margin-top: 14px; }
.panel h2 { margin: 0 0 6px; font-size: 12px; letter-spacing: .14em; text-transform: uppercase; color: var(--ink-3); }
table.list { border-collapse: collapse; width: 100%; font-size: 12px; }
.list th, .list td { border-bottom: 1px solid var(--line); padding: 4px 6px; text-align: left; vertical-align: top; }
.list th { color: var(--ink-3); font-weight: 600; background: var(--head); }
.list .mono { font-family: var(--mono); }
.legend { display: flex; flex-wrap: wrap; gap: 8px 22px; align-items: center; margin-top: 14px; padding-top: 10px;
  border-top: 1px solid var(--line); color: var(--ink-2); font-size: 12px; }
.legend .item { display: inline-flex; align-items: center; gap: 6px; }
.notes { margin: 10px 0 0; padding-left: 18px; color: var(--ink-2); font-size: 12px; }
.notes li { margin: 2px 0; }
footer { margin-top: 12px; display: flex; justify-content: space-between; gap: 12px; color: var(--ink-3);
  font-size: 11px; border-top: 1px solid var(--line); padding-top: 8px; }
footer .mono { font-family: var(--mono); }
@media (max-width: 900px) {
  body { padding: 8px; }
  .titleblock { grid-template-columns: 1fr; }
  .tb-stamp { border-left: 0; border-top: 2px solid var(--ink); min-width: 0; width: 100%; }
  .below { grid-template-columns: 1fr; }
}
@page { size: A3 landscape; margin: 8mm; }
@media print {
  html, body { background: #fff; padding: 0; }
  body { font-size: 11px; }
  .sheet { box-shadow: none; border: 0; padding: 0; max-width: none; }
  .matrix-scroll { overflow: visible; max-height: none; }
  .cem thead th { position: static; }
  .cem th.sticky-1, .cem td.sticky-1, .cem th.sticky-2, .cem td.sticky-2 { position: static; }
  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
"""

SCRIPT = """
(function () {
  var table = document.querySelector('table.cem');
  if (!table) { return; }
  function clear() {
    table.querySelectorAll('.hl-row, .hl-col, .hl-cross').forEach(function (el) {
      el.classList.remove('hl-row', 'hl-col', 'hl-cross');
    });
  }
  table.addEventListener('mouseover', function (event) {
    var cell = event.target.closest('td, th');
    if (!cell) { return; }
    clear();
    var col = cell.getAttribute('data-col');
    var row = cell.closest('tbody tr');
    if (row) { row.classList.add('hl-row'); }
    if (col) {
      table.querySelectorAll('[data-col="' + col + '"]').forEach(function (el) { el.classList.add('hl-col'); });
      if (row && cell.tagName === 'TD') { cell.classList.add('hl-cross'); }
    }
  });
  table.addEventListener('mouseleave', clear);
})();
"""


def _sep(effect_no: int) -> str:
    """Класс разделителя «причины | следствия» у первого столбца следствий."""
    return " sep" if effect_no == 1 else ""


def _sep_attr(effect_no: int) -> str:
    """Атрибут ``class="sep"`` у первого столбца следствий, иначе пусто."""
    return ' class="sep"' if effect_no == 1 else ""


def _e(text: str) -> str:
    return escape(text, quote=True)


def _setpoint_html(cause: Cause) -> str:
    if cause.analog is not None:
        a = cause.analog
        sign = "≥" if a.high else "≤"
        return f"{sign} {_e(format_dec(a.setpoint))} <small>{_e(a.units)}</small>"
    if cause.trip_on == 0:
        return "размыкание <small>(0)</small>"
    return "замыкание <small>(1)</small>"


def _channels_html(cause: Cause) -> str:
    tags = "<br>".join(_e(t) for t in cause.sources)
    return f'{tags}<br><span class="sig">{cause.signal.value}</span>'


def _vote_html(cause: Cause) -> str:
    if cause.vote is None or cause.policy is None:
        return '<span class="vote">ext</span>'
    policy = st_member(cause.policy)
    return (
        f'<span class="vote">{_e(cause.vote_text)}</span>'
        f'<span class="pol" title="{_e(policy)}">{POLICY_SHORT[cause.policy]} · {_e(policy)}</span>'
    )


def cem_html(matrix: Matrix, info: HeaderInfo) -> str:
    h = matrix.header
    effects = matrix.effects
    links = sum(len(c.effects) for c in matrix.causes if c.enable)
    keys = ", ".join(f"{tag} — {purpose}" for tag, purpose in matrix.key_tags) or "не заданы"
    comment = "\n     ".join(info.generated_lines())
    start = "в сработавшем состоянии до сброса" if h.start_tripped else "без срабатывания"
    out: list[str] = [
        "<!doctype html>",
        '<html lang="ru">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f'<meta name="generator" content="cemgen {__version__}">',
        f"<title>{_e(h.document)} — {_e(h.title)}</title>",
        f"<!-- {comment} -->",
        "<style>" + CSS + "</style>",
        "</head>",
        "<body>",
        '<div class="sheet">',
        '<header class="titleblock">',
        '<div class="tb-main">',
        '<div class="tb-kicker">Матрица причин и следствий ПАЗ · Cause &amp; Effect Matrix</div>',
        f"<h1>{_e(h.object_name)}</h1>",
        f'<div class="tb-sub">{_e(h.title)}</div>',
        "</div>",
        '<table class="tb-stamp">',
        f'<tr><th>Документ</th><td class="mono">{_e(h.document)}</td></tr>',
        f'<tr><th>Объект</th><td class="mono">{_e(h.object)}</td></tr>',
        f"<tr><th>Ревизия</th><td>{_e(h.revision)} от {_e(h.date)}</td></tr>",
        f"<tr><th>Разработал</th><td>{_e(h.author)}</td></tr>",
        f'<tr><th>CRC матрицы</th><td class="mono">16#{matrix.crc:04X}</td></tr>',
        f'<tr><th>SHA-256 сетки</th><td class="mono">{_e(matrix.grid_digest)}</td></tr>',
        f'<tr><th>Формат</th><td class="mono">{_e(h.format)} · cemgen {__version__}</td></tr>',
        "</table>",
        "</header>",
        f'<div class="disclaimer"><b>ВНИМАНИЕ.</b> {_e(DISCLAIMER[0].upper() + DISCLAIMER[1:])} '
        "Объект и все значения вымышленные.</div>",
        '<div class="facts">',
        f"<span>Причин: <b>{len(matrix.causes)}</b> (включено {len(matrix.enabled_causes)})</span>",
        f"<span>Следствий: <b>{len(effects)}</b></span>",
        f"<span>Связей «X»: <b>{links}</b></span>",
        f"<span>Старт ПЛК: <b>{start}</b></span>",
        f"<span>Ключи: <b>{_e(keys)}</b></span>",
        "</div>",
        '<div class="matrix-scroll">',
        '<table class="cem">',
        "<thead>",
        '<tr class="band">',
        '<th class="sticky-1 band-causes" colspan="2">Причины</th>',
        '<th colspan="7" class="band-causes"></th>',
        f'<th colspan="{len(effects)}" class="band-effects sep">Следствия · выходы ПАЗ</th>',
        '<th class="band-effects">Σ</th>',
        "</tr>",
        '<tr class="heads">',
        '<th class="c-no sticky-1">№</th>',
        '<th class="c-tag sticky-2">Тег</th>',
        '<th class="c-desc">Причина</th>',
        '<th class="c-ch">Каналы</th>',
        '<th class="c-vote">Схема</th>',
        '<th class="c-sp">Уставка</th>',
        '<th class="c-dly">Задержка</th>',
        '<th class="c-byp">Байпас</th>',
        '<th class="c-ovr">Пусковой<br>обход</th>',
    ]
    for effect in effects:
        css = SAFE_CLASS[effect.safe_state]
        out.append(
            f'<th class="eff ss-{css}{_sep(effect.no)}" data-col="{effect.no}"><div class="rot">'
            f'<span class="eno">{effect.no}</span>'
            f'<b>{_e(effect.tag)}</b><span class="edesc">{_e(effect.description)}</span></div></th>'
        )
    out.append('<th class="c-sum">Следст-<br>вий</th>')
    out += [
        "</tr>",
        '<tr class="safe">',
        '<th class="sticky-1"></th><th class="sticky-2"></th>',
        '<th colspan="7" class="safe-label">Безопасное состояние →</th>',
    ]
    for effect in effects:
        css = SAFE_CLASS[effect.safe_state]
        out.append(
            f'<th{_sep_attr(effect.no)} data-col="{effect.no}"><span class="ss ss-{css}">'
            f"{SAFE_STATE_RU[effect.safe_state]}</span></th>"
        )
    out += ["<th></th>", "</tr>", "</thead>", "<tbody>"]
    for cause in matrix.causes:
        row_class = "" if cause.enable else ' class="off"'
        title = f' title="{_e(cause.notes)}"' if cause.notes else ""
        off = '<span class="badge-off">выкл.</span>' if not cause.enable else ""
        cells = [
            f"<tr{row_class}{title}>",
            f'<td class="c-no sticky-1">{cause.no}</td>',
            f'<td class="c-tag sticky-2"><b>{_e(cause.tag)}</b>{off}</td>',
            f'<td class="c-desc">{_e(cause.description)}</td>',
            f'<td class="c-ch">{_channels_html(cause)}</td>',
            f'<td class="c-vote">{_vote_html(cause)}</td>',
            f'<td class="c-sp">{_setpoint_html(cause)}</td>',
            f'<td class="c-dly">{_e(format_duration_ru(cause.delay_ms))}</td>',
            f'<td class="c-byp">{_e(bypass_text(cause))}</td>',
            f'<td class="c-ovr">{_e(override_text(cause))}</td>',
        ]
        for effect in effects:
            mark = '<span class="x">X</span>' if effect.no in cause.effects else ""
            cells.append(f'<td class="cell{_sep(effect.no)}" data-col="{effect.no}">{mark}</td>')
        cells.append(f'<td class="c-sum">{len(cause.effects)}</td>')
        cells.append("</tr>")
        out.append("".join(cells))
    out += ["</tbody>", "<tfoot>", '<tr><td class="sticky-1"></td><td class="sticky-2"></td>']
    out.append('<td colspan="7" class="f-label">Причин на следствие</td>')
    for effect in effects:
        out.append(f'<td{_sep_attr(effect.no)} data-col="{effect.no}">{len(matrix.effect_causes(effect.no))}</td>')
    out += ["<td></td></tr>", '<tr><td class="sticky-1"></td><td class="sticky-2"></td>']
    out.append('<td colspan="7" class="f-label">Маска <span class="mono">wCauseMask</span>, 16#</td>')
    for effect in effects:
        out.append(f'<td class="mono{_sep(effect.no)}" data-col="{effect.no}">{matrix.effect_mask(effect.no):04X}</td>')
    out += ["<td></td></tr>", "</tfoot>", "</table>", "</div>"]
    # легенда
    out += [
        '<div class="legend">',
        '<span class="item"><span class="x">X</span> причина отключает следствие (выход обесточивается)</span>',
        '<span class="item"><span class="vote">2oo3</span> схема голосования MooN</span>',
        '<span class="item">VT · DS · DA — политика при отказе канала: VoteTrip, DegradeSafe, DegradeAvailable</span>',
        '<span class="item">≥ / ≤ — уставка включительно</span>',
    ]
    for state, css in SAFE_CLASS.items():
        if any(e.safe_state == state for e in effects):
            out.append(f'<span class="item"><span class="ss ss-{css}">{SAFE_STATE_RU[state]}</span></span>')
    out.append("</div>")
    # таблицы под матрицей
    out += [
        '<section class="below">',
        '<div class="panel">',
        "<h2>Следствия</h2>",
        '<table class="list"><tr><th>№</th><th>Тег</th><th>Исполнительный механизм</th><th>Безопасное</th>'
        "<th>Причины</th></tr>",
    ]
    for effect in effects:
        causes = ", ".join(str(c.no) for c in matrix.effect_causes(effect.no))
        css = SAFE_CLASS[effect.safe_state]
        out.append(
            f'<tr><td>{effect.no}</td><td class="mono">{_e(effect.tag)}</td><td>{_e(effect.actuator)}</td>'
            f'<td><span class="ss ss-{css}">{SAFE_STATE_RU[effect.safe_state]}</span></td><td>{_e(causes)}</td></tr>'
        )
    out += ["</table>", "</div>", '<div class="panel">', "<h2>Голосование и деградация</h2>"]
    out.append(
        '<table class="list"><tr><th>Тег</th><th>Схема</th><th>Деградация (эталонная модель)</th>'
        "<th>Рассогласование</th><th>Норма</th></tr>"
    )
    for cause in matrix.causes:
        if cause.analog is not None and cause.analog.discrepancy > 0 and cause.channels > 1:
            a = cause.analog
            disc = (
                f"&gt; {_e(format_dec(a.discrepancy))} {_e(a.units)}, {_e(format_duration_ru(a.discrepancy_delay_ms))}"
            )
        else:
            disc = "—"
        if cause.analog is not None:
            normal = (
                f"{_e(format_dec(cause.analog.normal))} {_e(cause.analog.units)} "
                f"({_e(format_float_ru(cause.analog.normal_ma))} мА)"
            )
        elif cause.signal is Signal.EXT:
            normal = "1" if cause.trip_on == 0 else "0"
        else:
            normal = ("1" if cause.trip_on == 0 else "0") + ", линия исправна"
        out.append(
            f'<tr><td class="mono">{_e(cause.tag)}</td><td>{_e(cause.vote_text)}</td>'
            f"<td>{_e(degradation_text(cause))}</td><td>{disc}</td><td>{normal}</td></tr>"
        )
    out += ["</table>", "</div>", "</section>"]
    notes = [c for c in matrix.causes if c.notes]
    if notes:
        out.append('<ul class="notes">')
        out += [f"<li><b>{_e(c.tag)}</b> — {_e(c.notes)}</li>" for c in notes]
        out.append("</ul>")
    out += [
        "<footer>",
        f"<span>AUTO-GENERATED by cemgen {__version__} — не редактировать: правьте матрицу и запустите "
        '<span class="mono">python -m cemgen generate</span>. Матрица в коде (GVL_SisCfg) и в документах '
        "строится из одного файла.</span>",
        f'<span class="mono">{_e(h.document)} · rev {_e(h.revision)} · CRC 16#{matrix.crc:04X}</span>',
        "</footer>",
        "</div>",
        "<script>" + SCRIPT + "</script>",
        "</body>",
        "</html>",
    ]
    text = "\n".join(line.rstrip() for line in "\n".join(out).splitlines())
    return text.rstrip("\n") + "\n"
