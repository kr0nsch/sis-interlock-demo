IF itfLog <> 0 THEN
    stEvent.ltTime := ltTime;
    stEvent.udiSeq := 0;
    stEvent.rValue := rValue;
    stEvent.eKind := eKind;
    stEvent.uiCause := uiCause;
    stEvent.uiEffect := uiEffect;
    stEvent.uiChannel := uiChannel;
    F_SisLogEvent := itfLog.AddEvent(stEvent := stEvent);
ELSE
    F_SisLogEvent := FALSE;
END_IF
