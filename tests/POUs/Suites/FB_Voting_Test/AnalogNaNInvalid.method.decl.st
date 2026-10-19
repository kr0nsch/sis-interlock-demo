// NaN при флаге достоверности TRUE — канал недостоверен (событие ChannelInvalid), 2oo3 VoteTrip → 1oo2;
// память гистерезиса канала сбрасывается
METHOD PRIVATE AnalogNaNInvalid
VAR
    fbRig : FB_VotingRig;      // стенд
    uBits : PL.U_RealBits;     // значение REAL по битам IEEE 754
    stEv  : ST_SisEvent;       // событие
END_VAR
