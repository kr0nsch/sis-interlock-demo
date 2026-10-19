# Ручные шаги

> **Внимание.** Код демонстрационный и не предназначен для систем безопасности. Реальная ПАЗ
> требует определения SIL, сертифицированных аппаратных и программных средств и валидации по
> ГОСТ Р МЭК 61511.

Шаги, которые выполняет человек в консоли Windows и в IDE CODESYS. Всё, что можно выполнить без
CODESYS (генератор, сборка текстов, линтер, статанализ), описано в
[README](../README.md#быстрый-старт-без-железа) и выполняется в CI. Специфика проекта — разделы 5
(библиотека plc-process-lib и полная проверка), 9 (демо-приложение в IDE), 10 (изменение матрицы)
и 11 (протокол FAT).

Команды разделов 3–7 проверены прогоном на CODESYS V3.5 SP17 Patch 3 (3.5.17.30, 32-битная сборка
ОВЕН) и CODESYS Control Win V3 в пользовательском процессе (16.10.2026), включая сборку, установку
и удаление библиотек и сборку зависимостей из соседних репозиториев. Что не проверено — отмечено
явно. Подробности об инструменте — [tools/README.md](../tools/README.md#codesyscdspy--codesys-из-консоли).

## 1. Установка CODESYS 3.5.17.30

1. Скачать CODESYS V3.5 SP17 Patch 3 (3.5.17.30) с сайта ОВЕН (раздел ПО для ПЛК2xx) и установить
   с компонентами CODESYS Control Win V3 и Gateway. Сборка ОВЕН 32-битная и ставится в
   `C:\Program Files (x86)\CODESYS 3.5.17.30\` — этот путь `cds.py` находит сам.
2. Для рабочего ПЛК — пакет таргет-файлов ОВЕН ПЛК210: «Инструменты → Установщик пакетов»
   (Tools → Package Manager). Версию таргет-файла сверить с прошивкой ПЛК. Для тестов он не нужен:
   тестовый проект собирается под CODESYS Control Win V3.
3. Имя профиля — по файлу в каталоге профилей (для 3.5.17.30 — `CODESYS V3.5 SP17 Patch 3`):

   ```bat
   dir "C:\Program Files (x86)\CODESYS 3.5.17.30\CODESYS\Profiles"
   ```

   `CODESYS.exe --help` и запуск без `--profile` открывают окно IDE (диалог выбора профиля), а не
   выводят справку в консоль — для проверки их не используйте.
4. Нужен Python 3.11+ (`python --version`), сторонние пакеты для `cds.py` не нужны.

## 2. coUnit (CfUnit) 1.2.0.0

В версии 1.2.0.0 CfUnit называется co♻e / coUnit, пространство имён в коде — `coUnit`
(см. [ASSUMPTIONS.md](ASSUMPTIONS.md), C6). Лицензия MIT.

1. Скачать `counit.library` из SVN проекта counit на CODESYS Forge (`tags/v1.2.0.0/`) обычным
   `GET` (браузером: запрос `HEAD` даёт 401).
2. Установить одним из способов:
   - в IDE: «Инструменты → Репозиторий библиотек → Установить» (Tools → Library Repository → Install);
   - или автоматически: задать путь к файлу в `COUNIT_LIBRARY` (раздел 3) — первый
     `cds.py import --tests`, не найдя coUnit 1.2.0.0 в репозиториях, установит её в репозиторий
     `System` (`librarymanager.install_library`). _Для coUnit ветка установки на этой машине не
     выполнялась: библиотека уже была установлена. Поиск по названию и версии проверен, установка
     из файла — на другой библиотеке (`cds.py deps`, тот же код)._
3. Параметры библиотеки менять не нужно: с параметрами по умолчанию тестовое приложение под
   Control Win собирается без ошибок (проверено, C7). Для ПЛК210 с меньшей памятью — сверить при
   переносе тестов на контроллер.

## 3. Переменные окружения

Абсолютных путей пользователя в репозитории нет: `cds.py` берёт их из переменных окружения, а без
них — из значений по умолчанию в `tools/codesys/config.json`. Обычно достаточно двух:

| Переменная | Значение | По умолчанию |
|---|---|---|
| `CODESYS_EXE` | полный путь к `CODESYS.exe` | `%ProgramFiles(x86)%\CODESYS 3.5.17.30\CODESYS\Common\CODESYS.exe`, затем `%ProgramFiles%\...` |
| `CODESYS_PROFILE` | имя профиля | `CODESYS V3.5 SP17 Patch 3` |
| `COUNIT_LIBRARY` | путь к `counit.library` (только если coUnit ещё не установлена) | — |
| `CODESYS_RUNTIME_CREDENTIALS` | файл с логином и паролем тестового пользователя рантайма | `%USERPROFILE%\.local\plc-tools\cds-runtime\credentials.json` |

Остальные (устройство, пути рантайма, таймауты, блокировка) — в
[tools/README.md](../tools/README.md#переменные-окружения). Задать для пользователя:

```bat
setx CODESYS_EXE "C:\Program Files (x86)\CODESYS 3.5.17.30\CODESYS\Common\CODESYS.exe"
setx CODESYS_PROFILE "CODESYS V3.5 SP17 Patch 3"
```

`setx` не меняет окружение уже открытых консолей; `cds.py` дочитывает переменные пользователя из
реестра (`HKCU\Environment`), поэтому перезапуск консоли не обязателен.

## 4. Рантайм CODESYS Control Win V3 без прав администратора

Служба Windows «CODESYS Control Win V3» требует прав администратора — её не используем. Тесты идут
в пользовательском процессе `CODESYSControlService.exe`, которым управляет `cds.py`. Команды
одинаково работают в cmd, PowerShell и Git Bash (из корня репозитория):

| Команда | Что делает |
|---|---|
| `python tools/codesys/cds.py runtime init` | один раз: каталог, `boot.cfg`, копия `CODESYSControl.cfg`, `credentials.json` |
| `python tools/codesys/cds.py runtime start` | скрытый запуск, ждёт порт 11740 |
| `python tools/codesys/cds.py runtime status` | PID, сколько работает, остаток демо-режима; код 1 — рантайм не запущен |
| `python tools/codesys/cds.py runtime restart` | остановить свой процесс и запустить заново |
| `python tools/codesys/cds.py runtime stop` | остановить свой процесс (службу Windows не трогает) |

- `runtime init` создаёт `%USERPROFILE%\.local\plc-tools\cds-runtime\`: `boot.cfg`, `work\` с
  копией штатного `CODESYSControl.cfg` (из `C:\ProgramData\CODESYS\CODESYSControlWinV3\<id>\`, файл
  только читается) и `credentials.json` с пользователем `cdsci` и случайным паролем. Пароль не
  печатается; файл лежит вне репозитория — не копируйте и не коммитьте его.
- Без лицензии рантайм работает 2 часа с момента запуска. `cds.py test` сам перезапускает его, если
  он работает дольше 100 минут (`CODESYS_RUNTIME_MAX_AGE_MIN`). Запуск и остановка — только своего
  процесса (с `-d <boot.cfg>`); если порт 11740 занят службой или чужим экземпляром, `cds.py`
  использует его, но не перезапускает.
- Состояние рантайма (пользователи, загруженные приложения, сертификаты, PlcLogic) из-за
  виртуализации UAC лежит не в `work\`, а в
  `%LOCALAPPDATA%\VirtualStore\Program Files (x86)\CODESYS 3.5.17.30\GatewayPLC\`; туда же
  попадает XML-отчёт coUnit (`%LOCALAPPDATA%\VirtualStore\coUnit_xunit_testresults.xml`).
  Чтобы «обнулить» рантайм (забыть пользователей и приложения), остановите его и удалите этот
  каталог вручную — это необратимо.

**Первый вход и создание пользователя.** Управление пользователями рантайма остаётся включённым
(отключать его не нужно). На свежем рантайме без пользователей `cds.py test` сам создаёт первого
пользователя из `credentials.json` (`set_credentials_for_initial_user` и подключение), если обычный
вход не удался. _Эта ветка реализована по API, но на этой машине не выполнялась: пользователь
`cdsci` уже был создан._ Если автоматически не получится — вручную в IDE: открыть тестовый проект
(раздел 6), «Устройство → Настройки соединения» (Communication Settings), выбрать шлюз `Gateway-1`
(localhost:1217) и устройство, войти — IDE предложит создать пользователя; ввести логин и пароль
из `credentials.json`.

## 5. Импорт, сборка, тесты

Все команды — из корня репозитория (cmd, PowerShell или Git Bash). Каждая запускает CODESYS без
окна (`--noUI`), длится 10–20 секунд и пишет журналы в `build/`.

| Команда | Что делает |
|---|---|
| `python tools/codesys/cds.py import` | `src/` → `build/<имя>.project` (MainTask 20 мс → `PRG_Main`) |
| `python tools/codesys/cds.py import --tests` | `src/` и `tests/` → `build/<имя>-tests.project` (TestTask 10 мс → `PRG_Tests`, coUnit) |
| `python tools/codesys/cds.py build` | импорт и полная сборка: `build/build.log`, `build/build.json` |
| `python tools/codesys/cds.py build --tests` | то же для тестового проекта |
| `python tools/codesys/cds.py check` | компиляция **всех** объектов `src/`, в том числе тех, что не вызывает ни одна задача: `build/check.log`, `build/check.json` |
| `python tools/codesys/cds.py check --tests` | то же для `src/` и `tests/` |
| `python tools/codesys/cds.py test` | импорт с тестами, сборка, прогон в рантайме |
| `python tools/codesys/cds.py roundtrip` | импорт в чистый проект → экспорт → сравнение с `src/` и `tests/` |
| `python tools/codesys/cds.py report` | итоги последнего `test` → `docs/TEST_REPORT.md` |

**Библиотека plc-process-lib.** Проект ссылается на неё (`PL.I_TimeSource`, `PL.FB_Delay`,
`PL.FB_FakeTime`, `PL.F_IsFinite`, константы NE 43). Клонируйте репозиторий библиотеки рядом —
`..\plc-process-lib` — или задайте путь в `PL_REPO`. Если библиотеки нет в репозитории библиотек
CODESYS, первый `build`, `check` или `test` соберёт её там (`cds.py library --install`) и повторит
задание; проверить, что установлено: `python tools\codesys\cds.py deps --check`. Версия — новейшая
установленная (`"*"` в `tools/codesys/config.json`); для релиза закрепите точную (раздел 7.3).
Проверено 16.10.2026: plc-process-lib 0.1.0.0, собрана из соседнего репозитория.

**Полная проверка этого проекта** (перед коммитом и релизом; DESIGN.md, 12.8):

```bat
python -m ruff check . && python -m ruff format --check . && python -m mypy && python -m pytest
python -m cemgen generate examples/separator/cem.csv --check
python tools_project\gen_voting_tests.py --check
python tools\assemble.py --tests
python tools\check\st_lint.py --strict
python tools\check\run_iec_checker.py --tests
python tools\codesys\cds.py build
python tools\codesys\cds.py build --tests
python tools\codesys\cds.py check --tests
python tools\codesys\cds.py test
python tools\codesys\cds.py roundtrip
python tools\codesys\cds.py report
python -m cemgen fat-report examples/separator/cem.csv --results build/test-results.json
```

Последний прогон (19.10.2026) — [TEST_REPORT.md](TEST_REPORT.md): сборки без ошибок и
предупреждений, 255 тестов из 255, roundtrip без диффа, протокол FAT — 55 шагов из 55.
`cds.py test` с этим проектом длится около 5 минут (импорт ~30 с, загрузка и прогон ~1 мин, ожидание
рантайма, если его занимает другой проект).

В каждом репозитории портфолио минимум тот же:

```bat
python tools\codesys\cds.py build
python tools\codesys\cds.py check --tests
python tools\codesys\cds.py test
python tools\codesys\cds.py roundtrip
```

`build` компилирует только объекты, достижимые из задач: ошибка в программе без задачи, в ФБ без
экземпляра, его методах или в неиспользуемом DUT даёт в `build` «0 ошибок» (проверено). Такие
ошибки находит `check`: он компилирует все объекты раскладки с теми же библиотеками, что у `build`
(из `config.json` и библиотеки устройства), проект проверки на диск не пишется, проекты `import` не
меняются. `check` не заменяет `build`: в нём нет задач и конфигурации ввода-вывода.

Что смотреть:

- `import` печатает, что создано, обновлено, удалено и перемещено. Повторный импорт без правок —
  «создано 0, обновлено 0, удалено 0». Ошибки раскладки (коды LAY) — отказ без изменений проекта.
- `build`: ошибки и предупреждения компилятора с файлом и строкой раскладки, например
  `src/POUs/Sis/F_SisAiToEu/F_SisAiToEu.impl.st:3: Error C0046 Идентификатор 'rLoX' не задан`. Сообщения
  IDE — на русском. Если в IDE видны ошибки, которых нет в выводе, — скопируйте их в
  [BUILD_ERRORS.md](BUILD_ERRORS.md). Перед открытием проекта `cds.py` удаляет кэш предкомпиляции
  `build/<имя>_project.precompilecache`: с ним CODESYS 3.5.17.30 после замены объявления ФБ с
  методами собирал старый текст (сломанное объявление — «0 ошибок», исправленное — старая ошибка).
- `check`: те же сообщения с файлом и строкой, что у `build`, например
  `src/POUs/Orphans/PRG_Orphan/PRG_Orphan.impl.st:2: Error C0032 Невозможно конвертировать тип 'DINT' в тип 'INT'`,
  и итог «все объекты src/ и tests/ скомпилированы без ошибок (N объектов)». Ошибки синтаксиса
  останавливают компиляцию до проверки типов: ошибки типов в других объектах появятся после их
  исправления — повторите `check`.
- `test` перед прогоном удаляет `build/test-results.json` и `build/junit.xml` прошлого запуска:
  при ошибке сборки или входа в рантайм старые зелёные результаты не остаются.
- `test`: итог по наборам и тестам; упавшие — с сообщением coUnit. Результаты — в
  `build/test-results.json` и `build/junit.xml`, журнал — `build/test.log`.
- `roundtrip`: «экспорт совпадает с src/ и tests/ побайтно» и «повторный импорт … — 0 изменений».
  Любой дифф — ошибка скриптов (issue).

Библиотека Standard (TON, R_TRIG, CTU, CONCAT) подключена по умолчанию — плейсхолдером
`#Standard` через `library.libraries` в `tools/codesys/config.json`: версию задаёт профиль CODESYS,
работают и `TON`, и `Standard.TON`, как в проекте, созданном в IDE
([tools/README.md](../tools/README.md#standard-по-умолчанию)).

Коды выхода: 0 — успех; 1 — ошибки раскладки, сборки или проверки всех объектов, упавшие тесты, дифф roundtrip;
2 — аргументы или `config.json`; 3 — окружение (нет CODESYS, рантайма, файла); 4 — таймаут;
5 — блокировка занята. Рантайм один на машину: команды, которые с ним работают, ждут друг друга
(блокировка `%LOCALAPPDATA%\plc-tools\codesys-runtime.lock`).

## 6. Работа в IDE и экспорт перед коммитом

1. Собрать проект: `python tools\codesys\cds.py import` (или `import --tests` для проекта с тестами).
2. Открыть его в IDE: «Файл → Открыть проект» → `build\<имя>.project` (`build\<имя>-tests.project`),
   либо из консоли cmd (из PowerShell — эту же строку через `cmd /c '<строка>'`: PowerShell и Git
   Bash переставляют кавычки в `--profile="..."`, и CODESYS не находит профиль; `cmd /c` проверен
   с `--noUI --runscript`). `%CODESYS_EXE%` виден в консолях, открытых после `setx`:

   ```bat
   "%CODESYS_EXE%" --profile="CODESYS V3.5 SP17 Patch 3" --project="%CD%\build\sis-interlock-demo.project"
   ```

   Вход в рантайм из IDE: «Онлайн → Логин» с пользователем из `credentials.json`. _Открытие из
   консоли с `--project` здесь не проверялось (ключ описан в справке CODESYS по командной строке)._
3. Править, сохранить проект, **закрыть IDE**. Пока проект открыт в IDE, `import`, `build`, `test`
   и `export` сразу отказываются: «проект … открыт в другом экземпляре CODESYS (пользователь, компьютер,
   PID)», код выхода 3 (проверено). Файл блокировки `<проект>.~u`, оставшийся после сбоя CODESYS
   или его остановки по таймауту, `cds.py` удаляет сам, если процесса с этим PID больше нет.
4. Выгрузить правки в тексты и проверить дифф:

   ```bat
   python tools/codesys/cds.py export
   python tools/codesys/cds.py export --tests
   git diff --stat
   ```

   `export` выгружает `build/<имя>.project` в `src/`; `export --tests` — `build/<имя>-tests.project`
   в `src/` и `tests/`.

Защита от потери правок:

- `import` отказывается перезаписывать проект, сохранённый в IDE после последнего
  `import`/`export`, — сначала `export` (или `--force`, если правки не нужны);
- `export` в репозиторий отказывается, если `src/` (`tests/`) изменились после последнего
  `import`/`export` этого проекта: экспорт удаляет файлы, которых нет в проекте. Сравнить можно
  выгрузкой в отдельный каталог: `cds.py export --to build\cmp`; перезапись — `--force`.

Не входит в раскладку (только в IDE, при экспорте не сохраняется — описывайте здесь и в docs):

- [ ] дерево устройств ПЛК210 и конфигурация модулей ввода-вывода; конфигураторы обмена (Modbus, OPC UA);
- [ ] визуализации, графические языки (FBD/LD/SFC/CFC), действия (`ACTION`) — `export` предупреждает о них;
- [ ] **Persistent Variables** (`*.pvl.st`): в SP17 скриптом не создаются. Создайте объект вручную
  («Application → Добавить объект → Persistent Variables» с именем как у файла), затем
  `cds.py import` обновит его текст из файла, а `export` выгрузит обратно.

Задачи и ссылки на библиотеки не правьте в IDE: их создаёт `import` по `tools/codesys/config.json`
(лишние задачи удаляются).

## 7. Релиз и библиотеки: `.project`, `.library`, зависимости

`.project` и `.library` в git не хранятся — прикладываются к релизу GitHub. Команды этого раздела
проверены на 3.5.17.30 (16.10.2026) на двух временных репозиториях — библиотеке и проекте, который
её использует; этот репозиторий собирается в библиотеку `sis-interlock-demo` (`cds.py library`, без
`PRG_Main`).

### 7.1. Выпуск релиза

1. `python tools\codesys\cds.py build` и `python tools\codesys\cds.py check --tests` — 0 ошибок;
   `python tools\codesys\cds.py test` — тесты зелёные; `python tools\codesys\cds.py roundtrip` — без диффа.
2. Версия: `library.version` в `tools/codesys/config.json` (четыре числа, `1.2.0.0`) и запись в
   `CHANGELOG.md`. Компанию (`library.company`) и название (`library.title`) после первого релиза не
   меняйте: по тройке «компания, название, версия» библиотеку находят проекты-потребители.
   Перед публикацией шаблона замените `plc-portfolio` на свой GitHub-логин (без символов
   `<>:"/\|?*,()`).
3. Библиотека (для репозиториев-библиотек):

   ```bat
   python tools\codesys\cds.py library --compiled --released
   ```

   Итог — `build\<имя>.library` (с исходниками) и `build\<имя>.compiled-library` (без исходников),
   Project Information — из раздела `library`, проверка «все объекты пула» — 0 ошибок. Ошибки
   выводятся с файлом и строкой в `src/`; при ошибках файлы не устанавливаются (код 1), а
   `build\<имя>.library` можно открыть в IDE и посмотреть. Ссылки самой библиотеки
   (`library.libraries`: `standard` — по умолчанию, другая библиотека портфолио) `cds.py` добавляет
   и в проекты приложения и тестов этого репозитория — в `modes` их повторять не нужно.
4. Приложить к релизу GitHub: `.compiled-library` — для использования, `.library` — для отладки и
   чтения исходников; `build\<имя>.project` — рабочий проект (для переноса на другую машину удобнее
   «Файл → Архив проекта → Сохранить/Отправить архив», `.projectarchive`).
5. Поставить тег `v1.2.0` на коммит релиза: потребители переключают на него соседний репозиторий
   (раздел 7.3), а `cds.py` проверяет, что версия в его `config.json` совпадает с закреплённой.
6. Записать в [TEST_REPORT.md](TEST_REPORT.md) итоги (`cds.py report`).

То же в IDE (если `cds.py` недоступен): открыть `build\<имя>.library` (или проект), заполнить
«Проект → Информация о проекте» (компания, название, версия, пространство имён по умолчанию),
выполнить «Сборка → Проверить все объекты пула» и «Файл → Сохранить проект как скомпилированную
библиотеку». _Названия пунктов меню — сверить с русской IDE 3.5.17.30; в IDE этот путь не
выполнялся, проверен только скриптовый._

### 7.2. Установка библиотеки в репозиторий библиотек

- Своя библиотека из репозитория-библиотеки: `python tools\codesys\cds.py library --install`
  (с `--compiled` ставится `.compiled-library`). Та же версия заменяется, другие версии остаются
  рядом. Репозиторий — `System` (`C:\ProgramData\CODESYS\Managed Libraries`), другой — по имени в
  `CDS_LIBRARY_REPOSITORY`.
- Файл, полученный готовым (релиз GitHub): в IDE «Инструменты → Репозиторий библиотек → Установить»
  или путь к файлу в переменной из `install_from` (например, `setx PL_LIBRARY "C:\dl\plc-process-lib.compiled-library"`)
  и `python tools\codesys\cds.py deps` — файл поставится, если нужной версии ещё нет.
- Удаление: `python tools\codesys\cds.py library --uninstall` (версия из `config.json`) или
  `--uninstall --all-versions` — в репозитории-библиотеке; в IDE — «Репозиторий библиотек →
  Удалить». Удалять стоит и временные версии, поставленные для экспериментов.
- Установленные версии и откуда они: `python tools\codesys\cds.py deps` в проекте-потребителе
  (строка «установлена cds.py из <рабочая копия> @ <коммит>»).

### 7.3. Проект, который использует библиотеку портфолио

В этом репозитории так подключена plc-process-lib (`tools/codesys/config.json`, ключ
`plc-process-lib`, версия `*` и `library.libraries`); ниже — общий порядок.

1. Клонировать репозиторий библиотеки рядом: `..\plc-process-lib` (или задать путь в переменной из
   `build_from_repo`, например `PL_REPO`) и переключить его на нужный тег.
2. Описать библиотеку в `tools/codesys/config.json` и сослаться на неё из режимов:

   ```json
   "libraries": {
     "plc-process-lib": {
       "namespace": "PL",
       "title_contains": "plc-process-lib",
       "version": "1.0.0.0",
       "build_from_repo": {"env": "PL_REPO", "default": "../plc-process-lib"},
       "install_from": {"env": "PL_LIBRARY", "default": null}
     }
   },
   "modes": {
     "normal": {"tasks": [...], "libraries": ["plc-process-lib"]},
     "test": {"tasks": [...], "libraries": ["counit", "plc-process-lib"]}
   }
   ```

   В коде — с пространством имён: `fbPump : PL.FB_Pump;`.
3. Версия: **точная** (`"1.0.0.0"`) — для релизов, сборка воспроизводима; **`"*"`** — новейшая из
   установленных (по номеру версии), удобно, пока библиотека и проект разрабатываются вместе.
   Смена закрепления — правка `version` и `cds.py build`: ссылка в проекте заменится.
4. `python tools\codesys\cds.py build` (или `test`). Если нужной версии нет в репозитории
   библиотек, `cds.py` соберёт её в соседнем репозитории (`cds.py library --install` там) и повторит
   задание. Если соседний репозиторий собирает другую версию — отказ с подсказкой (переключить его
   на тег или изменить `version`). Библиотека проверяется и по её собственным зависимостям: если
   их нет в репозитории библиотек, она пересобирается в соседнем репозитории вместе с ними.
   Явно: `cds.py deps` (проверить и доустановить),
   `cds.py deps --rebuild plc-process-lib` (пересобрать после правок в библиотеке),
   `cds.py deps --check` (только проверить). `--no-deps` у `build`/`test` отключает автосборку.
5. Плейсхолдер вместо прямой ссылки — `"placeholder": "plc-process-lib"` в описании: `cds.py`
   добавит `#plc-process-lib` с перенаправлением на закреплённую версию.

### 7.4. Параллельные рабочие копии (git worktree)

У каждой рабочей копии свои `build/` и блокировка, сборки идут параллельно; тесты в рантайме и
установка библиотек — по очереди (общие блокировки в `%LOCALAPPDATA%\plc-tools\`). Переменные
`CDS_PROJECT*`, `CDS_LIBRARY*`, `CDS_REPO_ROOT`, `CDS_CONFIG` задавайте только в консоли
(`set CDS_LIBRARY_VERSION=1.0.1.0`), не через `setx`: из реестра `cds.py` их не читает, иначе они
действовали бы на все копии. Библиотека одной версии из двух копий — одна запись в репозитории
библиотек (действует последняя установка, `cds.py` предупреждает): для экспериментов в отдельной
копии собирайте без `--install` или с другой версией.

## 8. Зеркало на GitVerse или GitFlic

1. Создать пустой репозиторий на GitVerse или GitFlic (без README и лицензии).
2. Добавить его как второй remote и отправить все ветки и теги:

   ```bash
   git remote add mirror <url-зеркала>
   git push mirror --all
   git push mirror --tags
   ```

3. После каждого релиза повторять `git push mirror --all` и `git push mirror --tags`.

## 9. Демо-приложение V-101 в IDE

Рабочий проект `build\sis-interlock-demo.project` (MainTask 20 мс → `PRG_Main` → `PRG_Sis`) работает
без ввода-вывода: в первом цикле `PRG_Main` ставит нормальные значения входов
(`GVL_Const.DEMO_IO_SIMULATION`), а воздействия — запись переменных из IDE.

_В IDE эта последовательность не выполнялась. Та же логика с той же конфигурацией проверена
автотестами на стенде `FB_SisHarness`: `Matrix_Start_TrippedUntilReset`,
`Matrix_PSHH101Demand_TripsOwnEffects`, `Matrix_PSHH101Reset_OnlyAfterClear`,
`Matrix_PSHH101ChannelInvalid_MatchesPolicy`, `Matrix_PSHH101Bypass_ExpiresBackToVoting`,
`Matrix_PSLL101Override_ExpiresThenTrips`._

1. `python tools\codesys\cds.py build`, затем `python tools\codesys\cds.py runtime start`.
2. Открыть `build\sis-interlock-demo.project` в IDE (раздел 6), «Онлайн → Логин» (пользователь из
   `credentials.json`), загрузить приложение и запустить (F5).
3. В окно наблюдения добавить `GVL_SisIo.stIo` (входы в мА, ключи и выходы `xQ*`),
   `GVL_Sis.fbApp.stCemSts` (первопричина, маски, блокирующая сброс причина, остатки задержек и
   обходов), `GVL_Sis.fbApp.astVoteSts[1]` (голосование PSHH101) и `GVL_Sis.stCmd`.
4. **Старт.** Все `xQ*` = `FALSE` (обесточены), `stCemSts.uiFirstOut` = 65534
   (`SIS_FIRST_OUT_START`): после старта ПЛК ПАЗ ждёт сброса оператором (D-03).
5. **Сброс.** Подготовить `GVL_Sis.stCmd.stCem.xReset := TRUE` и записать значения (Ctrl+F7) —
   ФБ сам снимает команду. Все `xQ*` = `TRUE`, `uiFirstOut` = 0. То же делает фронт кнопки
   `GVL_SisIo.stIo.xHS120`.
6. **Срабатывание PSHH101 (2oo3, 0,90 МПа, 2 с).** Записать `rPT101A_mA := 13.2` и
   `rPT101B_mA := 13.2` (0,92 МПа; норма — 10,0 мА = 0,60 МПа). Через 2 с `xQESDV101`, `xQH101`,
   `xQUA110` = `FALSE`, остальные `xQ*` — `TRUE`; `uiFirstOut` = 1, `wCauseLatched` = 1. Один канал
   (`rPT101A_mA` без `rPT101B_mA`) срабатывания не даёт. Через 10 с `astVoteSts[1].xDiscrepancy` =
   `TRUE`: каналы расходятся больше чем на 0,05 МПа — это диагностика, на срабатывание не влияет.
7. **Сброс при требовании.** Команда сброса отклоняется: `uiResetBlocker` = 1, следствия остаются
   обесточенными. Вернуть 10.0 мА на оба канала — следствия всё ещё обесточены (фиксация); сброс —
   под напряжением.
8. **Отказ канала.** `rPT101A_mA := 2.0` (обрыв, ниже 3,6 мА по NE 43): `astVoteSts[1].eArchEff` —
   `Vote1oo2` (политика VoteTrip), срабатывания нет; теперь хватает одного канала: `rPT101B_mA := 13.2`
   через 2 с даёт срабатывание.
9. **Байпас канала.** Ключ `xHS121 := TRUE`, запрос `GVL_Sis.stCmd.astVote[1].axBypassReq[1] := TRUE`
   (держится, пока нужен): `astVoteSts[1].aeBypass[1]` = `Active`, остаток — `atBypassRemain[1]`
   (8 ч). Снятие ключа или запроса заканчивает байпас; события — в `GVL_Sis.fbLog`.
10. **Пусковой обход PSLL101 (15 мин).** Ключ `xHS122 := TRUE`, `GVL_Sis.stCmd.stCem.wOverrideReq :=
    16#0002` (бит причины 2): `stCemSts.wOverridden` = 2; давление ниже 0,15 МПа (`rPT101A_mA`,
    `rPT101B_mA := 5.3`) не фиксируется, пока обход действует (`atOverrideRemain[2]`). Вернуть
    10.0 мА на оба канала: обход снимается сам через 30 с устойчивой нормы (`atOverrideClearRemain[2]`
    отсчитывает подтверждение, в журнале — `OverrideCleared`); после этого новое падение давления даёт
    срабатывание через 5 с.

Демо-режим рантайма — 2 часа, затем `python tools\codesys\cds.py runtime restart`. Закончив, выйти
из рантайма и закрыть IDE: иначе `cds.py` откажется работать с проектом (раздел 6).

## 10. Изменение матрицы причин и следствий

Матрица `examples/separator/cem.csv` — единственный источник конфигурации, тестов по матрице и
документов. Сгенерированные файлы (`src/**/Generated/`, `tests/**/Generated/`,
`docs/cause_effect_matrix.*`, `docs/FAT_protocol.md`, `docs/truth_tables/VOTING.md`, раздел 3
`docs/SRS.md`) руками не правятся: CI это заметит (`generate --check`), а ПЛК — по CRC.

1. Править CSV (UTF-8, разделитель `;`) или XLSX (лист `CEM`):
   `python -m cemgen convert examples/separator/cem.csv build\cem.xlsx`, правка в Excel, обратно —
   `python -m cemgen convert build\cem.xlsx examples/separator/cem.csv`. Поднять `revision` и `date`
   в `[header]`.
2. `python -m cemgen validate examples/separator/cem.csv --strict` — ошибки с номером строки и
   колонкой файла (как в Excel) и подсказкой «Как исправить».
3. `python -m cemgen generate examples/separator/cem.csv` — печатает новые, изменённые и удалённые
   файлы и число тестов по матрице.
4. Если меняли XLSX в репозитории: `python -m cemgen convert examples/separator/cem.csv
   examples/separator/cem.xlsx` (байты XLSX недетерминированы — коммитится вручную).
5. Полная проверка (раздел 5), затем `cemgen fat-report` (раздел 11). В ревью — дифф матрицы,
   `GVL_SisCfg.gvl.st` (маски, уставки, CRC), тестов и документов.

Формат матрицы и правила проверки — [DESIGN.md](DESIGN.md), раздел 9; генератор —
[CEMGEN.md](CEMGEN.md).

## 11. Протокол FAT

- `docs/FAT_protocol.md` — бланк: шаги, воздействия, ожидаемый результат и автотесты, графы
  «Результат» и «Отметка» пустые. Для испытаний на стенде его можно распечатать и заполнять вручную.
- `python -m cemgen fat-report examples/separator/cem.csv --results build/test-results.json` после
  `cds.py test` пишет `docs/FAT_REPORT.md`: шаг «соответствует», если по каждому его шаблону
  автотестов есть результаты и все пройдены; «не соответствует» — с сообщением первого упавшего
  теста; «не выполнялся» — нет результатов. Код выхода 1, если есть упавшие тесты.
- Раздел 8 протокола (замечания и подписи) заполняется вручную. FAT на реальном шкафу с ПЛК210 и
  модулями ввода-вывода — вне рамок демо.
