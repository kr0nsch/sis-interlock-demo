xFound := FALSE;
FOR uiBack := 0 TO GVL_Const.SIS_LOG_SIZE - 1 DO
    IF NOT xFound AND uiBack < uiUsed THEN
        stEv := GetEvent(uiBack := uiBack);
        IF stEv.eKind = eKind THEN
            stFound := stEv;
            xFound := TRUE;
        END_IF
    END_IF
END_FOR
LastOfKind := stFound;
