// Назначение: стенд сценарных тестов по матрице (DESIGN.md, 12.5): настоящие FB_SisApp, GVL_SisCfg
//             и ST_SisIo с подменным временем PL.FB_FakeTime и журналом FB_SisEventLog — от тегов на
//             входе до тегов на выходе, как на FAT. Тесты пишут stIo и stCmd по имени экземпляра
//             (они во VAR_INPUT: запись в VAR извне — ошибка C0037) и читают fbApp, fbLog.
// Автор:      <ИМЯ ФАМИЛИЯ>
// Версия:     0.1.0
// Документ:   docs/DESIGN.md, раздел «12.5 Стенд FB_SisHarness»
// ВНИМАНИЕ:   код демонстрационный и не предназначен для систем безопасности. Реальная ПАЗ
//             требует определения SIL, сертифицированных аппаратных и программных средств
//             и валидации по ГОСТ Р МЭК 61511.
FUNCTION_BLOCK FB_SisHarness
VAR_INPUT
    stIo  : ST_SisIo;              // образ ввода-вывода: тест ставит входы, читает выходы xQ*
    stCmd : ST_SisCmd;             // команды HMI: сброс, пусковые обходы, байпасы
END_VAR
VAR
    fbTime  : PL.FB_FakeTime;      // подменное время, старт LTIME#1H
    fbLog   : FB_SisEventLog;      // журнал событий ПАЗ
    fbApp   : FB_SisApp;           // ПАЗ объекта под тестом
    udiMark : UDINT;               // номер последнего события на момент MarkEvents
END_VAR
VAR CONSTANT
    RUN_MAX_ITERATIONS : UINT := 1500;   // предел шагов одного Run: все тесты идут в одном цикле задачи
END_VAR
