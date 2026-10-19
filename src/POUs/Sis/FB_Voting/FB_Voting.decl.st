// Назначение: группа голосования MooN одной причины: дискретные или аналоговые каналы
//             (уставка включительно, гистерезис, NaN — недостоверен), деградация по политике
//             (F_VoteEval), байпас канала с таймером, ключом разрешения и ограничением числа,
//             тревога рассогласования аналоговых каналов (на срабатывание не влияет), журнал.
//             Fail-safe: xTrip = TRUE до первого вызова и при ошибке конфигурации; «время назад» —
//             неисправность источника времени: байпасы заканчиваются (D-19).
// Автор:      <ИМЯ ФАМИЛИЯ>
// Версия:     0.2.0
// Документ:   docs/DESIGN.md, раздел «5. Голосование»
// ВНИМАНИЕ:   код демонстрационный и не предназначен для систем безопасности. Реальная ПАЗ
//             требует определения SIL, сертифицированных аппаратных и программных средств
//             и валидации по ГОСТ Р МЭК 61511.
FUNCTION_BLOCK FB_Voting
VAR_INPUT
    stIn          : ST_VoteIn;            // сигналы каналов
    stCmd         : ST_VoteCmd;           // запросы байпаса (уровни)
    stCfg         : ST_VotingCfg;         // копия: ~40 байт, ссылки не держим
    xBypassPermit : BOOL;                 // ключ разрешения байпасов; FALSE снимает действующие
    uiCause       : UINT;                 // номер причины для событий (0 — не указан)
    itfTime       : PL.I_TimeSource;      // 0 — встроенный PL.FB_SystemTime
    itfLog        : I_SisEventSink;       // 0 — без журнала
END_VAR
VAR_OUTPUT
    xTrip : BOOL := TRUE;                 // TRUE — требование срабатывания
    stSts : ST_VotingSts;                 // состояние группы
END_VAR
VAR
    fbSysTime   : PL.FB_SystemTime;       // запасной источник времени
    itfTimeAct  : PL.I_TimeSource;        // действующий источник этого вызова
    ltNow       : LTIME;                  // время этого вызова
    afbBypass   : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF PL.FB_Delay;   // таймеры байпасов
    fbDisc      : PL.FB_Delay;            // задержка тревоги рассогласования
    axDemMem    : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF BOOL;          // память гистерезиса
    axValidPrev : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF BOOL := [3(TRUE)];   // достоверность прошлого вызова
    aeBypass    : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF E_BypassState; // состояния байпасов
    xCfgErrPrev : BOOL;                   // ошибка конфигурации прошлого вызова (начально — нет)
    xDiscPrev   : BOOL;                   // тревога рассогласования прошлого вызова
    ltPrev      : LTIME;                  // время прошлого вызова: «время назад» — неисправность (D-19)
END_VAR
VAR_TEMP
    wErr      : WORD;                     // биты VOTE_CFG_*
    xCfgErr   : BOOL;                     // ошибка конфигурации
    xTimeBack : BOOL;                     // время источника меньше времени прошлого вызова
    uiN       : UINT;                     // каналов в схеме
    uiK       : UINT;                     // номер канала
    uiActive  : UINT;                     // действующих байпасов
    uiPart    : UINT;                     // каналов в контроле рассогласования
    rVal      : REAL;                     // значение канала
    rMin      : REAL;                     // минимум участвующих каналов
    rMax      : REAL;                     // максимум участвующих каналов
    rSpread   : REAL;                     // разброс
    xCond     : BOOL;                     // условие рассогласования до задержки
    xDisc     : BOOL;                     // тревога рассогласования
    xReq      : BOOL;                     // запрос байпаса канала
    eKind     : E_SisEventKind;           // вид события
    axValid   : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF BOOL;             // достоверность каналов
    axDem     : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF BOOL;             // требование каналов
    aeChState : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF E_ChannelState;   // состояния каналов
    atRemain  : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF TIME;             // остаток байпасов
    stRes     : ST_VoteResult;            // результат голосования
END_VAR
