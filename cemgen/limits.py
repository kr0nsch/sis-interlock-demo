"""Пределы и константы контракта, которые генератору нужны на стороне Python.

Значения ``SIS_*``, ``VOTE_CFG_*``, ``CEM_CFG_*`` и CRC повторяют ``src/GVLs/GVL_Const.gvl.st``
(DESIGN.md, 4.3). Тест ``pytests/test_limits.py`` сверяет их с текстом GVL разбором строк
``ИМЯ : ТИП := ЗНАЧЕНИЕ;`` — расхождение ловится до генерации. Константы NE 43 повторяют
``PL.GVL_Const`` библиотеки plc-process-lib (её контракт, 5.1; сверить с NAMUR NE 43).
Длительности — в миллисекундах (тип ``TIME``).
"""

from __future__ import annotations

# --- DESIGN.md, 4.3: размеры -------------------------------------------------------------
SIS_CAUSES_MAX = 16
SIS_EFFECTS_MAX = 16
SIS_VOTE_CH_MAX = 3
SIS_LOG_SIZE = 64

# --- пределы длительностей, мс -------------------------------------------------------------
SIS_DELAY_MAX_MS = 10 * 60 * 1000  # T#10M: задержка причины и задержка рассогласования
SIS_OVERRIDE_MAX_MS = 2 * 60 * 60 * 1000  # T#2H: пусковой обход
SIS_BYPASS_MAX_MS = 12 * 60 * 60 * 1000  # T#12H: байпас канала

# --- коды первопричины -----------------------------------------------------------------------
SIS_FIRST_OUT_NONE = 0
SIS_FIRST_OUT_START = 0xFFFE
SIS_FIRST_OUT_CFG = 0xFFFF

# --- CRC-16/CCITT-FALSE ------------------------------------------------------------------------
CRC16_INIT = 0xFFFF
CRC16_POLY = 0x1021

# --- биты ошибок конфигурации --------------------------------------------------------------
VOTE_CFG_ARCH = 0x0001
VOTE_CFG_POLICY = 0x0002
VOTE_CFG_INPUT = 0x0004
VOTE_CFG_LIMIT = 0x0008
VOTE_CFG_DISCREPANCY = 0x0010
VOTE_CFG_BYPASS = 0x0020

CEM_CFG_COUNT = 0x0001
CEM_CFG_CAUSE = 0x0002
CEM_CFG_EFFECT = 0x0004
CEM_CFG_CRC = 0x0008

# --- NE 43 и шкала 4–20 мА (PL.GVL_Const; сверить с NAMUR NE 43) ---------------------------
NE43_FAIL_LOW_MA = 3.6  # I <= — отказ (обрыв)
NE43_MEAS_LOW_MA = 3.8  # I < — вне диапазона снизу (ещё достоверно)
NE43_MEAS_HIGH_MA = 20.5  # I > — вне диапазона сверху (ещё достоверно)
NE43_FAIL_HIGH_MA = 21.0  # I >= — отказ (замыкание)
MA_ZERO = 4.0
MA_SPAN = 16.0
REAL_SANE_MAX = 1.0e30  # |x| больше — мусор (PL.F_IsFinite)

# --- стимулы и параметры сгенерированных тестов (DESIGN.md, 12.2, 12.4) -------------------
STIM_INVALID_MA = 2.0  # недостоверность аналогового канала — обрыв
STIM_MIN_SHIFT_FRACTION = 0.01  # требование: уставка ± max(hyst, 1 % шкалы)
TT_AI_LIMIT = 50.0  # таблицы уровня 2: уставка
TT_AI_DEMAND = 60.0  # таблицы уровня 2: значение «требование»
TT_AI_NORMAL = 40.0  # таблицы уровня 2: значение «норма»
TT_BYPASS_MAX_MS = 60 * 60 * 1000  # таблицы уровня 2: tBypassMax = T#1H
RUN_STEP_DIVISOR = 50  # шаг перехода к T - Δ — не крупнее T/50
RUN_MAX_ITERATIONS = 100  # итераций на один вызов Run в сгенерированном тесте
HARNESS_MAX_ITERATIONS = 1500  # предел Run стенда FB_SisHarness
TESTS_PER_SUITE_MAX = 40  # тестов в наборе FB_CemGenNN_Test

# --- значения по умолчанию формата cem/1 (DESIGN.md, 9.2) -------------------------------------
DEFAULT_TEST_STEP_MS = 100
DEFAULT_DISCREPANCY_DELAY_MS = 5000

ST_LINE_MAX = 120  # STL003
