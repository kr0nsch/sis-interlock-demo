"""Редактируемая копия матрицы для тестов правил проверки: правка ячеек по ключам и колонкам."""

from __future__ import annotations

import csv
import io
from pathlib import Path


class Sheet:
    """Строки CSV-матрицы как списки ячеек; правки — по ключу шапки, номеру причины, метке."""

    def __init__(self, rows: list[list[str]]) -> None:
        self.rows = rows

    @classmethod
    def read(cls, path: Path) -> Sheet:
        text = path.read_text(encoding="utf-8-sig")
        return cls([list(r) for r in csv.reader(io.StringIO(text, newline=""), delimiter=";")])

    def write(self, path: Path) -> Path:
        buffer = io.StringIO(newline="")
        csv.writer(buffer, delimiter=";", lineterminator="\n").writerows(self.rows)
        path.write_text(buffer.getvalue(), encoding="utf-8", newline="")
        return path

    def line_of(self, index: int) -> int:
        """Номер строки файла (с 1) для индекса строки (без многострочных ячеек)."""
        return index + 1

    # --- поиск -------------------------------------------------------------------------------------
    def find(self, first: str) -> int:
        return next(i for i, r in enumerate(self.rows) if r and r[0] == first)

    @property
    def header_index(self) -> int:
        return self.find("no")

    @property
    def label_col(self) -> int:
        return self.rows[self.header_index].index(">>")

    def col(self, name: str) -> int:
        return self.rows[self.header_index].index(name)

    def cause_index(self, no: int) -> int:
        return self.header_index + no

    def label_index(self, label: str) -> int:
        lc = self.label_col
        return next(i for i, r in enumerate(self.rows) if len(r) > lc and r[lc] == label)

    def _cell(self, row: int, col: int, value: str) -> None:
        cells = self.rows[row]
        while len(cells) <= col:
            cells.append("")
        cells[col] = value

    # --- правки ----------------------------------------------------------------------------------
    def set_header(self, key: str, value: str) -> Sheet:
        self._cell(self.find(key), 1, value)
        return self

    def set_header_cell(self, key: str, col: int, value: str) -> Sheet:
        self._cell(self.find(key), col, value)
        return self

    def drop_header(self, key: str) -> Sheet:
        del self.rows[self.find(key)]
        return self

    def add_header(self, key: str, value: str) -> Sheet:
        self.rows.insert(self.find("[matrix]"), [key, value])
        return self

    def set_cause(self, no: int, column: str, value: str) -> Sheet:
        self._cell(self.cause_index(no), self.col(column), value)
        return self

    def set_cause_label_cell(self, no: int, value: str) -> Sheet:
        self._cell(self.cause_index(no), self.label_col, value)
        return self

    def set_effect(self, effect_no: int, label: str, value: str) -> Sheet:
        self._cell(self.label_index(label), self.label_col + effect_no, value)
        return self

    def rename_label(self, label: str, new: str) -> Sheet:
        self._cell(self.label_index(label), self.label_col, new)
        return self

    def rename_column(self, name: str, new: str) -> Sheet:
        self._cell(self.header_index, self.col(name), new)
        return self

    def set_mark(self, cause_no: int, effect_no: int, value: str) -> Sheet:
        self._cell(self.cause_index(cause_no), self.label_col + effect_no, value)
        return self

    def clear_marks_of_cause(self, cause_no: int) -> Sheet:
        row = self.rows[self.cause_index(cause_no)]
        for col in range(self.label_col + 1, len(row)):
            row[col] = ""
        return self

    def clear_marks_of_effect(self, effect_no: int) -> Sheet:
        for index in range(self.header_index + 1, len(self.rows)):
            if self.rows[index]:
                self._cell(index, self.label_col + effect_no, "")
        return self

    def remove_marker(self, marker: str) -> Sheet:
        del self.rows[self.find(marker)]
        return self

    def duplicate_marker(self, marker: str) -> Sheet:
        index = self.find(marker)
        self.rows.insert(index + 1, [marker])
        return self

    def remove_label_mark(self) -> Sheet:
        self._cell(self.header_index, self.label_col, "")
        return self

    def append_row(self, cells: list[str]) -> Sheet:
        self.rows.append(cells)
        return self
