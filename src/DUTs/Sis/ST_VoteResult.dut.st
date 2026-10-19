// Назначение: результат F_VoteEval: требование, деградация, действующая схема и счётчики
//             состояний каналов (раздел 5.2).
// Автор:      kr0nsch
// Версия:     0.1.0
// Документ:   docs/DESIGN.md, раздел «4.2 Структуры»
// ВНИМАНИЕ:   код демонстрационный и не предназначен для систем безопасности. Реальная ПАЗ
//             требует определения SIL, сертифицированных аппаратных и программных средств
//             и валидации по ГОСТ Р МЭК 61511.
{attribute 'qualified_only'}
TYPE ST_VoteResult :
STRUCT
    xTrip      : BOOL := TRUE;                      // TRUE — требование срабатывания
    xDegraded  : BOOL;                              // есть байпасированные или недостоверные каналы
    eArchEff   : E_VoteArch := E_VoteArch.None;     // действующая схема
    uiDemand   : UINT;                              // каналов Demand
    uiInvalid  : UINT;                              // каналов Invalid
    uiBypassed : UINT;                              // каналов Bypassed
    uiNormal   : UINT;                              // каналов Normal
END_STRUCT
END_TYPE
