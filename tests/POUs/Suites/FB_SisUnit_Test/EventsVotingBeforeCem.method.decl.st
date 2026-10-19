// В одном вызове события групп голосования идут раньше событий матрицы: ChannelInvalid группы 1,
// затем CauseDemand причины 1 (недостоверный канал 1oo2 VoteTrip даёт требование)
METHOD PRIVATE EventsVotingBeforeCem
VAR
    fbRig : FB_UnitRig;     // стенд
    stEv  : ST_SisEvent;    // событие
END_VAR
