// Схема None и ForcedTrip как заданная схема: срабатывание, действующая схема None, без деградации,
// счётчики 0 — даже если все каналы в норме
METHOD PRIVATE ArchNoneTripsReportsNone
VAR
    aeCh  : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF E_ChannelState;   // состояния каналов
    stRes : ST_VoteResult;                                           // результат
END_VAR
