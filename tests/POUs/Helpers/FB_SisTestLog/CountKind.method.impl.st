uiHits := 0;
FOR uiBack := 0 TO GVL_Const.SIS_LOG_SIZE - 1 DO
    IF uiBack < uiUsed THEN
        stEv := GetEvent(uiBack := uiBack);
        IF stEv.eKind = eKind THEN
            uiHits := uiHits + 1;
        END_IF
    END_IF
END_FOR
CountKind := uiHits;
