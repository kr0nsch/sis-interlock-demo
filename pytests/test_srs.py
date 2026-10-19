"""Блок функций безопасности в docs/SRS.md: содержание по матрице, маркеры, --check."""

from __future__ import annotations

from pathlib import Path

import pytest

from cemgen import fat
from cemgen.cli import main
from cemgen.gen_srs import BEGIN, END, SIL_TEXT, SRS_PATH, sif_block, splice, spliced_docs
from cemgen.model import Matrix
from cemgen.stfmt import GenerationError
from pytests.conftest import DEMO_CSV, MINI_CSV, ROOT

REQUIRED_ROWS = (
    "Описание",
    "Инициирующая причина",
    "Голосование",
    "Безопасное состояние",
    "Время реакции логики",
    "Целевое время реакции",
    "Режим работы",
    "Интервал проверочных испытаний",
    "Целевой SIL",
    "Проверка",
)
SRS_STUB = f"# SRS\n\n## 3. Функции\n\n{BEGIN}\nстарый текст\n{END}\n\n## 4. Дальше\n"


def _section(block: str, no: int) -> str:
    start = block.index(f"### SIF-{no:02d}.")
    nxt = block.find("\n### SIF-", start + 1)
    return block[start:] if nxt < 0 else block[start:nxt]


def test_block_has_every_sif_with_required_rows(demo: Matrix) -> None:
    block = sif_block(demo)
    for cause in demo.causes:
        section = _section(block, cause.no)
        assert section.startswith(f"### SIF-{cause.no:02d}. {cause.tag} — {cause.description}")
        for row in REQUIRED_ROWS:
            assert f"| {row} |" in section, (cause.tag, row)
        assert f"| Целевой SIL | {SIL_TEXT} |" in section
        assert f"`Matrix_{cause.tag}*`" in section
        assert f"| SIF-{cause.no:02d} | {cause.tag} — " in block  # строка сводки
    assert "16#CD40" in block and demo.grid_digest in block


def test_block_values_come_from_matrix(demo: Matrix) -> None:
    block = sif_block(demo)
    pshh = _section(block, 1)
    assert "≥ 0,9 МПа по 2 из 3 каналов (PT101A, PT101B, PT101C)" in pshh
    assert "через 2 с" in pshh and "ESDV101 (клапан-отсекатель на входе V-101) — закрыт" in pshh
    assert "BDV101" not in pshh  # не своё следствие
    assert "| Пусковой обход | не предусмотрен |" in pshh
    assert "до 15 мин при ключе HS122" in _section(block, 2)
    assert "| Байпас канала | запрещён |" in _section(block, 8)  # HS106
    assert "1oo1 (1 из 1 канала)" in _section(block, 10)


def test_block_fat_steps_exist_in_protocol(demo: Matrix) -> None:
    ids = {step.id for s in fat.build_sections(demo) for step in s.steps}
    block = sif_block(demo)
    for cause in demo.causes:
        line = next(x for x in _section(block, cause.no).splitlines() if x.startswith("| Проверка |"))
        listed = [part.strip(" |") for part in line.split("протокол FAT — ", 1)[1].split(",")]
        assert listed and set(listed) <= ids, (cause.tag, listed)
        assert f"FAT-03-{cause.no:02d}" in listed


def test_splice_replaces_only_between_markers(demo: Matrix) -> None:
    block = sif_block(demo)
    text = splice(SRS_STUB, block)
    assert text.startswith("# SRS\n\n## 3. Функции\n\n" + BEGIN + "\n")
    assert text.endswith(END + "\n\n## 4. Дальше\n")
    assert "старый текст" not in text and block in text
    assert splice(text, block) == text  # повторный запуск ничего не меняет


@pytest.mark.parametrize(
    "text",
    [
        "без маркеров\n",
        f"{BEGIN}\n",
        f"{END}\n{BEGIN}\n",
        f"{BEGIN}\n{END}\n{BEGIN}\n{END}\n",
    ],
)
def test_splice_rejects_bad_markers(text: str) -> None:
    with pytest.raises(GenerationError, match="маркеру"):
        splice(text, "x\n")


def test_spliced_docs_skips_missing_file(tmp_path: Path, demo: Matrix) -> None:
    assert spliced_docs(tmp_path, demo) == {}


def test_cli_generate_updates_and_checks_srs(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    srs = tmp_path / SRS_PATH
    srs.parent.mkdir(parents=True)
    srs.write_bytes(SRS_STUB.encode("utf-8"))
    assert main(["generate", str(MINI_CSV), "--root", str(tmp_path)]) == 0
    text = srs.read_bytes().decode("utf-8")
    assert "### SIF-01." in text and "старый текст" not in text and text.endswith("## 4. Дальше\n")
    assert main(["generate", str(MINI_CSV), "--root", str(tmp_path), "--check"]) == 0
    srs.write_bytes(text.replace("### SIF-01.", "### SIF-1.").encode("utf-8"))
    capsys.readouterr()
    assert main(["generate", str(MINI_CSV), "--root", str(tmp_path), "--check"]) == 1
    assert f"изменён: {SRS_PATH}" in capsys.readouterr().out


def test_cli_generate_refuses_srs_without_markers(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    srs = tmp_path / SRS_PATH
    srs.parent.mkdir(parents=True)
    srs.write_bytes("# SRS без маркеров\n".encode())
    assert main(["generate", str(MINI_CSV), "--root", str(tmp_path)]) == 1
    assert "маркеру" in capsys.readouterr().err
    assert sorted(p.name for p in tmp_path.rglob("*") if p.is_file()) == ["SRS.md"]  # целиком или никак


def test_repository_srs_block_is_current(demo: Matrix) -> None:
    files = spliced_docs(ROOT, demo)
    assert SRS_PATH in files, "docs/SRS.md с маркерами cemgen:sif должен быть в репозитории"
    assert (ROOT / SRS_PATH).read_bytes().decode("utf-8") == files[SRS_PATH], (
        f"запустите python -m cemgen generate {DEMO_CSV.relative_to(ROOT).as_posix()}"
    )
