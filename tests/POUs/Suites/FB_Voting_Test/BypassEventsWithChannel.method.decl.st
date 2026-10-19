// События байпаса несут номер причины, номер канала и метку источника времени
METHOD PRIVATE BypassEventsWithChannel
VAR
    fbRig : FB_VotingRig;   // стенд
    stEv  : ST_SisEvent;    // событие
    ltOn  : LTIME;          // момент включения
END_VAR
