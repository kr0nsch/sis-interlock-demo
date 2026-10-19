# Статический анализ

Находки `iec_checker` по `build/assembled/` (и `st_lint` по `src/`, `tests/`), которые не
исправлены в коде, — с обоснованием. Исправленные находки сюда не пишутся. Здесь же — итог
проверки компиляции RuSTy.

## Как запускается

| Инструмент | Где | Вход | Отчёт |
|---|---|---|---|
| `tools/check/st_lint.py --strict` | локально и в CI | `src/`, `tests/` | вывод в консоль, код выхода ≠ 0 при нарушениях |
| `tools/check/run_iec_checker.py --tests` | локально и в CI (обязательно): бинарник iec_checker v0.4 из релизов github.com/jubnzv/iec-checker | `build/assembled/iec-checker/` (вариант сборки `iec-checker`) | `build/iec_checker.json`, `build/iec_checker.md` |
| то же с `--docker` | CI, необязательное задание: образ `jubnzv1/iec-checker:nightly`, закреплённый по дайджесту в `ci.yml` | то же | то же, артефакт `iec-checker-nightly-reports` |
| `tools/check/run_rusty.py` | локально и в CI (необязательное задание): RuSTy `plc --check` | `build/assembled/rusty/` (вариант сборки `rusty`, `src/` и `tests/`) | `build/rusty.log`, `build/rusty.json` |

Обоснования в `tools/check/iec_checker_allow.toml` подобраны под находки v0.4 — той же версии, что в
обязательном шаге CI. Образ `nightly` разбирает больше конструкций и может находить иначе: если
находка есть только в одной версии — укажите это в столбце «решение». Интеграционный тест
`tools/tests/test_run_iec_checker.py::test_integration_repository_sources` проверяет, что каждое
обоснование используется: после правок примера уберите устаревшие записи.

## Последний прогон

Весь репозиторий после интеграции и ревизии функциональной безопасности (логика ПАЗ с обработкой неисправности источника времени, DESIGN.md 1.1.0; `PRG_Main` по 8.4; сгенерированный по матрице код и тесты), 16.10.2026, Windows, локально; повторно — 19.10.2026 после автоснятия пускового обхода (DESIGN.md 1.2.0, R-12).

| Дата | Инструмент | Вход | Итог |
|---|---|---|---|
| 2026-10-19 | `st_lint --strict` | `src/`, `tests/` (747 файлов) | 0 ошибок, 0 предупреждений |
| 2026-10-19 | `run_iec_checker.py` (iec_checker 0.4) | 50 объектов `src/` | ошибок разбора нет; необоснованных 0; обоснованных 300; артефактов сборки 15 (CP3) |
| 2026-10-19 | `run_iec_checker.py --tests` (iec_checker 0.4) | 81 объект `src/` и `tests/` | ошибок разбора нет; необоснованных 0; обоснованных 2195; артефактов сборки 290 |
| 2026-10-19 | `run_rusty.py` (RuSTy 1.0.6, `plc --check`) | 47 файлов `build/assembled/rusty/`, исключено 35 (`rusty_exclude.txt`) | 0 ошибок; предупреждения E049 и E040, как раньше |
| 2026-10-16 | `st_lint --strict` | `src/`, `tests/` (711 файлов) | 0 ошибок, 0 предупреждений |
| 2026-10-16 | `run_iec_checker.py` (iec_checker 0.4) | 50 объектов `src/` | ошибок разбора нет; необоснованных 0; обоснованных 296; артефактов сборки 15 (CP3) |
| 2026-10-16 | `run_iec_checker.py --tests` (iec_checker 0.4) | 80 объектов `src/` и `tests/` | ошибок разбора нет; необоснованных 0; обоснованных 2104; артефактов сборки 266 |
| 2026-10-16 | `run_rusty.py` (RuSTy 1.0.6, `plc --check`) | 47 файлов `build/assembled/rusty/`, исключено 34 (`rusty_exclude.txt`) | 0 ошибок; предупреждения E049 (чтение переменных стендов тестами) и E040 (`E_SafeState.Off`) |
| — | iec_checker 0.4 (CI, Linux) | то же | _перенести из отчёта CI_ |

Пространство имён `PL.` iec_checker 0.4 после понижения разбирает: `--strip-namespace PL` не нужен
(DESIGN.md, P-06; docs/ASSUMPTIONS.md).

