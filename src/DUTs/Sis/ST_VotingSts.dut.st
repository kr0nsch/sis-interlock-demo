// Назначение: состояние группы голосования для HMI, журнала и тестов (раздел 5.5, шаг 9).
// Автор:      kr0nsch
// Версия:     0.1.0
// Документ:   docs/DESIGN.md, раздел «4.2 Структуры»
// ВНИМАНИЕ:   код демонстрационный и не предназначен для систем безопасности. Реальная ПАЗ
//             требует определения SIL, сертифицированных аппаратных и программных средств
//             и валидации по ГОСТ Р МЭК 61511.
{attribute 'qualified_only'}
TYPE ST_VotingSts :
STRUCT
    xTrip          : BOOL := TRUE;                  // TRUE — требование срабатывания (= FB_Voting.xTrip)
    eArchEff       : E_VoteArch := E_VoteArch.None; // действующая схема
    xDegraded      : BOOL;            // есть байпасированные или недостоверные каналы
    xCfgError      : BOOL;            // ошибка конфигурации группы
    wCfgErr        : WORD;            // биты VOTE_CFG_*
    xDiscrepancy   : BOOL;            // тревога рассогласования (после задержки)
    rSpread_eu     : REAL;            // max − min участвующих аналоговых каналов; 0.0, если их меньше двух
    uiDemand       : UINT;            // каналов Demand
    uiInvalid      : UINT;            // каналов Invalid
    uiBypassed     : UINT;            // каналов Bypassed
    uiNormal       : UINT;            // каналов Normal
    aeChState      : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF E_ChannelState;   // состояния каналов
    aeBypass       : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF E_BypassState;    // состояния байпасов
    atBypassRemain : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF TIME;   // остаток байпаса; T#0S, если не Active
END_STRUCT
END_TYPE
