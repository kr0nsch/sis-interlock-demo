"""Проверки эталонной модели голосования и сгенерированных тестов таблиц истинности.

1. Модель воспроизводит нормативные таблицы деградации раздела 5.3 docs/DESIGN.md (разбор таблиц
   прямо из документа) и пример диаграммы байпаса 5.7.
2. Сгенерированные файлы совпадают с выводом генератора (gen_voting_tests.py --check).
3. Наборы укладываются в лимиты coUnit, строки таблиц — в счёт раздела 12.2 (300 + 3888).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import gen_voting_tests as G
import vote_model as M

DESIGN = G.REPO_ROOT / "docs" / "DESIGN.md"
NAME_TO_ARCH = {name: arch for arch, name in M.ARCH_NAME.items()}


def degradation_tables() -> dict[str, list[tuple[int, int, list[str]]]]:
    """Таблицы раздела 5.3: схема -> [(B, F, [VoteTrip, DegradeSafe, DegradeAvailable])]."""
    text = DESIGN.read_text(encoding="utf-8")
    section = text.split("### 5.3", 1)[1].split("### 5.4", 1)[0]
    tables: dict[str, list[tuple[int, int, list[str]]]] = {}
    current = ""
    for line in section.splitlines():
        head = re.fullmatch(r"\*\*(\d oo\d|\doo\d)\*\*", line.strip())
        if head:
            current = head.group(1)
            tables[current] = []
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if current and len(cells) == 5 and cells[0].isdigit():
            tables[current].append((int(cells[0]), int(cells[1]), cells[2:]))
    return tables


def channels_for(arch: int, b: int, f: int) -> tuple[int, ...]:
    """B каналов в байпасе, затем F недостоверных, остальные — норма; k > N — NotUsed."""
    n = M.arch_channels(arch)
    states = [M.BYPASSED] * b + [M.INVALID] * f + [M.NORMAL] * (n - b - f)
    return tuple(states + [M.NOT_USED] * (M.CH_MAX - n))


def test_design_tables_found() -> None:
    tables = degradation_tables()
    assert set(tables) == {"2oo3", "1oo2", "2oo2"}
    assert len(tables["2oo3"]) == 10
    assert len(tables["1oo2"]) == 6
    assert len(tables["2oo2"]) == 6


@pytest.mark.parametrize("arch_name", ["2oo3", "1oo2", "2oo2"])
def test_model_reproduces_degradation_table(arch_name: str) -> None:
    arch = NAME_TO_ARCH[arch_name]
    for b, f, expected in degradation_tables()[arch_name]:
        for policy, name in zip(M.POLICIES, expected, strict=True):
            res = M.vote_eval(arch, policy, channels_for(arch, b, f))
            assert M.ARCH_NAME[res.arch_eff] == name, (arch_name, b, f, policy)
            assert res.degraded == (b + f > 0), (arch_name, b, f, policy)
            if res.arch_eff == M.FORCED_TRIP:
                assert res.trip


def test_model_1oo1_table() -> None:
    """1oo1: B = 0, F = 0 → 1oo1; иначе ForcedTrip (5.3)."""
    for policy in M.POLICIES:
        assert M.vote_eval(M.VOTE_1OO1, policy, channels_for(M.VOTE_1OO1, 0, 0)).arch_eff == M.VOTE_1OO1
        assert M.vote_eval(M.VOTE_1OO1, policy, channels_for(M.VOTE_1OO1, 1, 0)).arch_eff == M.FORCED_TRIP
        assert M.vote_eval(M.VOTE_1OO1, policy, channels_for(M.VOTE_1OO1, 0, 1)).arch_eff == M.FORCED_TRIP


def test_model_trip_needs_m_demands() -> None:
    """2oo3 без деградации: требование при двух каналах Demand, не при одном."""
    one = (M.DEMAND, M.NORMAL, M.NORMAL)
    two = (M.DEMAND, M.NORMAL, M.DEMAND)
    assert not M.vote_eval(M.VOTE_2OO3, M.VOTE_TRIP, one).trip
    assert M.vote_eval(M.VOTE_2OO3, M.VOTE_TRIP, two).trip


def test_model_invalid_arch_or_policy_trips_none() -> None:
    assert M.vote_eval(M.ARCH_NONE, M.VOTE_TRIP, (M.NORMAL,) * 3) == M.VoteResult(True, False, M.ARCH_NONE)
    assert M.vote_eval(M.VOTE_2OO3, 7, (M.NORMAL,) * 3) == M.VoteResult(True, False, M.ARCH_NONE)


def test_model_bypass_expires_exactly_at_max() -> None:
    """5.7: байпас истекает ровно в вызове, где прошло tBypassMax, и канал в том же вызове голосует."""
    cfg = M.table_cfg(M.VOTE_2OO3, M.VOTE_TRIP, M.DISCRETE)
    vin = M.VoteIn(di=[True] * 3, di_valid=[False, True, True])
    fb = M.Voting()
    t0 = M.TABLE_NOW
    sts = fb.call(t0, cfg, vin, [True, False, False], bypass_permit=True)
    assert sts.bypass[0] == M.BYPASS_ACTIVE and sts.ch_state[0] == M.BYPASSED
    sts = fb.call(t0 + cfg.bypass_max_ns - M.NS_PER_MS, cfg, vin, [True, False, False], bypass_permit=True)
    assert sts.bypass[0] == M.BYPASS_ACTIVE and sts.bypass_remain_ns[0] == M.NS_PER_MS
    sts = fb.call(t0 + cfg.bypass_max_ns, cfg, vin, [True, False, False], bypass_permit=True)
    assert sts.bypass[0] == M.BYPASS_EXPIRED and sts.ch_state[0] == M.INVALID
    assert [e.kind for e in fb.events][-1] == M.EV_BYPASS_EXPIRED


def test_model_time_backwards_ends_bypass() -> None:
    """D-19: «время назад» — срок байпаса недостоверен: TimeFault, байпас Expired, канал голосует."""
    cfg = M.table_cfg(M.VOTE_2OO3, M.VOTE_TRIP, M.DISCRETE)
    vin = M.VoteIn(di=[True] * 3, di_valid=[True] * 3)
    fb = M.Voting()
    t0 = M.TABLE_NOW
    sts = fb.call(t0, cfg, vin, [True, False, False], bypass_permit=True)
    assert sts.bypass[0] == M.BYPASS_ACTIVE
    sts = fb.call(t0 + 6 * M.NS_PER_MS, cfg, vin, [True, False, False], bypass_permit=True)
    assert sts.bypass[0] == M.BYPASS_ACTIVE
    sts = fb.call(t0 - M.NS_PER_MS, cfg, vin, [True, False, False], bypass_permit=True)
    assert sts.bypass[0] == M.BYPASS_EXPIRED and sts.ch_state[0] == M.NORMAL and sts.bypass_remain_ns[0] == 0
    assert [e.kind for e in fb.events][-2:] == [M.EV_TIME_FAULT, M.EV_BYPASS_EXPIRED]
    sts = fb.call(t0, cfg, vin, [False, False, False], bypass_permit=True)
    sts = fb.call(t0 + M.NS_PER_MS, cfg, vin, [True, False, False], bypass_permit=True)
    assert sts.bypass[0] == M.BYPASS_ACTIVE and sts.bypass_remain_ns[0] == cfg.bypass_max_ns
    assert sum(1 for e in fb.events if e.kind == M.EV_TIME_FAULT) == 1


def test_row_counts_match_design() -> None:
    """12.2: 12 таблиц уровня 1 (300 строк) и 24 таблицы уровня 2 (3888 строк)."""
    tables = G.all_tables()
    level1 = [t for t in tables if t.level == 1]
    level2 = [t for t in tables if t.level == 2]
    assert len(level1) == 12 and sum(len(t.expected()) for t in level1) == 300
    assert len(level2) == 24 and sum(len(t.expected()) for t in level2) == 3888


def test_suites_within_counit_limits() -> None:
    suites = G.plan_suites()
    names = [t.test_name for s in suites for t in s.tables]
    assert len(names) == len(set(names)) == 36
    for suite in suites:
        assert suite.asserts() < G.MAX_ASSERTS_PER_SUITE, suite.name
        assert len(suite.tables) <= G.MAX_TESTS_PER_SUITE, suite.name


def test_generated_files_are_up_to_date() -> None:
    """Сгенерированные тесты в репозитории совпадают с выводом генератора."""
    problems = G.compare(G.REPO_ROOT, G.build())
    assert not problems, "\n".join(problems[:20]) + f"\n... запустите python {G.GENERATOR}"


def test_check_mode_reports_drift(tmp_path: Path) -> None:
    """--check находит изменённый и лишний файл и ничего не пишет."""
    files = G.build()
    G.write(tmp_path, files)
    assert G.main(["--check", "--root", str(tmp_path)]) == 0
    first = sorted(files)[0]
    (tmp_path / first).write_text("changed\n", encoding="utf-8")
    extra = tmp_path / G.GEN_DIR / "FB_Stale_Test" / "FB_Stale_Test.decl.st"
    extra.parent.mkdir(parents=True)
    extra.write_text("x\n", encoding="utf-8")
    problems = G.compare(tmp_path, files)
    assert f"отличается: {first}" in problems
    assert any(p.startswith("лишний файл:") for p in problems)
    assert G.main(["--check", "--root", str(tmp_path)]) == 1
    assert (tmp_path / first).read_text(encoding="utf-8") == "changed\n"
    G.write(tmp_path, files)
    assert G.compare(tmp_path, files) == []
    assert not extra.parent.exists()
