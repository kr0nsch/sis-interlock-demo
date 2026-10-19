// Пусковой обход причины 2 (15 мин) и её требование в одном вызове t1: не фиксируется; на
// t1 + 14 мин 59,9 с обход действует (остаток 100 мс); на t1 + 15 мин — OverrideExpired, FirstOut,
// CauseTrip, EffectTrip в одном вызове (задержка 5 с прошла во время обхода)
METHOD PRIVATE OverrideExpiresExactly
VAR
    fbRig : FB_CemRig;   // стенд
END_VAR