## Логика ПАЗ (`src/POUs/Sis/`, `PRG_Main`) — команда A

Находки по коду команды A (`run_iec_checker.py`, только `src/`, 19.10.2026): CP3 — 185, L17 — 57 (56 в
`src/POUs/Sis/`, 1 в `PRG_Main`), CP9 — 12, UnusedVariable — 20; артефактов сборки 15. Прирост после
ревизии (CP3 +4, L17 +5) — новые ветви обработки «времени назад» в `FB_Voting` и `FB_CauseEffect` (D-19);
затем (CP3 +2, L17 +1, UnusedVariable +1) — автоснятие пускового обхода: таймеры подтверждения нормы
`afbOvrClear` и ветвь снятия в `FB_CauseEffect`, проверка `tOverrideClear` в `F_CemCheckCfg` (R-12, D-20).

| Правило | Файл | Находка | Решение / обоснование |
|---|---|---|---|
| PLCOPEN-CP3 | все POU `src/` | «Variable … shall be initialized before being used» | Обосновано общей записью: переменная без явного начального значения получает значение по умолчанию своего типа (МЭК 61131-3, CODESYS); вариант сборки `iec-checker` убирает неконстантные начальные значения (`:= E_VoteArch.None`, `:= [3(TRUE)]`) |
| PLCOPEN-CP9 | `FB_Voting`, `FB_CauseEffect`, `FB_SisUnit`, `F_VoteEval`, `F_VoteCheckCfg`, `F_CemCheckCfg` | «Code is too complex» (iec_checker: 233, 292, 24, 54, 31, 36 по McCabe) | Обосновано. Тела — нормативная последовательность шагов контракта (5.2, 5.5, 5.9, 6.3, 6.8, 8.1) с номерами шагов в комментариях; порядок шагов задаёт порядок событий журнала, и деление на методы его спрятало бы (у `FB_Voting` методов по 5.4 нет). Классическая цикломатическая сложность (точки ветвления `IF`/`ELSIF`/`FOR`/`WHILE`/метки `CASE` + 1, без логических операций): `FB_CauseEffect` — 57, `FB_Voting` — 45, `F_VoteEval` — 14, `F_CemCheckCfg` — 11, `F_VoteCheckCfg` — 9, `FB_SisUnit` — 5. Поведение покрыто граничными тестами (раздел 12.3) и исчерпывающими таблицами истинности `F_VoteEval` и `FB_Voting` |
| PLCOPEN-L17 | `src/POUs/Sis/*` (56) | «Each IF instruction should have an ELSE clause» | Обосновано: у условий нет действия «иначе» — событие по смене состояния, бит ошибки конфигурации, счётчик, поиск младшего бита, реакция на «время назад». Пустая ветвь `ELSE` только добавила бы шум (как в plc-process-lib) |
| PLCOPEN-L17 | `PRG_Main` (1) | то же | Обосновано: нормальные значения входов ставятся только в первом цикле демо без ввода-вывода (DESIGN.md, 8.4) — действия «иначе» нет |
| UnusedVariable | `FB_Voting` (`afbBypass`, `fbDisc`, `stIn`, `stCmd`, `stSts`), `FB_CauseEffect` (`afbDelay`, `afbOverride`, `afbOvrClear`, `stCmd`, `stSts`), `FB_SisUnit` (`afbVote`, `fbCem`), `F_VoteCheckCfg`, `F_CemCrc` (`stCfg`) | «Found unused local variable» | Ложное срабатывание iec_checker 0.4: экземпляры ФБ используются вызовом (`fbDisc(...)`, `afbBypass[k](...)`) и чтением выходов, структуры — обращением к полям; это он не считает использованием |
| UnusedVariable | `FB_SisEventLog` (`astRing`, `uiNext`, `uiUsed`, `udiSeq`) | то же | Переменные журнала используются только в методах и свойствах, которые понижение выносит в отдельные функции; тело ФБ пустое |
| UnusedVariable | `F_SisCrc16Byte` (`bData`), `F_VoteEval` (`eArch`) | то же | Ложное срабатывание: `bData` — аргумент вложенного вызова `SHL(BYTE_TO_WORD(bData), …)`; `eArch` передаётся как `F_VoteArchChannels(eArch := eArch)` — присваивание формальному параметру с тем же именем iec_checker принимает за сам параметр |

### Тесты команды A (`tests/POUs/Suites/`, `Helpers/`, `TruthTables/`)

