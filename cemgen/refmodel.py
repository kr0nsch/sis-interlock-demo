"""Эталонная модель логики ПАЗ (DESIGN.md, разделы 3.3, 5–8, 10.5, 12.5).

Построчный перенос нормативного псевдокода контракта на Python, с теми же шагами в
комментариях. Модель независима от ST: ожидаемые значения сгенерированных тестов (таблицы
истинности 12.2, сценарии по матрице 12.4) считает она, а реализацию на ST пишут по тому же
тексту контракта отдельно. Расхождение ловят тесты coUnit; спор решает текст контракта.

Соглашения:

* время — целые наносекунды (``LTIME``), длительности ``TIME`` — целые миллисекунды;
* вещественные значения ``REAL`` округляются до float32 на каждой операции (:func:`f32`),
  как в ПЛК;
* каналы ``k = 1..3`` хранятся в списках с индексами ``0..2``; причины и следствия
  ``1..16`` — с индексами ``0..15``.
"""

from __future__ import annotations

import binascii
import math
import struct
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Protocol

from cemgen import limits
from cemgen.model import Cause, Matrix, Signal
from cemgen.sisdefs import (
    ARCH_INDEX,
    ARCH_NM,
    BypassState,
    CauseSource,
    ChannelState,
    EventKind,
    InputKind,
    LimitDir,
    Policy,
    SafeState,
    VoteArch,
)

NS_PER_MS = 1_000_000
LTIME_START_NS = 3600 * 1000 * NS_PER_MS  # FB_FakeTime: старт LTIME#1H
CH = limits.SIS_VOTE_CH_MAX
NC = limits.SIS_CAUSES_MAX
NE = limits.SIS_EFFECTS_MAX


# --- REAL ----------------------------------------------------------------------------------------
def f32(value: float) -> float:
    """Округлить до float32 (REAL); NaN и бесконечности сохраняются."""
    if math.isnan(value) or math.isinf(value):
        return value
    try:
        return float(struct.unpack("<f", struct.pack("<f", value))[0])
    except OverflowError:
        return math.copysign(math.inf, value)


def is_finite(value: float) -> bool:
    """``PL.F_IsFinite``: не NaN, не ±Inf и ``|x| <= REAL_SANE_MAX``."""
    return not (math.isnan(value) or math.isinf(value)) and abs(value) <= f32(limits.REAL_SANE_MAX)


def ai_to_eu(ma: float, lo: float, hi: float) -> float:
    """``F_SisAiToEu``: ``rLo + (rIn − MA_ZERO) / MA_SPAN · (rHi − rLo)`` без ограничения."""
    part = f32(f32(f32(ma) - f32(limits.MA_ZERO)) / f32(limits.MA_SPAN))
    return f32(f32(lo) + f32(part * f32(f32(hi) - f32(lo))))


def ne43_valid(ma: float) -> bool:
    """``F_SisNe43Valid``: конечно и 3,6 мА < I < 21,0 мА."""
    return is_finite(ma) and f32(ma) > f32(limits.NE43_FAIL_LOW_MA) and f32(ma) < f32(limits.NE43_FAIL_HIGH_MA)


# --- время и журнал --------------------------------------------------------------------------------
@dataclass
class FakeTime:
    """``PL.FB_FakeTime``: время меняется только методами."""

    now_ns: int = LTIME_START_NS

    def advance(self, ms: int) -> None:
        self.now_ns += ms * NS_PER_MS

    def now(self) -> int:
        return self.now_ns


@dataclass
class Delay:
    """``PL.FB_Delay`` (контракт PL, 7.4) — по тексту реализации библиотеки."""

    x_out: bool = False
    timing_on: bool = False
    timing_off: bool = False
    remaining_ms: int = 0
    lt_change: int = 0
    x_in_prev: bool = False
    restart: bool = True

    def __call__(self, x_in: bool, on_ms: int, off_ms: int, now: int) -> None:
        # 2. отметка: «время назад», первый вызов, Preset, смена xIn
        if now < self.lt_change or self.restart or x_in != self.x_in_prev:
            self.lt_change = now
        self.restart = False
        self.x_in_prev = x_in
        # 3. задержка для текущего xIn
        delay = (on_ms if x_in else off_ms) * NS_PER_MS
        elapsed = now - self.lt_change
        # 4. смена выхода
        if elapsed >= delay:
            self.x_out = x_in
        # 5. диагностика отсчёта
        self.timing_on = x_in and not self.x_out
        self.timing_off = self.x_out and not x_in
        self.remaining_ms = (delay - elapsed) // NS_PER_MS if x_in != self.x_out else 0

    def preset(self, value: bool) -> None:
        """``Preset``: выход без задержки, отсчёт — заново с ближайшего вызова."""
        self.x_out = value
        self.restart = True


@dataclass(frozen=True)
class Event:
    """``ST_SisEvent``."""

    time: int
    seq: int
    value: float
    kind: EventKind
    cause: int = 0
    effect: int = 0
    channel: int = 0


EMPTY_EVENT = Event(0, 0, 0.0, EventKind.NONE)


class EventSink(Protocol):
    def add(self, event: Event) -> bool: ...


@dataclass
class EventLog:
    """``FB_SisEventLog``: кольцо ``SIS_LOG_SIZE`` событий, номер присваивает журнал."""

    ring: list[Event] = field(default_factory=lambda: [EMPTY_EVENT] * limits.SIS_LOG_SIZE)
    next: int = 0
    used: int = 0
    seq: int = 0
    history: list[Event] = field(default_factory=list)  # вся история — только для отладки модели

    def add(self, event: Event) -> bool:
        self.seq = 1 if self.seq == 0xFFFFFFFF else self.seq + 1
        stored = Event(event.time, self.seq, event.value, event.kind, event.cause, event.effect, event.channel)
        self.ring[self.next] = stored
        self.next = (self.next + 1) % limits.SIS_LOG_SIZE
        self.used = min(self.used + 1, limits.SIS_LOG_SIZE)
        self.history.append(stored)
        return True

    def get(self, back: int) -> Event:
        if back >= self.used:
            return EMPTY_EVENT
        return self.ring[(self.next - 1 - back) % limits.SIS_LOG_SIZE]

    @property
    def count(self) -> int:
        return self.used

    def clear(self) -> None:
        self.used = 0
        self.next = 0


def _emit(log: EventSink | None, event: Event) -> None:
    if log is not None:
        log.add(event)


