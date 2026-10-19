coUnit.TEST('Log_Ring_OverwritesOldest');
stEv.eKind := E_SisEventKind.CauseDemand;
FOR uiI := 1 TO 70 DO
    stEv.uiCause := uiI;
    xAdded := fbLog.AddEvent(stEvent := stEv);
    xAll := xAll AND xAdded;
END_FOR
AssertTrue(Condition := xAll, Message := 'AddEvent always TRUE');
AssertEquals_UINT(Expected := 64, Actual := fbLog.Count, Message := 'ring full: 64');
AssertEquals_UDINT(Expected := 70, Actual := fbLog.LastSeq, Message := 'last seq 70');
stEv := fbLog.GetEvent(uiBack := 0);
AssertEquals_UDINT(Expected := 70, Actual := stEv.udiSeq, Message := 'newest: seq 70');
AssertEquals_UINT(Expected := 70, Actual := stEv.uiCause, Message := 'newest: cause 70');
stEv := fbLog.GetEvent(uiBack := 63);
AssertEquals_UDINT(Expected := 7, Actual := stEv.udiSeq, Message := 'oldest kept: seq 7');
AssertEquals_UINT(Expected := 7, Actual := stEv.uiCause, Message := 'oldest kept: cause 7');
coUnit.TEST_FINISHED();
