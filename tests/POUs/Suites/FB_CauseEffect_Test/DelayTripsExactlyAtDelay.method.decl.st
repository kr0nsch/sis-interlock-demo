// Причина 1 с задержкой 2 с: на t0 + 1,9 с не зафиксирована (остаток 100 мс), на t0 + 2,0 с —
// FirstOut, CauseTrip, следствия 1 и 3 обесточены, метка первопричины t0 + 2 с
METHOD PRIVATE DelayTripsExactlyAtDelay
VAR
    fbRig : FB_CemRig;   // стенд
    ltT0  : LTIME;       // момент появления требования
END_VAR