# --- конфигурация (DESIGN.md, 4.2) -------------------------------------------------------------------
@dataclass
class VotingCfg:
    """``ST_VotingCfg`` с умолчаниями ST (поля — целые коды перечислений)."""

    arch: int = VoteArch.NONE
    policy: int = Policy.VOTE_TRIP
    input: int = InputKind.DISCRETE
    di_healthy: bool = True
    limit_dir: int = LimitDir.HIGH
    trip_limit: float = 0.0
    hyst: float = 0.0
    disc_max: float = 0.0
    disc_delay_ms: int = 0
    bypass_max_ms: int = 0
    max_bypass: int = 0


@dataclass
class CauseCfg:
    """``ST_CauseCfg``."""

    enable: bool = False
    source: int = CauseSource.VOTING
    delay_ms: int = 0
    override_allowed: bool = False
    override_max_ms: int = 0
    override_clear_ms: int = 0  # tOverrideClear: подтверждение нормы для автоснятия обхода (6.4)


@dataclass
class EffectCfg:
    """``ST_EffectCfg``."""

    safe_state: int = SafeState.OFF
    mask: int = 0


@dataclass
class CemCfg:
    """``ST_CemCfg``."""

    cause_count: int = 0
    effect_count: int = 0
    start_tripped: bool = True
    causes: list[CauseCfg] = field(default_factory=lambda: [CauseCfg() for _ in range(NC)])
    effects: list[EffectCfg] = field(default_factory=lambda: [EffectCfg() for _ in range(NE)])
    crc: int = 0


def voting_cfg(cause: Cause) -> VotingCfg:
    """Элемент ``VOTE_CFG`` причины; ext — ``(eArch := None)``: группа не вызывается."""
    if cause.vote is None or cause.policy is None:
        return VotingCfg()
    cfg = VotingCfg(
        arch=cause.vote,
        policy=cause.policy,
        input=cause.input_kind,
        di_healthy=cause.di_healthy,
        bypass_max_ms=cause.bypass_time_ms,
        max_bypass=cause.bypass_max,
    )
    if cause.analog is not None:
        a = cause.analog
        cfg.limit_dir = LimitDir.HIGH if a.high else LimitDir.LOW
        cfg.trip_limit = f32(float(a.setpoint))
        cfg.hyst = f32(float(a.hyst))
        cfg.disc_max = f32(float(a.discrepancy))
        cfg.disc_delay_ms = a.discrepancy_delay_ms
    return cfg


def voting_cfgs(matrix: Matrix) -> list[VotingCfg]:
    """``VOTE_CFG`` целиком: 16 элементов, неиспользуемые — ``(eArch := None)``."""
    result = [VotingCfg() for _ in range(NC)]
    for cause in matrix.causes:
        result[cause.no - 1] = voting_cfg(cause)
    return result


def cem_cfg(matrix: Matrix) -> CemCfg:
    """``CEM_CFG`` по матрице, с CRC."""
    cfg = CemCfg(cause_count=len(matrix.causes), effect_count=len(matrix.effects))
    cfg.start_tripped = matrix.header.start_tripped
    for cause in matrix.causes:
        cfg.causes[cause.no - 1] = CauseCfg(
            enable=cause.enable,
            source=cause.source_kind,
            delay_ms=cause.delay_ms,
            override_allowed=cause.override,
            override_max_ms=cause.override_time_ms,
            override_clear_ms=cause.override_clear_ms,
        )
    for effect in matrix.effects:
        cfg.effects[effect.no - 1] = EffectCfg(effect.safe_state, matrix.effect_mask(effect.no))
    cfg.crc = cem_crc(cfg)
    return cfg


# --- голосование (DESIGN.md, 5) --------------------------------------------------------------------
def arch_channels(arch: int) -> int:
    """``F_VoteArchChannels``: N; 0 для None, ForcedTrip и значений вне перечисления."""
    return ARCH_NM[VoteArch(arch)][0] if arch in ARCH_NM else 0


def arch_required(arch: int) -> int:
    """``F_VoteArchRequired``: M; 0 — как выше."""
    return ARCH_NM[VoteArch(arch)][1] if arch in ARCH_NM else 0


@dataclass(frozen=True)
class VoteResult:
    """``ST_VoteResult``."""

    trip: bool = True
    degraded: bool = False
    arch_eff: VoteArch = VoteArch.NONE
    demand: int = 0
    invalid: int = 0
    bypassed: int = 0
    normal: int = 0


_EFF_BY_MR = {(1, 1): VoteArch.V1OO1, (1, 2): VoteArch.V1OO2, (2, 2): VoteArch.V2OO2, (2, 3): VoteArch.V2OO3}


def vote_eval(arch: int, policy: int, states: Sequence[int]) -> VoteResult:
    """``F_VoteEval`` — нормативный алгоритм 5.2."""
    n = arch_channels(arch)
    m = arch_required(arch)
    if n == 0 or policy not in (Policy.VOTE_TRIP, Policy.DEGRADE_SAFE, Policy.DEGRADE_AVAILABLE):
        return VoteResult()
    b = f = d = h = 0
    for k in range(n):
        state = states[k]
        if state == ChannelState.BYPASSED:
            b += 1
        elif state == ChannelState.DEMAND:
            d += 1
        elif state == ChannelState.NORMAL:
            h += 1
        else:  # Invalid и NotUsed внутри N
            f += 1
    degraded = (b + f) > 0
    if policy == Policy.VOTE_TRIP:
        x, fv = b, f  # недостоверные голосуют «на останов»
    else:
        x, fv = b + f, 0  # недостоверные исключаются
    r = n - x  # каналов в голосовании
    if r == 0:
        return VoteResult(True, degraded, VoteArch.FORCED_TRIP, d, f, b, h)
    meff = min(m, r) if policy == Policy.DEGRADE_AVAILABLE else max(1, m - x)
    mh = meff - fv
    rh = r - fv
    if mh <= 0:
        return VoteResult(True, degraded, VoteArch.FORCED_TRIP, d, f, b, h)
    trip = d >= mh
    eff = _EFF_BY_MR.get((mh, rh))
    if eff is None:  # недостижимо, защитная ветвь
        return VoteResult(True, degraded, VoteArch.NONE, d, f, b, h)
    return VoteResult(trip, degraded, eff, d, f, b, h)


