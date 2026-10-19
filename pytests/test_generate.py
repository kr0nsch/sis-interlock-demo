"""Генерация (DESIGN.md, 10.2–10.5, 12.4): состав, формат, детерминизм, эталоны, запись и --check."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from cemgen import DISCLAIMER
from cemgen.convert import convert
from cemgen.generate import GENERATED_DIRS, Outputs, apply, build_outputs, compare
from cemgen.model import Matrix
from cemgen.validate import load
from pytests.conftest import DEMO_CSV, MINI_CSV, ROOT

GOLDEN = Path(__file__).resolve().parent / "golden" / "mini"
UPDATE_GOLDEN = os.environ.get("CEMGEN_UPDATE_GOLDEN") == "1"
DECL_SUFFIXES = (".decl.st", ".dut.st", ".gvl.st", ".itf.st")


def _norm(text: str) -> str:
    """Комментарий без //, (*, *) и со схлопнутыми пробелами — как проверка дисклеймера (3.1)."""
    text = text.replace("//", " ").replace("(*", " ").replace("*)", " ")
    return " ".join(text.split())


def _leading_comment(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if line.startswith("//"):
            lines.append(line)
        else:
            break
    return "\n".join(lines)


# --- состав --------------------------------------------------------------------------------------------
def test_files_of_section_10_2(demo_outputs: Outputs) -> None:
    files = demo_outputs.files
    for rel in (
        "src/DUTs/Generated/ST_SisIo.dut.st",
        "src/GVLs/Generated/GVL_SisCfg.gvl.st",
        "src/GVLs/Generated/GVL_SisIo.gvl.st",
        "src/GVLs/Generated/GVL_Sis.gvl.st",
        "src/POUs/Generated/FB_SisApp/FB_SisApp.decl.st",
        "src/POUs/Generated/PRG_Sis/PRG_Sis.impl.st",
        "src/POUs/Generated/F_SisIoNormal/F_SisIoNormal.decl.st",
        "src/POUs/Generated/F_SisIoKeys/F_SisIoKeys.decl.st",
        "tests/GVLs/Generated/GVL_VoteTruthTable.gvl.st",
        "tests/GVLs/Generated/GVL_TestsGenerated.gvl.st",
        "tests/POUs/Generated/FB_VoteTruth_Test/FB_VoteTruth_Test.decl.st",
        "tests/POUs/Generated/FB_CemGen01_Test/FB_CemGen01_Test.decl.st",
        "tests/POUs/Generated/FB_CemGen02_Test/FB_CemGen02_Test.decl.st",
        "docs/cause_effect_matrix.md",
        "docs/cause_effect_matrix.html",
        "docs/truth_tables/VOTING.md",
        "docs/FAT_protocol.md",
    ):
        assert rel in files, rel
    st = [p for p in files if p.endswith(".st")]
    assert all(any(p.startswith(d + "/") for d in GENERATED_DIRS) for p in st)


def test_demo_test_counts(demo_outputs: Outputs) -> None:
    names = [c.name for c in demo_outputs.cases]
    assert len(names) == 83
    assert len(set(names)) == 83
    kinds = {
        "Demand_": 10,
        "Delay_": 8,
        "Override_ExpiresThenTrips": 3,
        "Override_ClearsAfterConfirm": 3,
        "Override_DemandBackRestartsConfirm": 3,
        "Override_ExpiryBoundsConfirm": 3,
        "Override_ClearedThenDelayTrips": 3,
        "Override_Denied": 7,
        "Reset_": 10,
        "ChannelInvalid_": 10,
        "Bypass_Expires": 8,
        "Bypass_Denied": 2,
        "RecordsFirst": 10,
    }
    for fragment, count in kinds.items():
        assert sum(fragment in n for n in names) == count, fragment
    common = {
        "Matrix_Start_TrippedUntilReset",
        "Matrix_FirstOutSimultaneous_LowestIndex",
        "Matrix_GeneratedCfg_PassesChecks",
    }
    assert common <= set(names)
    suites = [p for p in demo_outputs.files if re.search(r"FB_CemGen\d\d_Test\.decl\.st$", p)]
    assert len(suites) == 3


def test_suite_structure(demo_outputs: Outputs) -> None:
    files = demo_outputs.files
    for suite in ("FB_CemGen01_Test", "FB_CemGen02_Test", "FB_CemGen03_Test", "FB_VoteTruth_Test"):
        base = f"tests/POUs/Generated/{suite}"
        body = files[f"{base}/{suite}.impl.st"]
        methods = sorted(
            p.rsplit("/", 1)[1].split(".")[0]
            for p in files
            if p.startswith(base + "/") and p.endswith(".method.impl.st")
        )
        tests = []
        for method in methods:
            impl = files[f"{base}/{method}.method.impl.st"]
            match = re.search(r"coUnit\.TEST\('([^']+)'\)", impl)
            if match is None:
                continue  # вспомогательный метод
            name = match.group(1)
            assert method == "".join(name.split("_")[1:]), (method, name)
            assert f"\n{method}();" in body, method
            assert impl.rstrip().endswith("coUnit.TEST_FINISHED();")
            assert f"METHOD PRIVATE {method}" in files[f"{base}/{method}.method.decl.st"]
            tests.append(name)
        assert len(tests) <= 40
    assert sum(1 for p in files if "/FB_VoteTruth_Test/" in p and p.endswith(".method.impl.st")) == 36 + 6
    gvl = files["tests/GVLs/Generated/GVL_TestsGenerated.gvl.st"]
    assert "{attribute 'linkalways'}" in gvl
    assert "fbCemGen01Test" in gvl and "fbCemGen02Test" in gvl and "fbCemGen03Test" in gvl
    assert "fbVoteTruthTest" in gvl


def test_gvl_siscfg_content(demo_outputs: Outputs) -> None:
    gvl = demo_outputs.files["src/GVLs/Generated/GVL_SisCfg.gvl.st"]
    assert "wMatrixCrc := 16#CD40" in gvl
    for mask in ("16#01E7", "16#00C0", "16#01EA", "16#03EA", "16#03FF"):
        assert f"wCauseMask := {mask}" in gvl
    assert gvl.count("// 16 — резерв") == 3  # astCause, astEffect, VOTE_CFG выписаны целиком
    assert "CAUSE_PSHH101 " in gvl and "CAUSE_COUNT" in gvl and "EFFECT_COUNT" in gvl
    assert re.search(r"AI_PT101A_NORMAL_MA\s*: REAL := 10\.0;", gvl)
    assert "rTripLimit_eu := 0.9, rHyst_eu := 0.02" in gvl
    assert "tOverrideMax := T#15M, tOverrideClear := T#30S" in gvl
    assert "tOverrideMax := T#30M, tOverrideClear := T#1M" in gvl


def test_fb_sisapp_bindings(demo_outputs: Outputs) -> None:
    impl = demo_outputs.files["src/POUs/Generated/FB_SisApp/FB_SisApp.impl.st"]
    assert "astIn[GVL_SisCfg.CAUSE_PSHH101].arAi_eu[1] := F_SisAiToEu(rIn_mA := stIo.rPT101A_mA," in impl
    assert "astIn[GVL_SisCfg.CAUSE_HS106].axDiValid[2] := stIo.xHS106B_Ok;" in impl
    assert "xBypassPermit := stIo.xHS121, xOverridePermit := stIo.xHS122, xResetHw := stIo.xHS120" in impl
    assert "stIo.xQUA110 := fbUnit.axEffectOut[GVL_SisCfg.EFFECT_UA110];" in impl


def test_mini_without_keys_and_ext(mini_outputs: Outputs) -> None:
    impl = mini_outputs.files["src/POUs/Generated/FB_SisApp/FB_SisApp.impl.st"]
    assert "xBypassPermit := TRUE, xOverridePermit := TRUE, xResetHw := FALSE" in impl
    assert "astIn[GVL_SisCfg.CAUSE_XS303].xExtDemand := stIo.xXS303;" in impl
    keys = mini_outputs.files["src/POUs/Generated/F_SisIoKeys/F_SisIoKeys.impl.st"]
    assert "F_SisIoKeys := FALSE;" in keys
    gvl = mini_outputs.files["src/GVLs/Generated/GVL_SisCfg.gvl.st"]
    assert "(eArch := E_VoteArch.None),   " in gvl or "3 XS303 — ext, без голосования" in gvl
    assert "xStartTripped := FALSE" in gvl
    names = [c.name for c in mini_outputs.cases]
    assert "Matrix_Start_EnergizedWithoutReset" in names
    assert not any(n.startswith("Matrix_XS303ChannelInvalid") or n.startswith("Matrix_XS303Bypass") for n in names)
    # PSL302: обход без задержки причины — сценария «задержка после автоснятия» нет
    assert "Matrix_PSL302Override_ClearsAfterConfirm" in names
    assert "Matrix_PSL302Override_ClearedThenDelayTrips" not in names


# --- формат -------------------------------------------------------------------------------------------
@pytest.mark.parametrize("which", ["demo_outputs", "mini_outputs"])
def test_text_format_rules(which: str, request: pytest.FixtureRequest) -> None:
    outputs: Outputs = request.getfixturevalue(which)
    for rel, text in outputs.files.items():
        data = text.encode("utf-8")
        assert not data.startswith(b"\xef\xbb\xbf"), rel
        assert "\r" not in text, rel
        assert text.endswith("\n") and not text.endswith("\n\n"), rel
        for no, line in enumerate(text.splitlines(), 1):
            assert line == line.rstrip(), f"{rel}:{no}: хвостовые пробелы"
            if rel.endswith(".st"):
                assert len(line) <= 120, f"{rel}:{no}: {len(line)} символов"
                assert "\t" not in line


def test_headers_and_disclaimer(demo_outputs: Outputs) -> None:
    expected = _norm(DISCLAIMER)
    for rel, text in demo_outputs.files.items():
        if not rel.endswith(".st"):
            continue
        assert text.startswith("// AUTO-GENERATED by cemgen "), rel
        assert "не редактировать" in text.splitlines()[0]
        assert "SHA-256 сетки " in text.splitlines()[2], rel
        if rel.endswith(DECL_SUFFIXES):
            comment = _norm(_leading_comment(text)).lower()
            assert expected.lower() in comment, rel
            assert "назначение:" in comment and "автор:" in comment and "версия:" in comment
            assert "docs/design.md" in comment


def test_matrix_path_not_in_outputs(tmp_path: Path) -> None:
    """Путь к файлу матрицы в выход не попадает (10.3)."""
    unique = tmp_path / "matrix_Q7Z3.csv"
    unique.write_bytes(MINI_CSV.read_bytes())
    result = load(unique)
    assert result.matrix is not None
    for rel, text in build_outputs(result.matrix).files.items():
        assert "matrix_Q7Z3" not in text and str(tmp_path) not in text, rel


def test_deterministic(demo: Matrix) -> None:
    first = build_outputs(demo).files
    second = build_outputs(load(DEMO_CSV).matrix).files  # type: ignore[arg-type]
    assert first == second


def test_csv_and_xlsx_generate_identical_files(tmp_path: Path, demo_outputs: Outputs) -> None:
    xlsx = tmp_path / "cem.xlsx"
    convert(DEMO_CSV, xlsx)
    result = load(xlsx)
    assert result.matrix is not None
    assert build_outputs(result.matrix).files == demo_outputs.files


def test_repository_matches_matrix(demo_outputs: Outputs) -> None:
    """То же, что ``python -m cemgen generate examples/separator/cem.csv --check`` в CI."""
    diff = compare(ROOT, demo_outputs.files)
    assert diff.clean, diff.lines()


def test_golden_mini(mini_outputs: Outputs) -> None:
    """Эталон мини-матрицы: ST объекта, сценарные тесты и документы (без таблиц истинности)."""
    selected = {
        rel: text
        for rel, text in mini_outputs.files.items()
        if "FB_VoteTruth_Test" not in rel and "GVL_VoteTruthTable" not in rel and not rel.endswith("VOTING.md")
    }
    if UPDATE_GOLDEN:
        for old in GOLDEN.rglob("*") if GOLDEN.exists() else []:
            if old.is_file():
                old.unlink()
        for rel, text in selected.items():
            path = GOLDEN / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(text.encode("utf-8"))
    present = sorted(p.relative_to(GOLDEN).as_posix() for p in GOLDEN.rglob("*") if p.is_file())
    assert present == sorted(selected), (
        "эталон устарел: CEMGEN_UPDATE_GOLDEN=1 python -m pytest pytests/test_generate.py"
    )
    for rel, text in selected.items():
        assert (GOLDEN / rel).read_bytes() == text.encode("utf-8"), rel


# --- запись ----------------------------------------------------------------------------------------------
def test_apply_check_and_extra_files(tmp_path: Path, mini_outputs: Outputs) -> None:
    files = mini_outputs.files
    diff = compare(tmp_path, files)
    assert len(diff.new) == len(files) and not diff.changed
    apply(tmp_path, files)
    assert compare(tmp_path, files).clean
    # ручная правка — «изменён»; лишний .st в Generated — «лишний», удаляется при генерации
    gvl = tmp_path / "src/GVLs/Generated/GVL_SisCfg.gvl.st"
    gvl.write_text(gvl.read_text(encoding="utf-8").replace("16#", "16#0"), encoding="utf-8", newline="\n")
    stale = tmp_path / "src/POUs/Generated/FB_Old/FB_Old.decl.st"
    stale.parent.mkdir(parents=True)
    stale.write_text("// old\n", encoding="utf-8")
    keep = tmp_path / "src/POUs/Sis/FB_Hand/FB_Hand.decl.st"  # вне Generated — не трогается
    keep.parent.mkdir(parents=True)
    keep.write_text("// hand\n", encoding="utf-8")
    diff = compare(tmp_path, files)
    assert diff.changed == ["src/GVLs/Generated/GVL_SisCfg.gvl.st"]
    assert diff.extra == ["src/POUs/Generated/FB_Old/FB_Old.decl.st"]
    apply(tmp_path, files)
    assert compare(tmp_path, files).clean
    assert not stale.exists() and not stale.parent.exists() and keep.exists()


def test_generated_tree_passes_st_lint_and_assemble(tmp_path: Path, mini_outputs: Outputs) -> None:
    """Сгенерированный ST проходит st_lint --strict (настройки репозитория) и сборку раскладки."""
    apply(tmp_path, {k: v for k, v in mini_outputs.files.items() if k.endswith(".st")})
    (tmp_path / "tools" / "check").mkdir(parents=True)
    config = ROOT / "tools" / "check" / "st_lint.toml"
    lint = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/check/st_lint.py"),
            "--root",
            str(tmp_path),
            "--config",
            str(config),
            "--strict",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert lint.returncode == 0, lint.stdout + lint.stderr
    asm = subprocess.run(
        [sys.executable, str(ROOT / "tools/assemble.py"), "--root", str(tmp_path), "--tests", "--check-only", "-q"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert asm.returncode == 0, asm.stdout + asm.stderr


def test_mini_fixture_parses() -> None:
    assert load(MINI_CSV).matrix is not None
