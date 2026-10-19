// Счётчики D, F, B, H равны числу каналов в каждом состоянии
METHOD PRIVATE CountersReportStates
VAR
    aeCh  : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF E_ChannelState;   // состояния каналов
    stRes : ST_VoteResult;                                           // результат
END_VAR
