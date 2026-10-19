"""Командная строка (DESIGN.md, 10.1): команды и коды выхода 0, 1, 2."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from cemgen.cli import main
from pytests.conftest import DEMO_CSV, MINI_CSV
from pytests.sheet import Sheet


def test_validate_ok(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["validate", str(DEMO_CSV)]) == 0
    out = capsys.readouterr().out
    assert "SIS-V101-CEM" in out and "16#CD40" in out


def test_validate_json(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["validate", str(DEMO_CSV), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["ok"] is True and data["errors"] == 0
    assert data["matrix"] == {
        "document": "SIS-V101-CEM",
        "revision": "B",
        "causes": 10,
        "effects": 7,
        "crc": "16#CD40",
        "grid_sha256": data["matrix"]["grid_sha256"],
    }


def test_validate_errors_exit_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    bad = Sheet.read(DEMO_CSV).set_cause(1, "vote", "3oo3").write(tmp_path / "bad.csv")
    assert main(["validate", str(bad)]) == 1
    err = capsys.readouterr().err
    assert "CEM-E016" in err and "Как исправить:" in err
    assert main(["validate", str(bad), "--json"]) == 1
    data = json.loads(capsys.readouterr().out)
    assert data["diagnostics"][0]["code"] == "CEM-E016" and data["diagnostics"][0]["column"] == "F"


def test_validate_strict_warnings(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["validate", str(MINI_CSV)]) == 0
    assert main(["validate", str(MINI_CSV), "--strict"]) == 1


def test_file_and_argument_errors_exit_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["validate", str(tmp_path / "none.csv")]) == 2
    assert main(["frobnicate"]) == 2
    assert main([]) == 2
    assert main(["generate", str(DEMO_CSV), "--root", str(tmp_path / "missing")]) == 2
    assert main(["convert", str(tmp_path / "none.csv"), str(tmp_path / "x.xlsx")]) == 2


def test_generate_check_and_write(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["generate", str(MINI_CSV), "--root", str(tmp_path), "--check"]) == 1
    assert "новый:" in capsys.readouterr().out
    assert main(["generate", str(MINI_CSV), "--root", str(tmp_path)]) == 0
    assert "тестов по матрице 24" in capsys.readouterr().out
    assert main(["generate", str(MINI_CSV), "--root", str(tmp_path), "--check"]) == 0
    assert (tmp_path / "docs/cause_effect_matrix.html").is_file()
    assert main(["generate", str(MINI_CSV), "--root", str(tmp_path), "--strict"]) == 1  # W005 — файлы не пишутся


def test_generate_refuses_broken_matrix(tmp_path: Path) -> None:
    bad = Sheet.read(DEMO_CSV).set_mark(1, 1, "?").write(tmp_path / "bad.csv")
    root = tmp_path / "repo"
    root.mkdir()
    assert main(["generate", str(bad), "--root", str(root)]) == 1
    assert not any(root.iterdir())  # целиком или никак


def test_convert_roundtrip(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    xlsx = tmp_path / "m.xlsx"
    back = tmp_path / "m.csv"
    assert main(["convert", str(DEMO_CSV), str(xlsx)]) == 0
    assert main(["convert", str(xlsx), str(back)]) == 0
    assert main(["validate", str(xlsx)]) == 0
    assert main(["validate", str(back)]) == 0


def _results(path: Path, cases: list[tuple[str, str]]) -> Path:
    payload = {
        "schema": 1,
        "suites": [
            {
                "name": "GVL_TestsGenerated.fbCemGen01Test",
                "cases": [{"name": n, "status": s, "message": "boom" if s == "FAIL" else None} for n, s in cases],
            }
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_fat_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    passing = _results(
        tmp_path / "ok.json",
        [("Matrix_PSHH101Demand_TripsOwnEffects", "PASS"), ("Matrix_PSHH101Delay_TripsExactlyAtDelay", "PASS")],
    )
    out = tmp_path / "FAT_REPORT.md"
    assert main(["fat-report", str(DEMO_CSV), "--results", str(passing), "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "| FAT-03-01 |" in text and "соответствует" in text and "не выполнялся" in text
    failing = _results(tmp_path / "bad.json", [("Matrix_PSHH101Demand_TripsOwnEffects", "FAIL")])
    assert main(["fat-report", str(DEMO_CSV), "--results", str(failing), "--out", str(out)]) == 1
    text = out.read_text(encoding="utf-8")
    row = next(line for line in text.splitlines() if line.startswith("| FAT-03-01 |"))
    assert "не соответствует" in row and "boom" in row
    assert main(["fat-report", str(DEMO_CSV), "--results", str(tmp_path / "none.json"), "--out", str(out)]) == 2


def test_module_entry_point(tmp_path: Path) -> None:
    import subprocess
    import sys

    shutil.copy(DEMO_CSV, tmp_path / "cem.csv")
    run = subprocess.run(
        [sys.executable, "-m", "cemgen", "validate", str(tmp_path / "cem.csv")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        cwd=Path(__file__).resolve().parent.parent,
    )
    assert run.returncode == 0, run.stderr
    assert "CRC 16#CD40" in run.stdout
