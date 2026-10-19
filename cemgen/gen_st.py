"""Генерация ST объекта по матрице: ``src/**/Generated/`` (DESIGN.md, 10.2, 10.4, 10.5).

Все функции возвращают словарь «путь от корня репозитория → текст». Тексты детерминированы:
порядок — по номерам причин, каналов и следствий; дат и случайных значений нет.
"""

from __future__ import annotations

from cemgen import limits
from cemgen.model import Cause, Matrix, Signal, format_dec
from cemgen.refmodel import VotingCfg, bindings, cem_cfg, f32, voting_cfg
from cemgen.sisdefs import ARCH_TEXT, InputKind, LimitDir, Policy, VoteArch, st_enum
from cemgen.stfmt import HeaderInfo, comment_lines, join_lines, pack, st_bool, st_header, st_real, st_time, st_word

SRC_DUT = "src/DUTs/Generated"
SRC_GVL = "src/GVLs/Generated"
SRC_POU = "src/POUs/Generated"

Files = dict[str, str]


def _field(name: str, st_type: str, comment: str, width: int, indent: str = "    ") -> list[str]:
    """Объявление ``name : TYPE;`` с комментарием справа; длинный комментарий — строкой выше."""
    decl = f"{indent}{name.ljust(width)} : {st_type};"
    line = f"{decl}   // {comment}" if comment else decl
    if len(line) <= limits.ST_LINE_MAX:
        return [line]
    return [*comment_lines(comment, indent=indent), decl]


def _const(name: str, st_type: str, value: str, comment: str, width: int) -> list[str]:
    decl = f"    {name.ljust(width)} : {st_type} := {value};"
    line = f"{decl}   // {comment}" if comment else decl
    if len(line) <= limits.ST_LINE_MAX:
        return [line]
    return [*comment_lines(comment, indent="    "), decl]


COMMENT_COLUMN = 96


def _element(items: list[str], indent: str, suffix: str, comment: str, column: int = COMMENT_COLUMN) -> list[str]:
    """Элемент массива-инициализатора на своих строках с комментарием в конце последней строки.

    Комментарии выравниваются по колонке ``COMMENT_COLUMN``; если не помещаются — элемент
    переносится уже, чтобы строка с комментарием не была длиннее ``ST_LINE_MAX``.
    """
    tail = f"// {comment}"
    column = min(column, limits.ST_LINE_MAX - len(tail))
    lines: list[str] = []
    for width in range(column - 3, 40, -4):
        lines = pack(items, indent + "(", indent + "    ", suffix, width=width)
        if len(lines[-1]) + 3 <= column:
            break
    last = lines[-1]
    lines[-1] = last.ljust(column) + tail if len(last) + 3 <= column else f"{last}   {tail}"
    return lines


# --- ST_SisIo ---------------------------------------------------------------------------------------
def st_sisio(matrix: Matrix, info: HeaderInfo) -> Files:
    fields = matrix.io_fields
    width = max(len(f.name) for f in fields)
    lines = st_header(
        info,
        f"образ ввода-вывода ПАЗ объекта {matrix.header.object}: токи датчиков 4–20 мА, дискретные входы "
        "с контролем линии, ключи и кнопка, выходы-разрешения xQ* (TRUE — под напряжением). Поля — по "
        "тегам матрицы (DESIGN.md, 9.3), порядок — первое появление каналов, затем ключи и выходы.",
    )
    lines += ["{attribute 'qualified_only'}", "TYPE ST_SisIo :", "STRUCT"]
    introduced: dict[str, int] = {}
    for channel in matrix.channels:
        introduced.setdefault(channel.tag, channel.causes[0])
    current_group = 0
    section = ""
    for f in fields:
        if f.kind in ("ai", "di", "di_ok", "ext"):
            group = introduced[f.tag]
            if group != current_group:
                cause = matrix.cause(group)
                lines += comment_lines(
                    f"--- {cause.no} {cause.tag}: {cause.description} ({cause.signal.value}, {cause.vote_text}) ---",
                    indent="    ",
                )
                current_group = group
        elif f.kind != section:
            title = {
                "key": "--- ключи и кнопка ---",
                "out": "--- выходы ПАЗ: разрешения, обесточивание на срабатывание ---",
            }
            lines += [f"    // {title[f.kind]}"]
        section = f.kind
        lines += _field(f.name, f.st_type, f.comment, width)
    lines += ["END_STRUCT", "END_TYPE"]
    return {f"{SRC_DUT}/ST_SisIo.dut.st": join_lines(lines)}