def vote_check_cfg(cfg: VotingCfg) -> int:
    """``F_VoteCheckCfg`` — сумма битов ``VOTE_CFG_*`` (5.9)."""
    err = 0
    n = arch_channels(cfg.arch)
    if n == 0:
        err |= limits.VOTE_CFG_ARCH
    if cfg.policy not in (Policy.VOTE_TRIP, Policy.DEGRADE_SAFE, Policy.DEGRADE_AVAILABLE):
        err |= limits.VOTE_CFG_POLICY
    if cfg.input not in (InputKind.DISCRETE, InputKind.ANALOG):
        err |= limits.VOTE_CFG_INPUT
    if cfg.input == InputKind.ANALOG:
        if (
            not is_finite(cfg.trip_limit)
            or not is_finite(cfg.hyst)
            or cfg.hyst < 0.0
            or cfg.limit_dir not in (LimitDir.HIGH, LimitDir.LOW)
        ):
            err |= limits.VOTE_CFG_LIMIT
        if not is_finite(cfg.disc_max) or cfg.disc_max < 0.0 or cfg.disc_delay_ms > limits.SIS_DELAY_MAX_MS:
            err |= limits.VOTE_CFG_DISCREPANCY
    if (n == 0 and cfg.max_bypass > 0) or (n > 0 and cfg.max_bypass > n - 1):
        err |= limits.VOTE_CFG_BYPASS
    if cfg.bypass_max_ms > limits.SIS_BYPASS_MAX_MS:
        err |= limits.VOTE_CFG_BYPASS
    return err


@dataclass
class VoteIn:
    """``ST_VoteIn``."""

    di: list[bool] = field(default_factory=lambda: [False] * CH)
    di_valid: list[bool] = field(default_factory=lambda: [False] * CH)
    ai: list[float] = field(default_factory=lambda: [0.0] * CH)
    ai_valid: list[bool] = field(default_factory=lambda: [False] * CH)
    ext_demand: bool = False


@dataclass
class VoteCmd:
    """``ST_VoteCmd``: запросы байпаса — уровни."""

    bypass_req: list[bool] = field(default_factory=lambda: [False] * CH)


@dataclass
class VotingSts:
    """``ST_VotingSts`` с умолчаниями ST."""

    trip: bool = True
    arch_eff: VoteArch = VoteArch.NONE
    degraded: bool = False
    cfg_error: bool = False
    cfg_err: int = 0
    discrepancy: bool = False
    spread: float = 0.0
    demand: int = 0
    invalid: int = 0
    bypassed: int = 0
    normal: int = 0
    ch_state: list[ChannelState] = field(default_factory=lambda: [ChannelState.NOT_USED] * CH)
    bypass: list[BypassState] = field(default_factory=lambda: [BypassState.OFF] * CH)
    bypass_remain_ms: list[int] = field(default_factory=lambda: [0] * CH)