| Правило | Файл | Находка | Решение / обоснование |
|---|---|---|---|
| UnusedVariable | наборы `tests/POUs/Suites/*`: `fbRig` (стенды), `fbVote`, `fbCem`, `stCfg`, `uBad`, `uBits`, `wMask` и т. п. | «Found unused local variable» | Ложное срабатывание iec_checker 0.4: стенд используется вызовом методов и чтением выходов (`fbRig.Cycle()`, `fbRig.fbVote.xTrip`), объединения — полями (`uBad.ePolicy`), `wMask` — аргументом `SIZEOF` |
| UnusedVariable | стенды `FB_VotingRig`, `FB_CemRig`, `FB_UnitRig` | то же | Переменные стендов используются только в их методах (понижение выносит методы в функции); `uiCh`, `uiEffect` — индексы массивов, переменные индексов iec_checker 0.4 использованием не считает |
| UnusedVariable | таблицы истинности `tests/POUs/TruthTables/*` | то же | Сгенерированные тесты: стенд `fbRig` используется вызовом методов (`fbRig.EvalRow(...)`), переменные `FB_VoteTableRig` — в его методах |
| PLCOPEN-L17 | `FB_SisTestLog`, `FB_VoteTableRig` | «Each IF instruction should have an ELSE clause» | Обосновано: поиск по виду события и сборка байта по битам — действия «иначе» нет |
| PLCOPEN-CP9 | наборы тестов | «Code is too complex» | Обосновано общей записью шаблона: методы-тесты — последовательности вызовов и проверок (у таблиц истинности — 512 строк без ветвлений); метрика для тестов не показательна |
| PLCOPEN-CP3 | тесты | как выше | Обосновано, как для `src/` |

### Сгенерированный код (`src/**/Generated/`, `tests/**/Generated/`) и стенд `FB_SisHarness` — команда B

`st_lint --strict` — 0 находок. iec_checker 0.4 (`run_iec_checker.py --tests`, без `--strip-namespace PL`):
ошибок разбора 0, необоснованных находок 0; обоснования — раздел «Сгенерированный код (cemgen)» в конце
`tools/check/iec_checker_allow.toml`. Генератор сам избегает находок, где это не портит код: сравнение строк
таблиц истинности — без `IF` (через `SEL`), сообщение ассерта собирается из временных переменных.

| Правило | Файл | Находка | Решение / обоснование |
|---|---|---|---|
| UnusedVariable | `FB_CemGen*_Test` (`fbH001`…`fbH040`) | «Found unused local variable» | Экземпляры стенда — по одному на тест — используются в методах-тестах; понижение выносит методы в функции, и в теле набора экземпляр не виден |
| UnusedVariable | `FB_SisHarness` (`stIo`, `stCmd`, `fbTime`, `fbLog`, `fbApp`, `udiMark`, `RUN_MAX_ITERATIONS`) | то же | Переменные стенда используются только в его методах; `stIo` и `stCmd` пишут тесты по имени экземпляра (они во `VAR_INPUT`, ASSUMPTIONS B-01) |
| UnusedVariable | методы `FB_VoteTruth_Test` (`fbVote`, `stRes`, `stSts`, `stIn`, `stCmd`, `uiRow`) | то же | Ложное срабатывание: вызов экземпляра `fbVote(...)` и чтение выходов, обращения к полям структур, аргументы вложенных вызовов (`SHR(uiRow, …)`, `UINT_TO_STRING(uiRow)`) iec_checker 0.4 использованием не считает |
| UnusedVariable | `FB_SisApp`, `F_SisIoNormal`, `F_SisIoKeys` (`stIo`), `FB_SisApp` (`fbUnit`) | то же | Ложное срабатывание: `VAR_IN_OUT stIo` используется обращениями к полям, `fbUnit` — вызовом и чтением выходов |
| PLCOPEN-CP9 | `FB_SisApp` (102 оператора), `F_SisIoNormal` (29) | «Code is too complex» | Сгенерированная привязка и нормальные значения — линейная последовательность присваиваний без ветвлений (классическая сложность 1); число операторов растёт с числом каналов матрицы |
| PLCOPEN-CP3, CP9 | сгенерированные тесты | как у тестов команды A | Общие записи для `tests/*` |

## RuSTy (`plc --check`)

