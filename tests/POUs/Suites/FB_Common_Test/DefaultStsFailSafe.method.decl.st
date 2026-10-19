// Умолчания состояний: ST_VoteResult и ST_VotingSts — срабатывание без схемы; свежий FB_Voting —
// xTrip = TRUE, свежий FB_CauseEffect — xTripped = TRUE и все выходы FALSE (до первого вызова)
METHOD PRIVATE DefaultStsFailSafe
VAR
    stRes  : ST_VoteResult;    // результат по умолчанию
    stSts  : ST_VotingSts;     // состояние группы по умолчанию
    fbVote : FB_Voting;        // не вызывался
    fbCem  : FB_CauseEffect;   // не вызывался
    uiJ    : UINT;             // индекс следствия
    xAnyOn : BOOL;             // хотя бы один выход под напряжением
END_VAR
