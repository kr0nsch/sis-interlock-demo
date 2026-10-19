"""Эталонная модель (DESIGN.md, 10.6): таблицы 5.3, диаграмма 6.11, CRC 6.8, примеры 12.4."""

from __future__ import annotations

import math

import pytest

from cemgen import limits
from cemgen.model import Matrix
from cemgen.refmodel import (
    NS_PER_MS,
    CauseCfg,
    CauseEffect,
    CauseEffectSts,
    CemCfg,
    CemCmd,
    Delay,
    EffectCfg,
    EventLog,
    FakeTime,
    Harness,
    VoteCmd,
    VoteIn,
    Voting,
    VotingCfg,
    VotingSts,
    ai_to_eu,
    cem_check_cfg,
    cem_crc,
    channel_demand,
    channel_invalid,
    cross_demands,
    degradation,
    eval_table,
    f32,
    fb_table,
    ne43_valid,
    vote_check_cfg,
    vote_eval,
)
from cemgen.sisdefs import (
    ARCH_TEXT,
    POLICIES,
    VOTING_ARCHS,
    BypassState,
    CauseSource,
    ChannelState,
    EventKind,
    InputKind,
    LimitDir,
    Policy,
    VoteArch,
)

# Таблицы 5.3 контракта дословно: (B, F) → (VoteTrip, DegradeSafe, DegradeAvailable); FT — ForcedTrip
FT = "ForcedTrip"
TABLES_5_3: dict[str, dict[tuple[int, int], tuple[str, str, str]]] = {
    "2oo3": {
        (0, 0): ("2oo3", "2oo3", "2oo3"),
        (0, 1): ("1oo2", "1oo2", "2oo2"),
        (0, 2): (FT, "1oo1", "1oo1"),
        (0, 3): (FT, FT, FT),
        (1, 0): ("1oo2", "1oo2", "2oo2"),
        (1, 1): (FT, "1oo1", "1oo1"),
        (1, 2): (FT, FT, FT),
        (2, 0): ("1oo1", "1oo1", "1oo1"),
        (2, 1): (FT, FT, FT),
        (3, 0): (FT, FT, FT),
    },
    "1oo2": {
        (0, 0): ("1oo2", "1oo2", "1oo2"),
        (0, 1): (FT, "1oo1", "1oo1"),
        (0, 2): (FT, FT, FT),
        (1, 0): ("1oo1", "1oo1", "1oo1"),
        (1, 1): (FT, FT, FT),
        (2, 0): (FT, FT, FT),
    },
    "2oo2": {
        (0, 0): ("2oo2", "2oo2", "2oo2"),
        (0, 1): ("1oo1", "1oo1", "1oo1"),
        (0, 2): (FT, FT, FT),
        (1, 0): ("1oo1", "1oo1", "1oo1"),
        (1, 1): (FT, FT, FT),
        (2, 0): (FT, FT, FT),
    },
    "1oo1": {(0, 0): ("1oo1", "1oo1", "1oo1"), (0, 1): (FT, FT, FT), (1, 0): (FT, FT, FT)},
}


@pytest.mark.parametrize("arch", VOTING_ARCHS, ids=lambda a: ARCH_TEXT[a])
def test_degradation_tables_5_3(arch: VoteArch) -> None:
    expected = TABLES_5_3[ARCH_TEXT[arch]]
    got = {(b, f): tuple(ARCH_TEXT[degradation(arch, p, b, f)] for p in POLICIES) for (b, f) in expected}
    assert got == expected


def test_degraded_flag_everywhere_but_first_row() -> None:
    for arch in VOTING_ARCHS:
        for policy in POLICIES:
            for b, f in TABLES_5_3[ARCH_TEXT[arch]]:
                n = {VoteArch.V1OO1: 1, VoteArch.V1OO2: 2, VoteArch.V2OO2: 2, VoteArch.V2OO3: 3}[arch]
                states = [ChannelState.BYPASSED] * b + [ChannelState.INVALID] * f
                states += [ChannelState.NORMAL] * (n - b - f) + [ChannelState.NOT_USED] * (3 - n)
                assert vote_eval(arch, policy, states).degraded == (b + f > 0)


