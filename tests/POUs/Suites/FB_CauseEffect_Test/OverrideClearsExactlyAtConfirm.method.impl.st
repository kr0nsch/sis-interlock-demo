coUnit.TEST('Cem_Override_ClearsExactlyAtConfirm');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.stCmd.wOverrideReq := 16#0002;
fbRig.axCauseIn[2] := TRUE;
fbRig.Step(tStep := T#100MS);                                   // t1: обход причины 2 и требование
AssertEquals_TIME(Expected := T#0S, Actual := fbRig.fbCem.stSts.atOverrideClearRemain[2],
    Message := 't1: demand present, no confirm running');
fbRig.Run(tDuration := T#10S, tStep := T#1S);                   // t1 + 10 с
AssertEquals_WORD(Expected := 16#0002, Actual := fbRig.fbCem.stSts.wCauseActive, Message := 'active under override');
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := 'not latched under override');
fbRig.axCauseIn[2] := FALSE;
fbRig.Step(tStep := T#100MS);                                   // t2: требование ушло
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.CauseClear), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := 't2: CauseClear');
AssertEquals_TIME(Expected := T#30S, Actual := fbRig.fbCem.stSts.atOverrideClearRemain[2],
    Message := 't2: confirm of normal 30 s');
fbRig.Run(tDuration := T#29S900MS, tStep := T#100MS);           // t2 + 29,9 с
AssertEquals_WORD(Expected := 16#0002, Actual := fbRig.fbCem.stSts.wOverridden,
    Message := 't2 + 29.9 s: override still active');
AssertEquals_TIME(Expected := T#100MS, Actual := fbRig.fbCem.stSts.atOverrideClearRemain[2],
    Message := 't2 + 29.9 s: 100 ms of confirm left');
AssertEquals_UINT(Expected := 0, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.OverrideCleared),
    Message := 't2 + 29.9 s: no OverrideCleared yet');
fbRig.Step(tStep := T#100MS);                                   // t2 + 30 с
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.OverrideCleared), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := 't2 + 30 s: OverrideCleared');
stEv := fbRig.fbLog.GetEvent(uiBack := 0);
AssertEquals_UINT(Expected := 2, Actual := stEv.uiCause, Message := 'OverrideCleared carries cause 2');
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wOverridden, Message := 't2 + 30 s: override cleared');
AssertEquals_TIME(Expected := T#0S, Actual := fbRig.fbCem.stSts.atOverrideRemain[2], Message := 'no override left');
AssertEquals_TIME(Expected := T#0S, Actual := fbRig.fbCem.stSts.atOverrideClearRemain[2],
    Message := 'no confirm left');
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := 'cleared without demand');
AssertTrue(Condition := fbRig.Out(uiEffect := 1), Message := 'effect 1 energized after clear');
fbRig.axCauseIn[2] := TRUE;
fbRig.Step(tStep := T#100MS);                                   // t3: новое требование
fbRig.Run(tDuration := T#4S900MS, tStep := T#100MS);            // t3 + 4,9 с
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wCauseLatched,
    Message := 't3 + 4.9 s: delay counts again from demand');
fbRig.Step(tStep := T#100MS);                                   // t3 + 5 с
AssertEquals_WORD(Expected := 16#0002, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := 't3 + 5 s: latched');
AssertFalse(Condition := fbRig.Out(uiEffect := 1), Message := 't3 + 5 s: effect 1 tripped');
coUnit.TEST_FINISHED();
