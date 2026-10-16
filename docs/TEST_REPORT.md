# Отчёт о тестировании

Результаты юнит-тестов CfUnit (coUnit 1.2.0.0) в CODESYS Control Win V3 и проверок без CODESYS.
Запись «проверено в CODESYS» появляется только после реального прогона. Раздел «Последний прогон
в CODESYS» обновляет `python tools/codesys/cds.py report` по итогам `cds.py test`
(`build/test-results.json`); правки внутри него вручную перезаписываются.

<!-- cds:test-report:begin (раздел обновляет `python tools/codesys/cds.py report`) -->
## Последний прогон в CODESYS

Проверено в CODESYS 3.5.17.30 / CODESYS Control Win V3 (пользовательский процесс) — 2026-10-16 07:14:13. Итог: **все тесты пройдены**.

| Параметр | Значение |
|---|---|
| Дата прогона | 2026-10-16 07:14:13 |
| Коммит | 63edb70-dirty |
| CODESYS | 3.5.17.30 (профиль `CODESYS V3.5 SP17 Patch 3`) |
| Устройство в проекте | CODESYS Control Win V3 (4096 / 0000 0001 / 3.5.17.30) |
| Рантайм | CODESYS Control Win V3 (пользовательский процесс) |
| Фреймворк тестов | coUnit (CfUnit) 1.2.0.0 |
| Сборка | ошибок 0, предупреждений 0 |
| Способ запуска | `python tools/codesys/cds.py test` |

| Набор | Тестов | Пройдено | Упало | Пропущено | Итог |
|---|---|---|---|---|---|
| `PRG_Tests.fbF_ClampTest` | 7 | 7 | 0 | 0 | пройдено |
| `PRG_Tests.fbExampleTest` | 11 | 11 | 0 | 0 | пройдено |
| **Всего** | 18 | 18 | 0 | 0 | **пройдено** |

### Результаты тестов

| Набор | Тест | Итог |
|---|---|---|
| `PRG_Tests.fbF_ClampTest` | `InsideRangeReturnsValue` | пройден |
| `PRG_Tests.fbF_ClampTest` | `BelowLowReturnsLow` | пройден |
| `PRG_Tests.fbF_ClampTest` | `AboveHighReturnsHigh` | пройден |
| `PRG_Tests.fbF_ClampTest` | `AtLowBoundaryReturnsLow` | пройден |
| `PRG_Tests.fbF_ClampTest` | `AtHighBoundaryReturnsHigh` | пройден |
| `PRG_Tests.fbF_ClampTest` | `EqualBoundsReturnsBound` | пройден |
| `PRG_Tests.fbF_ClampTest` | `LowGreaterThanHighSwapsBounds` | пройден |
| `PRG_Tests.fbExampleTest` | `AutoSwitchesOnBelowThreshold` | пройден |
| `PRG_Tests.fbExampleTest` | `AutoThresholdsAreInclusive` | пройден |
| `PRG_Tests.fbExampleTest` | `AutoHoldsStateInsideHysteresis` | пройден |
| `PRG_Tests.fbExampleTest` | `InvalidValueLatchesFault` | пройден |
| `PRG_Tests.fbExampleTest` | `AcknowledgeClearsFaultWhenValid` | пройден |
| `PRG_Tests.fbExampleTest` | `AcknowledgeKeepsFaultWhileInvalid` | пройден |
| `PRG_Tests.fbExampleTest` | `ManualFollowsCommand` | пройден |
| `PRG_Tests.fbExampleTest` | `LocalAndOutOfServiceSwitchOff` | пройден |
| `PRG_Tests.fbExampleTest` | `DefaultModeIsOutOfService` | пройден |
| `PRG_Tests.fbExampleTest` | `ParametersAreClamped` | пройден |
| `PRG_Tests.fbExampleTest` | `CountsSwitchOnsAndResetClears` | пройден |

### Упавшие тесты

_Нет._

Машиночитаемые результаты: `build/test-results.json`, `build/junit.xml` (не в git).
<!-- cds:test-report:end -->

## Сборка и полная проверка компиляции в CODESYS

CODESYS 3.5.17.30, профиль `CODESYS V3.5 SP17 Patch 3`, локально, 2026-10-16. `build` компилирует
объекты, достижимые из задач; `check` — все объекты раскладки (docs/MANUAL_STEPS.md, раздел 5).

| Команда | Итог | Примечание |
|---|---|---|
| `cds.py build` | 0 ошибок, 0 предупреждений | ссылки проекта: `#Standard` из `config.json` и плейсхолдеры устройства (`#IoStandard`, `#3SLicense`, `#CAA Device Diagnosis`, `#BreakpointLogging`); повторный импорт — 0 изменений |
| `cds.py check` | 0 ошибок, 0 предупреждений | 8 объектов `src/` (включая `PRG_Main`) |
| `cds.py check --tests` | 0 ошибок, 0 предупреждений | 11 объектов `src/` и `tests/` |
| `cds.py test` | 18 из 18 | раздел выше |
| `cds.py roundtrip` | без диффа (60 файлов), повторный импорт — 0 изменений | — |
| `cds.py library` | 0 ошибок проверки пула | 7 объектов, ссылка библиотеки — `#Standard` |

