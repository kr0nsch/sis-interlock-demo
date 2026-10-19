// Назначение: сигналы каналов одной группы голосования: дискретные значения с контролем линии,
//             аналоговые значения в инж. ед. с достоверностью, внешнее требование (раздел 5.6).
// Автор:      kr0nsch
// Версия:     0.1.0
// Документ:   docs/DESIGN.md, раздел «4.2 Структуры»
// ВНИМАНИЕ:   код демонстрационный и не предназначен для систем безопасности. Реальная ПАЗ
//             требует определения SIL, сертифицированных аппаратных и программных средств
//             и валидации по ГОСТ Р МЭК 61511.
{attribute 'qualified_only'}
TYPE ST_VoteIn :
STRUCT
    axDi       : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF BOOL;   // дискретные каналы (значение с поля)
    axDiValid  : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF BOOL;   // контроль линии / диагностика: TRUE — исправен
    arAi_eu    : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF REAL;   // аналоговые каналы, инж. ед.
    axAiValid  : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF BOOL;   // достоверность (NE 43 и т. п.): TRUE — достоверен
    xExtDemand : BOOL;                                          // для eSource = External: TRUE — требование
END_STRUCT
END_TYPE
