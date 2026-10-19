"""Сборка всех выходов генератора и запись в репозиторий (DESIGN.md, 10.1–10.3).

:func:`build_outputs` строит все файлы в памяти (путь от корня → текст). :func:`apply` пишет
их только после того, как построено всё: генерация целиком или никак. Каталоги
``*/Generated/`` принадлежат генератору — лишние ``*.st`` в них удаляются. :func:`compare`
ничего не пишет и возвращает расхождения (``generate --check``). Блок функций безопасности в
рукописном ``docs/SRS.md`` добавляет к файлам командная строка (:func:`cemgen.gen_srs.spliced_docs`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from cemgen.gen_docs import generate_docs
from cemgen.gen_st import generate_src
from cemgen.gen_tests import TestCase, generate_tests
from cemgen.gen_truth import generate_truth
from cemgen.model import Matrix

GENERATED_DIRS = (
    "src/DUTs/Generated",
    "src/GVLs/Generated",
    "src/POUs/Generated",
    "tests/GVLs/Generated",
    "tests/POUs/Generated",
)
"""Каталоги, которые генератор ведёт целиком (лишние ``*.st`` удаляются)."""


@dataclass
class Outputs:
    """Файлы генератора и сценарные тесты (для отчётов и протокола)."""

    files: dict[str, str]
    cases: list[TestCase] = field(default_factory=list)


def build_outputs(matrix: Matrix) -> Outputs:
    """Все файлы раздела 10.2 в памяти."""
    files: dict[str, str] = {}
    files.update(generate_src(matrix))
    files.update(generate_truth(matrix))
    test_files, cases = generate_tests(matrix)
    files.update(test_files)
    files.update(generate_docs(matrix))
    return Outputs(dict(sorted(files.items())), cases)


@dataclass
class Diff:
    """Расхождения сгенерированного с файлами на диске."""

    changed: list[str] = field(default_factory=list)
    new: list[str] = field(default_factory=list)
    extra: list[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return not (self.changed or self.new or self.extra)

    def lines(self) -> list[str]:
        out = [f"изменён: {p}" for p in self.changed]
        out += [f"новый:   {p}" for p in self.new]
        out += [f"лишний:  {p}" for p in self.extra]
        return out


def _extra_files(root: Path, files: dict[str, str]) -> list[str]:
    extra: list[str] = []
    for rel_dir in GENERATED_DIRS:
        base = root / rel_dir
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.st")):
            rel = path.relative_to(root).as_posix()
            if rel not in files:
                extra.append(rel)
    return extra


def compare(root: Path, files: dict[str, str]) -> Diff:
    """Сравнить с диском побайтно (UTF-8, LF)."""
    diff = Diff()
    for rel, text in files.items():
        path = root / rel
        data = text.encode("utf-8")
        if not path.is_file():
            diff.new.append(rel)
        elif path.read_bytes() != data:
            diff.changed.append(rel)
    diff.extra = _extra_files(root, files)
    return diff


def apply(root: Path, files: dict[str, str]) -> Diff:
    """Записать изменившиеся файлы, удалить лишние ``*.st`` из ``Generated``; вернуть, что изменилось."""
    diff = compare(root, files)
    for rel in [*diff.new, *diff.changed]:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(files[rel].encode("utf-8"))
    for rel in diff.extra:
        (root / rel).unlink()
    for rel_dir in GENERATED_DIRS:
        base = root / rel_dir
        if not base.is_dir():
            continue
        for directory in sorted((p for p in base.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
            if not any(directory.iterdir()):
                directory.rmdir()
    return diff
