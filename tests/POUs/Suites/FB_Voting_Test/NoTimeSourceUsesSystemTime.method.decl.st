// Без источника времени (itfTime = 0) группа работает от встроенного PL.FB_SystemTime: голосует,
// байпас включается с полным остатком
METHOD PRIVATE NoTimeSourceUsesSystemTime
VAR
    fbVote : FB_Voting;      // ФБ без источника времени
    stIn   : ST_VoteIn;      // входы
    stCmd  : ST_VoteCmd;     // запросы байпаса
    stCfg  : ST_VotingCfg;   // конфигурация
END_VAR