# --- GVL_SisCfg -------------------------------------------------------------------------------------
def _cause_items(cause: Cause) -> list[str]:
    items = [
        f"xEnable := {st_bool(cause.enable)}",
        f"eSource := {st_enum(cause.source_kind)}",
        f"tDelay := {st_time(cause.delay_ms)}",
    ]
    if cause.override:
        items += ["xOverrideAllowed := TRUE", f"tOverrideMax := {st_time(cause.override_time_ms)}"]
    return items


def _vote_items(cfg: VotingCfg) -> list[str]:
    if cfg.arch == VoteArch.NONE:
        return ["eArch := E_VoteArch.None"]
    items = [
        f"eArch := {st_enum(VoteArch(cfg.arch))}",
        f"ePolicy := {st_enum(Policy(cfg.policy))}",
        f"eInput := {st_enum(InputKind(cfg.input))}",
    ]
    if cfg.input == InputKind.ANALOG:
        items += [
            f"eLimitDir := {st_enum(LimitDir(cfg.limit_dir))}",
            f"rTripLimit_eu := {st_real(cfg.trip_limit)}",
            f"rHyst_eu := {st_real(cfg.hyst)}",
            f"rDiscrepancyMax_eu := {st_real(cfg.disc_max)}",
            f"tDiscrepancyDelay := {st_time(cfg.disc_delay_ms)}",
        ]
    else:
        items.append(f"xDiHealthy := {st_bool(cfg.di_healthy)}")
    items += [f"tBypassMax := {st_time(cfg.bypass_max_ms)}", f"uiMaxBypass := {cfg.max_bypass}"]
    return items


def _array(items_per_element: list[tuple[list[str], str]], first_indent: str, closing: str) -> list[str]:
    """Элементы массива-инициализатора: каждый на своих строках, комментарий ``// <no> <TAG>``."""
    lines: list[str] = []
    column = min(COMMENT_COLUMN, *(limits.ST_LINE_MAX - len(comment) - 3 for _, comment in items_per_element))
    for index, (items, comment) in enumerate(items_per_element):
        last = index == len(items_per_element) - 1
        suffix = ")" + (closing if last else ",")
        lines += _element(items, first_indent, suffix, comment, column)
    return lines


