// Снятие и новый запрос обхода в одном вызове (D-13: продление — явной отменой и новым запросом):
// OverrideOff, затем OverrideOn, и новый обход отсчитывается от этого вызова — полные 10 с
METHOD PRIVATE OverrideCancelAndRequestRestarts
VAR
    fbRig : FB_CemRig;   // стенд
END_VAR
