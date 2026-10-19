"""Правила проверки матрицы (DESIGN.md, 9.4): каждое правило — срабатывание и тишина.

Тишина: демо-матрица и мини-матрица проходят без ошибок (у мини — только ожидаемые CEM-W005).
Срабатывание: одна правка демо-матрицы даёт сообщение с нужным кодом, строкой и колонкой.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

import pytest

from cemgen.validate import Result, load
from pytests.conftest import DEMO_CSV, MINI_CSV
from pytests.sheet import Sheet

Edit = Callable[[Sheet], Sheet]

FORMAT_RE = re.compile(r"^[^:]+:(\d+(:[A-Z]+)?:)? CEM-[EW]\d{3} .+\. Как исправить: .+\.$")


def run(tmp_path: Path, edit: Edit) -> Result:
    sheet = edit(Sheet.read(DEMO_CSV))
    return load(sheet.write(tmp_path / "m.csv"))


def codes(result: Result) -> set[str]:
    return {d.code for d in result.diagnostics}


def test_demo_matrix_is_clean() -> None:
    result = load(DEMO_CSV)
    assert result.matrix is not None
    assert result.diagnostics == ()


def test_mini_matrix_only_permit_warnings() -> None:
    # У мини-матрицы нет тегов ключей (два CEM-W005), а внешний вход XS303 — с требованием при 1
    # (CEM-W006): так проверяется ветвь привязки ext под напряжением
    result = load(MINI_CSV)
    assert result.matrix is not None
    assert codes(result) == {"CEM-W005", "CEM-W006"}
    assert len(result.warnings) == 3


ERROR_CASES: list[tuple[str, str, Edit]] = [
    ("CEM-E002", "нет [header]", lambda s: s.remove_marker("[header]")),
    ("CEM-E002", "повтор [matrix]", lambda s: s.duplicate_marker("[matrix]")),
    ("CEM-E002", "строка до [header]", lambda s: Sheet([["stray"], *s.rows])),
    ("CEM-E003", "неизвестный ключ", lambda s: s.add_header("color", "red")),
    ("CEM-E003", "нет обязательного ключа", lambda s: s.drop_header("title")),
    ("CEM-E003", "повтор ключа", lambda s: s.add_header("object", "V-102")),
    ("CEM-E003", "лишние ячейки", lambda s: s.set_header_cell("object", 2, "x")),
    ("CEM-E004", "формат", lambda s: s.set_header("format", "cem/2")),
    ("CEM-E004", "дата", lambda s: s.set_header("date", "16.10.2026")),
    ("CEM-E004", "object не ASCII", lambda s: s.set_header("object", "В-101")),
    ("CEM-E005", "нет >>", lambda s: s.remove_label_mark()),
    ("CEM-E006", "неизвестная метка", lambda s: s.rename_label("actuator", "actor")),
    ("CEM-E006", "нет обязательной метки", lambda s: s.rename_label("effect_notes", "actuator")),
    ("CEM-E007", "метка в строке причины", lambda s: s.set_cause_label_cell(1, "zz")),
    ("CEM-E007", "значение правее следствий", lambda s: s.set_mark(1, 9, "X")),
    ("CEM-E008", "неизвестная колонка", lambda s: s.rename_column("hyst", "hysteresis")),
    ("CEM-E008", "нет обязательной колонки", lambda s: s.rename_column("delay", "")),
    ("CEM-E010", "номер не по порядку", lambda s: s.set_cause(2, "no", "3")),
    ("CEM-E010", "номер не число", lambda s: s.set_cause(2, "no", "два")),
    ("CEM-E011", "effect_no не по порядку", lambda s: s.set_effect(2, "effect_no", "5")),
    ("CEM-E012", "тег причины", lambda s: s.set_cause(1, "tag", "PSHH-101")),
    ("CEM-E012", "тег канала", lambda s: s.set_cause(1, "source", "PT101A,pt101b,PT101C")),
    ("CEM-E012", "тег ключа", lambda s: s.set_header("reset_tag", "HS_120")),
    ("CEM-E013", "дубль тега причины", lambda s: s.set_cause(2, "tag", "PSHH101")),
    ("CEM-E013", "тег следствия = тег причины", lambda s: s.set_effect(7, "effect_tag", "ESL109")),
    ("CEM-E013", "поле ST_SisIo дважды", lambda s: s.set_header("reset_tag", "ES109")),
    ("CEM-E013", "зарезервированный тег", lambda s: s.set_cause(10, "tag", "COUNT")),
    ("CEM-E014", "пустое описание", lambda s: s.set_cause(1, "description", "")),
    ("CEM-E014", "пустой actuator", lambda s: s.set_effect(3, "actuator", "")),
    ("CEM-E015", "signal", lambda s: s.set_cause(1, "signal", "analog")),
    ("CEM-E016", "vote", lambda s: s.set_cause(1, "vote", "3oo3")),
    ("CEM-E016", "число тегов", lambda s: s.set_cause(1, "source", "PT101A,PT101B")),
    ("CEM-E017", "policy", lambda s: s.set_cause(1, "policy", "trip")),
    ("CEM-E018", "trip_on ai", lambda s: s.set_cause(1, "trip_on", "1")),
    ("CEM-E018", "trip_on di", lambda s: s.set_cause(7, "trip_on", "low")),
    ("CEM-E019", "normal не на стороне нормы", lambda s: s.set_cause(1, "normal", "0.89")),
    ("CEM-E019", "шкала", lambda s: s.set_cause(5, "range_lo", "150")),
    ("CEM-E019", "уставка не число", lambda s: s.set_cause(5, "setpoint", "85C")),
    ("CEM-E020", "гистерезис < 0", lambda s: s.set_cause(5, "hyst", "-1")),
    ("CEM-E020", "нет units", lambda s: s.set_cause(5, "units", "")),
    ("CEM-E020", "поле ai у di", lambda s: s.set_cause(7, "units", "V")),
    ("CEM-E021", "не кратно шагу", lambda s: s.set_cause(1, "delay", "2.05s")),
    ("CEM-E021", "больше предела", lambda s: s.set_cause(1, "delay", "11m")),
    ("CEM-E021", "не разбирается", lambda s: s.set_cause(1, "delay", "2 s")),
    ("CEM-E021", "test_step", lambda s: s.set_header("test_step", "0s")),
    ("CEM-E021", "подтверждение нормы не кратно шагу", lambda s: s.set_cause(2, "override_clear", "30.05s")),
    ("CEM-E021", "подтверждение нормы больше предела", lambda s: s.set_cause(2, "override_clear", "3h")),
    ("CEM-E022", "обход без срока", lambda s: s.set_cause(2, "override_time", "")),
    ("CEM-E022", "срок без обхода", lambda s: s.set_cause(1, "override_time", "5m")),
    ("CEM-E022", "подтверждение нормы без обхода", lambda s: s.set_cause(1, "override_clear", "30s")),
    ("CEM-E023", "bypass_max > N − 1", lambda s: s.set_cause(1, "bypass_max", "3")),
    ("CEM-E023", "bypass_time 0", lambda s: s.set_cause(1, "bypass_time", "0s")),
    ("CEM-E024", "общий канал, разная шкала", lambda s: s.set_cause(2, "range_hi", "2.5")),
    ("CEM-E025", "ячейка матрицы", lambda s: s.set_mark(1, 2, "Y")),
    ("CEM-E026", "причина без X", lambda s: s.clear_marks_of_cause(5)),
    ("CEM-E027", "следствие без X", lambda s: s.clear_marks_of_effect(2)),
    ("CEM-E028", "safe_state", lambda s: s.set_effect(1, "safe_state", "shut")),
    ("CEM-E029", "enable", lambda s: s.set_cause(1, "enable", "maybe")),
    ("CEM-E029", "start_tripped", lambda s: s.set_header("start_tripped", "sometimes")),
    ("CEM-E030", "стимул вне 3,8…20,5 мА", lambda s: s.set_cause(1, "setpoint", "1.55").set_cause(1, "hyst", "0.2")),
    ("CEM-E031", "подтверждение нормы = срок", lambda s: s.set_cause(2, "override_clear", "15m")),
    ("CEM-E031", "подтверждение нормы 0", lambda s: s.set_cause(2, "override_clear", "0s")),
    (
        "CEM-E031",
        "умолчание 30s не короче срока",
        lambda s: s.set_cause(2, "override_clear", "").set_cause(2, "override_time", "30s"),
    ),
]


@pytest.mark.parametrize(("code", "what", "edit"), ERROR_CASES, ids=[f"{c[0]}-{c[1]}" for c in ERROR_CASES])
def test_error_rule_triggers(tmp_path: Path, code: str, what: str, edit: Edit) -> None:
    result = run(tmp_path, edit)
    assert code in codes(result), [d.format("m.csv") for d in result.diagnostics]
    assert result.matrix is None
    for diag in result.diagnostics:
        assert FORMAT_RE.match(diag.format("m.csv")), diag.format("m.csv")


WARNING_CASES: list[tuple[str, str, Edit]] = [
    ("CEM-W001", "выключенная причина с X", lambda s: s.set_cause(5, "enable", "no")),
    (
        "CEM-W002",
        "стимул вызывает другую причину",
        lambda s: s.set_cause(2, "trip_on", "high").set_cause(2, "setpoint", "0.95").set_cause(2, "normal", "0.60"),
    ),
    (
        "CEM-W003",
        "обход короче задержки",
        lambda s: s.set_cause(2, "override_time", "3s").set_cause(2, "override_clear", "1s"),
    ),
    (
        "CEM-W004",
        "рассогласование при N = 1",
        lambda s: (
            s.set_cause(5, "vote", "1oo1")
            .set_cause(5, "source", "TT103A")
            .set_cause(5, "bypass_max", "0")
            .set_cause(5, "bypass_time", "0s")
        ),
    ),
    ("CEM-W005", "нет ключа байпасов", lambda s: s.drop_header("bypass_permit_tag")),
    ("CEM-W005", "нет ключа обходов", lambda s: s.drop_header("override_permit_tag")),
    ("CEM-W006", "di: требование при 1 (под напряжением)", lambda s: s.set_cause(10, "trip_on", "1")),
    (
        "CEM-W006",
        "ext: требование при 1 (под напряжением, без контроля линии)",
        lambda s: (
            s.set_cause(10, "signal", "ext")
            .set_cause(10, "vote", "-")
            .set_cause(10, "policy", "")
            .set_cause(10, "trip_on", "1")
        ),
    ),
]


def test_ext_deenergize_to_trip_no_warning(tmp_path: Path) -> None:
    # Тишина CEM-W006 для ext: требование при 0 — срабатывание на обесточивание
    result = run(
        tmp_path,
        lambda s: (
            s.set_cause(10, "signal", "ext")
            .set_cause(10, "vote", "-")
            .set_cause(10, "policy", "")
            .set_cause(10, "trip_on", "0")
        ),
    )
    assert result.matrix is not None, [d.format("m.csv") for d in result.errors]
    assert "CEM-W006" not in codes(result)


@pytest.mark.parametrize(("code", "what", "edit"), WARNING_CASES, ids=[f"{c[0]}-{c[1]}" for c in WARNING_CASES])
def test_warning_rule_triggers(tmp_path: Path, code: str, what: str, edit: Edit) -> None:
    result = run(tmp_path, edit)
    assert result.matrix is not None, [d.format("m.csv") for d in result.errors]
    assert code in codes(result)
    assert not result.errors


def test_location_row_and_column(tmp_path: Path) -> None:
    sheet = Sheet.read(DEMO_CSV)
    line = sheet.line_of(sheet.cause_index(2))
    result = run(tmp_path, lambda s: s.set_cause(2, "no", "3"))
    diag = next(d for d in result.diagnostics if d.code == "CEM-E010")
    assert (diag.row, diag.col) == (line, 1)
    assert diag.format("m.csv").startswith(f"m.csv:{line}:A: CEM-E010 ")


def test_matrix_cell_column_letter(tmp_path: Path) -> None:
    sheet = Sheet.read(DEMO_CSV)
    result = run(tmp_path, lambda s: s.set_mark(1, 2, "Y"))
    diag = next(d for d in result.diagnostics if d.code == "CEM-E025")
    assert diag.col == sheet.label_col + 1 + 2  # колонки с 1, следствие 2 правее колонки меток
    assert diag.row == sheet.line_of(sheet.cause_index(1))


def test_cyrillic_x_accepted(tmp_path: Path) -> None:
    result = run(tmp_path, lambda s: s.set_mark(1, 1, "Х").set_mark(3, 1, "х"))
    assert result.matrix is not None
    assert 1 in result.matrix.cause(1).effects


def test_comma_decimal_and_case_insensitive_units(tmp_path: Path) -> None:
    result = run(tmp_path, lambda s: s.set_cause(1, "setpoint", "0,90").set_cause(1, "delay", "2S"))
    assert result.matrix is not None
    analog = result.matrix.cause(1).analog
    assert analog is not None and str(analog.setpoint) == "0.90"
    assert result.matrix.cause(1).delay_ms == 2000


def test_override_clear_values_and_default(tmp_path: Path) -> None:
    # Демо-матрица: подтверждение нормы для автоснятия обходов задано явно (DESIGN.md, 11.3)
    demo = load(DEMO_CSV).matrix
    assert demo is not None
    assert [(c.tag, c.override_clear_ms) for c in demo.causes if c.override] == [
        ("PSLL101", 30_000),
        ("LSLL102", 60_000),
        ("PSLL108", 30_000),
    ]
    assert all(c.override_clear_ms == 0 for c in demo.causes if not c.override)
    # Пустая ячейка при override = yes — по умолчанию 30s; у мини-матрицы колонки нет вовсе
    result = run(tmp_path, lambda s: s.set_cause(4, "override_clear", ""))
    assert result.matrix is not None and result.matrix.cause(4).override_clear_ms == 30_000
    mini = load(MINI_CSV).matrix
    assert mini is not None and mini.cause(2).override_clear_ms == 30_000
    # Граница: на шаг короче срока — допустимо
    result = run(tmp_path, lambda s: s.set_cause(2, "override_clear", "899.9s"))
    assert result.matrix is not None and result.matrix.cause(2).override_clear_ms == 15 * 60_000 - 100


def test_override_clear_error_does_not_cascade(tmp_path: Path) -> None:
    # Срок обхода с ошибкой — отношение подтверждения к сроку не проверяется
    result = run(tmp_path, lambda s: s.set_cause(2, "override_time", "0s"))
    assert codes(result) == {"CEM-E022"}


def test_bom_and_crlf_accepted(tmp_path: Path) -> None:
    data = DEMO_CSV.read_bytes().replace(b"\n", b"\r\n")
    path = tmp_path / "bom.csv"
    path.write_bytes(b"\xef\xbb\xbf" + data)
    result = load(path)
    assert result.matrix is not None
    assert result.matrix.grid_digest == load(DEMO_CSV).matrix.grid_digest  # type: ignore[union-attr]


def test_unreadable_files(tmp_path: Path) -> None:
    missing = load(tmp_path / "nope.csv")
    assert [d.code for d in missing.diagnostics] == ["CEM-E001"]
    wrong = tmp_path / "m.txt"
    wrong.write_text("x", encoding="utf-8")
    assert [d.code for d in load(wrong).diagnostics] == ["CEM-E001"]
    cp1251 = tmp_path / "cp.csv"
    cp1251.write_bytes("[header]\nobject;Сепаратор\n".encode("cp1251"))
    assert [d.code for d in load(cp1251).diagnostics] == ["CEM-E001"]


def test_unclosed_quote_is_file_error(tmp_path: Path) -> None:
    path = tmp_path / "q.csv"
    path.write_text('[header]\nformat;"cem/1\n', encoding="utf-8")
    assert [d.code for d in load(path).diagnostics] == ["CEM-E001"]


def test_errors_do_not_cascade(tmp_path: Path) -> None:
    result = run(tmp_path, lambda s: s.set_cause(1, "signal", "analog"))
    assert codes(result) == {"CEM-E015"}


def test_column_order_is_free(tmp_path: Path) -> None:
    sheet = Sheet.read(DEMO_CSV)
    hdr = sheet.header_index
    lc = sheet.label_col
    # меняем местами колонки notes и description во всех строках раздела причин
    a, b = sheet.col("notes"), sheet.col("description")
    for index in range(hdr, len(sheet.rows)):
        row = sheet.rows[index]
        if len(row) > max(a, b):
            row[a], row[b] = row[b], row[a]
    assert lc == sheet.label_col
    result = load(sheet.write(tmp_path / "m.csv"))
    assert result.matrix is not None
    assert result.matrix.cause(1).description == load(DEMO_CSV).matrix.cause(1).description  # type: ignore[union-attr]
