// Политика вне перечисления (7): срабатывание, схема None, счётчики 0
METHOD PRIVATE PolicyOutOfEnumTripsNone
VAR
    aeCh  : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF E_ChannelState;   // состояния каналов
    stRes : ST_VoteResult;                                           // результат
    uBad  : U_SisEnumInt;                                            // значение вне перечисления
END_VAR
