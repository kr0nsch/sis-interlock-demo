// Запрос обхода причины без xOverrideAllowed и выключенной причины — OverrideDenied, обхода нет
METHOD PRIVATE OverrideDeniedNotAllowed
VAR
    fbRig : FB_CemRig;     // стенд
    stEv  : ST_SisEvent;   // событие
END_VAR
