coUnit.TEST('Cem_Override_CancelRestoresTrip');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.stCmd.wOverrideReq := 16#0004;
fbRig.axCauseIn[3] := TRUE;
fbRig.Step(tStep := T#100MS);
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := 'overridden: not latched');
AssertTrue(Condition := fbRig.Out(uiEffect := 2), Message := 'overridden: effect 2 energized');
fbRig.stCmd.wOverrideCancel := 16#0004;
fbRig.Step(tStep := T#100MS);
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wOverridden, Message := 'override cancelled');
AssertEquals_WORD(Expected := 16#0004, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := 'latched in same call');
AssertFalse(Condition := fbRig.Out(uiEffect := 2), Message := 'effect 2 tripped');
AssertEquals_UINT(Expected := 1, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.OverrideOff),
    Message := 'OverrideOff');
coUnit.TEST_FINISHED();
