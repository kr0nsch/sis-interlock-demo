// Каналы с номером больше N не голосуют: 1oo1 с требованием на каналах 2 и 3 — нет срабатывания
METHOD PRIVATE ChannelsBeyondNIgnored
VAR
    aeCh  : ARRAY[1..GVL_Const.SIS_VOTE_CH_MAX] OF E_ChannelState;   // состояния каналов
    stRes : ST_VoteResult;                                           // результат
END_VAR
