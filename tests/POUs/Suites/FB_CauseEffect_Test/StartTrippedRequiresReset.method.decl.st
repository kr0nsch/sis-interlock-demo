// xStartTripped = TRUE: после старта все следствия сработали (StartTrip, затем FirstOut START), пока
// оператор не выполнит сброс
METHOD PRIVATE StartTrippedRequiresReset
VAR
    fbRig : FB_CemRig;     // стенд
    stEv  : ST_SisEvent;   // событие
END_VAR