def gvl_siscfg(matrix: Matrix, info: HeaderInfo) -> Files:
    cfg = cem_cfg(matrix)
    lines = st_header(
        info,
        f"конфигурация ПАЗ объекта {matrix.header.object} из матрицы причин и следствий: номера причин и "
        "следствий, шкалы датчиков, матрица CEM_CFG (с CRC) и группы голосования VOTE_CFG. VAR_GLOBAL "
        "CONSTANT: с HMI не меняется (решение D-09), правка — только через матрицу и генератор.",
    )
    lines += ["{attribute 'qualified_only'}", "VAR_GLOBAL CONSTANT"]
    names = [c.const_name for c in matrix.causes] + [e.const_name for e in matrix.effects]
    names += ["CAUSE_COUNT", "EFFECT_COUNT"]
    for ch in matrix.channels:
        if ch.analog is not None:
            names += [f"AI_{ch.tag}_LO_EU", f"AI_{ch.tag}_HI_EU", f"AI_{ch.tag}_NORMAL_MA"]
    width = max(len(n) for n in names)
    lines.append("    // Номера причин: индекс i строки матрицы, бит маски i − 1")
    for cause in matrix.causes:
        state = "" if cause.enable else " (выключена)"
        lines += _const(cause.const_name, "UINT", str(cause.no), cause.description + state, width)
    lines += _const("CAUSE_COUNT", "UINT", str(len(matrix.causes)), "причин в матрице", width)
    lines.append("    // Номера следствий: индекс j столбца матрицы")
    for effect in matrix.effects:
        lines += _const(effect.const_name, "UINT", str(effect.no), effect.description, width)
    lines += _const("EFFECT_COUNT", "UINT", str(len(matrix.effects)), "следствий в матрице", width)
    if any(ch.analog is not None for ch in matrix.channels):
        lines.append("    // Шкалы датчиков 4–20 мА (инж. ед.) и нормальные токи для демо и тестов")
    for ch in matrix.channels:
        if ch.analog is None:
            continue
        a = ch.analog
        scale = f"{ch.tag}: шкала {format_dec(a.range_lo)}…{format_dec(a.range_hi)} {a.units}"
        lines += _const(f"AI_{ch.tag}_LO_EU", "REAL", st_real(a.range_lo), scale, width)
        lines += _const(f"AI_{ch.tag}_HI_EU", "REAL", st_real(a.range_hi), "", width)
        lines += _const(
            f"AI_{ch.tag}_NORMAL_MA", "REAL", st_real(f32(a.normal_ma)), f"{format_dec(a.normal)} {a.units}", width
        )
    # CEM_CFG
    lines.append("    // Матрица причин и следствий (DESIGN.md, 4.2, 6.8): маска следствия — «X» в его столбце")
    lines.append(
        f"    CEM_CFG : ST_CemCfg := (uiCauseCount := {cfg.cause_count}, uiEffectCount := {cfg.effect_count}, "
        f"xStartTripped := {st_bool(cfg.start_tripped)},"
    )
    lines.append(f"        wMatrixCrc := {st_word(cfg.crc)},")
    lines.append("        astCause := [")
    elements: list[tuple[list[str], str]] = []
    for i in range(limits.SIS_CAUSES_MAX):
        if i < len(matrix.causes):
            cause = matrix.causes[i]
            elements.append((_cause_items(cause), f"{cause.no} {cause.tag}"))
        else:
            elements.append((["xEnable := FALSE"], f"{i + 1} — резерв"))
    lines += _array(elements, "            ", "],")
    lines.append("        astEffect := [")
    elements = []
    for j in range(limits.SIS_EFFECTS_MAX):
        if j < len(matrix.effects):
            effect = matrix.effects[j]
            mask = matrix.effect_mask(effect.no)
            causes = ", ".join(str(c.no) for c in matrix.effect_causes(effect.no))
            elements.append(
                (
                    [f"eSafeState := {st_enum(effect.safe_state)}", f"wCauseMask := {st_word(mask)}"],
                    f"{effect.no} {effect.tag}: {causes}",
                )
            )
        else:
            elements.append((["wCauseMask := 0"], f"{j + 1} — резерв"))
    lines += _array(elements, "            ", "]);")
    # VOTE_CFG
    lines.append("    // Группы голосования по причинам (DESIGN.md, 5); ext — без голосования (eArch := None)")
    lines.append("    VOTE_CFG : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF ST_VotingCfg := [")
    elements = []
    for i in range(limits.SIS_CAUSES_MAX):
        if i < len(matrix.causes):
            cause = matrix.causes[i]
            note = "" if cause.is_voting else " — ext, без голосования"
            elements.append((_vote_items(voting_cfg(cause)), f"{cause.no} {cause.tag}{note}"))
        else:
            elements.append((["eArch := E_VoteArch.None"], f"{i + 1} — резерв"))
    lines += _array(elements, "        ", "];")
    lines.append("END_VAR")
    return {f"{SRC_GVL}/GVL_SisCfg.gvl.st": join_lines(lines)}


