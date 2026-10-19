HasEvent := FALSE;
uiBack := 0;
xNewer := TRUE;
WHILE xNewer AND uiBack < fbLog.Count DO
    stEv := fbLog.GetEvent(uiBack := uiBack);
    xNewer := stEv.udiSeq > udiMark;
    HasEvent := HasEvent OR (xNewer AND stEv.eKind = eKind AND stEv.uiCause = uiCause);
    uiBack := uiBack + 1;
END_WHILE