class Voting:
    """``FB_Voting`` — порядок тела 5.5."""

    def __init__(self) -> None:
        self.trip = True
        self.sts = VotingSts()
        self.bypass_timers = [Delay() for _ in range(CH)]
        self.disc_timer = Delay()
        self.dem_mem = [False] * CH
        self.valid_prev = [True] * CH
        self.bypass = [BypassState.OFF] * CH
        self.cfg_err_prev = False
        self.disc_prev = False
        self.lt_prev = 0

    def __call__(
        self,
        vin: VoteIn,
        cmd: VoteCmd,
        cfg: VotingCfg,
        bypass_permit: bool,
        cause: int,
        now: int,
        log: EventSink | None,
    ) -> None:
        # 1. Время — один раз (now); «время назад» — неисправность источника (D-19)
        def ev(kind: EventKind, value: float = 0.0, channel: int = 0) -> None:
            _emit(log, Event(now, 0, value, kind, cause, 0, channel))

        time_back = now < self.lt_prev
        self.lt_prev = now
        # 2. Конфигурация
        err = vote_check_cfg(cfg)
        cfg_error = err != 0
        if cfg_error and not self.cfg_err_prev:
            ev(EventKind.CFG_ERROR, float(err))
        elif not cfg_error and self.cfg_err_prev:
            ev(EventKind.CFG_OK)
        self.cfg_err_prev = cfg_error
        if time_back:
            ev(EventKind.TIME_FAULT)
        if cfg_error:
            for k in range(CH):
                if self.bypass[k] == BypassState.ACTIVE:
                    ev(EventKind.BYPASS_OFF, channel=k + 1)
            self.bypass = [BypassState.OFF] * CH
            for k in range(CH):
                self.bypass_timers[k](False, cfg.bypass_max_ms, 0, now)
            self.disc_timer(False, cfg.disc_delay_ms, 0, now)
            discrepancy = self.disc_timer.x_out
            if self.disc_prev and not discrepancy:
                ev(EventKind.DISCREPANCY_OFF)
            self.disc_prev = discrepancy
            self.trip = True
            self.sts = VotingSts(
                trip=True,
                arch_eff=VoteArch.NONE,
                degraded=False,
                cfg_error=True,
                cfg_err=err,
                discrepancy=discrepancy,
                spread=0.0,
                bypass=list(self.bypass),
            )
            return
        n = arch_channels(cfg.arch)
        # 3. Сырые состояния каналов
        valid = [False] * CH
        dem = [False] * CH
        for k in range(CH):
            if k >= n:
                self.dem_mem[k] = False
                continue
            if cfg.input == InputKind.DISCRETE:
                valid[k] = vin.di_valid[k]
                dem[k] = vin.di[k] != cfg.di_healthy
            else:
                r = f32(vin.ai[k])
                valid[k] = vin.ai_valid[k] and is_finite(r)
                lim = f32(cfg.trip_limit)
                hyst = f32(cfg.hyst)
                if not valid[k]:
                    self.dem_mem[k] = False
                elif cfg.limit_dir == LimitDir.HIGH:
                    self.dem_mem[k] = r >= lim or (self.dem_mem[k] and r >= f32(lim - hyst))
                else:
                    self.dem_mem[k] = r <= lim or (self.dem_mem[k] and r <= f32(lim + hyst))
                dem[k] = self.dem_mem[k]
        # 4. События достоверности
        for k in range(n):
            if valid[k] != self.valid_prev[k]:
                value = f32(vin.ai[k]) if cfg.input == InputKind.ANALOG else 0.0
                ev(EventKind.CHANNEL_VALID if valid[k] else EventKind.CHANNEL_INVALID, value, k + 1)
                self.valid_prev[k] = valid[k]
        # 5. Байпасы (5.7)
        for k in range(CH):  # 5.1 таймеры
            self.bypass_timers[k](self.bypass[k] == BypassState.ACTIVE, cfg.bypass_max_ms, 0, now)
        for k in range(n):  # 5.2 окончания
            req = cmd.bypass_req[k]
            if self.bypass[k] == BypassState.ACTIVE:
                if not req:
                    self.bypass[k] = BypassState.OFF
                    ev(EventKind.BYPASS_OFF, channel=k + 1)
                elif not bypass_permit:
                    self.bypass[k] = BypassState.DENIED
                    ev(EventKind.BYPASS_OFF, channel=k + 1)
                elif self.bypass_timers[k].x_out or time_back:
                    self.bypass[k] = BypassState.EXPIRED
                    ev(EventKind.BYPASS_EXPIRED, channel=k + 1)
            elif self.bypass[k] in (BypassState.EXPIRED, BypassState.DENIED) and not req:
                self.bypass[k] = BypassState.OFF
        for k in range(n):  # 5.3 включения
            if self.bypass[k] == BypassState.OFF and cmd.bypass_req[k]:
                active = sum(1 for s in self.bypass if s == BypassState.ACTIVE)
                if bypass_permit and cfg.bypass_max_ms > 0 and active < cfg.max_bypass:
                    self.bypass[k] = BypassState.ACTIVE
                    ev(EventKind.BYPASS_ON, channel=k + 1)
                    self.bypass_timers[k](True, cfg.bypass_max_ms, 0, now)
                else:
                    self.bypass[k] = BypassState.DENIED
                    ev(EventKind.BYPASS_DENIED, channel=k + 1)
        for k in range(n, CH):  # 5.4 каналы k > N
            self.bypass[k] = BypassState.OFF
        remain = [
            self.bypass_timers[k].remaining_ms if self.bypass[k] == BypassState.ACTIVE else 0 for k in range(CH)
        ]  # 5.5
        # 6. Состояния каналов
        states: list[ChannelState] = []
        for k in range(CH):
            if k >= n:
                states.append(ChannelState.NOT_USED)
            elif self.bypass[k] == BypassState.ACTIVE:
                states.append(ChannelState.BYPASSED)
            elif not valid[k]:
                states.append(ChannelState.INVALID)
            elif dem[k]:
                states.append(ChannelState.DEMAND)
            else:
                states.append(ChannelState.NORMAL)
        # 7. Голосование
        res = vote_eval(cfg.arch, cfg.policy, states)
        self.trip = res.trip
        # 8. Рассогласование (5.8)
        part = [f32(vin.ai[k]) for k in range(n) if states[k] in (ChannelState.NORMAL, ChannelState.DEMAND)]
        spread = 0.0
        cond = False
        if cfg.input == InputKind.ANALOG and cfg.disc_max > 0.0 and len(part) >= 2:
            spread = f32(max(part) - min(part))
            cond = spread > f32(cfg.disc_max)
        self.disc_timer(cond, cfg.disc_delay_ms, 0, now)
        discrepancy = self.disc_timer.x_out
        if discrepancy and not self.disc_prev:
            ev(EventKind.DISCREPANCY_ON, spread)
        elif self.disc_prev and not discrepancy:
            ev(EventKind.DISCREPANCY_OFF)
        self.disc_prev = discrepancy
        # 9. Состояние
        self.sts = VotingSts(
            trip=res.trip,
            arch_eff=res.arch_eff,
            degraded=res.degraded,
            cfg_error=False,
            cfg_err=0,
            discrepancy=discrepancy,
            spread=spread,
            demand=res.demand,
            invalid=res.invalid,
            bypassed=res.bypassed,
            normal=res.normal,
            ch_state=states,
            bypass=list(self.bypass),
            bypass_remain_ms=remain,
        )


# --- матрица (DESIGN.md, 6) ----------------------------------------------------------------------------
def cem_crc(cfg: CemCfg) -> int:
    """``F_CemCrc``: CRC-16/CCITT-FALSE по 36 байтам (6.8)."""
    data = struct.pack("<HH", cfg.cause_count & 0xFFFF, cfg.effect_count & 0xFFFF)
    data += b"".join(struct.pack("<H", effect.mask & 0xFFFF) for effect in cfg.effects)
    return binascii.crc_hqx(data, limits.CRC16_INIT)


def low_mask(count: int) -> int:
    """``F_SisLowMask``: биты 0..count−1; 0 → 0; ≥ 16 → 16#FFFF."""
    if count <= 0:
        return 0
    if count >= 16:
        return 0xFFFF
    return (1 << count) - 1


def cem_check_cfg(cfg: CemCfg) -> int:
    """``F_CemCheckCfg`` — сумма битов ``CEM_CFG_*`` (6.8, таблица 4.3)."""
    err = 0
    if not (1 <= cfg.cause_count <= NC) or not (1 <= cfg.effect_count <= NE):
        err |= limits.CEM_CFG_COUNT
    else:
        for i in range(cfg.cause_count):
            c = cfg.causes[i]
            if (
                c.source not in (CauseSource.VOTING, CauseSource.EXTERNAL)
                or c.delay_ms > limits.SIS_DELAY_MAX_MS
                or (c.override_allowed and (c.override_max_ms == 0 or c.override_max_ms > limits.SIS_OVERRIDE_MAX_MS))
                or (c.override_allowed and (c.override_clear_ms == 0 or c.override_clear_ms >= c.override_max_ms))
            ):
                err |= limits.CEM_CFG_CAUSE
        allowed = low_mask(cfg.cause_count)
        for j in range(NE):
            e = cfg.effects[j]
            if j < cfg.effect_count:
                if e.safe_state not in tuple(SafeState) or e.mask == 0 or (e.mask & ~allowed) != 0:
                    err |= limits.CEM_CFG_EFFECT
            elif e.mask != 0:
                err |= limits.CEM_CFG_EFFECT
    if cem_crc(cfg) != cfg.crc:
        err |= limits.CEM_CFG_CRC
    return err


@dataclass
class CemCmd:
    """``ST_CemCmd`` — импульсы HMI, ФБ сбрасывает их в том же вызове."""

    reset: bool = False
    startup_override: bool = False
    override_req: int = 0
    override_cancel: int = 0


