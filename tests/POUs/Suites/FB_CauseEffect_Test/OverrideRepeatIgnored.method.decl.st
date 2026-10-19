// Повторный запрос действующего обхода игнорируется: событий нет, срок не продлевается (D-13)
METHOD PRIVATE OverrideRepeatIgnored
VAR
    fbRig    : FB_CemRig;   // стенд
    uiEvents : UINT;        // событий до повторного запроса
END_VAR
