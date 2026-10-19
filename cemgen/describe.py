"""Описания причин словами — общие для Markdown, HTML и протокола FAT."""

from __future__ import annotations

from cemgen.model import Cause, format_dec
from cemgen.refmodel import degradation
from cemgen.sisdefs import ARCH_NM, ARCH_TEXT, VoteArch
from cemgen.values import format_duration_ru


def setpoint_text(cause: Cause) -> str:
    """Уставка словами: «≥ 0,9 МПа», «размыкание (0)», «1»."""
    if cause.analog is not None:
        sign = "≥" if cause.analog.high else "≤"
        return f"{sign} {format_dec(cause.analog.setpoint)} {cause.analog.units}"
    if cause.trip_on == 0:
        return "0 (размыкание)"
    return "1 (замыкание)"


def bypass_text(cause: Cause) -> str:
    if not cause.is_voting:
        return "—"
    if cause.bypass_max == 0:
        return "запрещён"
    return f"{cause.bypass_max} кан., {format_duration_ru(cause.bypass_time_ms)}"


def override_text(cause: Cause) -> str:
    return format_duration_ru(cause.override_time_ms) if cause.override else "—"


def degradation_text(cause: Cause) -> str:
    """Действующая схема при отказе одного и двух каналов и при байпасе одного."""
    if cause.vote is None or cause.policy is None:
        return "—"
    n = ARCH_NM[cause.vote][0]
    parts = []
    for invalid in range(1, n + 1):
        arch = degradation(cause.vote, cause.policy, 0, invalid)
        name = "останов" if arch == VoteArch.FORCED_TRIP else ARCH_TEXT[arch]
        parts.append(f"{invalid} недост.: {name}")
    if cause.bypass_max:
        arch = degradation(cause.vote, cause.policy, 1, 0)
        name = "останов" if arch == VoteArch.FORCED_TRIP else ARCH_TEXT[arch]
        parts.append(f"байпас 1: {name}")
    return "; ".join(parts)
