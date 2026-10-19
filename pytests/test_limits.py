"""Пределы cemgen/limits.py совпадают с GVL_Const проекта (DESIGN.md, 4.3)."""

from __future__ import annotations

import re

import pytest

from cemgen import limits
from pytests.conftest import ROOT

GVL = ROOT / "src" / "GVLs" / "GVL_Const.gvl.st"
DECL_RE = re.compile(r"^\s*([A-Z][A-Z0-9_]*)\s*:\s*([A-Z]+)\s*:=\s*([^;]+);", re.MULTILINE)
EXPECTED = {
    "SIS_CAUSES_MAX": limits.SIS_CAUSES_MAX,
    "SIS_EFFECTS_MAX": limits.SIS_EFFECTS_MAX,
    "SIS_VOTE_CH_MAX": limits.SIS_VOTE_CH_MAX,
    "SIS_LOG_SIZE": limits.SIS_LOG_SIZE,
    "SIS_DELAY_MAX": limits.SIS_DELAY_MAX_MS,
    "SIS_OVERRIDE_MAX": limits.SIS_OVERRIDE_MAX_MS,
    "SIS_BYPASS_MAX": limits.SIS_BYPASS_MAX_MS,
    "SIS_FIRST_OUT_NONE": limits.SIS_FIRST_OUT_NONE,
    "SIS_FIRST_OUT_START": limits.SIS_FIRST_OUT_START,
    "SIS_FIRST_OUT_CFG": limits.SIS_FIRST_OUT_CFG,
    "CRC16_INIT": limits.CRC16_INIT,
    "CRC16_POLY": limits.CRC16_POLY,
    "VOTE_CFG_ARCH": limits.VOTE_CFG_ARCH,
    "VOTE_CFG_POLICY": limits.VOTE_CFG_POLICY,
    "VOTE_CFG_INPUT": limits.VOTE_CFG_INPUT,
    "VOTE_CFG_LIMIT": limits.VOTE_CFG_LIMIT,
    "VOTE_CFG_DISCREPANCY": limits.VOTE_CFG_DISCREPANCY,
    "VOTE_CFG_BYPASS": limits.VOTE_CFG_BYPASS,
    "CEM_CFG_COUNT": limits.CEM_CFG_COUNT,
    "CEM_CFG_CAUSE": limits.CEM_CFG_CAUSE,
    "CEM_CFG_EFFECT": limits.CEM_CFG_EFFECT,
    "CEM_CFG_CRC": limits.CEM_CFG_CRC,
}


def _value(st_type: str, text: str) -> int:
    text = text.strip()
    if st_type == "TIME":
        match = re.fullmatch(r"T#(?:(\d+)H)?(?:(\d+)M(?!S))?(?:(\d+)S)?(?:(\d+)MS)?", text.upper())
        assert match, text
        h, m, s, ms = (int(g) if g else 0 for g in match.groups())
        return ((h * 60 + m) * 60 + s) * 1000 + ms
    if text.startswith("16#"):
        return int(text[3:].replace("_", ""), 16)
    return int(text)


def test_limits_match_gvl_const() -> None:
    if not GVL.is_file():
        pytest.skip("src/GVLs/GVL_Const.gvl.st ещё нет")
    found = {name: (st_type, value) for name, st_type, value in DECL_RE.findall(GVL.read_text(encoding="utf-8"))}
    if "SIS_CAUSES_MAX" not in found:
        pytest.skip("GVL_Const ещё не содержит констант ПАЗ (этап A1)")
    for name, expected in EXPECTED.items():
        assert name in found, name
        st_type, text = found[name]
        assert _value(st_type, text) == expected, name