# --- GVL_SisIo, GVL_Sis ----------------------------------------------------------------------------------
def gvl_sisio(matrix: Matrix, info: HeaderInfo) -> Files:
    lines = st_header(
        info,
        f"образ ввода-вывода ПАЗ объекта {matrix.header.object}. Поля stIo привязываются к каналам модулей "
        "ввода-вывода; в демо без ввода-вывода PRG_Main ставит нормальные значения (F_SisIoNormal).",
    )
    lines += [
        "{attribute 'qualified_only'}",
        "VAR_GLOBAL",
        "    stIo : ST_SisIo;   // входы датчиков, ключи, кнопка, выходы-разрешения xQ*",
        "END_VAR",
    ]
    return {f"{SRC_GVL}/GVL_SisIo.gvl.st": join_lines(lines)}


def gvl_sis(matrix: Matrix, info: HeaderInfo) -> Files:
    lines = st_header(
        info,
        f"экземпляры ПАЗ объекта {matrix.header.object}: источник времени, журнал событий, приложение ПАЗ "
        "и команды HMI (ST_SisCmd). Вызов — PRG_Sis.",
    )
    lines += [
        "{attribute 'qualified_only'}",
        "VAR_GLOBAL",
        "    fbTime : PL.FB_SystemTime;   // монотонное время LTIME (PL.I_TimeSource)",
        "    fbLog  : FB_SisEventLog;     // журнал событий ПАЗ, кольцо GVL_Const.SIS_LOG_SIZE",
        "    fbApp  : FB_SisApp;          // ПАЗ объекта: привязка, голосование, матрица, выходы",
        "    stCmd  : ST_SisCmd;          // команды HMI: сброс, пусковые обходы, байпасы каналов",
        "END_VAR",
    ]
    return {f"{SRC_GVL}/GVL_Sis.gvl.st": join_lines(lines)}