def test_vote_eval_trips_on_m_demands() -> None:
    n, d = ChannelState.NORMAL, ChannelState.DEMAND
    assert not vote_eval(VoteArch.V2OO3, Policy.VOTE_TRIP, [d, n, n]).trip
    assert vote_eval(VoteArch.V2OO3, Policy.VOTE_TRIP, [d, d, n]).trip
    assert vote_eval(VoteArch.V1OO2, Policy.VOTE_TRIP, [n, d, ChannelState.NOT_USED]).trip
    assert not vote_eval(VoteArch.V2OO2, Policy.VOTE_TRIP, [n, d, ChannelState.NOT_USED]).trip


def test_vote_eval_invalid_config_trips_none() -> None:
    res = vote_eval(VoteArch.NONE, Policy.VOTE_TRIP, [ChannelState.NORMAL] * 3)
    assert res.trip and res.arch_eff == VoteArch.NONE and not res.degraded
    res = vote_eval(VoteArch.V2OO3, 7, [ChannelState.NORMAL] * 3)
    assert res.trip and res.arch_eff == VoteArch.NONE


def test_vote_eval_not_used_inside_n_counts_invalid() -> None:
    res = vote_eval(
        VoteArch.V2OO3, Policy.DEGRADE_SAFE, [ChannelState.NOT_USED, ChannelState.NORMAL, ChannelState.NORMAL]
    )
    assert res.invalid == 1 and res.arch_eff == VoteArch.V1OO2


def test_truth_table_sizes() -> None:
    level1 = sum(len(eval_table(a, p)) for a in VOTING_ARCHS for p in POLICIES)
    level2 = sum(
        len(fb_table(a, p, k)) for a in VOTING_ARCHS for p in POLICIES for k in (InputKind.DISCRETE, InputKind.ANALOG)
    )
    assert (level1, level2) == (300, 3888)


def test_truth_table_spot_values() -> None:
    # 2oo3 VoteTrip, все каналы в норме: xTrip 0, xDegraded 0, схема 2oo3 (индекс 4) → 16#10
    assert eval_table(VoteArch.V2OO3, Policy.VOTE_TRIP)[0] == 0x10
    # строка 2oo3 DA AI r = 0: все недостоверны → ForcedTrip, деградация → 16#17
    assert fb_table(VoteArch.V2OO3, Policy.DEGRADE_AVAILABLE, InputKind.ANALOG)[0] == 0x17
    # r = 4: канал 1 — запрос байпаса, недостоверен → байпас Active (бит 5), ForcedTrip → 16#37
    assert fb_table(VoteArch.V2OO3, Policy.DEGRADE_AVAILABLE, InputKind.ANALOG)[4] == 0x37


# Чтение состояния через функции: иначе mypy сужает тип атрибута после assert и не видит, что
# вызов ФБ его меняет.
def _out(d: Delay) -> bool:
    return d.x_out


def _sts(fb: Voting) -> VotingSts:
    return fb.sts


def _last(log: EventLog) -> EventKind:
    return log.history[-1].kind


def _energized(fb: CauseEffect) -> bool:
    return fb.effect_out[0]


# --- PL.FB_Delay -------------------------------------------------------------------------------------
def test_delay_on_exactly_at_delay() -> None:
    t = FakeTime()
    d = Delay()
    d(True, 2000, 0, t.now())
    for _ in range(19):
        t.advance(100)
        d(True, 2000, 0, t.now())
    assert not _out(d) and d.remaining_ms == 100
    t.advance(100)
    d(True, 2000, 0, t.now())
    assert _out(d) and d.remaining_ms == 0


def test_delay_zero_same_call_and_time_backwards() -> None:
    t = FakeTime()
    d = Delay()
    d(True, 0, 0, t.now())
    assert d.x_out
    d2 = Delay()
    d2(True, 1000, 0, t.now())
    t.now_ns -= 500 * NS_PER_MS  # время назад
    d2(True, 1000, 0, t.now())
    t.advance(999)
    d2(True, 1000, 0, t.now())
    assert not _out(d2)  # отсчёт начат заново
    t.advance(1)
    d2(True, 1000, 0, t.now())
    assert _out(d2)


# --- функции ------------------------------------------------------------------------------------------
def test_crc_check_values(demo: Matrix) -> None:
    import binascii

    assert binascii.crc_hqx(b"123456789", limits.CRC16_INIT) == 0x29B1
    assert demo.crc == 0xCD40
    cfg = CemCfg(cause_count=10, effect_count=7)
    for j, mask in enumerate((0x01E7, 0x00C0, 0x01EA, 0x03EA, 0x03EA, 0x03FF, 0x03FF)):
        cfg.effects[j] = EffectCfg(1, mask)
    assert cem_crc(cfg) == 0xCD40


