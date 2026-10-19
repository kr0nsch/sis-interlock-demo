// Назначение: стенд тестов FB_CauseEffect: подменное время (старт LTIME#1H), журнал событий и
//             исполнитель матрицы; тест пишет входы, команды и конфигурацию стенда и вызывает
//             Cycle/Step/Run/PressReset.
// Автор:      <ИМЯ ФАМИЛИЯ>
// Версия:     0.1.0
// Документ:   docs/DESIGN.md, раздел «12.3 Граничные случаи (вручную, команда A)»
// ВНИМАНИЕ:   код демонстрационный и не предназначен для систем безопасности. Реальная ПАЗ
//             требует определения SIL, сертифицированных аппаратных и программных средств
//             и валидации по ГОСТ Р МЭК 61511.
FUNCTION_BLOCK FB_CemRig
VAR_INPUT
    stCfg           : ST_CemCfg;        // конфигурация матрицы
    stCmd           : ST_CemCmd;        // команды HMI (ФБ сбрасывает)
    axCauseIn       : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF BOOL;   // требования причин
    xOverridePermit : BOOL := TRUE;     // ключ разрешения обходов
    xResetHw        : BOOL;             // кнопка «Сброс ПАЗ»
END_VAR
VAR
    fbTime : PL.FB_FakeTime;            // подменное время
    fbLog  : FB_SisTestLog;             // журнал событий
    fbCem  : FB_CauseEffect;            // ФБ под тестом
END_VAR
