// 2oo3 без деградации: один канал Demand — нет срабатывания, два — срабатывание; схема 2oo3
METHOD PRIVATE TwoOfThreeTripsOnSecondDemand
VAR
    aeCh  : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF E_ChannelState;   // состояния каналов
    stRes : ST_VoteResult;                                           // результат
END_VAR
