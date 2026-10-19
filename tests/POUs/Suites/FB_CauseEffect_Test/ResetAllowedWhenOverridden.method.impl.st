coUnit.TEST('Cem_Reset_AllowedWhenOverridden');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.axCauseIn[3] := TRUE;
fbRig.Step(tStep := T#100MS);
fbRig.axCauseIn[3] := FALSE;
fbRig.stCmd.wOverrideReq := 16#0002;
fbRig.axCauseIn[2] := TRUE;
fbRig.Step(tStep := T#100MS);
AssertEquals_WORD(Expected := 16#0002, Actual := fbRig.fbCem.stSts.wOverridden, Message := 'cause 2 overridden');
AssertTrue(Condition := fbRig.fbCem.stSts.xResetPermitted, Message := 'overridden demand does not block reset');
fbRig.PressReset();
AssertEquals_UINT(Expected := 1, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.ResetDone),
    Message := 'ResetDone');
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := 'latches cleared');
AssertTrue(Condition := fbRig.Out(uiEffect := 1), Message := 'effect 1 energized under override');
AssertTrue(Condition := fbRig.Out(uiEffect := 2), Message := 'effect 2 restored');
AssertEquals_WORD(Expected := 16#0002, Actual := fbRig.fbCem.stSts.wOverridden, Message := 'reset keeps override');
coUnit.TEST_FINISHED();
