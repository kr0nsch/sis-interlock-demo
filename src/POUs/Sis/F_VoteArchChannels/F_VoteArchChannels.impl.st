CASE eArch OF
    E_VoteArch.Vote1oo1:
        F_VoteArchChannels := 1;
    E_VoteArch.Vote1oo2, E_VoteArch.Vote2oo2:
        F_VoteArchChannels := 2;
    E_VoteArch.Vote2oo3:
        F_VoteArchChannels := GVL_Const.VOTE_2OO3_CHANNELS;
ELSE
    // None, ForcedTrip и значения вне перечисления — схемы нет
    F_VoteArchChannels := 0;
END_CASE
