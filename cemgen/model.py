"""Модель проверенной матрицы причин и следствий.

Модель строит только проверка (:func:`cemgen.validate.parse_grid`) и только без ошибок:
генераторы получают согласованные данные и ничего не перепроверяют. Здесь же — производные
величины, общие для ST, тестов и документов: маски следствий, CRC, каналы, поля
``ST_SisIo`` и стимулы испытаний (DESIGN.md, 12.4).
"""

from __future__ import annotations

import binascii
import struct
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

from cemgen import limits
from cemgen.sisdefs import (
    ARCH_NM,
    ARCH_TEXT,
    SAFE_STATE_RU,
    CauseSource,
    InputKind,
    LimitDir,
    Policy,
    SafeState,
    VoteArch,
)
from cemgen.values import format_decimal_ru


class Signal(Enum):
    """Вид входов причины (колонка ``signal``)."""

    AI = "ai"
    DI = "di"
    EXT = "ext"


@dataclass(frozen=True)
class Header:
    """Раздел ``[header]``."""

    format: str
    object: str
    object_name: str
    title: str
    document: str
    revision: str
    date: str
    author: str
    start_tripped: bool = True
    test_step_ms: int = limits.DEFAULT_TEST_STEP_MS
    reset_tag: str | None = None
    bypass_permit_tag: str | None = None
    override_permit_tag: str | None = None


@dataclass(frozen=True)
class Effect:
    """Столбец матрицы — следствие ``j``."""

    no: int
    tag: str
    description: str
    actuator: str
    safe_state: SafeState
    notes: str = ""

    @property
    def const_name(self) -> str:
        return f"EFFECT_{self.tag}"

    @property
    def io_field(self) -> str:
        return f"xQ{self.tag}"


@dataclass(frozen=True)
class Analog:
    """Параметры аналоговой причины: уставка, гистерезис, шкала датчиков, норма."""

    high: bool
    setpoint: Decimal
    hyst: Decimal
    units: str
    range_lo: Decimal
    range_hi: Decimal
    normal: Decimal
    discrepancy: Decimal
    discrepancy_delay_ms: int

    @property
    def span(self) -> Decimal:
        return self.range_hi - self.range_lo

    def to_ma(self, value: Decimal) -> float:
        """Значение в инж. ед. → ток 4–20 мА по шкале датчика."""
        return limits.MA_ZERO + float((value - self.range_lo) / self.span) * limits.MA_SPAN

    @property
    def demand_value(self) -> Decimal:
        """Стимул «требование» в инж. ед.: уставка ± max(hyst, 1 % шкалы) (12.4)."""
        shift = max(self.hyst, self.span * Decimal(str(limits.STIM_MIN_SHIFT_FRACTION)))
        return self.setpoint + shift if self.high else self.setpoint - shift

    @property
    def demand_ma(self) -> float:
        return self.to_ma(self.demand_value)

    @property
    def normal_ma(self) -> float:
        return self.to_ma(self.normal)


@dataclass(frozen=True)
class Cause:
    """Строка матрицы — причина ``i``."""

    no: int
    tag: str
    description: str
    signal: Signal
    sources: tuple[str, ...]
    vote: VoteArch | None  # None — ext (без голосования)
    policy: Policy | None  # None — ext
    trip_on: int | None  # di/ext: значение входа, означающее требование
    analog: Analog | None  # только ai
    delay_ms: int
    bypass_max: int
    bypass_time_ms: int
    override: bool
    override_time_ms: int
    enable: bool
    notes: str
    effects: frozenset[int]  # номера следствий с «X»
    row: int = 0  # строка файла (для сообщений)

    @property
    def const_name(self) -> str:
        return f"CAUSE_{self.tag}"

    @property
    def bit(self) -> int:
        return 1 << (self.no - 1)

    @property
    def channels(self) -> int:
        """N — каналов в группе голосования (ext — 1 вход без голосования)."""
        return ARCH_NM[self.vote][0] if self.vote is not None else 1

    @property
    def is_voting(self) -> bool:
        return self.signal is not Signal.EXT

    @property
    def source_kind(self) -> CauseSource:
        return CauseSource.EXTERNAL if self.signal is Signal.EXT else CauseSource.VOTING

    @property
    def input_kind(self) -> InputKind:
        return InputKind.ANALOG if self.signal is Signal.AI else InputKind.DISCRETE

    @property
    def limit_dir(self) -> LimitDir:
        return LimitDir.LOW if self.analog is not None and not self.analog.high else LimitDir.HIGH

    @property
    def di_healthy(self) -> bool:
        """``xDiHealthy := trip_on = 0``: значение входа в норме."""
        return self.trip_on != 1

    @property
    def vote_text(self) -> str:
        return ARCH_TEXT[self.vote] if self.vote is not None else "—"


@dataclass(frozen=True)
class Channel:
    """Тег канала (прибора) и причины, в которые он входит, в порядке первого появления."""

    tag: str
    signal: Signal
    causes: tuple[int, ...]
    analog: Analog | None = None
    trip_on: int | None = None


@dataclass(frozen=True)
class IoField:
    """Поле ``ST_SisIo``: имя, тип ST, комментарий и вид (канал, ключ, выход)."""

    name: str
    st_type: str
    comment: str
    kind: str  # "ai", "di", "di_ok", "ext", "key", "out"
    tag: str


