"""Перечисления контракта (DESIGN.md, 4.1) на стороне Python: коды, имена ST и подписи.

Коды совпадают со значениями ``TYPE E_... : (...) INT;`` — их используют и эталонная модель,
и генераторы ST. Имя элемента ST получается функцией :func:`st_enum`
(``E_VoteArch.Vote2oo3``).
"""

from __future__ import annotations

from enum import IntEnum


class VoteArch(IntEnum):
    """``E_VoteArch``."""

    NONE = 0
    V1OO1 = 11
    V1OO2 = 12
    V2OO2 = 22
    V2OO3 = 23
    FORCED_TRIP = 99


class Policy(IntEnum):
    """``E_DegradePolicy``."""

    VOTE_TRIP = 1
    DEGRADE_SAFE = 2
    DEGRADE_AVAILABLE = 3


class ChannelState(IntEnum):
    """``E_ChannelState``."""

    NOT_USED = 0
    NORMAL = 1
    DEMAND = 2
    INVALID = 3
    BYPASSED = 4


class BypassState(IntEnum):
    """``E_BypassState``."""

    OFF = 0
    ACTIVE = 1
    EXPIRED = 2
    DENIED = 3


class InputKind(IntEnum):
    """``E_SisInputKind``."""

    DISCRETE = 1
    ANALOG = 2


class LimitDir(IntEnum):
    """``E_LimitDir``."""

    HIGH = 1
    LOW = 2


class CauseSource(IntEnum):
    """``E_CauseSource``."""

    VOTING = 1
    EXTERNAL = 2


class SafeState(IntEnum):
    """``E_SafeState``."""

    CLOSED = 1
    OPEN = 2
    STOPPED = 3
    OFF = 4
    ALARM = 5


class EventKind(IntEnum):
    """``E_SisEventKind``."""

    NONE = 0
    CAUSE_DEMAND = 1
    CAUSE_CLEAR = 2
    CAUSE_TRIP = 3
    FIRST_OUT = 4
    EFFECT_TRIP = 5
    EFFECT_RESTORE = 6
    RESET_DONE = 7
    RESET_DENIED = 8
    OVERRIDE_ON = 9
    OVERRIDE_OFF = 10
    OVERRIDE_EXPIRED = 11
    OVERRIDE_DENIED = 12
    BYPASS_ON = 13
    BYPASS_OFF = 14
    BYPASS_EXPIRED = 15
    BYPASS_DENIED = 16
    CHANNEL_INVALID = 17
    CHANNEL_VALID = 18
    DISCREPANCY_ON = 19
    DISCREPANCY_OFF = 20
    CFG_ERROR = 21
    CFG_OK = 22
    START_TRIP = 23
    TIME_FAULT = 24


# Имена типов и элементов перечислений в ST
_ST_TYPE: dict[type[IntEnum], str] = {
    VoteArch: "E_VoteArch",
    Policy: "E_DegradePolicy",
    ChannelState: "E_ChannelState",
    BypassState: "E_BypassState",
    InputKind: "E_SisInputKind",
    LimitDir: "E_LimitDir",
    CauseSource: "E_CauseSource",
    SafeState: "E_SafeState",
    EventKind: "E_SisEventKind",
}

_ST_MEMBER: dict[type[IntEnum], dict[int, str]] = {
    VoteArch: {
        VoteArch.NONE: "None",
        VoteArch.V1OO1: "Vote1oo1",
        VoteArch.V1OO2: "Vote1oo2",
        VoteArch.V2OO2: "Vote2oo2",
        VoteArch.V2OO3: "Vote2oo3",
        VoteArch.FORCED_TRIP: "ForcedTrip",
    },
    Policy: {
        Policy.VOTE_TRIP: "VoteTrip",
        Policy.DEGRADE_SAFE: "DegradeSafe",
        Policy.DEGRADE_AVAILABLE: "DegradeAvailable",
    },
    ChannelState: {
        ChannelState.NOT_USED: "NotUsed",
        ChannelState.NORMAL: "Normal",
        ChannelState.DEMAND: "Demand",
        ChannelState.INVALID: "Invalid",
        ChannelState.BYPASSED: "Bypassed",
    },
    BypassState: {
        BypassState.OFF: "Off",
        BypassState.ACTIVE: "Active",
        BypassState.EXPIRED: "Expired",
        BypassState.DENIED: "Denied",
    },
    InputKind: {
        InputKind.DISCRETE: "Discrete",
        InputKind.ANALOG: "Analog",
    },
    LimitDir: {
        LimitDir.HIGH: "High",
        LimitDir.LOW: "Low",
    },
    CauseSource: {
        CauseSource.VOTING: "Voting",
        CauseSource.EXTERNAL: "External",
    },
    SafeState: {
        SafeState.CLOSED: "Closed",
        SafeState.OPEN: "Open",
        SafeState.STOPPED: "Stopped",
        SafeState.OFF: "Off",
        SafeState.ALARM: "Alarm",
    },
    EventKind: {
        EventKind.NONE: "None",
        EventKind.CAUSE_DEMAND: "CauseDemand",
        EventKind.CAUSE_CLEAR: "CauseClear",
        EventKind.CAUSE_TRIP: "CauseTrip",
        EventKind.FIRST_OUT: "FirstOut",
        EventKind.EFFECT_TRIP: "EffectTrip",
        EventKind.EFFECT_RESTORE: "EffectRestore",
        EventKind.RESET_DONE: "ResetDone",
        EventKind.RESET_DENIED: "ResetDenied",
        EventKind.OVERRIDE_ON: "OverrideOn",
        EventKind.OVERRIDE_OFF: "OverrideOff",
        EventKind.OVERRIDE_EXPIRED: "OverrideExpired",
        EventKind.OVERRIDE_DENIED: "OverrideDenied",
        EventKind.BYPASS_ON: "BypassOn",
        EventKind.BYPASS_OFF: "BypassOff",
        EventKind.BYPASS_EXPIRED: "BypassExpired",
        EventKind.BYPASS_DENIED: "BypassDenied",
        EventKind.CHANNEL_INVALID: "ChannelInvalid",
        EventKind.CHANNEL_VALID: "ChannelValid",
        EventKind.DISCREPANCY_ON: "DiscrepancyOn",
        EventKind.DISCREPANCY_OFF: "DiscrepancyOff",
        EventKind.CFG_ERROR: "CfgError",
        EventKind.CFG_OK: "CfgOk",
        EventKind.START_TRIP: "StartTrip",
        EventKind.TIME_FAULT: "TimeFault",
    },
}


