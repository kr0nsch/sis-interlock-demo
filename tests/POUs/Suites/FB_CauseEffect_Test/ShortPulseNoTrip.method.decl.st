// Требование 1,9 с при задержке 2 с не фиксируется (CauseDemand, CauseClear); новое требование
// отсчитывает задержку заново
METHOD PRIVATE ShortPulseNoTrip
VAR
    fbRig : FB_CemRig;   // стенд
END_VAR
