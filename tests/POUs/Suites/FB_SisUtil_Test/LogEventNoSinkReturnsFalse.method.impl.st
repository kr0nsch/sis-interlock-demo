coUnit.TEST('Sis_LogEvent_NoSinkReturnsFalse');
xRes := F_SisLogEvent(itfLog := itfNone, ltTime := LTIME#2H, eKind := E_SisEventKind.CauseTrip, uiCause := 3,
    uiEffect := 0, uiChannel := 0, rValue := 0.0);
AssertFalse(Condition := xRes, Message := 'no sink: FALSE');
xRes := F_SisLogEvent(itfLog := fbLog, ltTime := LTIME#2H, eKind := E_SisEventKind.EffectTrip, uiCause := 3,
    uiEffect := 5, uiChannel := 2, rValue := 1.5);
AssertTrue(Condition := xRes, Message := 'sink: TRUE');
stEv := fbLog.GetEvent(uiBack := 0);
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.EffectTrip), Actual := TO_INT(stEv.eKind), Message := 'kind');
AssertEquals_LTIME(Expected := LTIME#2H, Actual := stEv.ltTime, Message := 'time');
AssertEquals_UINT(Expected := 3, Actual := stEv.uiCause, Message := 'cause');
AssertEquals_UINT(Expected := 5, Actual := stEv.uiEffect, Message := 'effect');
AssertEquals_UINT(Expected := 2, Actual := stEv.uiChannel, Message := 'channel');
AssertEquals_REAL(Expected := 1.5, Actual := stEv.rValue, Delta := 0.0, Message := 'value');
AssertEquals_UDINT(Expected := 1, Actual := stEv.udiSeq, Message := 'seq assigned by log');
coUnit.TEST_FINISHED();
