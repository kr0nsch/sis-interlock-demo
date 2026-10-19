IF uiBack < uiUsed THEN
    // uiBack < uiUsed <= SIS_LOG_SIZE: выражение не уходит в минус
    uiIdx := (uiNext + GVL_Const.SIS_LOG_SIZE - 1 - uiBack) MOD GVL_Const.SIS_LOG_SIZE;
    GetEvent := astRing[uiIdx];
ELSE
    GetEvent := stEmpty;
END_IF
