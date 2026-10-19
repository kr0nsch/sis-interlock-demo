"""Разбор значений ячеек матрицы (DESIGN.md, 9.1 и 9.3).

Функции возвращают ``None``, если значение не разбирается; сообщение с кодом правила
формирует проверка (:mod:`cemgen.validate`), которая знает строку и колонку.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

TAG_RE = re.compile(r"^[A-Z][A-Z0-9]{0,23}$")
_NUMBER_RE = re.compile(r"^[+-]?(\d+([.,]\d*)?|[.,]\d+)$")
_DURATION_RE = re.compile(r"^([+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+))(ms|s|m|h)?$", re.IGNORECASE)
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_UINT_RE = re.compile(r"^\d+$")

_TRUE = frozenset({"yes", "да", "1", "true"})
_FALSE = frozenset({"no", "нет", "0", "false"})

_UNIT_MS = {"ms": Decimal(1), "s": Decimal(1000), "m": Decimal(60_000), "h": Decimal(3_600_000)}

MATRIX_MARKS = frozenset({"X", "x", "Х", "х"})  # латинские и кириллические Х/х


def parse_number(text: str) -> Decimal | None:
    """Число: десятичная точка или запятая, без разделителей разрядов и единиц."""
    if not _NUMBER_RE.match(text):
        return None
    try:
        return Decimal(text.replace(",", "."))
    except InvalidOperation:  # pragma: no cover - регулярное выражение уже отсекло мусор
        return None


def parse_uint(text: str) -> int | None:
    """Целое без знака (``bypass_max``, номера)."""
    return int(text) if _UINT_RE.match(text) else None


def parse_int_number(text: str) -> int | None:
    """Целое число, записанное как число (``2``, ``2.0`` из XLSX уже приведено к ``2``)."""
    value = parse_number(text)
    if value is None or value != value.to_integral_value():
        return None
    return int(value)


class DurationError(ValueError):
    """Длительность не разбирается или не целое число миллисекунд."""


def parse_duration_ms(text: str) -> int:
    """Длительность → мс: ``500ms``, ``2s``, ``1.5s``, ``15m``, ``8h``; без единицы — секунды.

    Регистр единицы не важен, пробелов нет. Значение округляется до 1 мс; если дробная часть
    миллисекунды не нулевая — :class:`DurationError`. Отрицательное значение возвращается как
    есть: пределы проверяет вызывающий.
    """
    match = _DURATION_RE.match(text)
    if not match:
        raise DurationError(f"«{text}» — не длительность")
    number = Decimal(match.group(1).replace(",", "."))
    unit = (match.group(2) or "s").lower()
    value = number * _UNIT_MS[unit]
    if value != value.to_integral_value():
        raise DurationError(f"«{text}» — не целое число миллисекунд")
    return int(value)


def parse_bool(text: str) -> bool | None:
    """Логическое: ``yes``/``no``, ``да``/``нет``, ``1``/``0``, ``true``/``false``."""
    folded = text.casefold()
    if folded in _TRUE:
        return True
    if folded in _FALSE:
        return False
    return None


def is_tag(text: str) -> bool:
    """Тег: заглавные латинские буквы и цифры, первая — буква, до 24 символов (9.3)."""
    return bool(TAG_RE.match(text))


def is_iso_date(text: str) -> bool:
    import datetime as dt

    if not _DATE_RE.match(text):
        return False
    try:
        dt.date.fromisoformat(text)
    except ValueError:
        return False
    return True


def is_ascii_text(text: str) -> bool:
    """ASCII без управляющих символов."""
    return all(32 <= ord(ch) < 127 for ch in text)


def matrix_mark(text: str) -> bool | None:
    """Ячейка матрицы: «X» (латиница или кириллица, любой регистр) → True, пусто → False."""
    if not text:
        return False
    if text in MATRIX_MARKS:
        return True
    return None


def format_decimal_ru(value: Decimal) -> str:
    """Число для документов: десятичная запятая, без лишних нулей справа (``0,9``, ``85``)."""
    text = format(value.normalize(), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text.replace(".", ",").replace("-", "−")


def format_float_ru(value: float, digits: int = 2) -> str:
    """Вещественное для документов: ``digits`` знаков после запятой, десятичная запятая."""
    return f"{value:.{digits}f}".replace(".", ",").replace("-", "−")


def format_duration_ru(ms: int) -> str:
    """Длительность для документов: ``2 с``, ``1,5 с``, ``15 мин``, ``8 ч``, ``14 мин 59,9 с``."""
    if ms == 0:
        return "0 с"
    if ms < 1000:
        return f"{ms} мс"
    hours, rest = divmod(ms, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    parts = []
    if hours:
        parts.append(f"{hours} ч")
    if minutes:
        parts.append(f"{minutes} мин")
    if rest:
        parts.append(format_decimal_ru(Decimal(rest) / 1000) + " с")
    return " ".join(parts)
