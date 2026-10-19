coUnit.TEST('Cem_FirstOut_TimestampFromSource');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.SetNow(ltValue := LTIME#5H7M);
fbRig.axCauseIn[3] := TRUE;
fbRig.Cycle();
AssertEquals_LTIME(Expected := LTIME#5H7M, Actual := fbRig.fbCem.stSts.ltFirstOut,
    Message := 'first-out time = source');
stEv := fbRig.fbLog.LastOfKind(eKind := E_SisEventKind.FirstOut);
AssertEquals_LTIME(Expected := LTIME#5H7M, Actual := stEv.ltTime, Message := 'FirstOut event time = source');
AssertEquals_UINT(Expected := 3, Actual := stEv.uiCause, Message := 'FirstOut event: cause 3');
coUnit.TEST_FINISHED();
