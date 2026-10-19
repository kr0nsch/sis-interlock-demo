// NotUsed и значение вне перечисления внутри N считаются недостоверными каналами (безопасная сторона)
METHOD PRIVATE NotUsedInsideNCountsInvalid
VAR
    aeCh  : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF E_ChannelState;   // состояния каналов
    stRes : ST_VoteResult;                                           // результат
    uBad  : U_SisEnumInt;                                            // значение вне перечисления
END_VAR