@dataclass
class CauseEffectSts:
    """``ST_CauseEffectSts``."""

    first_out: int = 0
    lt_first_out: int = 0
    first_out_mask: int = 0
    present: int = 0
    active: int = 0
    latched: int = 0
    overridden: int = 0
    effect_tripped: int = 0
    tripped: bool = False
    reset_permitted: bool = False
    reset_blocker: int = 0
    cfg_error: bool = False
    cfg_err: int = 0
    trip_count: int = 0
    override_remain_ms: list[int] = field(default_factory=lambda: [0] * NC)
    delay_remain_ms: list[int] = field(default_factory=lambda: [0] * NC)
    override_clear_remain_ms: list[int] = field(default_factory=lambda: [0] * NC)


def _lowest_bit(mask: int) -> int:
    """Номер (с 1) младшего бита маски; 0 — маска пуста."""
    return (mask & -mask).bit_length() if mask else 0


class CauseEffect:
    """``FB_CauseEffect`` — порядок тела 6.3."""

    def __init__(self) -> None:
        self.effect_out = [False] * NE
        self.tripped = True
        self.sts = CauseEffectSts()
        self.delays = [Delay() for _ in range(NC)]
        self.override_timers = [Delay() for _ in range(NC)]
        self.clear_timers = [Delay() for _ in range(NC)]  # подтверждение нормы для автоснятия обхода (6.4, п. 5)
        self.latched = 0
        self.overridden = [False] * NC
        self.cfg_latch = False
        self.start_latch = False
        self.first_call = True
        self.reset_hw_prev = True
        self.cfg_err_prev = False
        self.present_prev = 0
        self.eff_tripped_prev = 0xFFFF
        self.first_out = limits.SIS_FIRST_OUT_NONE
        self.lt_first_out = 0
        self.first_out_mask = 0
        self.trip_count = 0
        self.lt_prev = 0

    def __call__(
        self,
        cause_in: Sequence[bool],
        override_permit: bool,
        reset_hw: bool,
        now: int,
        log: EventSink | None,
        cmd: CemCmd,
        cfg: CemCfg,
    ) -> None:
        # 1. Время (now); «время назад» — неисправность источника (D-19)
        time_back = now < self.lt_prev
        self.lt_prev = now

        def ev(kind: EventKind, cause: int = 0, effect: int = 0, value: float = 0.0) -> None:
            _emit(log, Event(now, 0, value, kind, cause, effect, 0))

        def set_first_out(code: int, mask: int) -> None:
            self.first_out = code
            self.first_out_mask = mask
            self.lt_first_out = now
            self.trip_count = (self.trip_count + 1) & 0xFFFFFFFF
            ev(EventKind.FIRST_OUT, code)

        # 2. Конфигурация
        err = cem_check_cfg(cfg)
        cfg_error = err != 0
        nc = 0 if cfg_error else min(cfg.cause_count, NC)
        ne = 0 if cfg_error else min(cfg.effect_count, NE)
        if cfg_error and not self.cfg_err_prev:
            ev(EventKind.CFG_ERROR, 0, 0, float(err))
            self.cfg_latch = True
            if self.first_out == limits.SIS_FIRST_OUT_NONE:
                set_first_out(limits.SIS_FIRST_OUT_CFG, 0)
        elif not cfg_error and self.cfg_err_prev:
            ev(EventKind.CFG_OK)
        self.cfg_err_prev = cfg_error
        if self.first_call and not cfg_error and cfg.start_tripped:
            self.start_latch = True
            ev(EventKind.START_TRIP, limits.SIS_FIRST_OUT_START)
            if self.first_out == limits.SIS_FIRST_OUT_NONE:
                set_first_out(limits.SIS_FIRST_OUT_START, 0)
        if time_back:
            ev(EventKind.TIME_FAULT)
        # 3. Причины; при «времени назад» идущая задержка завершается сразу (D-19)
        present = [False] * NC
        active = [False] * NC
        for i in range(NC):
            used = i < nc
            present[i] = used and cfg.causes[i].enable and bool(cause_in[i])
            if time_back and present[i]:
                self.delays[i].preset(True)
            self.delays[i](present[i], cfg.causes[i].delay_ms if used else 0, 0, now)
            active[i] = self.delays[i].x_out
        w_present = sum(1 << i for i in range(NC) if present[i])
        for i in range(NC):
            bit = 1 << i
            if (w_present & bit) != (self.present_prev & bit):
                ev(EventKind.CAUSE_DEMAND if present[i] else EventKind.CAUSE_CLEAR, i + 1)
        self.present_prev = w_present
        # 4. Пусковые обходы (6.4)
        if cfg_error:
            for i in range(NC):
                if self.overridden[i]:
                    self.overridden[i] = False
                    ev(EventKind.OVERRIDE_OFF, i + 1)
        else:
            if time_back:  # срок обходов недостоверен — обходы снимаются (D-19)
                for i in range(NC):
                    if self.overridden[i]:
                        self.overridden[i] = False
                        ev(EventKind.OVERRIDE_EXPIRED, i + 1)
            for i in range(nc):  # снятие командой
                if cmd.override_cancel & (1 << i) and self.overridden[i]:
                    self.overridden[i] = False
                    ev(EventKind.OVERRIDE_OFF, i + 1)
            req = cmd.override_req
            if cmd.startup_override:
                for i in range(nc):
                    if cfg.causes[i].enable and cfg.causes[i].override_allowed:
                        req |= 1 << i
            for i in range(nc):  # запросы
                if req & (1 << i) and not self.overridden[i]:
                    c = cfg.causes[i]
                    if c.enable and c.override_allowed and c.override_max_ms > 0 and override_permit:
                        self.overridden[i] = True
                        # срок и подтверждение нормы — от ltNow этого вызова (6.4, п. 3; D-13)
                        self.override_timers[i].preset(False)
                        self.clear_timers[i].preset(False)
                        ev(EventKind.OVERRIDE_ON, i + 1)
                    else:
                        ev(EventKind.OVERRIDE_DENIED, i + 1)
        for i in range(NC):  # п. 4: срок — верхняя граница, проверяется раньше подтверждения нормы
            self.override_timers[i](self.overridden[i], cfg.causes[i].override_max_ms, 0, now)
            if self.overridden[i] and self.override_timers[i].x_out:
                self.overridden[i] = False
                ev(EventKind.OVERRIDE_EXPIRED, i + 1)
        for i in range(NC):  # п. 5: автоснятие — сырого требования нет непрерывно tOverrideClear (R-12)
            self.clear_timers[i](self.overridden[i] and not present[i], cfg.causes[i].override_clear_ms, 0, now)
            if self.overridden[i] and self.clear_timers[i].x_out:
                self.overridden[i] = False
                ev(EventKind.OVERRIDE_CLEARED, i + 1)
        cmd.override_req = 0
        cmd.override_cancel = 0
        cmd.startup_override = False
        override_remain = [self.override_timers[i].remaining_ms if self.overridden[i] else 0 for i in range(NC)]
        clear_remain = [self.clear_timers[i].remaining_ms if self.overridden[i] else 0 for i in range(NC)]
        # 5. Сброс (6.5)
        reset_req = cmd.reset or (reset_hw and not self.reset_hw_prev)
        self.reset_hw_prev = reset_hw
        cmd.reset = False
        if cfg_error:
            blocker = limits.SIS_FIRST_OUT_CFG
        else:
            blocker = next((i + 1 for i in range(nc) if present[i] and not self.overridden[i]), 0)
        reset_permitted = blocker == 0
        if reset_req:
            if reset_permitted:
                self.latched = 0
                self.cfg_latch = False
                self.start_latch = False
                self.first_out = limits.SIS_FIRST_OUT_NONE
                self.lt_first_out = 0
                self.first_out_mask = 0
                ev(EventKind.RESET_DONE)
            else:
                ev(EventKind.RESET_DENIED, blocker)
        # 6. Фиксация и первопричина (6.6)
        new = 0
        for i in range(nc):
            bit = 1 << i
            if active[i] and not self.overridden[i] and not (self.latched & bit):
                new |= bit
        if new:
            if self.first_out == limits.SIS_FIRST_OUT_NONE:
                set_first_out(_lowest_bit(new), new)
            self.latched |= new
            for i in range(NC):
                if new & (1 << i):
                    ev(EventKind.CAUSE_TRIP, i + 1)
        # 7. Следствия (6.7)
        w_tripped = 0
        for j in range(NE):
            mask = cfg.effects[j].mask
            trip = j >= ne or cfg_error or self.cfg_latch or self.start_latch or (self.latched & mask) != 0
            self.effect_out[j] = not trip
            if trip and j < ne:
                w_tripped |= 1 << j
        if cfg_error:
            w_tripped = 0xFFFF
        else:
            for j in range(ne):
                bit = 1 << j
                if (w_tripped & bit) != (self.eff_tripped_prev & bit):
                    if w_tripped & bit:
                        mask = cfg.effects[j].mask & self.latched
                        if mask:
                            code = _lowest_bit(mask)
                        elif self.cfg_latch:
                            code = limits.SIS_FIRST_OUT_CFG
                        else:
                            code = limits.SIS_FIRST_OUT_START
                        ev(EventKind.EFFECT_TRIP, code, j + 1)
                    else:
                        ev(EventKind.EFFECT_RESTORE, 0, j + 1)
        self.eff_tripped_prev = w_tripped
        self.tripped = cfg_error or self.cfg_latch or self.start_latch or w_tripped != 0
        # 8. Состояние
        self.sts = CauseEffectSts(
            first_out=self.first_out,
            lt_first_out=self.lt_first_out,
            first_out_mask=self.first_out_mask,
            present=w_present,
            active=sum(1 << i for i in range(NC) if active[i]),
            latched=self.latched,
            overridden=sum(1 << i for i in range(NC) if self.overridden[i]),
            effect_tripped=w_tripped,
            tripped=self.tripped,
            reset_permitted=reset_permitted,
            reset_blocker=blocker,
            cfg_error=cfg_error,
            cfg_err=err,
            trip_count=self.trip_count,
            override_remain_ms=override_remain,
            delay_remain_ms=[self.delays[i].remaining_ms for i in range(NC)],
            override_clear_remain_ms=clear_remain,
        )
        self.first_call = False


