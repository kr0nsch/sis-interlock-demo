"""Таблицы истинности голосования и их набор coUnit (DESIGN.md, 12.2).

* ``tests/GVLs/Generated/GVL_VoteTruthTable.gvl.st`` — 12 таблиц уровня 1 (``F_VoteEval``,
  300 строк) и 24 таблицы уровня 2 (``FB_Voting``, 3888 строк), ожидаемые байты — от эталонной
  модели;
* ``tests/POUs/Generated/FB_VoteTruth_Test/`` — 36 тестов: каждый перебирает строки своей
  таблицы и сравнивает байт результата с ожидаемым.
"""

from __future__ import annotations

from dataclasses import dataclass

from cemgen.model import Matrix
from cemgen.refmodel import arch_channels, eval_table, fb_table
from cemgen.sisdefs import (
    ARCH_TEXT,
    POLICIES,
    POLICY_SHORT,
    VOTING_ARCHS,
    InputKind,
    Policy,
    VoteArch,
    st_enum,
    st_member,
)
from cemgen.stfmt import HeaderInfo, join_lines, pack, st_byte, st_header

TESTS_GVL = "tests/GVLs/Generated"
TESTS_POU = "tests/POUs/Generated"
SUITE = "FB_VoteTruth_Test"
KINDS: tuple[InputKind, ...] = (InputKind.DISCRETE, InputKind.ANALOG)
KIND_SHORT = {InputKind.DISCRETE: "DI", InputKind.ANALOG: "AI"}

Files = dict[str, str]


@dataclass(frozen=True)
class Table:
    """Таблица истинности: имя константы, теста, параметры и ожидаемые байты."""

    level: int
    arch: VoteArch
    policy: Policy
    kind: InputKind | None
    values: tuple[int, ...]

    @property
    def arch_upper(self) -> str:
        return ARCH_TEXT[self.arch].upper()

    @property
    def const(self) -> str:
        base = f"{self.arch_upper}_{POLICY_SHORT[self.policy]}"
        if self.level == 1:
            return f"TT_EVAL_{base}"
        assert self.kind is not None
        return f"TT_FB_{base}_{KIND_SHORT[self.kind]}"

    @property
    def case(self) -> str:
        """Сегмент имени теста: ``Eval2oo3VT``, ``Fb2oo3VTAI``."""
        arch = ARCH_TEXT[self.arch]
        if self.level == 1:
            return f"Eval{arch}{POLICY_SHORT[self.policy]}"
        assert self.kind is not None
        return f"Fb{arch}{POLICY_SHORT[self.policy]}{KIND_SHORT[self.kind]}"

    @property
    def test_name(self) -> str:
        return f"VoteTruth_{self.case}_MatchesTable"

    @property
    def method(self) -> str:
        return f"{self.case}MatchesTable"

    @property
    def channels(self) -> int:
        return arch_channels(self.arch)


def tables() -> list[Table]:
    """Все 36 таблиц в порядке: уровень 1 по схемам и политикам, затем уровень 2."""
    result: list[Table] = []
    for arch in VOTING_ARCHS:
        for policy in POLICIES:
            result.append(Table(1, arch, policy, None, tuple(eval_table(arch, policy))))
    for arch in VOTING_ARCHS:
        for policy in POLICIES:
            for kind in KINDS:
                result.append(Table(2, arch, policy, kind, tuple(fb_table(arch, policy, kind))))
    return result


