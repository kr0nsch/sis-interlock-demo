"""Прогон демо-сценария срабатывания ПАЗ в CODESYS Control Win и запись трассировки в CSV.

Демо-проект собирается во временном каталоге build/demo-trip/: копия src/ плюс программа
PRG_TripDemo и буфер GVL_TripTrace из tools_project/demo/st/ (в библиотеку и приложение они не
входят). Задача MainTask (20 мс) вызывает PRG_TripDemo вместо PRG_Main: та задаёт входы простой
моделью давления и вызывает неизменённую PRG_Sis. Сценарий идёт в реальном времени задачи ~46 с,
затем буфер читается (шаг trace — tools_project/demo/cds_trace_step.py) и пишется в CSV.

Запуск (Windows, CODESYS 3.5.17.30, библиотека PL установлена — как для cds.py test):
    python tools_project/demo/trip_trace.py [--out build/demo-trip/trip-trace.csv]

Берёт те же блокировки, что cds.py test (репозиторий и общий рантайм), и тот же рантайм.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEMO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "codesys"))

from cdshost import cli  # noqa: E402

STAGE = REPO_ROOT / "build" / "demo-trip"
PROJECT_NAME = "sis-interlock-demo-trip"
TASK = {"name": "MainTask", "interval_ms": 20, "pous": ["PRG_TripDemo"]}
TRACE_TIMEOUT_S = 180

# Колонки CSV: поле GVL_TripTrace -> заголовок
COLUMNS = {
    "arT_s": "t_s",
    "arPA_MPa": "pt101a_mpa",
    "arPB_MPa": "pt101b_mpa",
    "arPC_mA": "pt101c_ma",
    "aiArchPshh": "arch_pshh101",
    "aiArchPsll": "arch_psll101",
    "aiChStateC": "ch3_state_pshh101",
    "awCausePresent": "cause_present",
    "awCauseActive": "cause_active",
    "awCauseLatched": "cause_latched",
    "awEffectTripped": "effect_tripped",
    "auiFirstOut": "first_out",
    "awFirstOutMask": "first_out_mask",
    "axResetPermitted": "reset_permitted",
    "auiResetBlocker": "reset_blocker",
    "axResetButton": "hs120",
    "awOutputs": "outputs",
}


def stage_sources() -> Path:
    """build/demo-trip/src = src/ + демо-объекты (папка Demo в проекте)."""
    src = STAGE / "src"
    if src.exists():
        shutil.rmtree(src)
    shutil.copytree(REPO_ROOT / "src", src)
    st = DEMO_DIR / "st"
    for kind in ("GVLs", "POUs"):
        shutil.copytree(st / kind, src / kind / "Demo")
    return STAGE


def build_steps(settings: cli.Settings, stage: Path) -> list[dict[str, Any]]:
    project = stage / f"{PROJECT_NAME}.project"
    imp = cli.import_step(settings, False, project, clean=True, log_dir=stage, name="import")
    imp["repo_root"] = str(stage)
    imp["mode_config"] = dict(imp["mode_config"], tasks=[TASK])
    build = cli.build_step(settings, project)
    build["log"] = str(stage / "build.log")
    build["report"] = str(stage / "build.json")
    test = cli.test_step(settings, project)
    trace = {
        "action": "trace",
        "project": str(project),
        "credentials": test["credentials"],
        "runtime": test["runtime"],
        "timeout_s": TRACE_TIMEOUT_S,
        "meta": dict(test["meta"], task=TASK),
        "log": str(stage / "trace.log"),
        "out": str(stage / "trace.json"),
    }
    return [imp, build, trace]


def write_csv(trace: dict[str, Any], out: Path) -> int:
    fields = trace["fields"]
    count = int(trace["count"])
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as handle:
        w = csv.writer(handle, lineterminator="\n")
        w.writerow(list(COLUMNS.values()))
        for i in range(count):
            row: list[Any] = []
            for name in COLUMNS:
                v = fields[name][i]
                if isinstance(v, bool):
                    row.append(int(v))
                elif isinstance(v, float):
                    row.append(round(v, 4))
                else:
                    row.append(v)
            w.writerow(row)
    return count


def main(argv: list[str] | None = None) -> int:
    # Вывод по-русски — в UTF-8 и в канал (pipe), и в консоль со старой кодовой страницей
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Демо-сценарий срабатывания ПАЗ в Control Win -> CSV")
    ap.add_argument("--out", type=Path, default=STAGE / "trip-trace.csv")
    args = ap.parse_args(argv)
    settings = cli.make_settings(REPO_ROOT)
    stage = stage_sources()
    with (
        cli.repo_lock(settings, "demo-trip"),
        cli.runtime_lock(settings, f"demo-trip {REPO_ROOT.name}"),
    ):
        cli.ensure_runtime(settings)
        job = {"steps": build_steps(settings, stage), "sys_path": [str(cli.TOOLS_CODESYS), str(DEMO_DIR)]}
        result = cli.run_codesys(settings, str(DEMO_DIR / "cds_trace_step.py"), job, "demo-trip", TRACE_TIMEOUT_S + 600)
    for step in result.get("steps", []):
        print(f"[demo] {step.get('action')}: {'OK' if step.get('ok') else 'ошибка'} {step.get('error') or ''}".rstrip())
    if not result.get("ok"):
        return 1
    trace = json.loads((stage / "trace.json").read_text(encoding="utf-8"))
    n = write_csv(trace, args.out)
    print(f"[demo] отсчётов {n}: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