Проверка самой команды `check` на копии шаблона (вне репозитория): программа без задачи с
`iX := diZ;`, ФБ без экземпляра с ошибкой в методе, неиспользуемый DUT, вспомогательный ФБ в
`tests/` с ошибкой — `build` «0 ошибок» (код 0), `check` / `check --tests` — каждая ошибка с файлом
и строкой раскладки (код 1); после удаления — код 0. GVL с типами библиотек устройства
(`IoStandard.IoConfigConnector`, `DED.DEVICE_STATE`): `build` и `check` — 0 ошибок (ссылки
устройства копируются в пул проверки). Standard в той же копии (TON, R_TRIG, CTU, CONCAT без
пространства имён и с `Standard.`): `build`, `check --tests`, `library` — 0 ошибок, `test` — 19 из
19; без ссылки `standard` — C0077 «Неизвестный тип: 'TON'» (docs/ASSUMPTIONS.md, D37–D39).

## Что проверяют тесты

| Набор | Тест | Что проверяет |
|---|---|---|
| `FB_F_Clamp_Test` | `InsideRangeReturnsValue` | значение внутри диапазона не меняется |
| `FB_F_Clamp_Test` | `BelowLowReturnsLow` | значение ниже диапазона → нижняя граница |
| `FB_F_Clamp_Test` | `AboveHighReturnsHigh` | значение выше диапазона → верхняя граница |
| `FB_F_Clamp_Test` | `AtLowBoundaryReturnsLow` | значение на нижней границе не меняется |
| `FB_F_Clamp_Test` | `AtHighBoundaryReturnsHigh` | значение на верхней границе не меняется |
| `FB_F_Clamp_Test` | `EqualBoundsReturnsBound` | вырожденный диапазон `rLow = rHigh` |
| `FB_F_Clamp_Test` | `LowGreaterThanHighSwapsBounds` | `rLow > rHigh`: границы меняются местами |
| `FB_Example_Test` | `AutoSwitchesOnBelowThreshold` | авторежим: значение ниже порога включения (уставка − гистерезис) включает выход, отказа нет |
| `FB_Example_Test` | `AutoThresholdsAreInclusive` | авторежим: на пороге включения выход включается, на уставке — отключается |
| `FB_Example_Test` | `AutoHoldsStateInsideHysteresis` | авторежим: в зоне гистерезиса выход сохраняет состояние (после включения и после отключения) |
| `FB_Example_Test` | `InvalidValueLatchesFault` | недостоверное измерение в авторежиме: отказ, выход отключён; отказ держится после восстановления измерения |
| `FB_Example_Test` | `AcknowledgeClearsFaultWhenValid` | `Acknowledge()` при достоверном измерении снимает отказ и возвращает TRUE, выход снова управляется |
| `FB_Example_Test` | `AcknowledgeKeepsFaultWhileInvalid` | `Acknowledge()` при недостоверном измерении возвращает FALSE, отказ остаётся |
| `FB_Example_Test` | `ManualFollowsCommand` | ручной режим: выход повторяет `xManualOn`, недостоверное измерение отказа не даёт |
| `FB_Example_Test` | `LocalAndOutOfServiceSwitchOff` | `Local` и `OutOfService` отключают выход при любых измерении и команде |
| `FB_Example_Test` | `DefaultModeIsOutOfService` | режим по умолчанию — `OutOfService`: выход отключён |
| `FB_Example_Test` | `ParametersAreClamped` | уставка и гистерезис вне диапазона ограничиваются `EXAMPLE_SP_MAX_PCT` и `EXAMPLE_HYST_MIN_PCT` |
| `FB_Example_Test` | `CountsSwitchOnsAndResetClears` | счётчик `Count` считает только фронты включения; `Reset()` через `I_Resettable` отключает выход и обнуляет счётчик |

## Проверки без CODESYS

Итоги последнего прогона CI (ссылка на запуск GitHub Actions) или локального прогона.

| Проверка | Итог | Примечание |
|---|---|---|
| `ruff check`, `ruff format --check`, `mypy`, `pytest` | пройдено, 2026-10-16, локально | pytest: все тесты, включая интеграционные с настоящими `plc` и iec_checker |
| `tools/assemble.py` (все варианты, с `--tests` и без) | пройдено, 2026-10-16, локально | 8 объектов `src/` + 3 объекта `tests/` |
| `tools/check/st_lint.py --strict` | пройдено, 2026-10-16, локально | 60 файлов, 0 замечаний |
| iec_checker 0.4 (локально, `run_iec_checker.py --tests`) | пройдено, 2026-10-16 | 11 файлов, ошибок разбора нет; необоснованных находок 0, обоснованных 100 — разбор в [STATIC_ANALYSIS.md](STATIC_ANALYSIS.md) |
| RuSTy 1.0.6 (локально, `run_rusty.py`) | пройдено, 2026-10-16 | 11 файлов (`src/` и `tests/` с прокладкой coUnit), исключений нет, 0 ошибок, 0 предупреждений |
