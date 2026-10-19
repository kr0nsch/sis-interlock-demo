"""Необязательный адаптер: тот же генератор как плагин iolistgen (DESIGN.md, 10.7).

Точка входа ``sis-cem`` в группе ``iolistgen.generators`` объявлена в ``pyproject.toml``. iolistgen
загружает её, только если сам установлен в том же окружении; ``cemgen`` от iolistgen не зависит
(решение D-04): этот модуль импортирует iolistgen лениво — при создании опций и в ``generate``.

Что делает плагин:

1. берёт матрицу из опции ``cem`` (``--set sis-cem.cem=examples/separator/cem.csv``; относительный
   путь — от текущего каталога, затем от каталога перечня сигналов);
2. проверяет матрицу теми же правилами CEM-Exxx (ошибка — ``GenerationError``, предупреждения —
   ``ctx.warn``);
3. сверяет теги каналов и ключей матрицы с перечнем сигналов (``Signal.ident`` или ``Signal.tag``
   без учёта регистра): отсутствующий тег — предупреждение, с опцией ``strict_tags`` — ошибка;
4. пишет те же файлы, что ``python -m cemgen generate``, в каталог вывода iolistgen через
   ``ctx.write_text`` (идемпотентно, с отложенной записью команды ``iolistgen generate``).

Лишние ``*.st`` в каталогах ``*/Generated/`` плагин не удаляет (контекст iolistgen умеет только
писать) — для этого есть ``python -m cemgen generate``.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from cemgen.generate import build_outputs
from cemgen.model import Matrix
from cemgen.stfmt import GenerationError as CemGenerationError
from cemgen.validate import load

PLUGIN_NAME = "sis-cem"


def matrix_tags(matrix: Matrix) -> list[str]:
    """Теги, которые должны быть в перечне сигналов: каналы причин и ключи (без следствий)."""
    tags = [channel.tag for channel in matrix.channels]
    tags += [tag for tag, _ in matrix.key_tags]
    return tags


def missing_tags(matrix: Matrix, signals: Sequence[Any]) -> list[str]:
    """Теги матрицы, которых нет в перечне: сравнение с ``ident`` и ``tag`` сигналов без учёта регистра."""
    known: set[str] = set()
    for signal in signals:
        for attr in ("ident", "tag"):
            value = getattr(signal, attr, None)
            if isinstance(value, str):
                known.add(value.casefold())
                known.add(value.replace("-", "").replace("_", "").casefold())
    return [tag for tag in matrix_tags(matrix) if tag.casefold() not in known]


def _resolve(option: str, source_path: str | None) -> Path:
    path = Path(option)
    if path.is_absolute() or path.exists() or source_path is None:
        return path
    candidate = Path(source_path).parent / path
    return candidate if candidate.exists() else path


class SisCemGenerator:
    """Генератор iolistgen ``sis-cem``: ПАЗ по матрице причин и следствий через ``cemgen``."""

    name = PLUGIN_NAME
    description = "ПАЗ по матрице причин и следствий (cemgen): конфигурация ST, тесты coUnit, документы"

    @property
    def options(self) -> Sequence[Any]:
        from iolistgen.generators import GeneratorOption

        return (
            GeneratorOption("cem", "файл матрицы причин и следствий (.csv или .xlsx)", "str", ""),
            GeneratorOption("strict_tags", "тег матрицы, которого нет в перечне, — ошибка", "bool", False),
        )

    def generate(self, model: Any, out_dir: Path, ctx: Any) -> list[Path]:
        from iolistgen.generators import GenerationError

        option = ctx.str_option("cem")
        if not option:
            raise GenerationError("sis-cem: не задан файл матрицы — --set sis-cem.cem=<файл .csv или .xlsx>")
        path = _resolve(option, getattr(getattr(ctx, "source", None), "path", None))
        result = load(path)
        if result.matrix is None:
            text = "; ".join(d.format(option) for d in result.errors) or "матрица не принята"
            raise GenerationError(f"sis-cem: {text}")
        for diag in result.warnings:
            ctx.warn(f"sis-cem: {diag.format(option)}")
        missing = missing_tags(result.matrix, getattr(model, "signals", ()))
        if missing:
            text = f"sis-cem: тегов матрицы нет в перечне сигналов: {', '.join(missing)}"
            if ctx.bool_option("strict_tags"):
                raise GenerationError(text)
            ctx.warn(text)
        try:
            outputs = build_outputs(result.matrix)
        except CemGenerationError as exc:
            raise GenerationError(f"sis-cem: {exc}") from exc
        return [ctx.write_text(rel, text) for rel, text in outputs.files.items()]