def test_ne43_and_scaling() -> None:
    assert not ne43_valid(3.6) and ne43_valid(3.61) and ne43_valid(20.99) and not ne43_valid(21.0)
    assert not ne43_valid(math.nan) and not ne43_valid(math.inf)
    assert ai_to_eu(12.0, 0.0, 1.6) == f32(0.8)
    assert ai_to_eu(4.0, -10.0, 10.0) == -10.0


def test_default_configs_fail_safe() -> None:
    assert vote_check_cfg(VotingCfg()) & limits.VOTE_CFG_ARCH
    assert cem_check_cfg(CemCfg()) & limits.CEM_CFG_COUNT


def test_generated_config_passes_checks(demo: Matrix) -> None:
    h = Harness(demo)
    assert cem_check_cfg(h.app.cem_cfg) == 0
    for cause in demo.causes:
        if cause.is_voting:
            assert vote_check_cfg(h.app.vote_cfg[cause.no - 1]) == 0


# --- FB_Voting ---------------------------------------------------------------------------------------------
def _analog_cfg(**kw: object) -> VotingCfg:
    cfg = VotingCfg(
        arch=VoteArch.V2OO3,
        policy=Policy.VOTE_TRIP,
        input=InputKind.ANALOG,
        limit_dir=LimitDir.HIGH,
        trip_limit=50.0,
        hyst=2.0,
        bypass_max_ms=1000,
        max_bypass=1,
    )
    for key, value in kw.items():
        setattr(cfg, key, value)
    return cfg


def _vin(*values: float) -> VoteIn:
    vin = VoteIn()
    for k, v in enumerate(values):
        vin.ai[k] = v
        vin.ai_valid[k] = True
    return vin


def test_voting_inclusive_limit_and_hysteresis() -> None:
    fb = Voting()
    cfg = _analog_cfg()
    fb(_vin(50.0, 50.0, 10.0), VoteCmd(), cfg, True, 1, 0, None)
    assert fb.trip  # уставка включительна
    fb(_vin(48.0, 48.0, 10.0), VoteCmd(), cfg, True, 1, 0, None)
    assert fb.trip  # 48 = уставка − гистерезис: требование держится
    fb(_vin(47.9, 47.9, 10.0), VoteCmd(), cfg, True, 1, 0, None)
    assert not fb.trip


def test_voting_bypass_expires_exactly_and_lowest_channel_wins() -> None:
    fb = Voting()
    cfg = _analog_cfg()
    log = EventLog()
    t = FakeTime()
    cmd = VoteCmd([True, True, False])
    fb(_vin(10, 10, 10), cmd, cfg, True, 3, t.now(), log)
    assert fb.sts.bypass[:2] == [BypassState.ACTIVE, BypassState.DENIED]
    for _ in range(9):
        t.advance(100)
        fb(_vin(10, 10, 10), cmd, cfg, True, 3, t.now(), log)
    assert _sts(fb).bypass[0] == BypassState.ACTIVE and _sts(fb).bypass_remain_ms[0] == 100
    t.advance(100)
    fb(_vin(10, 10, 10), cmd, cfg, True, 3, t.now(), log)
    assert _sts(fb).bypass[0] == BypassState.EXPIRED
    kinds = [(e.kind, e.channel, e.cause) for e in log.history]
    assert kinds == [
        (EventKind.BYPASS_ON, 1, 3),
        (EventKind.BYPASS_DENIED, 2, 3),
        (EventKind.BYPASS_EXPIRED, 1, 3),
    ]


def test_voting_permit_lost_ends_bypass_and_cfg_error_trips() -> None:
    fb = Voting()
    cfg = _analog_cfg()
    log = EventLog()
    fb(_vin(10, 10, 10), VoteCmd([True, False, False]), cfg, True, 1, 0, log)
    fb(_vin(10, 10, 10), VoteCmd([True, False, False]), cfg, False, 1, 0, log)
    assert _sts(fb).bypass[0] == BypassState.DENIED
    assert _last(log) == EventKind.BYPASS_OFF
    bad = _analog_cfg(arch=VoteArch.NONE)
    fb(_vin(10, 10, 10), VoteCmd(), bad, True, 1, 0, log)
    assert fb.trip and fb.sts.cfg_error and fb.sts.arch_eff == VoteArch.NONE
    assert _last(log) == EventKind.CFG_ERROR


