// Сброс при требовании причины: ResetDenied с номером мешающей причины, состояние не меняется
METHOD PRIVATE ResetDeniedWhilePresent
VAR
    fbRig : FB_CemRig;     // стенд
    stEv  : ST_SisEvent;   // событие
END_VAR