@dataclass(frozen=True)
class Matrix:
    """Проверенная матрица: шапка, причины, следствия и SHA-256 сетки."""

    header: Header
    causes: tuple[Cause, ...]
    effects: tuple[Effect, ...]
    grid_digest: str
    warnings: tuple[str, ...] = field(default=())

    # --- маски и CRC ------------------------------------------------------------------------
    def effect_mask(self, effect_no: int) -> int:
        """``wCauseMask`` следствия: бит ``i-1`` — причина ``i`` с «X» (включённая или нет)."""
        mask = 0
        for cause in self.causes:
            if effect_no in cause.effects:
                mask |= cause.bit
        return mask

    def effect_causes(self, effect_no: int) -> list[Cause]:
        return [cause for cause in self.causes if effect_no in cause.effects]

    @property
    def masks(self) -> list[int]:
        """Маски всех ``SIS_EFFECTS_MAX`` следствий (неиспользуемые — 0)."""
        result = [0] * limits.SIS_EFFECTS_MAX
        for effect in self.effects:
            result[effect.no - 1] = self.effect_mask(effect.no)
        return result

    @property
    def crc(self) -> int:
        """CRC-16/CCITT-FALSE по 36 байтам (DESIGN.md, 6.8)."""
        data = struct.pack("<HH", len(self.causes), len(self.effects))
        data += b"".join(struct.pack("<H", mask) for mask in self.masks)
        return binascii.crc_hqx(data, limits.CRC16_INIT)

    # --- выборки -----------------------------------------------------------------------------
    @property
    def enabled_causes(self) -> list[Cause]:
        return [cause for cause in self.causes if cause.enable]

    def cause(self, no: int) -> Cause:
        return self.causes[no - 1]

    def effect(self, no: int) -> Effect:
        return self.effects[no - 1]

    @property
    def channels(self) -> list[Channel]:
        """Каналы в порядке первого появления (причины по ``no``, каналы по ``source``)."""
        order: list[str] = []
        users: dict[str, list[int]] = {}
        first: dict[str, Cause] = {}
        for cause in self.causes:
            for tag in cause.sources:
                if tag not in users:
                    order.append(tag)
                    users[tag] = []
                    first[tag] = cause
                users[tag].append(cause.no)
        return [
            Channel(tag, first[tag].signal, tuple(users[tag]), first[tag].analog, first[tag].trip_on) for tag in order
        ]

    @property
    def key_tags(self) -> list[tuple[str, str]]:
        """Ключи и кнопка: (тег, назначение) в порядке reset, bypass, override."""
        result: list[tuple[str, str]] = []
        h = self.header
        if h.reset_tag:
            result.append((h.reset_tag, "кнопка «Сброс ПАЗ» (действует фронт)"))
        if h.bypass_permit_tag:
            result.append((h.bypass_permit_tag, "ключ «Разрешение байпасов»"))
        if h.override_permit_tag:
            result.append((h.override_permit_tag, "ключ «Разрешение пусковых обходов»"))
        return result

    @property
    def io_fields(self) -> list[IoField]:
        """Поля ``ST_SisIo``: каналы (порядок первого появления), ключи, выходы ``xQ*``."""
        fields: list[IoField] = []
        for channel in self.channels:
            causes = ", ".join(f"{no} {self.cause(no).tag}" for no in channel.causes)
            if channel.signal is Signal.AI and channel.analog is not None:
                a = channel.analog
                scale = f"{format_dec(a.range_lo)}…{format_dec(a.range_hi)} {a.units}"
                fields.append(
                    IoField(
                        f"r{channel.tag}_mA", "REAL", f"{channel.tag}, мА: шкала {scale}; {causes}", "ai", channel.tag
                    )
                )
            elif channel.signal is Signal.DI:
                norm = "1" if channel.trip_on == 0 else "0"
                fields.append(
                    IoField(f"x{channel.tag}", "BOOL", f"{channel.tag}: норма {norm}; {causes}", "di", channel.tag)
                )
                fields.append(
                    IoField(
                        f"x{channel.tag}_Ok",
                        "BOOL",
                        f"{channel.tag}: контроль линии, TRUE — исправна",
                        "di_ok",
                        channel.tag,
                    )
                )
            else:
                norm = "1" if channel.trip_on == 0 else "0"
                fields.append(
                    IoField(
                        f"x{channel.tag}",
                        "BOOL",
                        f"{channel.tag}: внешнее требование, норма {norm}; {causes}",
                        "ext",
                        channel.tag,
                    )
                )
        for tag, purpose in self.key_tags:
            fields.append(IoField(f"x{tag}", "BOOL", f"{tag}: {purpose}", "key", tag))
        for effect in self.effects:
            fields.append(
                IoField(
                    effect.io_field,
                    "BOOL",
                    f"{effect.tag}: разрешение, TRUE — под напряжением; FALSE — {_safe_word(effect.safe_state)}",
                    "out",
                    effect.tag,
                )
            )
        return fields


def format_dec(value: Decimal) -> str:
    """Число для комментариев и документов: десятичная запятая."""
    return format_decimal_ru(value)


def _safe_word(state: SafeState) -> str:
    return SAFE_STATE_RU[state]
