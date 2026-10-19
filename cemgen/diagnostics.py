"""Сообщения проверки матрицы (DESIGN.md, 9.4).

Формат: ``<файл>:<строка>:<колонка>: <код> <что не так>. Как исправить: <подсказка>``.
Строки нумеруются с 1 (строка файла CSV или листа XLSX), колонки — буквами (``A``, ``AA``).
Сообщение о файле целиком — без строки и колонки, о строке целиком — без колонки.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

ERROR = "error"
WARNING = "warning"


def column_letter(col: int) -> str:
    """Номер колонки с единицы → буквы: 1 → ``A``, 27 → ``AA``."""
    if col < 1:
        raise ValueError(f"номер колонки {col} < 1")
    letters = ""
    while col:
        col, rest = divmod(col - 1, 26)
        letters = chr(ord("A") + rest) + letters
    return letters


@dataclass(frozen=True)
class Diagnostic:
    """Ошибка (``CEM-Exxx``) или предупреждение (``CEM-Wxxx``) с местом в файле."""

    code: str
    message: str
    hint: str
    row: int | None = None
    col: int | None = None

    @property
    def severity(self) -> str:
        return WARNING if self.code.startswith("CEM-W") else ERROR

    @property
    def is_error(self) -> bool:
        return self.severity == ERROR

    @property
    def location(self) -> str:
        """``строка:колонка``, ``строка`` или пусто."""
        if self.row is None:
            return ""
        if self.col is None:
            return str(self.row)
        return f"{self.row}:{column_letter(self.col)}"

    def format(self, source: str) -> str:
        where = f"{source}:{self.location}" if self.location else source
        text = self.message.rstrip(".")
        hint = self.hint.rstrip(".")
        return f"{where}: {self.code} {text}. Как исправить: {hint}."

    def to_json(self) -> dict[str, object]:
        return {
            "code": self.code,
            "severity": self.severity,
            "row": self.row,
            "column": column_letter(self.col) if self.col is not None else None,
            "message": self.message,
            "hint": self.hint,
        }


def sort_key(diag: Diagnostic) -> tuple[int, int, str]:
    return (diag.row or 0, diag.col or 0, diag.code)


def errors(diags: Iterable[Diagnostic]) -> list[Diagnostic]:
    return [d for d in diags if d.is_error]


def warnings(diags: Iterable[Diagnostic]) -> list[Diagnostic]:
    return [d for d in diags if not d.is_error]


class MatrixFileError(Exception):
    """Файл матрицы не читается (CEM-E001, CEM-E009): дальше проверять нечего."""

    def __init__(self, diagnostic: Diagnostic) -> None:
        super().__init__(diagnostic.message)
        self.diagnostic = diagnostic