Компилятор RuSTy 1.0.6 проверяет синтаксис и типы варианта сборки `rusty` (`src/` и `tests/`); компоновки
нет. Пространства имён `coUnit.`/`CfUnit.` убираются, объявления coUnit и блоков CODESYS Standard берутся
из прокладок `tools/check/rusty_shims/` шаблона. Объявлений plc-process-lib (пространство `PL`) для RuSTy
нет, поэтому файлы с `PL.*` и файлы, которые объявляют экземпляры таких ФБ, исключены
(`tools/check/rusty_exclude.txt`, с причиной у каждого; DESIGN.md, 12.8). RuSTy проверяет то, что от
библиотеки не зависит: типы, `GVL_Const`, `I_SisEventSink`, `F_VoteEval` и функции схем, функции битов и
CRC, `F_CemCheckCfg`, `F_SisLogEvent`, `FB_SisEventLog` и их тесты — 0 ошибок. Ожидаемые предупреждения:
E049 (тесты читают переменные стендов и журнала по имени, как в CODESYS), E040 «Non-standard enum value
`E_SafeState.Off`» (имя `Off` есть и в `E_BypassState`; в CODESYS перечисления `qualified_only` и
`strict`, конфликта нет). Компиляция всех объектов — `cds.py check --tests` (CODESYS 3.5.17.30).

### RuSTy: сгенерированный код (команда B)

Без объявлений `PL` в репозитории исключены файлы, которые объявляют `PL.*` или зависят от исключённых
(раздел «Сгенерированный код» в `tools/check/rusty_exclude.txt`): `GVL_Sis`, `FB_SisApp`, `PRG_Sis`,
`FB_SisHarness`, `FB_VoteTruth_Test`, `FB_CemGen01_Test` … `FB_CemGen03_Test`, `GVL_TestsGenerated`
(новый набор сценариев по матрице добавляется в `rusty_exclude.txt` вместе с ним).
Остальное (`ST_SisIo`, `GVL_SisCfg`, `GVL_SisIo`, `F_SisIoNormal`, `F_SisIoKeys`, `GVL_VoteTruthTable`) RuSTy
проверяет — 0 ошибок. Отдельно, с локальной прокладкой `PL` (объявления `I_TimeSource`, `FB_SystemTime`,
`FB_FakeTime`, `FB_Delay`, `F_IsFinite`, констант NE 43) и `--strip-namespace PL`, весь сгенерированный код и
стенд проходят `plc --check`, кроме двух E031 в `FB_SisApp`: константы `GVL_SisCfg.CEM_CFG`/`VOTE_CFG` во
`VAR_IN_OUT CONSTANT` `FB_SisUnit` — после замены R13 это `VAR_IN_OUT`, а RuSTy требует переменную с
правом записи (ограничение RuSTy; в CODESYS так и задумано, 10.5). Прогон 16.10.2026.

## Ограничения разборщика

Конструкции CODESYS, которые iec_checker 0.4 не разбирает, — и что с ними делает вариант сборки
`iec-checker` (подробно — [LAYOUT.md](LAYOUT.md#собранный-текст-buildassembled) и `tools/README.md`):

| Конструкция | Где | Как обходится |
|---|---|---|
| метки `CASE` вида `E_VoteArch.Vote1oo1` | `F_VoteArchChannels`, `F_VoteEval`, `FB_Voting` | сборка заменяет метки целыми значениями перечисления |
| неконстантные начальные значения (`:= E_VoteArch.None`, `:= [3(TRUE)]`, `:= T#0S` в `STRUCT`) | DUT `src/DUTs/Sis/`, `FB_Voting` | сборка убирает начальное значение (отсюда часть находок CP3) |
| `VAR_GLOBAL` вне `CONFIGURATION`, прагмы `{attribute …}` | `GVL_Const`, все DUT | сборка понижает |
| методы и свойства внутри `FUNCTION_BLOCK`, `IMPLEMENTS`, `EXTENDS` | `FB_SisEventLog`, стенды и наборы тестов | сборка выносит методы в функции `<ФБ>__<метод>` — анализ методов приблизительный |
| вызов элемента массива ФБ `afbBypass[k](...)`, поле элемента `stCfg.astCause[i].x` | `FB_Voting`, `FB_CauseEffect`, `FB_SisUnit` | сборка переписывает в `afbBypass(..., k)`; в коде поля элементов копируются в локальные переменные (`stCause := stCfg.astCause[i]`) |
