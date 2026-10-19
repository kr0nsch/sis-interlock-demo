coUnit.TEST('Cem_Override_ExpiresExactly');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.stCmd.wOverrideReq := 16#0002;
fbRig.axCauseIn[2] := TRUE;
fbRig.Step(tStep := T#100MS);                                   // t1
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.CauseDemand), Actual := fbRig.fbLog.KindAt(uiBack := 1),
    Message := 't1: CauseDemand');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.OverrideOn), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := 't1: then OverrideOn');
AssertEquals_TIME(Expected := T#15M, Actual := fbRig.fbCem.stSts.atOverrideRemain[2], Message := 't1: 15 min left');
fbRig.Step(tStep := T#14M59S900MS);                             // t1 + 14 мин 59,9 с
AssertEquals_WORD(Expected := 16#0002, Actual := fbRig.fbCem.stSts.wOverridden, Message := 'override still active');
AssertEquals_TIME(Expected := T#100MS, Actual := fbRig.fbCem.stSts.atOverrideRemain[2], Message := '100 ms left');
AssertEquals_WORD(Expected := 16#0002, Actual := fbRig.fbCem.stSts.wCauseActive, Message := 'delay elapsed: active');
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := 'not latched under override');
AssertTrue(Condition := fbRig.Out(uiEffect := 1), Message := 'effect 1 energized under override');
fbRig.Step(tStep := T#100MS);                                   // t1 + 15 мин
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.OverrideExpired), Actual := fbRig.fbLog.KindAt(uiBack := 4),
    Message := 'OverrideExpired');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.FirstOut), Actual := fbRig.fbLog.KindAt(uiBack := 3),
    Message := 'then FirstOut');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.CauseTrip), Actual := fbRig.fbLog.KindAt(uiBack := 2),
    Message := 'then CauseTrip');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.EffectTrip), Actual := fbRig.fbLog.KindAt(uiBack := 1),
    Message := 'then EffectTrip');
AssertEquals_UINT(Expected := 2, Actual := fbRig.fbCem.stSts.uiFirstOut, Message := 'first-out cause 2');
AssertFalse(Condition := fbRig.Out(uiEffect := 1), Message := 'effect 1 tripped');
AssertEquals_TIME(Expected := T#0S, Actual := fbRig.fbCem.stSts.atOverrideRemain[2], Message := 'no override left');
coUnit.TEST_FINISHED();
