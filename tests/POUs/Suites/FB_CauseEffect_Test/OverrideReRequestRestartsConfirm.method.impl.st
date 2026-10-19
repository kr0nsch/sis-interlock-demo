coUnit.TEST('Cem_Override_ReRequestRestartsConfirm');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.stCmd.wOverrideReq := 16#0004;
fbRig.Step(tStep := T#100MS);                                   // t1: обход причины 3 без требования
AssertEquals_WORD(Expected := 16#0004, Actual := fbRig.fbCem.stSts.wOverridden, Message := 't1: override accepted');
AssertEquals_TIME(Expected := T#2S, Actual := fbRig.fbCem.stSts.atOverrideClearRemain[3],
    Message := 't1: confirm counts from acceptance');
fbRig.Run(tDuration := T#1S500MS, tStep := T#100MS);            // t1 + 1,5 с
AssertEquals_TIME(Expected := T#500MS, Actual := fbRig.fbCem.stSts.atOverrideClearRemain[3],
    Message := 't1 + 1.5 s: 500 ms of confirm left');
fbRig.stCmd.wOverrideReq := 16#0004;
fbRig.Step(tStep := T#100MS);                                   // t1 + 1,6 с: повторный запрос
AssertEquals_TIME(Expected := T#400MS, Actual := fbRig.fbCem.stSts.atOverrideClearRemain[3],
    Message := 'repeat request: confirm not restarted');
fbRig.stCmd.wOverrideCancel := 16#0004;
fbRig.stCmd.wOverrideReq := 16#0004;
fbRig.Step(tStep := T#100MS);                                   // t2 = t1 + 1,7 с: снятие и запрос
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.OverrideOff), Actual := fbRig.fbLog.KindAt(uiBack := 1),
    Message := 't2: OverrideOff');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.OverrideOn), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := 't2: then OverrideOn');
AssertEquals_TIME(Expected := T#2S, Actual := fbRig.fbCem.stSts.atOverrideClearRemain[3],
    Message := 't2: new override, full confirm');
fbRig.Run(tDuration := T#1S900MS, tStep := T#100MS);            // t2 + 1,9 с (позже t1 + 2 с)
AssertEquals_WORD(Expected := 16#0004, Actual := fbRig.fbCem.stSts.wOverridden,
    Message := 't2 + 1.9 s: override still active');
AssertEquals_UINT(Expected := 0, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.OverrideCleared),
    Message := 't2 + 1.9 s: no OverrideCleared');
fbRig.Step(tStep := T#100MS);                                   // t2 + 2 с
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.OverrideCleared), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := 't2 + 2 s: OverrideCleared');
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wOverridden, Message := 't2 + 2 s: override cleared');
fbRig.stCmd.wOverrideReq := 16#0004;
fbRig.Step(tStep := T#100MS);                                   // t3: запрос сразу после автоснятия
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.OverrideOn), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := 't3: last event OverrideOn');
AssertEquals_WORD(Expected := 16#0004, Actual := fbRig.fbCem.stSts.wOverridden, Message := 't3: override active');
AssertEquals_TIME(Expected := T#2S, Actual := fbRig.fbCem.stSts.atOverrideClearRemain[3],
    Message := 't3: full confirm again');
coUnit.TEST_FINISHED();
