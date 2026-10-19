// Общий пусковой обход ставит обходы только включённым причинам с xOverrideAllowed (2 и 3), без
// событий отказа для остальных
METHOD PRIVATE OverrideStartupMaskAllowedOnly
VAR
    fbRig : FB_CemRig;   // стенд
END_VAR
