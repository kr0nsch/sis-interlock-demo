CASE eArch OF
    E_VoteArch.Vote1oo1, E_VoteArch.Vote1oo2:
        F_VoteArchRequired := 1;
    E_VoteArch.Vote2oo2, E_VoteArch.Vote2oo3:
        F_VoteArchRequired := 2;
ELSE
    // None, ForcedTrip и значения вне перечисления — схемы нет
    F_VoteArchRequired := 0;
END_CASE