# --- узел ПАЗ (DESIGN.md, 8.1) --------------------------------------------------------------------------
@dataclass
class SisCmd:
    """``ST_SisCmd``."""

    cem: CemCmd = field(default_factory=CemCmd)
    vote: list[VoteCmd] = field(default_factory=lambda: [VoteCmd() for _ in range(NC)])


class SisUnit:
    """``FB_SisUnit``."""

    def __init__(self) -> None:
        self.votes = [Voting() for _ in range(NC)]
        self.cem = CauseEffect()
        self.effect_out = [False] * NE
        self.tripped = True
        self.cem_sts = CauseEffectSts()
        self.vote_sts = [VotingSts() for _ in range(NC)]

    def __call__(
        self,
        vin: Sequence[VoteIn],
        bypass_permit: bool,
        override_permit: bool,
        reset_hw: bool,
        now: int,
        log: EventSink | None,
        cmd: SisCmd,
        cem_cfg_: CemCfg,
        vote_cfg: Sequence[VotingCfg],
    ) -> None:
        demand = [False] * NC
        count = min(cem_cfg_.cause_count, NC)
        for i in range(NC):
            c = cem_cfg_.causes[i]
            if i < count and c.enable and c.source == CauseSource.VOTING:
                self.votes[i](vin[i], cmd.vote[i], vote_cfg[i], bypass_permit, i + 1, now, log)
                demand[i] = self.votes[i].trip
                self.vote_sts[i] = self.votes[i].sts
            elif i < count and c.enable and c.source == CauseSource.EXTERNAL:
                demand[i] = vin[i].ext_demand
                self.vote_sts[i] = VotingSts()
            else:
                self.vote_sts[i] = VotingSts()
        self.cem(demand, override_permit, reset_hw, now, log, cmd.cem, cem_cfg_)
        self.effect_out = list(self.cem.effect_out)
        self.tripped = self.cem.tripped
        self.cem_sts = self.cem.sts


# --- привязка объекта (DESIGN.md, 10.5): общая для ST и модели ------------------------------------------
@dataclass(frozen=True)
class Binding:
    """Одна строка привязки ``FB_SisApp``: что пишется в ``astIn[cause]`` из ``stIo``."""

    cause: Cause
    channel: int  # 1..3; 0 — xExtDemand
    tag: str


def bindings(matrix: Matrix) -> list[Binding]:
    """Привязка входов по причинам в порядке ``no``, каналы — по ``source``."""
    result: list[Binding] = []
    for cause in matrix.causes:
        if cause.signal is Signal.EXT:
            result.append(Binding(cause, 0, cause.sources[0]))
        else:
            for k, tag in enumerate(cause.sources, 1):
                result.append(Binding(cause, k, tag))
    return result


