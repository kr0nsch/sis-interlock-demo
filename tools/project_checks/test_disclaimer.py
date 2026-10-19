"""Обязательный дисклеймер ПАЗ (docs/DESIGN.md, раздел 3.1; спецификация проекта 10).

В каждом файле объявления объекта ST (POU, DUT, GVL, интерфейс) в src/ и tests/ — в том числе в
сгенерированных — комментарий до первой строки кода содержит дословно текст дисклеймера (после
удаления //, (*, *) и схлопывания пробелов; регистр первой буквы не проверяется). В README —
дисклеймер цитатой в начале.

Запуск: python -m pytest (каталог входит в testpaths, pyproject.toml).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import stlayout as L

REPO_ROOT = Path(__file__).resolve().parents[2]
DISCLAIMER = (
    "код демонстрационный и не предназначен для систем безопасности. Реальная ПАЗ требует определения SIL, "
    "сертифицированных аппаратных и программных средств и валидации по ГОСТ Р МЭК 61511."
)


def normalize(text: str) -> str:
    """Убрать маркеры комментариев и схлопнуть пробелы; первая буква дисклеймера — без учёта регистра."""
    text = text.replace("(*", " ").replace("*)", " ").replace("//", " ")
    return re.sub(r"\s+", " ", text).strip()


def header_comment(decl: str) -> str:
    """Комментарии до первой строки кода (прагма — уже код)."""
    parts: list[str] = []
    for tok in L.tokenize(decl):
        if tok.kind == L.TK_COMMENT:
            parts.append(tok.text)
        elif tok.kind != L.TK_WS:
            break
    return normalize("\n".join(parts))


def contains_disclaimer(text: str) -> bool:
    expected = normalize(DISCLAIMER)
    return expected in text or (expected[0].upper() + expected[1:]) in text


def objects() -> list[tuple[str, L.StObject]]:
    found: list[tuple[str, L.StObject]] = []
    for subdir in ("src", "tests"):
        result = L.scan(str(REPO_ROOT), subdir)
        assert result.ok, [issue.format() for issue in result.errors]
        found += [(subdir, obj) for obj in result.objects]
    return found


def test_objects_found() -> None:
    names = {obj.name for _, obj in objects()}
    assert {"FB_Voting", "FB_CauseEffect", "GVL_Const", "I_SisEventSink", "ST_SisEvent"} <= names


@pytest.mark.parametrize("subdir_obj", objects(), ids=lambda so: f"{so[0]}:{so[1].name}")
def test_every_object_header_has_disclaimer(subdir_obj: tuple[str, L.StObject]) -> None:
    _, obj = subdir_obj
    assert contains_disclaimer(header_comment(obj.decl)), (
        f"{obj.name}: в комментарии-заголовке нет дисклеймера DESIGN.md 3.1"
    )


def test_readme_starts_with_disclaimer() -> None:
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    head = "\n".join(text.splitlines()[:20])
    quote = normalize(" ".join(line.lstrip("> ") for line in head.splitlines() if line.startswith(">")))
    assert contains_disclaimer(quote), "README: дисклеймер — цитатой в начале файла"


def test_header_comment_parser() -> None:
    decl = "// a\n(* b *)\n{attribute 'x'}\n// not header\nTYPE X : INT; END_TYPE\n"
    assert header_comment(decl) == "a b"
    assert contains_disclaimer(normalize("// К" + DISCLAIMER[1:]))
