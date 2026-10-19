"""Проверки соглашений проекта, которые не ловят линтер и компилятор CODESYS (DESIGN.md, 12.1).

1. Регистрация наборов coUnit: набор, объявленный в GVL без {attribute 'linkalways'}, или тест-метод,
   который тело набора не вызывает, молча не выполняются — CODESYS 3.5.17 компилирует только
   объекты, достижимые из задач. PRG_Tests содержит только coUnit.RUN().
2. Имена тестов: TEST('<Объект>_<Случай>_<Ожидание>'), имя метода — без первого сегмента и без
   подчёркиваний, METHOD PRIVATE, coUnit.TEST_FINISHED(); имена уникальны во всём проекте.
3. Время — только PL.FB_FakeTime / PL.FB_Delay: TON, TOF, TP в src/ и tests/ запрещены (3.3).
4. GVL_Const против таблицы 4.3 контракта, коды перечислений против раздела 4.1.

Запуск: python -m pytest (каталог входит в testpaths, pyproject.toml).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import stlayout as L

REPO_ROOT = Path(__file__).resolve().parents[2]
DESIGN = REPO_ROOT / "docs" / "DESIGN.md"
_SCAN_CACHE: dict[str, L.ScanResult] = {}


def scan(subdir: str) -> L.ScanResult:
    if subdir not in _SCAN_CACHE:
        _SCAN_CACHE[subdir] = L.scan(str(REPO_ROOT), subdir)
    return _SCAN_CACHE[subdir]


def code_text(text: str) -> str:
    """Текст без комментариев (для поиска вызовов)."""
    return str(L.strip_comments(text, pragmas=False))


def suites() -> list[L.StObject]:
    """Наборы coUnit: FUNCTION_BLOCK ... EXTENDS coUnit.FB_TestSuite в tests/."""
    return [
        obj
        for obj in scan("tests").objects
        if obj.kind == L.KIND_POU
        and obj.header is not None
        and any(base.lower() == "counit.fb_testsuite" for base in obj.header.extends)
    ]


_TEST_RE = re.compile(r"coUnit\.TEST\s*\(\s*'(?P<name>[^']*)'\s*\)", re.IGNORECASE)
_FINISHED_RE = re.compile(r"coUnit\.TEST_FINISHED\s*\(\s*\)", re.IGNORECASE)


def suite_cases(suite: L.StObject) -> list[tuple[L.StMethod, str]]:
    """(метод, имя TEST) для методов набора, которые объявляют тест."""
    result = []
    for method in suite.methods:
        match = _TEST_RE.search(method.impl or "")
        if match:
            result.append((method, match.group("name")))
    return result


def suite_gvls() -> list[L.StObject]:
    return [obj for obj in scan("tests").objects if obj.kind == L.KIND_GVL]


# ---------------------------------------------------------------------------
# 1. Регистрация наборов
# ---------------------------------------------------------------------------


def test_layout_is_valid() -> None:
    for subdir in ("src", "tests"):
        result = scan(subdir)
        assert result.ok, [issue.format() for issue in result.errors]


def test_suites_exist() -> None:
    names = {s.name for s in suites()}
    expected = {
        "FB_VoteEval_Test",
        "FB_Voting_Test",
        "FB_CauseEffect_Test",
        "FB_SisEventLog_Test",
        "FB_SisUnit_Test",
        "FB_SisUtil_Test",
        "FB_Common_Test",
    }
    assert expected <= names, f"нет наборов раздела 12.3: {sorted(expected - names)}"


def test_suite_gvls_are_linked_always() -> None:
    """Каждая GVL наборов — с {attribute 'linkalways'}: без него CODESYS не включает её в приложение."""
    gvls = suite_gvls()
    assert gvls, "нет tests/GVLs/GVL_Tests*.gvl.st"
    for gvl in gvls:
        if not any(s.name.lower() in gvl.decl.lower() for s in suites()):
            continue  # GVL с данными тестов (например, таблицы), а не с экземплярами наборов
        assert gvl.name.startswith("GVL_Tests"), f"{gvl.name}: GVL наборов называется GVL_Tests<Группа>"
        assert re.search(r"\{\s*attribute\s+'linkalways'\s*\}", gvl.decl), (
            f"{gvl.name}: нет {{attribute 'linkalways'}} — наборы этой GVL не выполнятся"
        )
        assert re.search(r"\{\s*attribute\s+'qualified_only'\s*\}", gvl.decl), f"{gvl.name}: нет qualified_only"


def _instances(objects: list[L.StObject]) -> dict[str, list[str]]:
    """Тип набора -> где объявлены его экземпляры."""
    names = {s.name.lower() for s in suites()}
    found: dict[str, list[str]] = {}
    for obj in objects:
        for block in L.parse_var_blocks(obj.decl):
            for decl in block.decls:
                type_name = decl.type_text.strip().lower()
                if type_name in names:
                    for name in decl.name_list:
                        found.setdefault(type_name, []).append(f"{obj.name}.{name}")
    return found


def test_every_suite_registered_once_in_a_test_gvl() -> None:
    found = _instances(suite_gvls())
    others = _instances([o for o in scan("tests").objects if o.kind != L.KIND_GVL])
    for suite in suites():
        where = found.get(suite.name.lower(), [])
        assert len(where) == 1, f"{suite.name}: экземпляр должен быть ровно один в tests/GVLs/, найдено {where}"
        assert suite.name.lower() not in others, (
            f"{suite.name}: экземпляр вне tests/GVLs/: {others[suite.name.lower()]}"
        )


def test_prg_tests_only_runs_counit() -> None:
    """PRG_Tests не правит ни одна команда: в нём только coUnit.RUN()."""
    prg = scan("tests").find("PRG_Tests")
    assert prg is not None
    assert not _instances([prg]), "экземпляры наборов объявляются в tests/GVLs/, а не в PRG_Tests"
    statements = [s.strip() for s in code_text(prg.impl or "").split(";") if s.strip()]
    assert statements == ["coUnit.RUN()"], statements


def test_suite_body_calls_every_test_method() -> None:
    for suite in suites():
        body = code_text(suite.impl or "")
        for method, _ in suite_cases(suite):
            call = re.compile(rf"(?<![\w.]){re.escape(method.name)}\s*\(\s*\)\s*;", re.IGNORECASE)
            assert call.search(body), f"{suite.name}: тело набора не вызывает {method.name}() — тест не выполнится"


def test_suite_limits() -> None:
    """Лимиты coUnit 1.2.0.0 по умолчанию: 100 тестов на набор; ассертов — меньше 1000 (берём 900)."""
    assert_re = re.compile(r"(?<![\w.])Assert\w*\s*\(", re.IGNORECASE)
    for suite in suites():
        cases = suite_cases(suite)
        assert len(cases) <= 100, f"{suite.name}: тестов {len(cases)}"
        asserts = sum(len(assert_re.findall(code_text(m.impl or ""))) for m, _ in cases)
        loops = any(re.search(r"\bFOR\b|\bWHILE\b", code_text(m.impl or ""), re.IGNORECASE) for m, _ in cases)
        if not loops:
            assert asserts < 900, f"{suite.name}: ассертов {asserts}"


# ---------------------------------------------------------------------------
# 2. Имена тестов
# ---------------------------------------------------------------------------


def test_test_names_follow_the_convention() -> None:
    seen: dict[str, str] = {}
    for suite in suites():
        for method, test in suite_cases(suite):
            where = f"{suite.name}.{method.name}"
            assert re.fullmatch(r"[A-Z][A-Za-z0-9]*(_[A-Za-z0-9]+){2,}", test), (
                f"{where}: имя теста '{test}' — вида <Объект>_<Случай>_<Ожидание>"
            )
            assert test.isascii(), f"{where}: имя теста — ASCII"
            expected = "".join(test.split("_")[1:])
            assert method.name == expected, f"{where}: имя метода должно быть {expected}"
            assert re.search(r"\bMETHOD\s+PRIVATE\b", method.decl, re.IGNORECASE), (
                f"{where}: метод-тест объявляется METHOD PRIVATE"
            )
            assert test.lower() not in seen, f"тест '{test}' повторяется: {seen.get(test.lower())} и {where}"
            seen[test.lower()] = where
            assert _FINISHED_RE.search(method.impl or ""), f"{where}: нет coUnit.TEST_FINISHED()"


DESIGN_12_3_TESTS = {
    "Vote_ArchNone_TripsReportsNone",
    "Vote_PolicyOutOfEnum_TripsNone",
    "Vote_NotUsedInsideN_CountsInvalid",
    "Vote_ArchHelpers_ChannelsAndRequired",
    "Voting_DefaultCfg_TripsCfgError",
    "Voting_Bypass_ExpiresExactlyAtMax",
    "Voting_Discrepancy_AfterDelayExactly",
    "Voting_CfgError_RemovesBypasses",
    "Voting_NoTimeSource_UsesSystemTime",
    "Cem_DefaultCfg_AllTripped",
    "Cem_CrcMismatch_AllTripped",
    "Cem_StartTripped_RequiresReset",
    "Cem_Reset_DeniedWhilePending",
    "Cem_FirstOut_SimultaneousLowestAndMask",
    "Cem_Override_ExpiresExactly",
    "Cem_Events_OrderInCall",
    "Log_SizeOfEvent_Is24",
    "Unit_Events_VotingBeforeCem",
    "Sis_Crc16_CheckValue",
    "Sis_CemCrc_DemoMatrixValue",
    "Common_DefaultCfg_FailsSafe",
}


def test_design_minimum_tests_present() -> None:
    """Нормативные имена раздела 12.3 (выборка из каждого набора; полный список — в наборах)."""
    names = {test for suite in suites() for _, test in suite_cases(suite)}
    table = DESIGN.read_text(encoding="utf-8").split("### 12.3", 1)[1].split("### 12.4", 1)[0]
    required = set(re.findall(r"`((?:Vote|Voting|Cem|Log|Unit|Sis|Common)_[A-Za-z0-9]+_[A-Za-z0-9]+)`", table))
    assert required >= DESIGN_12_3_TESTS, "выборка должна быть из таблицы 12.3"
    missing = sorted(required - names)
    assert not missing, f"нет тестов раздела 12.3: {missing}"


def test_no_real_time_timers() -> None:
    """Время — только I_TimeSource и PL.FB_Delay: TON/TOF/TP запрещены в src/ и tests/ (3.3)."""
    for subdir in ("src", "tests"):
        for obj in scan(subdir).objects:
            for rel, text in L.object_files(obj):
                for block in L.parse_var_blocks(text):
                    for decl in block.decls:
                        type_name = decl.type_text.strip().upper()
                        assert type_name not in {"TON", "TOF", "TP", "STANDARD.TON", "STANDARD.TOF", "STANDARD.TP"}, (
                            f"{rel}: {decl.name_list}"
                        )


# ---------------------------------------------------------------------------
# 3. GVL_Const и перечисления против контракта
# ---------------------------------------------------------------------------


def design_constants() -> dict[str, tuple[str, str]]:
    """Таблица 4.3: имя -> (тип, значение)."""
    section = DESIGN.read_text(encoding="utf-8").split("### 4.3", 1)[1].split("### 4.4", 1)[0]
    found: dict[str, tuple[str, str]] = {}
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and re.fullmatch(r"`[A-Z0-9_]+`", cells[0]):
            found[cells[0].strip("`")] = (cells[1], cells[2])
    return found


def gvl_constants() -> dict[str, tuple[str, str]]:
    gvl = scan("src").find("GVL_Const")
    assert gvl is not None
    found: dict[str, tuple[str, str]] = {}
    for match in re.finditer(r"^\s*([A-Z0-9_]+)\s*:\s*(\w+)\s*:=\s*([^;]+);", gvl.decl, re.MULTILINE):
        found[match.group(1)] = (match.group(2), match.group(3).strip())
    return found


def test_gvl_const_matches_design_table() -> None:
    design = design_constants()
    assert len(design) >= 27, f"таблица 4.3 не разобрана: {len(design)}"
    actual = gvl_constants()
    for name, (type_name, value) in design.items():
        assert name in actual, f"GVL_Const: нет {name}"
        assert actual[name] == (type_name, value), (
            f"GVL_Const.{name}: {actual[name]}, по контракту {(type_name, value)}"
        )


def design_enums() -> dict[str, dict[str, int]]:
    """Раздел 4.1: перечисление -> {имя: код}."""
    section = DESIGN.read_text(encoding="utf-8").split("### 4.1", 1)[1].split("### 4.2", 1)[0]
    enums: dict[str, dict[str, int]] = {}
    for match in re.finditer(r"TYPE (E_\w+)\s*:.*?\((.*?)\)\s*INT;", section, re.DOTALL):
        values = re.findall(r"^\s*(\w+)\s*:=\s*(\d+)", match.group(2), re.MULTILINE)
        enums[match.group(1)] = {name: int(code) for name, code in values}
    return enums


ENUM_NAMES = sorted(design_enums())


def test_design_enums_parsed() -> None:
    assert len(ENUM_NAMES) == 9, ENUM_NAMES


@pytest.mark.parametrize("name", ENUM_NAMES)
def test_enum_matches_design(name: str) -> None:
    dut = scan("src").find(name)
    assert dut is not None, f"нет {name}"
    actual = {n: int(c) for n, c in re.findall(r"^\s*(\w+)\s*:=\s*(\d+)", dut.decl, re.MULTILINE)}
    assert actual == design_enums()[name]
    assert re.search(r"\{\s*attribute\s+'strict'\s*\}", dut.decl), f"{name}: нет {{attribute 'strict'}}"
    assert re.search(r"\)\s*INT\s*;", dut.decl), f"{name}: базовый тип INT"


def test_duts_are_qualified_only() -> None:
    for obj in scan("src").objects:
        if obj.kind in (L.KIND_DUT, L.KIND_GVL):
            assert re.search(r"\{\s*attribute\s+'qualified_only'\s*\}", obj.decl), f"{obj.name}: нет qualified_only"


def test_sis_event_field_order() -> None:
    """ST_SisEvent — порядок полей без выравнивающих пропусков (4.2): SIZEOF = 24 проверяет coUnit."""
    dut = scan("src").find("ST_SisEvent")
    assert dut is not None
    fields = re.findall(r"^\s*(\w+)\s*:\s*(\w+)\s*;", dut.decl, re.MULTILINE)
    assert fields == [
        ("ltTime", "LTIME"),
        ("udiSeq", "UDINT"),
        ("rValue", "REAL"),
        ("eKind", "E_SisEventKind"),
        ("uiCause", "UINT"),
        ("uiEffect", "UINT"),
        ("uiChannel", "UINT"),
    ]
