coUnit.TEST('Cem_Override_ExpiryWinsTieWithConfirm');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.stCmd.wOverrideReq := 16#0004;
fbRig.axCauseIn[3] := TRUE;
fbRig.Step(tStep := T#100MS);                                   // t1: обход причины 3 и требование
fbRig.Run(tDuration := T#7S900MS, tStep := T#100MS);            // t1 + 7,9 с: требование ещё есть
fbRig.axCauseIn[3] := FALSE;
fbRig.Step(tStep := T#100MS);                                   // t1 + 8 с: норма, подтверждение 2 с
fbRig.Run(tDuration := T#1S900MS, tStep := T#100MS);            // t1 + 9,9 с
AssertEquals_WORD(Expected := 16#0004, Actual := fbRig.fbCem.stSts.wOverridden,
    Message := 't1 + 9.9 s: override still active');
AssertEquals_TIME(Expected := T#100MS, Actual := fbRig.fbCem.stSts.atOverrideRemain[3],
    Message := 't1 + 9.9 s: 100 ms of override left');
AssertEquals_TIME(Expected := T#100MS, Actual := fbRig.fbCem.stSts.atOverrideClearRemain[3],
    Message := 't1 + 9.9 s: 100 ms of confirm left');
fbRig.Step(tStep := T#100MS);                                   // t1 + 10 с: оба отсчёта закончились
AssertEquals_UINT(Expected := 1, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.OverrideExpired),
    Message := 'tie: OverrideExpired');
AssertEquals_UINT(Expected := 0, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.OverrideCleared),
    Message := 'tie: no OverrideCleared');
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wOverridden, Message := 'tie: override removed');
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := 'tie: no demand, no latch');
coUnit.TEST_FINISHED();
