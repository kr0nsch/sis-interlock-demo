"""Эталонная модель голосования ПАЗ на Python — по тексту docs/DESIGN.md, а не по коду ST.

Переносит нормативные части контракта:
- 3.3 — семантика PL.FB_Delay (отметка при смене входа и в первом вызове, «время назад»);
- 5.1, 5.2 — состояния каналов и алгоритм F_VoteEval;
- 5.5–5.9 — порядок тела FB_Voting: конфигурация, каналы, достоверность, байпасы, голосование,
  рассогласование, состояние;
- 12.2 — кодирование строк таблиц истинности и ожидаемого байта.

Модель и код ST пишутся по контракту независимо: расхождение ловят сгенерированные тесты coUnit
(tools_project/gen_voting_tests.py), спор решает текст контракта. Время — целые наносекунды.
Только стандартная библиотека Python.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

# --- Перечисления (раздел 4.1): коды как в ST --------------------------------------------------

ARCH_NONE = 0
VOTE_1OO1 = 11
VOTE_1OO2 = 12
VOTE_2OO2 = 22
VOTE_2OO3 = 23
FORCED_TRIP = 99

VOTE_TRIP = 1
DEGRADE_SAFE = 2
DEGRADE_AVAILABLE = 3
POLICIES = (VOTE_TRIP, DEGRADE_SAFE, DEGRADE_AVAILABLE)

NOT_USED = 0
NORMAL = 1
DEMAND = 2
INVALID = 3
BYPASSED = 4

BYPASS_OFF = 0
BYPASS_ACTIVE = 1
BYPASS_EXPIRED = 2
BYPASS_DENIED = 3

DISCRETE = 1
ANALOG = 2

LIMIT_HIGH = 1
LIMIT_LOW = 2

# Коды событий E_SisEventKind, которые пишет FB_Voting (раздел 7.2)
EV_BYPASS_ON = 13
EV_BYPASS_OFF = 14
EV_BYPASS_EXPIRED = 15
EV_BYPASS_DENIED = 16
EV_CHANNEL_INVALID = 17
EV_CHANNEL_VALID = 18
EV_DISCREPANCY_ON = 19
EV_DISCREPANCY_OFF = 20
EV_CFG_ERROR = 21
EV_CFG_OK = 22
EV_TIME_FAULT = 24  # D-19: время источника пошло назад

# --- Константы (раздел 4.3) ----------------------------------------------------------------------

CH_MAX = 3  # SIS_VOTE_CH_MAX
NS_PER_MS = 1_000_000
SIS_DELAY_MAX_NS = 10 * 60 * 1000 * NS_PER_MS  # T#10M
SIS_BYPASS_MAX_NS = 12 * 3600 * 1000 * NS_PER_MS  # T#12H
REAL_SANE_MAX = 1.0e30  # PL.GVL_Const.REAL_SANE_MAX (PL.F_IsFinite)

VOTE_CFG_ARCH = 0x0001
VOTE_CFG_POLICY = 0x0002
VOTE_CFG_INPUT = 0x0004
VOTE_CFG_LIMIT = 0x0008
VOTE_CFG_DISCREPANCY = 0x0010
VOTE_CFG_BYPASS = 0x0020

# Таблица 5.1: схема -> (N, M)
ARCH_NM: dict[int, tuple[int, int]] = {
    VOTE_1OO1: (1, 1),
    VOTE_1OO2: (2, 1),
    VOTE_2OO2: (2, 2),
    VOTE_2OO3: (3, 2),
}
# Действующая схема по (Mh, Rh) — раздел 5.2
EFFECTIVE_ARCH: dict[tuple[int, int], int] = {
    (1, 1): VOTE_1OO1,
    (1, 2): VOTE_1OO2,
    (2, 2): VOTE_2OO2,
    (2, 3): VOTE_2OO3,
}
# Индекс схемы в ожидаемом байте (раздел 12.2, биты 2–4)
ARCH_INDEX: dict[int, int] = {
    ARCH_NONE: 0,
    VOTE_1OO1: 1,
    VOTE_1OO2: 2,
    VOTE_2OO2: 3,
    VOTE_2OO3: 4,
    FORCED_TRIP: 5,
}
ARCH_NAME: dict[int, str] = {
    ARCH_NONE: "None",
    VOTE_1OO1: "1oo1",
    VOTE_1OO2: "1oo2",
    VOTE_2OO2: "2oo2",
    VOTE_2OO3: "2oo3",
    FORCED_TRIP: "ForcedTrip",
}


def arch_channels(arch: int) -> int:
    """F_VoteArchChannels (5.10): N по таблице 5.1; 0 — для None, ForcedTrip и прочих."""
    return ARCH_NM.get(arch, (0, 0))[0]


def arch_required(arch: int) -> int:
    """F_VoteArchRequired (5.10): M; 0 — как выше."""
    return ARCH_NM.get(arch, (0, 0))[1]


def is_finite(value: float) -> bool:
    """PL.F_IsFinite: FALSE для NaN, ±Inf и |x| > REAL_SANE_MAX."""
    return math.isfinite(value) and abs(value) <= REAL_SANE_MAX


# --- 5.2 F_VoteEval ------------------------------------------------------------------------------


@dataclass(frozen=True)
class VoteResult:
    """ST_VoteResult."""

    trip: bool
    degraded: bool
    arch_eff: int
    demand: int = 0
    invalid: int = 0
    bypassed: int = 0
    normal: int = 0


def vote_eval(arch: int, policy: int, channels: tuple[int, ...]) -> VoteResult:
    """Нормативный псевдокод раздела 5.2, построчно."""
    n = arch_channels(arch)
    m = arch_required(arch)
    if n == 0 or policy not in POLICIES:
        return VoteResult(trip=True, degraded=False, arch_eff=ARCH_NONE)
    b = f = d = h = 0
    for state in channels[:n]:
        if state == BYPASSED:
            b += 1
        elif state == DEMAND:
            d += 1
        elif state == NORMAL:
            h += 1
        else:  # Invalid, NotUsed внутри N
            f += 1
    degraded = (b + f) > 0
    if policy == VOTE_TRIP:
        x, fv = b, f
    else:
        x, fv = b + f, 0
    r = n - x

    def forced() -> VoteResult:
        return VoteResult(True, degraded, FORCED_TRIP, d, f, b, h)

    if r == 0:
        return forced()
    meff = min(m, r) if policy == DEGRADE_AVAILABLE else max(1, m - x)
    mh = meff - fv
    rh = r - fv
    if mh <= 0:
        return forced()
    trip = d >= mh
    eff = EFFECTIVE_ARCH.get((mh, rh))
    if eff is None:  # недостижимо — защитная ветвь
        return VoteResult(True, degraded, ARCH_NONE, d, f, b, h)
    return VoteResult(trip, degraded, eff, d, f, b, h)


# --- 3.3 PL.FB_Delay -----------------------------------------------------------------------------


@dataclass
class Delay:
    """Задержка включения и отключения (контракт PL, 7.4; DESIGN 3.3)."""

    out: bool = False
    change: int = 0
    in_prev: bool = False
    restart: bool = True
    remaining_ns: int = 0

    def __call__(self, x_in: bool, on_ns: int, off_ns: int, now: int) -> bool:
        if now < self.change or self.restart or x_in != self.in_prev:
            self.change = now
        self.restart = False
        self.in_prev = x_in
        delay = on_ns if x_in else off_ns
        elapsed = now - self.change
        if x_in != self.out and elapsed >= delay:
            self.out = x_in
        self.remaining_ns = delay - elapsed if x_in != self.out else 0
        return self.out


# --- 5.4–5.9 FB_Voting ---------------------------------------------------------------------------


@dataclass
class VotingCfg:
    """ST_VotingCfg; длительности — нс."""

    arch: int = ARCH_NONE
    policy: int = VOTE_TRIP
    input_kind: int = DISCRETE
    di_healthy: bool = True
    limit_dir: int = LIMIT_HIGH
    trip_limit: float = 0.0
    hyst: float = 0.0
    discrepancy_max: float = 0.0
    discrepancy_delay_ns: int = 0
    bypass_max_ns: int = 0
    max_bypass: int = 0


@dataclass
class VoteIn:
    """ST_VoteIn: каналы 1..3 (индекс 0..2)."""

    di: list[bool] = field(default_factory=lambda: [False] * CH_MAX)
    di_valid: list[bool] = field(default_factory=lambda: [False] * CH_MAX)
    ai: list[float] = field(default_factory=lambda: [0.0] * CH_MAX)
    ai_valid: list[bool] = field(default_factory=lambda: [False] * CH_MAX)


@dataclass(frozen=True)
class Event:
    """Событие журнала (поля ST_SisEvent без номера)."""

    time: int
    kind: int
    cause: int
    channel: int
    value: float


@dataclass
class VotingSts:
    """ST_VotingSts (поля, которые нужны таблицам и сценариям)."""

    trip: bool = True
    arch_eff: int = ARCH_NONE
    degraded: bool = False
    cfg_error: bool = False
    cfg_err: int = 0
    discrepancy: bool = False
    spread: float = 0.0
    counts: tuple[int, int, int, int] = (0, 0, 0, 0)  # demand, invalid, bypassed, normal
    ch_state: tuple[int, ...] = (NOT_USED,) * CH_MAX
    bypass: tuple[int, ...] = (BYPASS_OFF,) * CH_MAX
    bypass_remain_ns: tuple[int, ...] = (0,) * CH_MAX


def check_cfg(cfg: VotingCfg) -> int:
    """F_VoteCheckCfg (5.9): сумма битов VOTE_CFG_*."""
    err = 0
    n = arch_channels(cfg.arch)
    if n == 0:
        err |= VOTE_CFG_ARCH
    if cfg.policy not in POLICIES:
        err |= VOTE_CFG_POLICY
    if cfg.input_kind not in (DISCRETE, ANALOG):
        err |= VOTE_CFG_INPUT
    if cfg.input_kind == ANALOG:
        if (
            not is_finite(cfg.trip_limit)
            or not is_finite(cfg.hyst)
            or cfg.hyst < 0.0
            or cfg.limit_dir not in (LIMIT_HIGH, LIMIT_LOW)
        ):
            err |= VOTE_CFG_LIMIT
        if (
            not is_finite(cfg.discrepancy_max)
            or cfg.discrepancy_max < 0.0
            or cfg.discrepancy_delay_ns > SIS_DELAY_MAX_NS
        ):
            err |= VOTE_CFG_DISCREPANCY
    bypass_bad = cfg.max_bypass > 0 if n == 0 else cfg.max_bypass > n - 1
    if bypass_bad or cfg.bypass_max_ns > SIS_BYPASS_MAX_NS:
        err |= VOTE_CFG_BYPASS
    return err


@dataclass
class Voting:
    """FB_Voting: состояние экземпляра между вызовами."""

    bypass_timers: list[Delay] = field(default_factory=lambda: [Delay() for _ in range(CH_MAX)])
    disc_timer: Delay = field(default_factory=Delay)
    dem_mem: list[bool] = field(default_factory=lambda: [False] * CH_MAX)
    valid_prev: list[bool] = field(default_factory=lambda: [True] * CH_MAX)
    bypass: list[int] = field(default_factory=lambda: [BYPASS_OFF] * CH_MAX)
    cfg_err_prev: bool = False
    disc_prev: bool = False
    lt_prev: int = 0
    events: list[Event] = field(default_factory=list)
    sts: VotingSts = field(default_factory=VotingSts)

    def _log(self, now: int, kind: int, cause: int, channel: int = 0, value: float = 0.0) -> None:
        self.events.append(Event(now, kind, cause, channel, value))

    def call(
        self,
        now: int,
        cfg: VotingCfg,
        vin: VoteIn,
        bypass_req: list[bool],
        bypass_permit: bool,
        cause: int = 0,
    ) -> VotingSts:
        # 1. Время: «время назад» (now меньше времени прошлого вызова) — неисправность источника (D-19)
        time_back = now < self.lt_prev
        self.lt_prev = now
        # 2. Конфигурация
        err = check_cfg(cfg)
        cfg_err = err != 0
        if cfg_err and not self.cfg_err_prev:
            self._log(now, EV_CFG_ERROR, cause, 0, float(err))
        elif self.cfg_err_prev and not cfg_err:
            self._log(now, EV_CFG_OK, cause)
        self.cfg_err_prev = cfg_err
        if time_back:
            self._log(now, EV_TIME_FAULT, cause)

        spread = 0.0
        disc = False
        remain = [0] * CH_MAX
        if cfg_err:
            for k in range(CH_MAX):
                if self.bypass[k] == BYPASS_ACTIVE:
                    self._log(now, EV_BYPASS_OFF, cause, k + 1)
                self.bypass[k] = BYPASS_OFF
                self.bypass_timers[k](False, cfg.bypass_max_ns, 0, now)
            self.disc_timer(False, cfg.discrepancy_delay_ns, 0, now)
            states = [NOT_USED] * CH_MAX
            res = VoteResult(trip=True, degraded=False, arch_eff=ARCH_NONE)
        else:
            n = arch_channels(cfg.arch)
            valid = [False] * CH_MAX
            dem = [False] * CH_MAX
            # 3. Сырые состояния (5.6)
            for k in range(CH_MAX):
                if k >= n:
                    self.dem_mem[k] = False
                    continue
                if cfg.input_kind == DISCRETE:
                    valid[k] = vin.di_valid[k]
                    dem[k] = vin.di[k] != cfg.di_healthy
                else:
                    r = vin.ai[k]
                    valid[k] = vin.ai_valid[k] and is_finite(r)
                    if not valid[k]:
                        self.dem_mem[k] = False
                    elif cfg.limit_dir == LIMIT_HIGH:
                        self.dem_mem[k] = r >= cfg.trip_limit or (self.dem_mem[k] and r >= cfg.trip_limit - cfg.hyst)
                    else:
                        self.dem_mem[k] = r <= cfg.trip_limit or (self.dem_mem[k] and r <= cfg.trip_limit + cfg.hyst)
                    dem[k] = self.dem_mem[k]
            # 4. События достоверности
            for k in range(n):
                if valid[k] != self.valid_prev[k]:
                    value = vin.ai[k] if cfg.input_kind == ANALOG else 0.0
                    self._log(now, EV_CHANNEL_VALID if valid[k] else EV_CHANNEL_INVALID, cause, k + 1, value)
                    self.valid_prev[k] = valid[k]
            # 5. Байпасы (5.7)
            for k in range(CH_MAX):
                self.bypass_timers[k](self.bypass[k] == BYPASS_ACTIVE, cfg.bypass_max_ns, 0, now)
            for k in range(n):
                req = bypass_req[k]
                if self.bypass[k] == BYPASS_ACTIVE:
                    if not req:
                        self.bypass[k] = BYPASS_OFF
                        self._log(now, EV_BYPASS_OFF, cause, k + 1)
                    elif not bypass_permit:
                        self.bypass[k] = BYPASS_DENIED
                        self._log(now, EV_BYPASS_OFF, cause, k + 1)
                    elif self.bypass_timers[k].out or time_back:
                        self.bypass[k] = BYPASS_EXPIRED
                        self._log(now, EV_BYPASS_EXPIRED, cause, k + 1)
                elif self.bypass[k] in (BYPASS_EXPIRED, BYPASS_DENIED) and not req:
                    self.bypass[k] = BYPASS_OFF
            for k in range(n):
                if self.bypass[k] == BYPASS_OFF and bypass_req[k]:
                    active = sum(1 for j in range(n) if self.bypass[j] == BYPASS_ACTIVE)
                    if bypass_permit and cfg.bypass_max_ns > 0 and active < cfg.max_bypass:
                        self.bypass[k] = BYPASS_ACTIVE
                        self._log(now, EV_BYPASS_ON, cause, k + 1)
                        self.bypass_timers[k](True, cfg.bypass_max_ns, 0, now)
                    else:
                        self.bypass[k] = BYPASS_DENIED
                        self._log(now, EV_BYPASS_DENIED, cause, k + 1)
            for k in range(n, CH_MAX):
                self.bypass[k] = BYPASS_OFF
            for k in range(CH_MAX):
                remain[k] = self.bypass_timers[k].remaining_ns if self.bypass[k] == BYPASS_ACTIVE else 0
            # 6. Состояния каналов
            states = []
            for k in range(CH_MAX):
                if k >= n:
                    states.append(NOT_USED)
                elif self.bypass[k] == BYPASS_ACTIVE:
                    states.append(BYPASSED)
                elif not valid[k]:
                    states.append(INVALID)
                elif dem[k]:
                    states.append(DEMAND)
                else:
                    states.append(NORMAL)
            # 7. Голосование
            res = vote_eval(cfg.arch, cfg.policy, tuple(states))
            # 8. Рассогласование (5.8)
            values = [vin.ai[k] for k in range(n) if states[k] in (NORMAL, DEMAND)]
            cond = False
            if cfg.input_kind == ANALOG and cfg.discrepancy_max > 0.0 and len(values) >= 2:
                spread = max(values) - min(values)
                cond = spread > cfg.discrepancy_max
            disc = self.disc_timer(cond, cfg.discrepancy_delay_ns, 0, now)
        if disc and not self.disc_prev:
            self._log(now, EV_DISCREPANCY_ON, cause, 0, spread)
        elif self.disc_prev and not disc:
            self._log(now, EV_DISCREPANCY_OFF, cause)
        self.disc_prev = disc
        # 9. Состояние
        self.sts = VotingSts(
            trip=res.trip,
            arch_eff=res.arch_eff,
            degraded=res.degraded,
            cfg_error=cfg_err,
            cfg_err=err,
            discrepancy=disc,
            spread=spread,
            counts=(res.demand, res.invalid, res.bypassed, res.normal),
            ch_state=tuple(states),
            bypass=tuple(self.bypass),
            bypass_remain_ns=tuple(remain),
        )
        return self.sts


# --- 12.2 Таблицы истинности ---------------------------------------------------------------------

ROW_STATE_CODES = (NORMAL, DEMAND, INVALID, BYPASSED)  # код 0..3 канала строки уровня 1
TABLE_TRIP_LIMIT = 50.0
TABLE_AI_DEMAND = 60.0
TABLE_AI_NORMAL = 40.0
TABLE_BYPASS_MAX_NS = 3600 * 1000 * NS_PER_MS  # T#1H
TABLE_NOW = 3600 * 1000 * NS_PER_MS  # PL.FB_FakeTime стартует с LTIME#1H; время не меняется


def encode(trip: bool, degraded: bool, arch_eff: int, bypass_active: tuple[bool, ...] = ()) -> int:
    """Ожидаемый байт: бит 0 — xTrip, бит 1 — xDegraded, биты 2–4 — индекс eArchEff,
    биты 5–7 — aeBypass[k] = Active для k = 1..3 (только уровень 2)."""
    value = int(trip) | (int(degraded) << 1) | (ARCH_INDEX[arch_eff] << 2)
    for k, active in enumerate(bypass_active):
        value |= int(active) << (5 + k)
    return value


def eval_row_states(arch: int, row: int) -> tuple[int, ...]:
    """Уровень 1: состояние канала k — код (row SHR 2(k−1)) AND 3; k > N — NotUsed."""
    n = arch_channels(arch)
    return tuple(ROW_STATE_CODES[(row >> (2 * k)) & 3] if k < n else NOT_USED for k in range(CH_MAX))


def eval_table(arch: int, policy: int) -> list[int]:
    """Таблица уровня 1: ожидаемые байты строк 0..4^N − 1."""
    n = arch_channels(arch)
    result = []
    for row in range(4**n):
        res = vote_eval(arch, policy, eval_row_states(arch, row))
        result.append(encode(res.trip, res.degraded, res.arch_eff))
    return result


@dataclass(frozen=True)
class FbRow:
    """Строка уровня 2 для канала k: требование, достоверность, запрос байпаса."""

    demand: tuple[bool, ...]
    valid: tuple[bool, ...]
    bypass_req: tuple[bool, ...]


def fb_row_inputs(arch: int, row: int) -> FbRow:
    """Уровень 2: для канала k биты b = 3(k−1): b — требование, b+1 — достоверность,
    b+2 — запрос байпаса; каналы k > N — всё FALSE."""
    n = arch_channels(arch)

    def bit(k: int, off: int) -> bool:
        return k < n and bool((row >> (3 * k + off)) & 1)

    return FbRow(
        demand=tuple(bit(k, 0) for k in range(CH_MAX)),
        valid=tuple(bit(k, 1) for k in range(CH_MAX)),
        bypass_req=tuple(bit(k, 2) for k in range(CH_MAX)),
    )


def table_cfg(arch: int, policy: int, input_kind: int) -> VotingCfg:
    """Конфигурация теста уровня 2 (раздел 12.2)."""
    n = arch_channels(arch)
    return VotingCfg(
        arch=arch,
        policy=policy,
        input_kind=input_kind,
        di_healthy=True,
        limit_dir=LIMIT_HIGH,
        trip_limit=TABLE_TRIP_LIMIT,
        hyst=0.0,
        discrepancy_max=0.0,
        discrepancy_delay_ns=0,
        bypass_max_ns=TABLE_BYPASS_MAX_NS,
        max_bypass=min(1, n - 1),
    )


def fb_row_vote_in(inputs: FbRow) -> VoteIn:
    """Входы группы для строки: DI — axDi := FALSE при требовании (xDiHealthy = TRUE);
    AI — 60.0 при требовании, иначе 40.0 (уставка 50.0)."""
    return VoteIn(
        di=[not d for d in inputs.demand],
        di_valid=list(inputs.valid),
        ai=[TABLE_AI_DEMAND if d else TABLE_AI_NORMAL for d in inputs.demand],
        ai_valid=list(inputs.valid),
    )


def fb_table(arch: int, policy: int, input_kind: int) -> list[int]:
    """Таблица уровня 2: один экземпляр на таблицу, строки по порядку; на строку два вызова —
    со снятыми запросами байпаса (сбрасывает байпасы прошлой строки) и с полной строкой."""
    n = arch_channels(arch)
    cfg = table_cfg(arch, policy, input_kind)
    fb = Voting()
    result = []
    for row in range(8**n):
        inputs = fb_row_inputs(arch, row)
        vin = fb_row_vote_in(inputs)
        fb.call(TABLE_NOW, cfg, vin, [False] * CH_MAX, bypass_permit=True, cause=1)
        sts = fb.call(TABLE_NOW, cfg, vin, list(inputs.bypass_req), bypass_permit=True, cause=1)
        active = tuple(state == BYPASS_ACTIVE for state in sts.bypass)
        result.append(encode(sts.trip, sts.degraded, sts.arch_eff, active))
    return result
