// Задержка причины идёт и во время обхода: через 5 с причина 2 активна, но не зафиксирована; снятие
// обхода фиксирует её сразу, без нового отсчёта задержки
METHOD PRIVATE OverrideDelayRunsDuringOverride
VAR
    fbRig : FB_CemRig;   // стенд
END_VAR
