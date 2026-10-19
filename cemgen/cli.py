"""Командная строка ``cemgen`` (DESIGN.md, 10.1).

::

    python -m cemgen validate MATRIX [--strict] [--json]
    python -m cemgen generate MATRIX [--root .] [--check] [--strict]
    python -m cemgen convert SRC DST
    python -m cemgen fat-report MATRIX --results build/test-results.json [--out docs/FAT_REPORT.md]

Коды выхода: 0 — успех; 1 — ошибки матрицы (с ``--strict`` — и предупреждения), ``--check``
нашёл расхождения, упавшие тесты в ``fat-report``; 2 — аргументы, файл, ввод-вывод.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from cemgen import __version__, fat
from cemgen.convert import convert
from cemgen.diagnostics import MatrixFileError
from cemgen.gen_srs import spliced_docs
from cemgen.generate import apply, build_outputs, compare
from cemgen.stfmt import GenerationError, HeaderInfo
from cemgen.validate import Result, load

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_USAGE = 2


def _print_diagnostics(result: Result, source: str) -> None:
    for diag in result.diagnostics:
        print(diag.format(source), file=sys.stderr)


def _file_unreadable(result: Result) -> bool:
    return result.matrix is None and len(result.diagnostics) == 1 and result.diagnostics[0].code == "CEM-E001"


def _summary(result: Result) -> str:
    return f"ошибок {len(result.errors)}, предупреждений {len(result.warnings)}"


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.matrix)
    result = load(path)
    if args.json:
        payload = {
            "file": args.matrix,
            "ok": result.matrix is not None and not (args.strict and result.warnings),
            "errors": len(result.errors),
            "warnings": len(result.warnings),
            "diagnostics": [d.to_json() for d in result.diagnostics],
        }
        if result.matrix is not None:
            payload["matrix"] = {
                "document": result.matrix.header.document,
                "revision": result.matrix.header.revision,
                "causes": len(result.matrix.causes),
                "effects": len(result.matrix.effects),
                "crc": f"16#{result.matrix.crc:04X}",
                "grid_sha256": result.matrix.grid_digest,
            }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_diagnostics(result, args.matrix)
        if result.matrix is not None:
            m = result.matrix
            print(
                f"{args.matrix}: {m.header.document} ревизия {m.header.revision} — причин {len(m.causes)}, "
                f"следствий {len(m.effects)}, CRC 16#{m.crc:04X}; {_summary(result)}"
            )
        else:
            print(f"{args.matrix}: матрица не принята — {_summary(result)}", file=sys.stderr)
    if _file_unreadable(result):
        return EXIT_USAGE
    if result.matrix is None or (args.strict and result.warnings):
        return EXIT_FAIL
    return EXIT_OK


def cmd_generate(args: argparse.Namespace) -> int:
    path = Path(args.matrix)
    root = Path(args.root)
    if not root.is_dir():
        print(f"cemgen: каталог --root «{args.root}» не найден", file=sys.stderr)
        return EXIT_USAGE
    result = load(path)
    _print_diagnostics(result, args.matrix)
    if _file_unreadable(result):
        return EXIT_USAGE
    if result.matrix is None:
        print(f"{args.matrix}: матрица не принята — {_summary(result)}; файлы не записаны", file=sys.stderr)
        return EXIT_FAIL
    if args.strict and result.warnings:
        print(f"{args.matrix}: --strict и предупреждений {len(result.warnings)}; файлы не записаны", file=sys.stderr)
        return EXIT_FAIL
    try:
        outputs = build_outputs(result.matrix)
        # блок функций безопасности в рукописном docs/SRS.md (между маркерами cemgen:sif)
        files = {**outputs.files, **spliced_docs(root, result.matrix)}
    except GenerationError as exc:
        print(f"cemgen: ошибка генерации: {exc}; файлы не записаны", file=sys.stderr)
        return EXIT_FAIL
    if args.check:
        diff = compare(root, files)
        if diff.clean:
            print(f"cemgen: сгенерированное совпадает с матрицей ({len(files)} файлов)")
            return EXIT_OK
        for line in diff.lines():
            print(line)
        print(
            f"cemgen: расхождений {len(diff.changed) + len(diff.new) + len(diff.extra)} — запустите "
            f"python -m cemgen generate {args.matrix}",
            file=sys.stderr,
        )
        return EXIT_FAIL
    try:
        diff = apply(root, files)
    except OSError as exc:
        print(f"cemgen: ошибка записи: {exc}", file=sys.stderr)
        return EXIT_USAGE
    unchanged = len(files) - len(diff.changed) - len(diff.new)
    for line in diff.lines():
        print(line)
    print(
        f"cemgen: файлов {len(files)} — новых {len(diff.new)}, изменено {len(diff.changed)}, удалено "
        f"{len(diff.extra)}, без изменений {unchanged}; тестов по матрице {len(outputs.cases)}"
    )
    return EXIT_OK


def cmd_convert(args: argparse.Namespace) -> int:
    try:
        convert(Path(args.src), Path(args.dst))
    except MatrixFileError as exc:
        print(exc.diagnostic.format(args.src), file=sys.stderr)
        return EXIT_USAGE if exc.diagnostic.code == "CEM-E001" else EXIT_FAIL
    except (OSError, ValueError) as exc:
        print(f"cemgen: {exc}", file=sys.stderr)
        return EXIT_USAGE
    print(f"cemgen: {args.src} → {args.dst}")
    return EXIT_OK


def cmd_fat_report(args: argparse.Namespace) -> int:
    result = load(Path(args.matrix))
    _print_diagnostics(result, args.matrix)
    if _file_unreadable(result):
        return EXIT_USAGE
    if result.matrix is None:
        return EXIT_FAIL
    results_path = Path(args.results)
    try:
        cases = fat.load_results(results_path)
    except (OSError, ValueError) as exc:
        print(f"cemgen: результаты тестов не читаются: {results_path}: {exc}", file=sys.stderr)
        return EXIT_USAGE
    matrix = result.matrix
    steps = fat.step_results(matrix, cases)
    info = HeaderInfo.of(matrix)
    lines = info.generated_lines()
    lines[1] = "  python -m cemgen fat-report <файл матрицы> --results build/test-results.json"
    started = fat.results_started(results_path)
    run = f", прогон {started}" if started else ""
    lines.append(f"Результаты: {results_path.name}{run}, тестов {len(cases)}")
    header = "<!-- " + "\n     ".join(lines) + " -->\n"
    text = fat.render(matrix, header, steps)
    out = Path(args.out)
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(text.encode("utf-8"))
    except OSError as exc:
        print(f"cemgen: ошибка записи: {exc}", file=sys.stderr)
        return EXIT_USAGE
    failed = [c for c in cases if c.status == "FAIL"]
    passed = len([c for c in cases if c.status == "PASS"])
    print(f"cemgen: {out} — тестов {len(cases)}, пройдено {passed}, упало {len(failed)}")
    return EXIT_FAIL if failed else EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cemgen",
        description="Генератор логики ПАЗ по матрице причин и следствий (формат cem/1): проверка матрицы, "
        "конфигурация ST, тесты coUnit, документы. Код демонстрационный и не предназначен для систем "
        "безопасности.",
    )
    parser.add_argument("--version", action="version", version=f"cemgen {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("validate", help="проверить матрицу (правила CEM-Exxx, CEM-Wxxx)")
    p.add_argument("matrix", help="файл матрицы .csv или .xlsx")
    p.add_argument("--strict", action="store_true", help="предупреждения — тоже ошибка (код 1)")
    p.add_argument("--json", action="store_true", help="результат в JSON на stdout")
    p.set_defaults(func=cmd_validate)
    p = sub.add_parser("generate", help="сгенерировать ST, тесты и документы")
    p.add_argument("matrix", help="файл матрицы .csv или .xlsx")
    p.add_argument("--root", default=".", help="корень репозитория (по умолчанию текущий каталог)")
    p.add_argument("--check", action="store_true", help="ничего не писать: показать расхождения, код 1")
    p.add_argument("--strict", action="store_true", help="не писать файлы, если есть предупреждения")
    p.set_defaults(func=cmd_generate)
    p = sub.add_parser("convert", help="CSV ↔ XLSX (лист CEM, все ячейки текстом)")
    p.add_argument("src")
    p.add_argument("dst")
    p.set_defaults(func=cmd_convert)
    p = sub.add_parser("fat-report", help="отчёт FAT по результатам cds.py test")
    p.add_argument("matrix", help="файл матрицы .csv или .xlsx")
    p.add_argument("--results", default="build/test-results.json", help="результаты cds.py test")
    p.add_argument("--out", default="docs/FAT_REPORT.md", help="файл отчёта")
    p.set_defaults(func=cmd_fat_report)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:  # argparse: --help — 0, ошибка аргументов — 2
        return int(exc.code) if isinstance(exc.code, int) else EXIT_USAGE
    code: int = args.func(args)
    return code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
