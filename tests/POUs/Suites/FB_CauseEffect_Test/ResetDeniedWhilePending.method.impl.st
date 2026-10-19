coUnit.TEST('Cem_Reset_DeniedWhilePending');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.axCauseIn[3] := TRUE;
fbRig.Step(tStep := T#100MS);
fbRig.axCauseIn[3] := FALSE;
fbRig.axCauseIn[1] := TRUE;
fbRig.Step(tStep := T#1S);
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wCauseActive AND 16#0001, Message := 'cause 1 pending');
fbRig.PressReset();
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.ResetDenied), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := 'pending cause blocks reset');
AssertEquals_UINT(Expected := 1, Actual := fbRig.fbCem.stSts.uiResetBlocker, Message := 'blocker cause 1');
AssertEquals_WORD(Expected := 16#0004, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := 'cause 3 still latched');
coUnit.TEST_FINISHED();