IoValue = float | bool


def io_defaults(matrix: Matrix) -> dict[str, IoValue]:
    """``ST_SisIo`` после инициализации: REAL — 0.0, BOOL — FALSE."""
    return {f.name: (0.0 if f.st_type == "REAL" else False) for f in matrix.io_fields}


def io_normal(matrix: Matrix) -> list[tuple[str, IoValue]]:
    """``F_SisIoNormal``: все каналы в норме и достоверны, ключи и кнопка FALSE; выходы не трогает."""
    result: list[tuple[str, IoValue]] = []
    for f in matrix.io_fields:
        if f.kind == "ai":
            channel = next(c for c in matrix.channels if c.tag == f.tag)
            assert channel.analog is not None
            result.append((f.name, f32(channel.analog.normal_ma)))
        elif f.kind in ("di", "ext"):
            channel = next(c for c in matrix.channels if c.tag == f.tag)
            result.append((f.name, channel.trip_on == 0))
        elif f.kind in ("di_ok",):
            result.append((f.name, True))
        elif f.kind == "key":
            result.append((f.name, False))
    return result


class SisApp:
    """``FB_SisApp``: привязка ``ST_SisIo`` → ``FB_SisUnit`` → выходы ``xQ*``."""

    def __init__(self, matrix: Matrix) -> None:
        self.matrix = matrix
        self.unit = SisUnit()
        self.vin = [VoteIn() for _ in range(NC)]
        self.cem_cfg = cem_cfg(matrix)
        self.vote_cfg = voting_cfgs(matrix)
        self.lo = {c.tag: f32(float(c.analog.range_lo)) for c in matrix.channels if c.analog is not None}
        self.hi = {c.tag: f32(float(c.analog.range_hi)) for c in matrix.channels if c.analog is not None}
        self.bindings = bindings(matrix)

    def __call__(self, now: int, log: EventSink | None, io: dict[str, IoValue], cmd: SisCmd) -> None:
        for b in self.bindings:
            vin = self.vin[b.cause.no - 1]
            if b.channel == 0:
                value = bool(io[f"x{b.tag}"])
                vin.ext_demand = (not value) if b.cause.trip_on == 0 else value
            elif b.cause.signal is Signal.AI:
                ma = float(io[f"r{b.tag}_mA"])
                vin.ai[b.channel - 1] = ai_to_eu(ma, self.lo[b.tag], self.hi[b.tag])
                vin.ai_valid[b.channel - 1] = ne43_valid(ma)
            else:
                vin.di[b.channel - 1] = bool(io[f"x{b.tag}"])
                vin.di_valid[b.channel - 1] = bool(io[f"x{b.tag}_Ok"])
        h = self.matrix.header
        bypass = bool(io[f"x{h.bypass_permit_tag}"]) if h.bypass_permit_tag else True
        override = bool(io[f"x{h.override_permit_tag}"]) if h.override_permit_tag else True
        reset = bool(io[f"x{h.reset_tag}"]) if h.reset_tag else False
        self.unit(self.vin, bypass, override, reset, now, log, cmd, self.cem_cfg, self.vote_cfg)
        for effect in self.matrix.effects:
            io[effect.io_field] = self.unit.effect_out[effect.no - 1]

    @property
    def tripped(self) -> bool:
        return self.unit.tripped

    @property
    def cem_sts(self) -> CauseEffectSts:
        return self.unit.cem_sts

    @property
    def vote_sts(self) -> list[VotingSts]:
        return self.unit.vote_sts


class Harness:
    """Стенд ``FB_SisHarness`` (12.5): подменное время, журнал, ``FB_SisApp``, образ ввода-вывода."""

    def __init__(self, matrix: Matrix) -> None:
        self.matrix = matrix
        self.time = FakeTime()
        self.log = EventLog()
        self.app = SisApp(matrix)
        self.io = io_defaults(matrix)
        self.cmd = SisCmd()
        self.mark = 0
        self.iterations = 0  # итераций Run с начала теста — проверка предела

    def cycle(self) -> None:
        self.app(self.time.now(), self.log, self.io, self.cmd)

    def step(self, ms: int) -> None:
        self.time.advance(ms)
        self.cycle()

    def run(self, duration_ms: int, step_ms: int) -> int:
        """Шаги ``step_ms``, последний — остаток; возвращает число итераций."""
        left = duration_ms
        count = 0
        while left > 0 and count < limits.HARNESS_MAX_ITERATIONS:
            this = step_ms if 0 < step_ms < left else left
            self.step(this)
            left -= this
            count += 1
        self.iterations += count
        return count

    def set_normal(self) -> None:
        for name, value in io_normal(self.matrix):
            self.io[name] = value

    def arm(self) -> bool:
        self.set_normal()
        self.cycle()
        self.press_reset()
        sts = self.app.cem_sts
        return sts.effect_tripped == 0 and sts.latched == 0 and not self.app.tripped

    def press_reset(self) -> None:
        self.cmd.cem.reset = True
        self.cycle()

    def keys(self, bypass: bool, override: bool) -> None:
        h = self.matrix.header
        if h.bypass_permit_tag:
            self.io[f"x{h.bypass_permit_tag}"] = bypass
        if h.override_permit_tag:
            self.io[f"x{h.override_permit_tag}"] = override
        if h.reset_tag:
            self.io[f"x{h.reset_tag}"] = False

    def mark_events(self) -> None:
        self.mark = self.log.seq

    def has_event(self, kind: EventKind, cause: int) -> bool:
        back = 0
        while back < self.log.count:
            event = self.log.get(back)
            if event.seq <= self.mark:
                break
            if event.kind == kind and event.cause == cause:
                return True
            back += 1
        return False

    def now(self) -> int:
        return self.time.now()


# --- стимулы (DESIGN.md, 12.4) -------------------------------------------------------------------------
def demand_values(cause: Cause) -> list[tuple[str, IoValue]]:
    """Стимул «требование» на всех каналах причины: (поле ST_SisIo, значение)."""
    if cause.signal is Signal.AI:
        assert cause.analog is not None
        ma = f32(cause.analog.demand_ma)
        return [(f"r{tag}_mA", ma) for tag in cause.sources]
    value = cause.trip_on == 1
    return [(f"x{tag}", value) for tag in cause.sources]


