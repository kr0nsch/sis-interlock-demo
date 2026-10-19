// Причины 1 и 3 фиксируются в одном вызове: первопричина — младшая (1), в маске — обе (D-08);
// события CauseTrip — по возрастанию индекса
METHOD PRIVATE FirstOutSimultaneousLowestAndMask
VAR
    fbRig : FB_CemRig;     // стенд
    stEv  : ST_SisEvent;   // событие
END_VAR
