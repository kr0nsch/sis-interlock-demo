"""Общие фикстуры тестов cemgen: пути, демо-матрица, мини-матрица, выходы генератора."""

from __future__ import annotations

from pathlib import Path

import pytest

from cemgen.generate import Outputs, build_outputs
from cemgen.model import Matrix
from cemgen.validate import load

ROOT = Path(__file__).resolve().parent.parent
DEMO_CSV = ROOT / "examples" / "separator" / "cem.csv"
MINI_CSV = Path(__file__).resolve().parent / "fixtures" / "mini.csv"


def _load(path: Path) -> Matrix:
    result = load(path)
    assert result.matrix is not None, [d.format(path.name) for d in result.diagnostics]
    return result.matrix


@pytest.fixture(scope="session")
def demo() -> Matrix:
    """Демо-матрица сепаратора V-101."""
    return _load(DEMO_CSV)


@pytest.fixture(scope="session")
def mini() -> Matrix:
    """Мини-матрица: ai 1oo1, di 2oo2, ext, без тегов ключей, старт без срабатывания."""
    return _load(MINI_CSV)


@pytest.fixture(scope="session")
def demo_outputs(demo: Matrix) -> Outputs:
    return build_outputs(demo)


@pytest.fixture(scope="session")
def mini_outputs(mini: Matrix) -> Outputs:
    return build_outputs(mini)
