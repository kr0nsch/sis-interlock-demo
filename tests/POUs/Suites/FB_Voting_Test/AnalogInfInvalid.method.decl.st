// +Inf, -Inf и 1.0E31 (больше REAL_SANE_MAX) — недостоверны; три недостоверных при VoteTrip — ForcedTrip
METHOD PRIVATE AnalogInfInvalid
VAR
    fbRig  : FB_VotingRig;      // стенд
    uPlus  : PL.U_RealBits;     // +Inf
    uMinus : PL.U_RealBits;     // -Inf
END_VAR
