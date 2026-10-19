"""Необязательный адаптер iolistgen (DESIGN.md, 10.7): сверка тегов и запись тех же файлов.

С настоящим iolistgen тест идёт, если пакет установлен или лежит рядом (переменная IOLISTGEN_REPO,
по умолчанию ../iolistgen); иначе пропускается — cemgen от iolistgen не зависит.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

import pytest

from cemgen.iolistgen_plugin import PLUGIN_NAME, SisCemGenerator, matrix_tags, missing_tags
from cemgen.model import Matrix
from pytests.conftest import DEMO_CSV, ROOT


@dataclass(frozen=True)
class _Signal:
    tag: str
    ident: str


def test_matrix_tags_and_missing(demo: Matrix) -> None:
    tags = matrix_tags(demo)
    assert tags[:3] == ["PT101A", "PT101B", "PT101C"]
    assert tags[-3:] == ["HS120", "HS121", "HS122"]
    assert "ESDV101" not in tags  # следствия — выходы ПАЗ, в перечне могут называться иначе
    signals = [_Signal(tag=f"{t[:2]}-{t[2:]}", ident=t) for t in tags if t != "ES109"]
    assert missing_tags(demo, signals) == ["ES109"]
    by_tag_only = [_Signal(tag=t, ident=f"x{t}") for t in tags]
    assert missing_tags(demo, by_tag_only) == []


def _iolistgen() -> ModuleType:
    repo = Path(os.environ.get("IOLISTGEN_REPO", str(ROOT.parent / "iolistgen")))
    if (repo / "iolistgen" / "__init__.py").is_file() and str(repo) not in sys.path:
        sys.path.append(str(repo))
    module: ModuleType = pytest.importorskip("iolistgen.generators")
    return module


def test_plugin_with_real_iolistgen(tmp_path: Path) -> None:
    gens = _iolistgen()
    from iolistgen.config import Config
    from iolistgen.model import SourceInfo

    generator = SisCemGenerator()
    assert isinstance(generator, gens.Generator)  # протокол iolistgen (runtime_checkable)
    assert generator.name == PLUGIN_NAME
    from iolistgen.generators import registry

    assert registry._check(SisCemGenerator, PLUGIN_NAME).name == PLUGIN_NAME  # как при загрузке точки входа
    options = gens.resolve_options(generator, {"cem": str(DEMO_CSV)})
    source = SourceInfo(path=str(tmp_path / "io.csv"), name="io.csv", format="csv", sha256="0" * 64)
    ctx = gens.GeneratorContext(
        generator=PLUGIN_NAME, out_dir=tmp_path, options=options, config=Config(), source=source, version="0.1.0"
    )

    @dataclass(frozen=True)
    class _Model:
        signals: tuple[_Signal, ...]

    model = _Model(signals=(_Signal("PT-101A", "PT101A"),))
    written = generator.generate(model, tmp_path, ctx)
    assert len(written) == 276
    assert (tmp_path / "src/GVLs/Generated/GVL_SisCfg.gvl.st").is_file()
    assert any("тегов матрицы нет в перечне" in w for w in ctx.warnings)
    strict = gens.resolve_options(generator, {"cem": str(DEMO_CSV), "strict_tags": True})
    ctx_strict = gens.GeneratorContext(
        generator=PLUGIN_NAME, out_dir=tmp_path, options=strict, config=Config(), source=source, version="0.1.0"
    )
    with pytest.raises(gens.GenerationError):
        generator.generate(model, tmp_path, ctx_strict)
    empty = gens.resolve_options(generator, {})
    ctx_empty = gens.GeneratorContext(
        generator=PLUGIN_NAME, out_dir=tmp_path, options=empty, config=Config(), source=source, version="0.1.0"
    )
    with pytest.raises(gens.GenerationError):
        generator.generate(model, tmp_path, ctx_empty)