def test_voting_discrepancy_after_delay_strict() -> None:
    fb = Voting()
    cfg = _analog_cfg(disc_max=5.0, disc_delay_ms=1000)
    t = FakeTime()
    fb(_vin(10, 15, 10), VoteCmd(), cfg, True, 1, t.now(), None)
    assert _sts(fb).spread == 5.0 and not _sts(fb).discrepancy  # ровно на пределе — норма
    fb(_vin(10, 15.5, 10), VoteCmd(), cfg, True, 1, t.now(), None)
    t.advance(1000)
    fb(_vin(10, 15.5, 10), VoteCmd(), cfg, True, 1, t.now(), None)
    assert _sts(fb).discrepancy and not fb.trip


# --- FB_CauseEffect: диаграмма 6.11 ---------------------------------------------------------------------
def test_timing_diagram_6_11() -> None:
    cfg = CemCfg(cause_count=2, effect_count=1, start_tripped=False)
    cfg.causes[0] = CauseCfg(enable=True, delay_ms=2000)
    cfg.causes[1] = CauseCfg(enable=True, delay_ms=5000, override_allowed=True, override_max_ms=15 * 60_000)
    cfg.effects[0] = EffectCfg(1, 0x0003)
    cfg.crc = cem_crc(cfg)
    fb = CauseEffect()
    log = EventLog()
    t = FakeTime()
    cmd = CemCmd()
    demand = [False] * 16

    def call() -> list[tuple[EventKind, int]]:
        before = len(log.history)
        fb(demand, True, False, t.now(), log, cmd, cfg)
        effect_kinds = (EventKind.EFFECT_TRIP, EventKind.EFFECT_RESTORE)
        # события следствий — с номером следствия (как «EffectTrip(1)» в 6.11), остальные — с причиной
        return [(e.kind, e.effect if e.kind in effect_kinds else e.cause) for e in log.history[before:]]

    def run(ms: int) -> list[tuple[EventKind, int]]:
        events: list[tuple[EventKind, int]] = []
        for _ in range(ms // 100):
            t.advance(100)
            events += call()
        return events

    call()
    assert _energized(fb)  # t0 — все следствия под напряжением
    t0 = t.now()
    demand[0] = True
    assert call() == [(EventKind.CAUSE_DEMAND, 1)]
    assert _energized(fb) and fb.sts.delay_remain_ms[0] == 2000
    run(1900)
    assert fb.sts.latched == 0
    assert run(100) == [(EventKind.FIRST_OUT, 1), (EventKind.CAUSE_TRIP, 1), (EventKind.EFFECT_TRIP, 1)]
    assert fb.sts.lt_first_out == t0 + 2000 * NS_PER_MS
    run(900)
    t.advance(100)
    cmd.reset = True
    assert call() == [(EventKind.RESET_DENIED, 1)]
    run(900)
    t.advance(100)
    demand[0] = False
    assert call() == [(EventKind.CAUSE_CLEAR, 1)]
    assert not _energized(fb)
    run(900)
    t.advance(100)
    cmd.reset = True
    events = call()
    assert events == [(EventKind.RESET_DONE, 0), (EventKind.EFFECT_RESTORE, 1)]
    assert _energized(fb) and fb.sts.first_out == 0
    # t1: обход причины 2 и её требование в одном вызове
    t.advance(1000)
    cmd.override_req = 0x0002
    demand[1] = True
    assert call() == [(EventKind.CAUSE_DEMAND, 2), (EventKind.OVERRIDE_ON, 2)]
    run(15 * 60_000 - 100)
    assert fb.sts.overridden == 0x0002 and fb.sts.override_remain_ms[1] == 100 and fb.sts.latched == 0
    assert run(100) == [
        (EventKind.OVERRIDE_EXPIRED, 2),
        (EventKind.FIRST_OUT, 2),
        (EventKind.CAUSE_TRIP, 2),
        (EventKind.EFFECT_TRIP, 1),
    ]
    assert log.history[-1].cause == 2  # EffectTrip несёт младшую зафиксированную причину из маски


def test_cem_start_tripped_and_cfg_error() -> None:
    cfg = CemCfg(cause_count=1, effect_count=1, start_tripped=True)
    cfg.causes[0] = CauseCfg(enable=True)
    cfg.effects[0] = EffectCfg(1, 0x0001)
    cfg.crc = cem_crc(cfg)
    fb = CauseEffect()
    fb([False] * 16, True, False, 0, None, CemCmd(), cfg)
    assert fb.sts.first_out == limits.SIS_FIRST_OUT_START and not fb.effect_out[0]
    cfg.crc ^= 1  # ручная правка конфигурации без генератора
    fb([False] * 16, True, False, 0, None, CemCmd(reset=True), cfg)
    assert fb.sts.cfg_error and fb.sts.reset_blocker == limits.SIS_FIRST_OUT_CFG and fb.tripped


# --- примеры 12.4 на демо-матрице --------------------------------------------------------------------------
def _invalid_then_second(demo: Matrix, tag: str) -> tuple[bool, bool]:
    cause = next(c for c in demo.causes if c.tag == tag)
    h = Harness(demo)
    assert h.arm()
    name, value = channel_invalid(cause, 1)
    h.io[name] = value
    h.cycle()
    h.run(cause.delay_ms, 100)
    first = bool(h.app.cem_sts.latched & cause.bit)
    name, value = channel_demand(cause, 2)
    h.io[name] = value
    h.cycle()
    h.run(cause.delay_ms, 100)
    return first, bool(h.app.cem_sts.latched & cause.bit)


def test_policy_difference_pshh101_trips_lshh102_not(demo: Matrix) -> None:
    assert _invalid_then_second(demo, "PSHH101") == (False, True)  # VoteTrip: 2oo3 → 1oo2
    assert _invalid_then_second(demo, "LSHH102") == (False, False)  # DegradeAvailable: 2oo3 → 2oo2


def test_demo_has_no_cross_demands(demo: Matrix) -> None:
    assert cross_demands(demo) == []


def test_demo_stimuli(demo: Matrix) -> None:
    pshh = demo.cause(1)
    assert pshh.analog is not None
    assert pshh.analog.demand_ma == pytest.approx(13.2)  # 0,92 МПа — как в примере 12.4
    assert pshh.analog.normal_ma == pytest.approx(10.0)


# --- неисправность источника времени (D-19) и срок нового обхода (6.4, D-13) ------------------------------
def test_voting_time_backwards_ends_bypass() -> None:
    fb = Voting()
    cfg = _analog_cfg(bypass_max_ms=10_000)
    log = EventLog()
    t = FakeTime()
    cmd = VoteCmd([True, False, False])
    fb(_vin(10, 10, 10), cmd, cfg, True, 1, t.now(), log)
    t0 = t.now()
    t.advance(6000)
    fb(_vin(10, 10, 10), cmd, cfg, True, 1, t.now(), log)
    assert _sts(fb).bypass[0] == BypassState.ACTIVE
    t.now_ns = t0 - 1000 * NS_PER_MS  # время назад
    fb(_vin(10, 10, 10), cmd, cfg, True, 1, t.now(), log)
    assert _sts(fb).bypass[0] == BypassState.EXPIRED and _sts(fb).bypass_remain_ms[0] == 0
    assert _sts(fb).ch_state[0] == ChannelState.NORMAL
    assert [(e.kind, e.channel) for e in log.history[-2:]] == [
        (EventKind.TIME_FAULT, 0),
        (EventKind.BYPASS_EXPIRED, 1),
    ]
    t.advance(100)
    fb(_vin(10, 10, 10), VoteCmd(), cfg, True, 1, t.now(), log)  # запрос снят
    t.advance(100)
    fb(_vin(10, 10, 10), cmd, cfg, True, 1, t.now(), log)  # новый запрос — полный срок
    assert _sts(fb).bypass[0] == BypassState.ACTIVE and _sts(fb).bypass_remain_ms[0] == 10_000
    assert sum(1 for e in log.history if e.kind == EventKind.TIME_FAULT) == 1


def _cem_base() -> CemCfg:
    """Матрица ручных тестов ST (``FB_CauseEffect_Test.CfgBase``)."""
    cfg = CemCfg(cause_count=4, effect_count=3, start_tripped=False)
    cfg.causes[0] = CauseCfg(enable=True, delay_ms=2000)
    cfg.causes[1] = CauseCfg(enable=True, delay_ms=5000, override_allowed=True, override_max_ms=15 * 60_000)
    cfg.causes[2] = CauseCfg(
        enable=True, source=CauseSource.EXTERNAL, delay_ms=0, override_allowed=True, override_max_ms=10_000
    )
    cfg.effects[0] = EffectCfg(1, 0x0003)
    cfg.effects[1] = EffectCfg(4, 0x0004)
    cfg.effects[2] = EffectCfg(5, 0x000F)
    cfg.crc = cem_crc(cfg)
    return cfg


class _Cem:
    """Стенд модели ``FB_CauseEffect`` с подменным временем (как ``FB_CemRig``)."""

    def __init__(self) -> None:
        self.cfg = _cem_base()
        self.fb = CauseEffect()
        self.log = EventLog()
        self.t = FakeTime()
        self.cmd = CemCmd()
        self.demand = [False] * 16

    def cycle(self) -> None:
        self.fb(self.demand, True, False, self.t.now(), self.log, self.cmd, self.cfg)

    def step(self, ms: int) -> None:
        self.t.advance(ms)
        self.cycle()

    def run(self, ms: int, step: int) -> None:
        for _ in range(ms // step):
            self.step(step)

    def sts(self) -> CauseEffectSts:
        return self.fb.sts

    def count(self, kind: EventKind) -> int:
        return sum(1 for e in self.log.history if e.kind == kind)


def test_cem_time_backwards_trips_pending_delay() -> None:
    r = _Cem()
    r.cycle()
    r.demand[0] = True
    r.step(100)
    t0 = r.t.now()
    r.run(1500, 100)
    assert r.sts().latched == 0
    r.t.now_ns = t0 - 1000 * NS_PER_MS  # время назад
    r.cycle()
    assert r.count(EventKind.TIME_FAULT) == 1
    assert r.sts().latched == 0x0001 and r.sts().first_out == 1  # причина 2 без требования — нет
    assert not r.fb.effect_out[0] and r.fb.effect_out[1]
    r.step(100)
    assert r.count(EventKind.TIME_FAULT) == 1


def test_cem_time_backwards_ends_override() -> None:
    r = _Cem()
    r.cycle()
    r.cmd.override_req = 0x0002
    r.demand[1] = True
    r.step(100)
    t1 = r.t.now()
    r.run(60_000, 10_000)
    assert r.sts().overridden == 0x0002 and r.sts().latched == 0
    r.t.now_ns = t1 - 1000 * NS_PER_MS  # время назад
    r.cycle()
    assert r.sts().overridden == 0 and r.sts().override_remain_ms[1] == 0
    assert r.count(EventKind.OVERRIDE_EXPIRED) == 1
    assert r.sts().latched == 0x0002 and not r.fb.effect_out[0]


def test_cem_override_rerequest_after_expiry_gets_full_time() -> None:
    r = _Cem()
    r.cycle()
    r.cmd.override_req = 0x0004
    r.step(100)
    r.run(10_000, 1000)
    assert r.sts().overridden == 0
    r.cmd.override_req = 0x0004
    r.step(100)  # новый запрос в вызове сразу после истечения
    assert _last(r.log) == EventKind.OVERRIDE_ON
    assert r.sts().overridden == 0x0004 and r.sts().override_remain_ms[2] == 10_000
    r.run(9900, 100)
    assert r.sts().overridden == 0x0004
    r.step(100)
    assert r.sts().overridden == 0


def test_cem_override_cancel_and_request_in_one_call_restarts() -> None:
    r = _Cem()
    r.cycle()
    r.cmd.override_req = 0x0004
    r.step(100)
    r.run(6000, 1000)
    assert r.sts().override_remain_ms[2] == 4000
    r.cmd.override_cancel = 0x0004
    r.cmd.override_req = 0x0004
    r.step(100)
    assert [e.kind for e in r.log.history[-2:]] == [EventKind.OVERRIDE_OFF, EventKind.OVERRIDE_ON]
    assert r.sts().override_remain_ms[2] == 10_000  # D-13: новый обход — полный срок
    r.run(9900, 100)
    assert r.sts().overridden == 0x0004
    r.step(100)
    assert r.sts().overridden == 0