def _gvl(info: HeaderInfo, all_tables: list[Table]) -> Files:
    lines = st_header(
        info,
        "таблицы истинности голосования (DESIGN.md, 12.2): ожидаемые байты результата F_VoteEval "
        "(уровень 1) и FB_Voting (уровень 2) для всех схем, политик и видов входа; считает эталонная "
        "модель cemgen. Байт: бит 0 — xTrip, бит 1 — xDegraded, биты 2–4 — eArchEff (0 None, 1 1oo1, "
        "2 1oo2, 3 2oo2, 4 2oo3, 5 ForcedTrip), биты 5–7 — байпас каналов 1–3 Active (уровень 2).",
    )
    lines += ["{attribute 'qualified_only'}", "VAR_GLOBAL CONSTANT"]
    for level in (1, 2):
        if level == 1:
            lines.append("    // Уровень 1 — F_VoteEval: строка r, состояние канала k — (r SHR 2(k − 1)) AND 3:")
            lines.append("    // 0 Normal, 1 Demand, 2 Invalid, 3 Bypassed; каналы k > N — NotUsed")
        else:
            lines.append("    // Уровень 2 — FB_Voting: строка r, биты канала k — 3(k − 1): требование, достоверность,")
            lines.append("    // запрос байпаса; на строку два вызова одного экземпляра (сначала без запросов байпаса)")
        for table in (t for t in all_tables if t.level == level):
            count = len(table.values)
            lines.append(f"    {table.const} : ARRAY[0..{count - 1}] OF BYTE := [")
            items = [st_byte(v) for v in table.values]
            for start in range(0, count, 16):
                chunk = items[start : start + 16]
                last = start + 16 >= count
                lines += pack(chunk, "        ", "        ", "];" if last else ",")
    lines.append("END_VAR")
    return {f"{TESTS_GVL}/GVL_VoteTruthTable.gvl.st": join_lines(lines)}


_COMMON_LOCALS = [
    ("uiRow", "UINT", "строка таблицы"),
    ("bAct", "BYTE", "фактический байт результата"),
    ("bExp", "BYTE", "ожидаемый байт из таблицы"),
    ("xMiss", "BOOL", "строка не совпала"),
    ("xFirst", "BOOL", "первая несовпавшая строка"),
    ("uiMismatch", "UINT", "несовпавших строк"),
    ("uiFirstRow", "UINT", "первая несовпавшая строка"),
    ("bFirstExp", "BYTE", "ожидаемый байт первой несовпавшей строки"),
    ("bFirstAct", "BYTE", "фактический байт первой несовпавшей строки"),
]


def _var_block(entries: list[tuple[str, str, str]], section: str = "VAR") -> list[str]:
    width = max(len(name) for name, _, _ in entries)
    type_width = max(len(st_type) for _, st_type, _ in entries)
    lines = [section]
    for name, st_type, comment in entries:
        lines.append(f"    {name.ljust(width)} : {(st_type + ';').ljust(type_width + 1)}   // {comment}")
    lines.append("END_VAR")
    return lines


def _compare_tail(table: Table) -> list[str]:
    # без ветвлений: первая несовпавшая строка запоминается через SEL
    return [
        f"    bExp := GVL_VoteTruthTable.{table.const}[uiRow];",
        "    xMiss := bAct <> bExp;",
        "    xFirst := xMiss AND uiMismatch = 0;",
        "    uiFirstRow := SEL(xFirst, uiFirstRow, uiRow);",
        "    bFirstExp := SEL(xFirst, bFirstExp, bExp);",
        "    bFirstAct := SEL(xFirst, bFirstAct, bAct);",
        "    uiMismatch := uiMismatch + BOOL_TO_UINT(xMiss);",
        "END_FOR",
        "AssertEquals_UINT(Expected := 0, Actual := uiMismatch,",
        f"    Message := MismatchText(sTable := '{table.const}', uiRow := uiFirstRow, bExpected := bFirstExp,",
        "        bActual := bFirstAct));",
        "coUnit.TEST_FINISHED();",
    ]