# --- FB_SisApp -------------------------------------------------------------------------------------------
def fb_sisapp(matrix: Matrix, info: HeaderInfo) -> Files:
    h = matrix.header
    decl = st_header(
        info,
        f"привязка ПАЗ объекта {h.object} к образу ввода-вывода: токи 4–20 мА → инж. ед. и достоверность "
        "по NE 43, дискретные входы и контроль линии → группы голосования по причинам; вызов FB_SisUnit "
        "с конфигурацией GVL_SisCfg; разрешения следствий → выходы xQ*.",
    )
    decl += [
        "FUNCTION_BLOCK FB_SisApp",
        "VAR_INPUT",
        "    itfTime : PL.I_TimeSource;      // 0 — системное время",
        "    itfLog  : I_SisEventSink;       // 0 — без журнала",
        "END_VAR",
        "VAR_IN_OUT",
        "    stIo  : ST_SisIo;               // входы читает, выходы xQ* пишет",
        "    stCmd : ST_SisCmd;              // команды HMI",
        "END_VAR",
        "VAR_OUTPUT",
        "    xTripped   : BOOL := TRUE;                                          // сработало хотя бы одно следствие",
        "    stCemSts   : ST_CauseEffectSts;                                     // состояние матрицы",
        "    astVoteSts : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF ST_VotingSts;   // состояние групп голосования",
        "END_VAR",
        "VAR",
        "    fbUnit : FB_SisUnit;                                                // общий узел ПАЗ",
        "    astIn  : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF ST_VoteIn;       // входы групп по причинам",
        "END_VAR",
    ]
    impl = st_header(info, "", declaration=False)
    impl.append("// 1. Привязка входов по причинам (DESIGN.md, 10.5)")
    current = 0
    for b in bindings(matrix):
        cause = b.cause
        idx = f"astIn[GVL_SisCfg.{cause.const_name}]"
        if cause.no != current:
            current = cause.no
            kinds = {Signal.AI: "ai", Signal.DI: "di", Signal.EXT: "ext"}
            vote = f"{ARCH_TEXT[cause.vote]}, " if cause.vote is not None else ""
            state = "" if cause.enable else " (выключена)"
            impl += comment_lines(
                f"{cause.no} {cause.tag} — {vote}{kinds[cause.signal]}: {', '.join(cause.sources)}{state}"
            )
        if b.channel == 0:
            source = f"NOT stIo.x{b.tag}" if cause.trip_on == 0 else f"stIo.x{b.tag}"
            impl.append(f"{idx}.xExtDemand := {source};")
        elif cause.signal is Signal.AI:
            impl.append(f"{idx}.arAi_eu[{b.channel}] := F_SisAiToEu(rIn_mA := stIo.r{b.tag}_mA,")
            impl.append(f"    rLo_eu := GVL_SisCfg.AI_{b.tag}_LO_EU, rHi_eu := GVL_SisCfg.AI_{b.tag}_HI_EU);")
            impl.append(f"{idx}.axAiValid[{b.channel}] := F_SisNe43Valid(rIn_mA := stIo.r{b.tag}_mA);")
        else:
            impl.append(f"{idx}.axDi[{b.channel}] := stIo.x{b.tag};")
            impl.append(f"{idx}.axDiValid[{b.channel}] := stIo.x{b.tag}_Ok;")
    bypass = f"stIo.x{h.bypass_permit_tag}" if h.bypass_permit_tag else "TRUE"
    override = f"stIo.x{h.override_permit_tag}" if h.override_permit_tag else "TRUE"
    reset = f"stIo.x{h.reset_tag}" if h.reset_tag else "FALSE"
    impl.append("")
    impl.append("// 2. Голосование и матрица (FB_SisUnit)")
    for tag, purpose in matrix.key_tags:
        impl.append(f"//    {tag} — {purpose}")
    if not matrix.key_tags:
        impl.append("//    теги ключей и кнопки не заданы: байпасы и обходы разрешены, кнопки сброса нет")
    impl.append(
        f"fbUnit(astIn := astIn, xBypassPermit := {bypass}, xOverridePermit := {override}, xResetHw := {reset},"
    )
    impl.append("    itfTime := itfTime, itfLog := itfLog, stCmd := stCmd,")
    impl.append("    stCemCfg := GVL_SisCfg.CEM_CFG, astVoteCfg := GVL_SisCfg.VOTE_CFG);")
    impl.append("")
    impl.append("// 3. Выходы: TRUE — под напряжением (разрешение), FALSE — безопасное состояние")
    for effect in matrix.effects:
        impl.append(f"stIo.{effect.io_field} := fbUnit.axEffectOut[GVL_SisCfg.{effect.const_name}];")
    impl += ["xTripped := fbUnit.xTripped;", "stCemSts := fbUnit.stCemSts;", "astVoteSts := fbUnit.astVoteSts;"]
    base = f"{SRC_POU}/FB_SisApp"
    return {f"{base}/FB_SisApp.decl.st": join_lines(decl), f"{base}/FB_SisApp.impl.st": join_lines(impl)}


# --- PRG_Sis, F_SisIoNormal, F_SisIoKeys -------------------------------------------------------------------
def prg_sis(matrix: Matrix, info: HeaderInfo) -> Files:
    decl = st_header(
        info,
        f"цикл ПАЗ объекта {matrix.header.object}: вызов GVL_Sis.fbApp с системным временем, журналом, "
        "образом ввода-вывода и командами HMI. Вызывается из PRG_Main (MainTask).",
    )
    decl += ["PROGRAM PRG_Sis", "VAR", "END_VAR"]
    impl = st_header(info, "", declaration=False)
    impl += [
        "// Привязка входов → голосование → матрица → выходы; порядок событий журнала тот же (DESIGN.md, 2.3)",
        "GVL_Sis.fbApp(itfTime := GVL_Sis.fbTime, itfLog := GVL_Sis.fbLog, stIo := GVL_SisIo.stIo,",
        "    stCmd := GVL_Sis.stCmd);",
    ]
    base = f"{SRC_POU}/PRG_Sis"
    return {f"{base}/PRG_Sis.decl.st": join_lines(decl), f"{base}/PRG_Sis.impl.st": join_lines(impl)}


