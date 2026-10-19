# -*- coding: utf-8 -*-
# mypy: ignore-errors
# ruff: noqa: UP009, UP010, UP020, UP031, UP035
"""Шаг trace: прогон демо-сценария PRG_TripDemo в CODESYS Control Win и чтение GVL_TripTrace.

Скрипт CODESYS Scripting (IronPython 2.7, общее подмножество с Python 3 — как tools/codesys/*.py),
поэтому mypy его не проверяет. Запускает его только tools_project/demo/trip_trace.py: задание из
трёх шагов в одном процессе CODESYS — import (исходники демо-проекта), build, trace. Шаги import и
build — общие скрипты tools/codesys; вход в рантайм — функции run_tests.py (шлюз, учётные данные,
создание первого пользователя), как у cds.py test.

Шаг trace: вход и загрузка приложения, старт, ожидание GVL_TripTrace.xDone (сценарий идёт в
реальном времени задачи), чтение отсчётов пачками read_values, стоп и выход. Результат — JSON
step["out"]: по массиву значений на поле.
"""

from __future__ import absolute_import, print_function, unicode_literals

import io
import json
import os
import sys
import time

MYPY = False
if MYPY:  # pragma: no cover
    from typing import Any, Dict, List  # noqa: F401

# Поля GVL_TripTrace в порядке чтения
FIELDS = (
    "arT_s",
    "arPA_MPa",
    "arPB_MPa",
    "arPC_mA",
    "aiArchPshh",
    "aiArchPsll",
    "aiChStateC",
    "awCausePresent",
    "awCauseActive",
    "awCauseLatched",
    "awEffectTripped",
    "auiFirstOut",
    "awFirstOutMask",
    "axResetPermitted",
    "auiResetBlocker",
    "axResetButton",
    "awOutputs",
)
GVL = "GVL_TripTrace"
BATCH = 120  # выражений в одном read_values


def _setup_path():
    # type: () -> None
    """Каталоги tools/codesys и этого скрипта — в sys.path (пути пишет trip_trace.py в задание)."""
    job_path = os.environ.get("CDS_JOB")
    if not job_path:
        return
    with io.open(job_path, "r", encoding="utf-8") as handle:
        job = json.loads(handle.read())
    for path in job.get("sys_path") or []:
        if path not in sys.path:
            sys.path.insert(0, path)


_setup_path()


def read_trace(reader, count):
    # type: (Any, int) -> Dict[str, List[Any]]
    data = {}  # type: Dict[str, List[Any]]
    for field in FIELDS:
        exprs = ["%s.%s[%d]" % (GVL, field, i) for i in range(1, count + 1)]
        values = []  # type: List[Any]
        for k in range(0, len(exprs), BATCH):
            values.extend(reader.values(exprs[k : k + BATCH]))
        data[field] = values
    return data


def run(ctx, step):
    # type: (Any, Dict[str, Any]) -> Dict[str, Any]
    C = __import__("cds_common")
    T = __import__("run_tests")
    log = C.Log(step.get("log"))
    se = C.api()
    oa = None
    try:
        timeout_s = float(step.get("timeout_s") or 120)
        creds = T.read_credentials(step["credentials"])
        proj, _ = ctx.open_project(step["project"], create=False, log=log)
        app = C.application(proj)
        dev = C.find_device(proj)
        if dev is None:
            raise C.StepError("в проекте нет устройства")
        target = T.setup_gateway(dev, step.get("runtime") or {}, log)
        log.info("вход в рантайм и загрузка демо-приложения")
        oa = T.login(app, dev, creds, target, log)
        oa.start()
        started = time.time()
        log.info("приложение запущено, ожидание %s.xDone" % GVL)
        reader = T.Reader(oa, log)
        done = False
        while time.time() - started < timeout_s:
            se.system.delay(500)
            if reader.value(GVL + ".xDone") is True:
                done = True
                break
        waited = round(time.time() - started, 1)
        if not done:
            raise C.StepError("сценарий не завершился за %s с (%s.xDone != TRUE)" % (timeout_s, GVL))
        count = int(reader.value(GVL + ".uiCount") or 0)
        log.info("сценарий завершён за %s с, отсчётов %d" % (waited, count))
        read_started = time.time()
        data = read_trace(reader, count)
        log.info("прочитано за %.1f с" % (time.time() - read_started))
        result = {
            "schema": 1,
            "captured": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "project": step.get("project"),
            "count": count,
            "wait_s": waited,
            "meta": step.get("meta") or {},
            "fields": data,
        }
        C.write_json(step["out"], result)
        return {"ok": True, "count": count, "out": step["out"]}
    except Exception as exc:
        log.error("%s" % exc)
        raise
    finally:
        if oa is not None:
            try:
                oa.stop()
                log.info("приложение остановлено")
            except Exception as exc:
                log.warn("stop: %s" % exc)
            try:
                oa.logout()
                log.info("выход из рантайма")
            except Exception as exc:
                log.warn("logout: %s" % exc)
        log.close()


if __name__ == "__main__":
    _C = __import__("cds_common")
    _C.ACTION_MODULES["trace"] = "cds_trace_step"
    _C.run_main("trace")