def _test_method(info: HeaderInfo, table: Table) -> Files:
    rows = len(table.values)
    arch = ARCH_TEXT[table.arch]
    policy = st_member(table.policy)
    if table.level == 1:
        what = (
            f"F_VoteEval, схема {arch}, политика {policy}: все {rows} сочетаний состояний каналов "
            f"(Normal, Demand, Invalid, Bypassed) совпадают с таблицей {table.const}."
        )
        locals_ = [
            *_COMMON_LOCALS[:1],
            ("aeCh", "ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF E_ChannelState", "состояния каналов строки"),
            ("stRes", "ST_VoteResult", "результат F_VoteEval"),
            *_COMMON_LOCALS[1:],
        ]
        body = [
            f"coUnit.TEST('{table.test_name}');",
            f"FOR uiRow := 0 TO {rows - 1} DO",
            f"    RowStates(uiRow := uiRow, uiChannels := {table.channels}, aeCh := aeCh);",
            f"    stRes := F_VoteEval(eArch := {st_enum(table.arch)}, ePolicy := {st_enum(table.policy)},",
            "        aeCh := aeCh);",
            "    bAct := EncodeEval(stRes := stRes);",
            *_compare_tail(table),
        ]
    else:
        assert table.kind is not None
        kind = "дискретные" if table.kind == InputKind.DISCRETE else "аналоговые"
        what = (
            f"FB_Voting, схема {arch}, политика {policy}, {kind} каналы: все {rows} сочетаний «требование × "
            f"достоверность × запрос байпаса» совпадают с таблицей {table.const}. На строку — два вызова "
            "одного экземпляра: без запросов байпаса (сброс байпасов прошлой строки) и с полной строкой."
        )
        locals_ = [
            ("fbTime", "PL.FB_FakeTime", "время не меняется"),
            ("fbVote", "FB_Voting", "ФБ под тестом, один экземпляр на все строки"),
            ("stCfg", "ST_VotingCfg", "конфигурация теста уровня 2"),
            ("stIn", "ST_VoteIn", "входы строки"),
            ("stCmd", "ST_VoteCmd", "запросы байпаса строки"),
            *_COMMON_LOCALS,
        ]
        n = table.channels
        body = [
            f"coUnit.TEST('{table.test_name}');",
            f"stCfg.eArch := {st_enum(table.arch)};",
            f"stCfg.ePolicy := {st_enum(table.policy)};",
            f"stCfg.eInput := {st_enum(table.kind)};",
            "stCfg.xDiHealthy := TRUE;",
            "stCfg.eLimitDir := E_LimitDir.High;",
            "stCfg.rTripLimit_eu := 50.0;",
            "stCfg.rHyst_eu := 0.0;",
            "stCfg.rDiscrepancyMax_eu := 0.0;",
            "stCfg.tDiscrepancyDelay := T#0S;",
            "stCfg.tBypassMax := T#1H;",
            f"stCfg.uiMaxBypass := {min(1, n - 1)};",
            f"FOR uiRow := 0 TO {rows - 1} DO",
            f"    RowInputs(uiRow := uiRow, uiChannels := {n}, xBypass := FALSE, stIn := stIn, stCmd := stCmd);",
            "    fbVote(stIn := stIn, stCmd := stCmd, stCfg := stCfg, xBypassPermit := TRUE, uiCause := 1,",
            "        itfTime := fbTime);",
            f"    RowInputs(uiRow := uiRow, uiChannels := {n}, xBypass := TRUE, stIn := stIn, stCmd := stCmd);",
            "    fbVote(stIn := stIn, stCmd := stCmd, stCfg := stCfg, xBypassPermit := TRUE, uiCause := 1,",
            "        itfTime := fbTime);",
            "    bAct := EncodeFb(xTrip := fbVote.xTrip, stSts := fbVote.stSts);",
            *_compare_tail(table),
        ]
    decl = st_header(info, f"тест {table.test_name} набора {SUITE}.")
    decl += [f"// {line}" for line in _wrap(what)]
    decl.append(f"METHOD PRIVATE {table.method}")
    decl += _var_block(locals_)
    impl = st_header(info, "", declaration=False) + body
    base = f"{TESTS_POU}/{SUITE}/{table.method}"
    return {f"{base}.method.decl.st": join_lines(decl), f"{base}.method.impl.st": join_lines(impl)}


def _wrap(text: str, width: int = 100) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if current and len(current) + 1 + len(word) > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}" if current else word
    if current:
        lines.append(current)
    return lines


def _helper(info: HeaderInfo, name: str, comment: str, signature: list[str], body: list[str]) -> Files:
    decl = st_header(info, f"вспомогательный метод набора {SUITE}.")
    decl += [f"// {line}" for line in _wrap(comment)]
    decl += signature
    impl = st_header(info, "", declaration=False) + body
    base = f"{TESTS_POU}/{SUITE}/{name}"
    return {f"{base}.method.decl.st": join_lines(decl), f"{base}.method.impl.st": join_lines(impl)}