def normal_values(cause: Cause) -> list[tuple[str, IoValue]]:
    """Стимул «норма» на всех каналах причины."""
    if cause.signal is Signal.AI:
        assert cause.analog is not None
        ma = f32(cause.analog.normal_ma)
        return [(f"r{tag}_mA", ma) for tag in cause.sources]
    result: list[tuple[str, IoValue]] = []
    for tag in cause.sources:
        result.append((f"x{tag}", cause.trip_on == 0))
        if cause.signal is Signal.DI:
            result.append((f"x{tag}_Ok", True))
    return result


def channel_demand(cause: Cause, channel: int) -> tuple[str, IoValue]:
    """Требование на одном канале ``channel`` (с 1)."""
    tag = cause.sources[channel - 1]
    if cause.signal is Signal.AI:
        assert cause.analog is not None
        return f"r{tag}_mA", f32(cause.analog.demand_ma)
    return f"x{tag}", cause.trip_on == 1


def channel_invalid(cause: Cause, channel: int) -> tuple[str, IoValue]:
    """Недостоверность канала: ai — 2,0 мА (обрыв), di — ``_Ok := FALSE``."""
    tag = cause.sources[channel - 1]
    if cause.signal is Signal.AI:
        return f"r{tag}_mA", f32(limits.STIM_INVALID_MA)
    return f"x{tag}_Ok", False


def cross_demands(matrix: Matrix) -> list[tuple[Cause, list[Cause]]]:
    """CEM-W002: для каждой включённой причины — другие причины, которые даёт её стимул."""
    result: list[tuple[Cause, list[Cause]]] = []
    for cause in matrix.enabled_causes:
        harness = Harness(matrix)
        harness.set_normal()
        for name, value in demand_values(cause):
            harness.io[name] = value
        harness.cycle()
        present = harness.app.cem_sts.present
        others = [other for other in matrix.enabled_causes if other.no != cause.no and present & other.bit]
        if others:
            result.append((cause, others))
    return result


# --- таблицы истинности (DESIGN.md, 12.2) ---------------------------------------------------------------
def encode_result(trip: bool, degraded: bool, arch_eff: VoteArch, bypass: Sequence[BypassState] = ()) -> int:
    """Байт таблицы: бит 0 — xTrip, бит 1 — xDegraded, биты 2–4 — схема, биты 5–7 — байпасы Active."""
    value = int(trip) | (int(degraded) << 1) | (ARCH_INDEX[arch_eff] << 2)
    for k, state in enumerate(bypass):
        if state == BypassState.ACTIVE:
            value |= 1 << (5 + k)
    return value


EVAL_CODES = (ChannelState.NORMAL, ChannelState.DEMAND, ChannelState.INVALID, ChannelState.BYPASSED)


def eval_row_states(row: int, n: int) -> list[ChannelState]:
    """Состояния каналов строки уровня 1: код ``(r SHR 2(k−1)) AND 3``; k > N — NotUsed."""
    return [EVAL_CODES[(row >> (2 * k)) & 3] if k < n else ChannelState.NOT_USED for k in range(CH)]


def eval_table(arch: VoteArch, policy: Policy) -> list[int]:
    """``TT_EVAL_<A>_<P>``: 4^N байт."""
    n = arch_channels(arch)
    table = []
    for row in range(4**n):
        res = vote_eval(arch, policy, eval_row_states(row, n))
        table.append(encode_result(res.trip, res.degraded, res.arch_eff))
    return table


def fb_table_cfg(arch: VoteArch, policy: Policy, kind: InputKind) -> VotingCfg:
    """Конфигурация теста уровня 2."""
    n = arch_channels(arch)
    return VotingCfg(
        arch=arch,
        policy=policy,
        input=kind,
        di_healthy=True,
        limit_dir=LimitDir.HIGH,
        trip_limit=limits.TT_AI_LIMIT,
        hyst=0.0,
        disc_max=0.0,
        disc_delay_ms=0,
        bypass_max_ms=limits.TT_BYPASS_MAX_MS,
        max_bypass=min(1, n - 1),
    )


def fb_row_inputs(row: int, n: int, with_bypass: bool) -> tuple[VoteIn, VoteCmd]:
    """Входы строки уровня 2 — как метод ``RowInputs`` набора: для канала k биты 3(k−1).

    Бит 0 — требование (DI: ``axDi := FALSE``, AI: 60.0 вместо 40.0), бит 1 — достоверность,
    бит 2 — запрос байпаса (только при ``with_bypass``). Поля DI и AI пишутся оба; каналы
    k > N — без требования, недостоверны, без запроса.
    """
    vin = VoteIn()
    cmd = VoteCmd()
    for k in range(CH):
        bits = (row >> (3 * k)) & 7 if k < n else 0
        demand = bool(bits & 1)
        vin.di[k] = not demand
        vin.di_valid[k] = bool(bits & 2)
        vin.ai[k] = limits.TT_AI_DEMAND if demand else limits.TT_AI_NORMAL
        vin.ai_valid[k] = bool(bits & 2)
        cmd.bypass_req[k] = with_bypass and bool(bits & 4)
    return vin, cmd


def fb_table(arch: VoteArch, policy: Policy, kind: InputKind) -> list[int]:
    """``TT_FB_<A>_<P>_<K>``: 8^N байт; на строку — два вызова одного экземпляра."""
    n = arch_channels(arch)
    cfg = fb_table_cfg(arch, policy, kind)
    fb = Voting()
    now = LTIME_START_NS
    table = []
    for row in range(8**n):
        vin, cmd = fb_row_inputs(row, n, with_bypass=False)
        fb(vin, cmd, cfg, True, 1, now, None)
        vin, cmd = fb_row_inputs(row, n, with_bypass=True)
        fb(vin, cmd, cfg, True, 1, now, None)
        table.append(encode_result(fb.trip, fb.sts.degraded, fb.sts.arch_eff, fb.sts.bypass))
    return table


def degradation(arch: VoteArch, policy: Policy, bypassed: int, invalid: int) -> VoteArch:
    """Действующая схема при B байпасированных и F недостоверных каналах (таблицы 5.3)."""
    states = [ChannelState.BYPASSED] * bypassed + [ChannelState.INVALID] * invalid
    n = arch_channels(arch)
    states += [ChannelState.NORMAL] * (n - len(states))
    states += [ChannelState.NOT_USED] * (CH - len(states))
    return vote_eval(arch, policy, states).arch_eff