def f_sisio_normal(matrix: Matrix, info: HeaderInfo) -> Files:
    decl = st_header(
        info,
        "нормальное состояние образа ввода-вывода: все каналы в норме и достоверны, контроль линии "
        "исправен, ключи и кнопка не нажаты; выходы xQ* не трогает. Для демо без ввода-вывода и тестов. "
        "Возвращает TRUE.",
    )
    decl += ["FUNCTION F_SisIoNormal : BOOL", "VAR_IN_OUT", "    stIo : ST_SisIo;   // образ ввода-вывода", "END_VAR"]
    impl = st_header(info, "", declaration=False)
    fields = {f.name: f for f in matrix.io_fields}
    for channel in matrix.channels:
        if channel.analog is not None:
            impl.append(
                f"stIo.r{channel.tag}_mA := GVL_SisCfg.AI_{channel.tag}_NORMAL_MA;"
                f"   // {format_dec(channel.analog.normal)} {channel.analog.units}"
            )
        else:
            impl.append(f"stIo.x{channel.tag} := {st_bool(channel.trip_on == 0)};")
            if f"x{channel.tag}_Ok" in fields:
                impl.append(f"stIo.x{channel.tag}_Ok := TRUE;")
    for tag, purpose in matrix.key_tags:
        impl.append(f"stIo.x{tag} := FALSE;   // {purpose}")
    impl.append("F_SisIoNormal := TRUE;")
    base = f"{SRC_POU}/F_SisIoNormal"
    return {f"{base}/F_SisIoNormal.decl.st": join_lines(decl), f"{base}/F_SisIoNormal.impl.st": join_lines(impl)}


def f_sisio_keys(matrix: Matrix, info: HeaderInfo) -> Files:
    h = matrix.header
    decl = st_header(
        info,
        "ключи и кнопка ПАЗ в образе ввода-вывода: пишет поля ключей разрешения байпасов и обходов и "
        "кнопки «Сброс ПАЗ», если их теги заданы в матрице. TRUE — заданы все три тега.",
    )
    decl += [
        "FUNCTION F_SisIoKeys : BOOL",
        "VAR_INPUT",
        "    xBypassPermit   : BOOL;   // ключ «Разрешение байпасов»",
        "    xOverridePermit : BOOL;   // ключ «Разрешение пусковых обходов»",
        "    xResetPressed   : BOOL;   // кнопка «Сброс ПАЗ» нажата",
        "END_VAR",
        "VAR_IN_OUT",
        "    stIo : ST_SisIo;          // образ ввода-вывода",
        "END_VAR",
    ]
    impl = st_header(info, "", declaration=False)
    pairs = [
        (h.bypass_permit_tag, "xBypassPermit", "bypass_permit_tag"),
        (h.override_permit_tag, "xOverridePermit", "override_permit_tag"),
        (h.reset_tag, "xResetPressed", "reset_tag"),
    ]
    for tag, name, key in pairs:
        if tag:
            impl.append(f"stIo.x{tag} := {name};")
        else:
            impl.append(f"// {key} не задан в матрице: {name} не используется")
    impl.append(f"F_SisIoKeys := {st_bool(all(tag for tag, _, _ in pairs))};")
    base = f"{SRC_POU}/F_SisIoKeys"
    return {f"{base}/F_SisIoKeys.decl.st": join_lines(decl), f"{base}/F_SisIoKeys.impl.st": join_lines(impl)}


def generate_src(matrix: Matrix) -> Files:
    """Все файлы ``src/**/Generated/``."""
    info = HeaderInfo.of(matrix)
    files: Files = {}
    for builder in (st_sisio, gvl_siscfg, gvl_sisio, gvl_sis, fb_sisapp, prg_sis, f_sisio_normal, f_sisio_keys):
        files.update(builder(matrix, info))
    return files
