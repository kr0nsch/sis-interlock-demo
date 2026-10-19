// Назначение: общий узел ПАЗ: группы голосования по причинам (FB_Voting × 16), исполнитель
//             матрицы (FB_CauseEffect) и единый источник времени для всех вложенных ФБ. Ничего
//             не знает о демо-объекте: привязку объекта генерирует cemgen (FB_SisApp).
// Автор:      kr0nsch
// Версия:     0.1.0
// Документ:   docs/DESIGN.md, раздел «8.1 FB_SisUnit — общий узел ПАЗ»
// ВНИМАНИЕ:   код демонстрационный и не предназначен для систем безопасности. Реальная ПАЗ
//             требует определения SIL, сертифицированных аппаратных и программных средств
//             и валидации по ГОСТ Р МЭК 61511.
FUNCTION_BLOCK FB_SisUnit
VAR_INPUT
    astIn           : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF ST_VoteIn;   // входы групп по причинам
    xBypassPermit   : BOOL;                 // ключ разрешения байпасов
    xOverridePermit : BOOL;                 // ключ разрешения пусковых обходов
    xResetHw        : BOOL;                 // кнопка «Сброс ПАЗ»
    itfTime         : PL.I_TimeSource;      // 0 — встроенный PL.FB_SystemTime
    itfLog          : I_SisEventSink;       // 0 — без журнала
END_VAR
VAR_IN_OUT
    stCmd : ST_SisCmd;                      // команды HMI
END_VAR
VAR_IN_OUT CONSTANT
    stCemCfg   : ST_CemCfg;                                                 // матрица
    astVoteCfg : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF ST_VotingCfg;        // группы голосования
END_VAR
VAR_OUTPUT
    axEffectOut : ARRAY[1..GVL_Const.SIS_EFFECTS_MAX] OF BOOL;   // TRUE — под напряжением, FALSE — сработало
    xTripped    : BOOL := TRUE;                                  // хотя бы одно следствие сработало
    stCemSts    : ST_CauseEffectSts;                             // состояние матрицы
    astVoteSts  : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF ST_VotingSts;   // состояния групп
END_VAR
VAR
    afbVote    : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF FB_Voting;   // группы голосования
    fbCem      : FB_CauseEffect;            // исполнитель матрицы
    fbSysTime  : PL.FB_SystemTime;          // запасной источник времени
    itfTimeAct : PL.I_TimeSource;           // действующий источник этого вызова
    axDemand   : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF BOOL;   // требования причин
    stVoteStsDefault : ST_VotingSts;        // состояние невызванной группы (значения по умолчанию)
END_VAR
VAR_TEMP
    uiNc    : UINT;                         // используемых причин
    uiI     : UINT;                         // индекс причины
    stCause : ST_CauseCfg;                  // копия строки матрицы
END_VAR