def st_member(value: IntEnum) -> str:
    """Имя элемента перечисления в ST без типа: ``Vote2oo3``.

    Ключ — тип и значение: у IntEnum разных типов с одним кодом одинаковый хеш.
    """
    return _ST_MEMBER[type(value)][int(value)]


def st_enum(value: IntEnum) -> str:
    """Полное имя элемента перечисления в ST: ``E_VoteArch.Vote2oo3``."""
    return f"{_ST_TYPE[type(value)]}.{st_member(value)}"


# --- схемы голосования (DESIGN.md, 5.1) ------------------------------------------------------
ARCH_NM: dict[VoteArch, tuple[int, int]] = {
    VoteArch.V1OO1: (1, 1),
    VoteArch.V1OO2: (2, 1),
    VoteArch.V2OO2: (2, 2),
    VoteArch.V2OO3: (3, 2),
}
"""Схема → (N каналов, M требуемых голосов)."""

VOTING_ARCHS: tuple[VoteArch, ...] = (VoteArch.V1OO1, VoteArch.V1OO2, VoteArch.V2OO2, VoteArch.V2OO3)

ARCH_TEXT: dict[VoteArch, str] = {
    VoteArch.NONE: "None",
    VoteArch.V1OO1: "1oo1",
    VoteArch.V1OO2: "1oo2",
    VoteArch.V2OO2: "2oo2",
    VoteArch.V2OO3: "2oo3",
    VoteArch.FORCED_TRIP: "ForcedTrip",
}
"""Запись схемы в матрице и документах."""

ARCH_INDEX: dict[VoteArch, int] = {
    VoteArch.NONE: 0,
    VoteArch.V1OO1: 1,
    VoteArch.V1OO2: 2,
    VoteArch.V2OO2: 3,
    VoteArch.V2OO3: 4,
    VoteArch.FORCED_TRIP: 5,
}
"""Индекс схемы в байте таблицы истинности (DESIGN.md, 12.2): биты 2–4."""

POLICIES: tuple[Policy, ...] = (Policy.VOTE_TRIP, Policy.DEGRADE_SAFE, Policy.DEGRADE_AVAILABLE)

POLICY_TEXT: dict[Policy, str] = {
    Policy.VOTE_TRIP: "vote_trip",
    Policy.DEGRADE_SAFE: "degrade_safe",
    Policy.DEGRADE_AVAILABLE: "degrade_available",
}
"""Запись политики в матрице."""

POLICY_SHORT: dict[Policy, str] = {
    Policy.VOTE_TRIP: "VT",
    Policy.DEGRADE_SAFE: "DS",
    Policy.DEGRADE_AVAILABLE: "DA",
}
"""Обозначение политики в именах таблиц и тестов (DESIGN.md, 12.2)."""

SAFE_STATE_WORDS: dict[SafeState, tuple[str, ...]] = {
    SafeState.CLOSED: ("closed", "закрыт"),
    SafeState.OPEN: ("open", "открыт"),
    SafeState.STOPPED: ("stopped", "остановлен"),
    SafeState.OFF: ("off", "отключен", "отключён"),
    SafeState.ALARM: ("alarm", "сигнал"),
}
"""Допустимые записи ``safe_state`` (DESIGN.md, 9.2)."""

SAFE_STATE_RU: dict[SafeState, str] = {
    SafeState.CLOSED: "закрыт",
    SafeState.OPEN: "открыт",
    SafeState.STOPPED: "остановлен",
    SafeState.OFF: "отключён",
    SafeState.ALARM: "сигнал",
}
"""Безопасное состояние словами — для документов и протокола FAT."""
