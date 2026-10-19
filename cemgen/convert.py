"""Перевод матрицы CSV ↔ XLSX (``cemgen convert``).

CSV → XLSX: лист ``CEM``, все ячейки текстом (формат ``@``), строка в строку — номера строк в
сообщениях проверки совпадают. Для чтения человеком — ширина колонок, перенос текста,
закреплённая строка заголовков причин и колонки меток. XLSX → CSV: UTF-8 без BOM, ``;``,
LF, кавычки по необходимости. Байты XLSX недетерминированы (метаданные книги), поэтому
равенство проверяется по сетке, а не по файлу.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path

from cemgen.grid import CSV_DELIMITER, SHEET_NAME, RawRow, read_raw


def write_xlsx(rows: list[RawRow], path: Path) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    book = Workbook()
    sheet = book.active
    assert sheet is not None
    sheet.title = SHEET_NAME
    width = max((len(r.cells) for r in rows), default=0)
    widths = [0] * width
    header_line: int | None = None
    label_col: int | None = None
    bold = Font(bold=True)
    header_fill = PatternFill("solid", fgColor="DDE4EE")
    for raw in rows:
        line = raw.line
        cells = list(raw.cells)
        if cells and cells[0].strip() == "no" and header_line is None:
            header_line = line
            label_col = next((i + 1 for i, v in enumerate(cells) if v.strip() == ">>"), None)
        for col, value in enumerate(cells, 1):
            if value == "":
                continue
            cell = sheet.cell(row=line, column=col, value=value)
            cell.number_format = "@"
            cell.data_type = "s"
            widths[col - 1] = max(widths[col - 1], min(len(value), 40))
            if cells[0].startswith("#"):
                cell.font = Font(italic=True, color="666666")
            elif line == header_line or value.strip().lower() in ("[header]", "[matrix]"):
                cell.font = bold
                cell.fill = header_fill
            if len(value) > 40:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
    for index, chars in enumerate(widths, 1):
        sheet.column_dimensions[get_column_letter(index)].width = max(4, chars + 2)
    if header_line is not None and label_col is not None:
        sheet.freeze_panes = f"C{header_line + 1}"
    book.save(path)


def write_csv(rows: list[RawRow], path: Path) -> None:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, delimiter=CSV_DELIMITER, quotechar='"', lineterminator="\n")
    line = 1
    for raw in rows:
        while line < raw.line:  # пустые строки листа сохраняют нумерацию
            writer.writerow([])
            line += 1
        cells = list(raw.cells)
        while cells and cells[-1] == "":
            cells.pop()
        writer.writerow(cells)
        line += 1
    path.write_bytes(buffer.getvalue().encode("utf-8"))


def convert(source: Path, target: Path) -> None:
    """CSV → XLSX или XLSX → CSV (по расширению ``target``)."""
    rows = read_raw(source)
    suffix = target.suffix.lower()
    if suffix == ".xlsx":
        write_xlsx(rows, target)
    elif suffix == ".csv":
        write_csv(rows, target)
    else:
        raise ValueError(f"расширение «{target.suffix}» не поддерживается: .csv или .xlsx")