def _helpers(info: HeaderInfo) -> Files:
    files: Files = {}
    files.update(
        _helper(
            info,
            "ArchIndex",
            "Индекс схемы в байте таблицы: 0 None, 1 1oo1, 2 1oo2, 3 2oo2, 4 2oo3, 5 ForcedTrip.",
            [
                "METHOD PRIVATE ArchIndex : BYTE",
                "VAR_INPUT",
                "    eArch : E_VoteArch;   // действующая схема",
                "END_VAR",
            ],
            [
                "CASE eArch OF",
                "    E_VoteArch.Vote1oo1:",
                "        ArchIndex := 1;",
                "    E_VoteArch.Vote1oo2:",
                "        ArchIndex := 2;",
                "    E_VoteArch.Vote2oo2:",
                "        ArchIndex := 3;",
                "    E_VoteArch.Vote2oo3:",
                "        ArchIndex := 4;",
                "    E_VoteArch.ForcedTrip:",
                "        ArchIndex := 5;",
                "ELSE",
                "    ArchIndex := 0;",
                "END_CASE",
            ],
        )
    )
    files.update(
        _helper(
            info,
            "EncodeEval",
            "Байт результата F_VoteEval: бит 0 — xTrip, бит 1 — xDegraded, биты 2–4 — индекс eArchEff.",
            [
                "METHOD PRIVATE EncodeEval : BYTE",
                "VAR_INPUT",
                "    stRes : ST_VoteResult;   // результат F_VoteEval",
                "END_VAR",
            ],
            [
                "EncodeEval := BOOL_TO_BYTE(stRes.xTrip) OR SHL(BOOL_TO_BYTE(stRes.xDegraded), 1)",
                "    OR SHL(ArchIndex(eArch := stRes.eArchEff), 2);",
            ],
        )
    )
    files.update(
        _helper(
            info,
            "EncodeFb",
            "Байт результата FB_Voting: как у EncodeEval, плюс биты 5–7 — байпас каналов 1–3 в состоянии Active.",
            [
                "METHOD PRIVATE EncodeFb : BYTE",
                "VAR_INPUT",
                "    xTrip : BOOL;           // выход xTrip",
                "    stSts : ST_VotingSts;   // состояние группы",
                "END_VAR",
                "VAR",
                "    uiCh : UINT;            // канал",
                "END_VAR",
            ],
            [
                "EncodeFb := BOOL_TO_BYTE(xTrip) OR SHL(BOOL_TO_BYTE(stSts.xDegraded), 1)",
                "    OR SHL(ArchIndex(eArch := stSts.eArchEff), 2);",
                "FOR uiCh := 1 TO GVL_Const.SIS_VOTE_CH_MAX DO",
                "    EncodeFb := EncodeFb OR SHL(BOOL_TO_BYTE(stSts.aeBypass[uiCh] = E_BypassState.Active), 4 + uiCh);",
                "END_FOR",
            ],
        )
    )
    files.update(
        _helper(
            info,
            "RowStates",
            "Состояния каналов строки уровня 1: код (r SHR 2(k − 1)) AND 3 — 0 Normal, 1 Demand, 2 Invalid, "
            "3 Bypassed; каналы k > N — NotUsed.",
            [
                "METHOD PRIVATE RowStates",
                "VAR_INPUT",
                "    uiRow      : UINT;   // строка таблицы",
                "    uiChannels : UINT;   // N схемы",
                "END_VAR",
                "VAR_IN_OUT",
                "    aeCh : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF E_ChannelState;   // состояния каналов",
                "END_VAR",
                "VAR",
                "    uiCh : UINT;         // канал",
                "END_VAR",
            ],
            [
                "FOR uiCh := 1 TO GVL_Const.SIS_VOTE_CH_MAX DO",
                "    IF uiCh > uiChannels THEN",
                "        aeCh[uiCh] := E_ChannelState.NotUsed;",
                "    ELSE",
                "        CASE SHR(uiRow, 2 * (uiCh - 1)) AND 3 OF",
                "            0:",
                "                aeCh[uiCh] := E_ChannelState.Normal;",
                "            1:",
                "                aeCh[uiCh] := E_ChannelState.Demand;",
                "            2:",
                "                aeCh[uiCh] := E_ChannelState.Invalid;",
                "        ELSE",
                "            aeCh[uiCh] := E_ChannelState.Bypassed;",
                "        END_CASE",
                "    END_IF",
                "END_FOR",
            ],
        )
    )
    files.update(
        _helper(
            info,
            "RowInputs",
            "Входы строки уровня 2: для канала k биты 3(k − 1) — требование (DI: axDi := FALSE, AI: 60.0 "
            "вместо 40.0 при уставке 50.0), +1 — достоверность, +2 — запрос байпаса (только при xBypass). "
            "Каналы k > N — без требования, недостоверны, без запроса.",
            [
                "METHOD PRIVATE RowInputs",
                "VAR_INPUT",
                "    uiRow      : UINT;   // строка таблицы",
                "    uiChannels : UINT;   // N схемы",
                "    xBypass    : BOOL;   // FALSE — запросы байпаса сняты (первый вызов строки)",
                "END_VAR",
                "VAR_IN_OUT",
                "    stIn  : ST_VoteIn;   // входы группы",
                "    stCmd : ST_VoteCmd;  // запросы байпаса",
                "END_VAR",
                "VAR",
                "    uiCh    : UINT;      // канал",
                "    uiBits  : UINT;      // три бита канала",
                "    xDemand : BOOL;      // требование канала",
                "END_VAR",
            ],
            [
                "FOR uiCh := 1 TO GVL_Const.SIS_VOTE_CH_MAX DO",
                "    uiBits := SEL(uiCh <= uiChannels, 0, SHR(uiRow, 3 * (uiCh - 1)) AND 7);",
                "    xDemand := (uiBits AND 1) <> 0;",
                "    stIn.axDi[uiCh] := NOT xDemand;",
                "    stIn.axDiValid[uiCh] := (uiBits AND 2) <> 0;",
                "    stIn.arAi_eu[uiCh] := SEL(xDemand, 40.0, 60.0);",
                "    stIn.axAiValid[uiCh] := (uiBits AND 2) <> 0;",
                "    stCmd.axBypassReq[uiCh] := xBypass AND ((uiBits AND 4) <> 0);",
                "END_FOR",
            ],
        )
    )
    files.update(
        _helper(
            info,
            "MismatchText",
            "Сообщение ассерта: таблица, первая несовпавшая строка, ожидаемый и фактический байты (ASCII).",
            [
                "METHOD PRIVATE MismatchText : STRING(255)",
                "VAR_INPUT",
                "    sTable    : STRING(40);   // имя таблицы",
                "    uiRow     : UINT;         // первая несовпавшая строка",
                "    bExpected : BYTE;         // ожидаемый байт",
                "    bActual   : BYTE;         // фактический байт",
                "END_VAR",
                "VAR",
                "    sRow      : STRING(12);   // номер строки текстом",
                "    sExpected : STRING(12);   // ожидаемый байт текстом",
                "    sActual   : STRING(12);   // фактический байт текстом",
                "END_VAR",
            ],
            [
                "sRow := UINT_TO_STRING(uiRow);",
                "sExpected := BYTE_TO_STRING(bExpected);",
                "sActual := BYTE_TO_STRING(bActual);",
                "MismatchText := CONCAT(sTable, CONCAT(': first mismatch at row ', sRow));",
                "MismatchText := CONCAT(MismatchText, CONCAT(', expected ', sExpected));",
                "MismatchText := CONCAT(MismatchText, CONCAT(', actual ', sActual));",
            ],
        )
    )
    return files


