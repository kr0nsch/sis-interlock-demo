coUnit.TEST('Cem_Override_ReRequestAfterExpiryFullTime');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.stCmd.wOverrideReq := 16#0004;
fbRig.axCauseIn[3] := TRUE;
fbRig.Step(tStep := T#100MS);                                   // t1: обход причины 3 (10 с) и требование
fbRig.Run(tDuration := T#10S, tStep := T#1S);                   // t1 + 10 с
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wOverridden, Message := 't1 + 10 s: expired');
fbRig.stCmd.wOverrideReq := 16#0004;
fbRig.Step(tStep := T#100MS);                                   // t2: новый запрос в следующем вызове
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.OverrideOn), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := 't2: last event OverrideOn');
AssertEquals_WORD(Expected := 16#0004, Actual := fbRig.fbCem.stSts.wOverridden, Message := 't2: override active');
AssertEquals_TIME(Expected := T#10S, Actual := fbRig.fbCem.stSts.atOverrideRemain[3], Message := 't2: full 10 s left');
fbRig.Run(tDuration := T#9S900MS, tStep := T#100MS);
AssertEquals_WORD(Expected := 16#0004, Actual := fbRig.fbCem.stSts.wOverridden, Message := 't2 + 9.9 s: active');
fbRig.Step(tStep := T#100MS);
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wOverridden, Message := 't2 + 10 s: expired');
coUnit.TEST_FINISHED();
