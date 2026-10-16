# Changelog

Все заметные изменения проекта записываются в этот файл.

Формат — [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/), версии — по
[Semantic Versioning](https://semver.org/lang/ru/spec/v2.0.0.html).

## [Unreleased]

### Added

- Раскладка исходников ST в `src/` и `tests/` и её формальный контракт `docs/LAYOUT.md`.
- Пример: `E_DeviceMode`, `ST_ExampleCmd`, `ST_ExampleSts`, `GVL_Const`, интерфейс `I_Resettable`,
  функция `F_Clamp`, `FB_Example` (метод `Acknowledge`, реализация `Reset`, свойство `Count`), `PRG_Main`.
- Тесты CfUnit (coUnit 1.2.0.0): наборы `FB_F_Clamp_Test` (7 тестов), `FB_Example_Test` (11 тестов:
  пороги и гистерезис, отказ и квитирование, режимы, ограничение параметров, счётчик, сброс через
  `I_Resettable`) и `PRG_Tests`.
- Инструменты: `tools/assemble.py`, `tools/check/` (линтер `st_lint.py`, запуск iec_checker и RuSTy),
  скрипты CODESYS Scripting в `tools/codesys/`.
- `tools/codesys/cds.py` — импорт, сборка, тесты coUnit в CODESYS Control Win V3 (пользовательский
  процесс), экспорт, roundtrip, JUnit и отчёт из консоли; настройки — `tools/codesys/config.json`.
  Проверено в CODESYS 3.5.17.30.
- `cds.py library [--install] [--compiled] [--released]`: библиотека CODESYS из `src/` — `build/<имя>.library`
  (и `.compiled-library`) с Project Information из `config.json: library`, «проверить все объекты пула»
  с ошибками в строках `src/`, установка в репозиторий библиотек; `library --uninstall [--all-versions]`.
  Проверено в CODESYS 3.5.17.30.
- Библиотеки-зависимости портфолио: в `config.json: libraries` — закрепление версии (точная или `*`),
  пространство имён ссылки, плейсхолдер, `install_from` и `build_from_repo`; `cds.py deps [--rebuild]
  [--check]`; `import`/`build`/`test` сами собирают недостающую библиотеку в соседнем репозитории
  (`cds.py library --install` там) и повторяют задание (`--no-deps` — отключить). Найденная библиотека
  проверяется и по её собственным зависимостям (рекурсивно); цикл зависимостей между репозиториями —
  отказ, а не бесконечная цепочка сборок. Ссылки `library.libraries` подключаются и к проектам
  приложения и тестов репозитория-библиотеки. Учёт установок: из какой рабочей копии и коммита
  поставлена версия.
- Разделы `library` и `library_repository` в `tools/codesys/config.json`, глобальная блокировка
  репозитория библиотек; тесты `tools/tests/test_cds_library.py`.
- CI GitHub Actions: ruff, mypy, pytest, сборка ST, линтер (`--strict`), iec_checker v0.4 (закреплён
  по размеру и SHA-256); необязательно — iec_checker `nightly` (образ закреплён по дайджесту) и RuSTy.
- Документы: архитектура, ручные шаги, допущения, отчёты статанализа и тестов, шаблоны ТЗ
  (ГОСТ 34.602-2020) и ПМИ.
- `LICENSE` (MIT), `.gitignore`, `.gitattributes`, `.editorconfig`.
- `cds.py check [--tests]`: компиляция всех объектов `src/` (и `tests/`) — и тех, что не достижимы из
  задач и которые `build` не компилирует (программа без задачи, ФБ без экземпляра, неиспользуемый
  DUT): «Проверить все объекты пула» в проекте без устройства, проект на диск не пишется; ошибки — с
  файлом и строкой, код 1. Библиотеки — те же, что у `build`: ссылки из `config.json` и копии ссылок,
  которые добавляет само устройство (`#IoStandard`, `#CAA Device Diagnosis`, ...). Persistent
  Variables проверяются как GVL. Рекомендуемая полная проверка — `build`, `check --tests`, `test`,
  `roundtrip` (`docs/MANUAL_STEPS.md`, раздел 5). Проверено в CODESYS 3.5.17.30.
- Библиотека Standard по умолчанию: в `config.json` ключ `standard` (плейсхолдер `#Standard`, версию
  задаёт профиль, явные `namespace: Standard` и `qualified_only: false` — доступ и `TON`, и
  `Standard.TON`, как в проекте IDE) в `library.libraries`, то есть во всех режимах, в `check` и в
  библиотеке репозитория. Проверено в CODESYS 3.5.17.30 (TON, R_TRIG, CTU, CONCAT в режимах normal,
  test и library).
- `tools/tests/test_cds_config.py`: `config.json` репозитория проверяется на уровне схемы (разделы и
  ключи — как у эталона `tools/tests/fixtures/config_template.json`, описания режимов, задач и
  библиотек полные и разрешаются).
- Понижение `iec-checker` (`tools/st_flavors.py`) для конструкций CODESYS, которых нет в грамматике
  iec_checker 0.4 (раньше — ParserError): операторы `TIME()`/`LTIME()` (вызов заглушки `CDS__TIME()`,
  `CDS__LTIME()`; литерал длительности давал бы ложные ZeroDivision и PLCOPEN-CP28), константы в границах массивов и длинах строк (`ARRAY[0..GVL_Const.N - 1]`
  → числа по константам GVL, `VAR CONSTANT` и перечислений), поле и вызов элемента массива (`a[i].x` →
  `a.x[i]`, `afb[i](...)` → `afb(..., i)`), несколько индексов, длительности с пропуском единиц
  (`T#1h500ms` → `T#1H0M0S500MS`), пустой оператор `;`, пустые ветви и тела (`CDS__NOP();`), пустые
  `PROGRAM`/`FUNCTION` (`{}`), имена — ключевые слова iec_checker (`Priority` → `Priority_`),
  `WORD#16#FF`, `BOOL#1`, `1E3`, `AND_THEN`/`OR_ELSE`, управляющие слова в нижнем регистре, вложенные
  массивы; целые константные начальные значения подставляются числом. Пример
  `tools/tests/fixtures/lowering/` и эталон `tools/tests/golden/iec-checker-lowering/`; проверено
  бинарником v0.4 и на копиях plc-process-lib и s7-to-codesys (ошибок разбора 0). В псевдониме типа с
  десятичными границами (`TYPE T_Pct : INT(0..100) := 50;`) поддиапазон больше не убирается: iec_checker
  его разбирает и проверяет начальное значение (OutOfBounds).
- `tools/README.md`, «Понижение для iec_checker»: у каждой замены — влияние на находки, в том числе какие
  виды находок она может скрыть (PLCOPEN-N3 у переименованных имён, OutOfBounds у невычисленных границ и
  массивов в `STRUCT`, PLCOPEN-CP13 у рекурсии методов) или добавить; сводная таблица по проверкам
  iec_checker 0.4.
- Пример `tools/tests/fixtures/sourcemap/` с многострочными конструкциями и тесты карты строк после
  понижения: по меткам строк (`test_source_map_multiline_constructs`, все варианты сборки) и по находкам
  настоящего iec_checker (`test_integration_findings_point_to_source_lines`).
- Вариант `rusty`: `VAR_IN_OUT CONSTANT` → `VAR_IN_OUT` (R13); прокладка
  `tools/check/rusty_shims/codesys_conversions.st` — преобразования TIME/LTIME ↔ целые, битовые и REAL
  (`TIME_TO_DINT`, `UDINT_TO_TIME`, ...), которых нет в stdlib RuSTy 1.0.6.
- `st_lint` STL007: составные префиксы массивов `a` + префикс элемента (`astAlarm`, `afbAlarm`,
  `aitfDev`, `altStart`, `audiReserve`), настройка `array_element_prefixes` (`match`, `any`, `off`);
  проверка ключей `st_lint.toml` (неизвестный ключ или значение не того вида — ошибка настроек).

### Changed

- Тесты `tools/tests/test_cds.py` и `test_cds_library.py` берут настройки из эталона
  `tools/tests/fixtures/config_template.json`, а не из `config.json` репозитория: проект может менять
  свои библиотеки, задачи и библиотеку репозитория без исключения тестов шаблона (`--deselect`).
  Проекту, который исключал их раньше, после обновления `tools/` исключения `test_cds.py` и
  `test_cds_library.py` в `pyproject.toml` и свои тесты-замены для них нужно убрать: тесты-замены,
  подменявшие `config.json` в модулях тестов шаблона, с новыми тестами не работают (проверено на копии
  s7-to-codesys: 7 падений замены, а сами тесты шаблона и `test_cds_config.py` проходят с его
  `config.json`).
- `tools/check/st_lint.toml` принадлежит проекту: тест `test_toml_matches_defaults` заменён на
  `test_template_toml_matches_defaults` (с умолчаниями сравнивается эталон
  `tools/tests/fixtures/st_lint_template.toml`) и `test_repository_toml_is_valid` (файл репозитория
  разбирается, все ключи известны); тесты линтера берут настройки из эталона. Проекту, который исключал
  `test_toml_matches_defaults` (`--deselect`), исключение нужно убрать.
- `test_run_rusty.py::test_integration_sample_passes` проверяет фикстуру со своим пустым файлом
  исключений, а не с `tools/check/rusty_exclude.txt` репозитория.
- `cds.py import`, `library`, `check`: два описания `libraries`, которые нашли одну библиотеку, дают
  одну ссылку (одинаковые сливаются с предупреждением, разные — отказ до открытия проекта, код 1);
  ссылки Library Manager после импорта — в поле `references` отчёта `build/import.json`.

### Fixed

- `st_lint` STL007: `VAR_IN_OUT CONSTANT` (и `VAR_INPUT CONSTANT`) больше не считается секцией
  констант — для параметров только для чтения действуют префиксы по типу, а не UPPER_SNAKE_CASE.
- Понижение `iec-checker`: начальное значение `[...]` массива в поле структуры убирается вместе с
  типом массива (раньше `x : REAL := [...]` — ParserError); `ARRAY[0..2 * N]` — умножение в границе
  больше не принимается за `ARRAY[*]`.
- Тесты coUnit: функции `TEST` и `TEST_FINISHED` вызываются с пространством имён (`coUnit.TEST(...)`) —
  без него сборка в CODESYS 3.5.17.30 давала ошибки C0046/C0035.
- `cds.py build`/`test`: перед открытием проекта удаляется кэш предкомпиляции CODESYS — с ним
  сломанное объявление ФБ с методами собиралось с «0 ошибок», а исправленное давало старую ошибку.
- `cds.py`: устаревший файл блокировки `<проект>.~u` (CODESYS остановлен по таймауту или упал)
  удаляется, проект, открытый в IDE, — понятный отказ с кодом 3 вместо трассировки.
- `cds.py import`: переименование только регистром (файл, метод, свойство, папка) доходит до проекта.
- `cds.py test`: старые `build/junit.xml` и `build/test-results.json` удаляются перед прогоном;
  неудачный вход в рантайм — одна строка с причиной и код 3 вместо трассировки; имя пользователя
  рантайма не пишется в журнал.
- `docs/MANUAL_STEPS.md`, `README.md`: команды без `& rem` — работают в cmd, PowerShell и Git Bash.
- `cds.py import`: ссылка на библиотеку другой версии заменяется (раньше оставалась старая, и в проекте
  оказывались обе); новейшая версия выбирается по номеру, а не по строке (`1.10` новее `1.9`); все
  недостающие библиотеки — в одном сообщении, до изменения проекта.
- `cds.py`: переменные рабочей копии (`CDS_REPO_ROOT`, `CDS_CONFIG`, `CDS_PROJECT*`, `CDS_LIBRARY*`) не
  читаются из `HKCU\Environment` — заданные через `setx`, они действовали бы на все git worktree сразу.
- Кэш предкомпиляции: имя по расширению файла (`<имя>_library.precompilecache` у библиотеки) — сборка
  библиотеки больше не удаляет кэш проекта `<имя>_project.precompilecache`.
