// Назначение: стенд тестов FB_SisUnit: подменное время (старт LTIME#1H), журнал событий и узел ПАЗ;
//             тест пишет входы групп, ключи, команды и конфигурации стенда и вызывает Cycle/Step/Run.
// Автор:      <ИМЯ ФАМИЛИЯ>
// Версия:     0.1.0
// Документ:   docs/DESIGN.md, раздел «12.3 Граничные случаи (вручную, команда A)»
// ВНИМАНИЕ:   код демонстрационный и не предназначен для систем безопасности. Реальная ПАЗ
//             требует определения SIL, сертифицированных аппаратных и программных средств
//             и валидации по ГОСТ Р МЭК 61511.
FUNCTION_BLOCK FB_UnitRig
VAR_INPUT
    astIn           : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF ST_VoteIn;      // входы групп
    stCmd           : ST_SisCmd;                                            // команды HMI
    stCemCfg        : ST_CemCfg;                                            // матрица
    astVoteCfg      : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF ST_VotingCfg;   // группы голосования
    xBypassPermit   : BOOL := TRUE;     // ключ разрешения байпасов
    xOverridePermit : BOOL := TRUE;     // ключ разрешения обходов
    xResetHw        : BOOL;             // кнопка «Сброс ПАЗ»
END_VAR
VAR
    fbTime : PL.FB_FakeTime;            // подменное время
    fbLog  : FB_SisTestLog;             // журнал событий
    fbUnit : FB_SisUnit;                // ФБ под тестом
END_VAR
