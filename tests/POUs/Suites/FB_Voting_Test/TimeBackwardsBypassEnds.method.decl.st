// «Время назад» во время байпаса (D-19): срок байпаса недостоверен — байпас заканчивается в том же
// вызове (TimeFault, затем BypassExpired), канал возвращается в голосование; новый байпас — только
// после снятия запроса, и он отсчитывается полностью
METHOD PRIVATE TimeBackwardsBypassEnds
VAR
    fbRig : FB_VotingRig;   // стенд
    ltT0  : LTIME;          // момент включения байпаса
    stEv  : ST_SisEvent;    // событие
END_VAR
