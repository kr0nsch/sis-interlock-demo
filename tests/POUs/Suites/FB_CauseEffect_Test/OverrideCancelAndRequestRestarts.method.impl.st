coUnit.TEST('Cem_Override_CancelAndRequestRestarts');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.stCmd.wOverrideReq := 16#0004;
fbRig.axCauseIn[3] := TRUE;
fbRig.Step(tStep := T#100MS);                                   // t1: обход причины 3 (10 с) и требование
fbRig.Run(tDuration := T#6S, tStep := T#1S);                    // t1 + 6 с
AssertEquals_TIME(Expected := T#4S, Actual := fbRig.fbCem.stSts.atOverrideRemain[3], Message := 't1 + 6 s: 4 s left');
fbRig.stCmd.wOverrideCancel := 16#0004;
fbRig.stCmd.wOverrideReq := 16#0004;
fbRig.Step(tStep := T#100MS);                                   // t2: снятие и запрос в одном вызове
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.OverrideOff), Actual := fbRig.fbLog.KindAt(uiBack := 1),
    Message := 't2: OverrideOff');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.OverrideOn), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := 't2: then OverrideOn');
AssertEquals_TIME(Expected := T#10S, Actual := fbRig.fbCem.stSts.atOverrideRemain[3],
    Message := 't2: new override counts full 10 s');
fbRig.Run(tDuration := T#9S900MS, tStep := T#100MS);
AssertEquals_WORD(Expected := 16#0004, Actual := fbRig.fbCem.stSts.wOverridden, Message := 't2 + 9.9 s: active');
fbRig.Step(tStep := T#100MS);
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wOverridden, Message := 't2 + 10 s: expired');
coUnit.TEST_FINISHED();