def generate_truth(matrix: Matrix) -> Files:
    """Таблицы истинности и набор ``FB_VoteTruth_Test`` (от матрицы зависит только заголовок)."""
    info = HeaderInfo.of(matrix)
    all_tables = tables()
    files = _gvl(info, all_tables)
    decl = st_header(
        info,
        "набор coUnit: таблицы истинности голосования — F_VoteEval и FB_Voting по всем схемам, "
        "политикам деградации и видам входа (DESIGN.md, 12.2). Экземпляр — GVL_TestsGenerated.",
    )
    decl += [f"FUNCTION_BLOCK {SUITE} EXTENDS coUnit.FB_TestSuite", "VAR", "END_VAR"]
    impl = st_header(info, "", declaration=False)
    impl.append("// Тесты выполняются за один вызов; coUnit сам отмечает завершённые")
    impl += [f"{table.method}();" for table in all_tables]
    files[f"{TESTS_POU}/{SUITE}/{SUITE}.decl.st"] = join_lines(decl)
    files[f"{TESTS_POU}/{SUITE}/{SUITE}.impl.st"] = join_lines(impl)
    for table in all_tables:
        files.update(_test_method(info, table))
    files.update(_helpers(info))
    return files


def truth_test_names() -> list[str]:
    return [table.test_name for table in tables()]
