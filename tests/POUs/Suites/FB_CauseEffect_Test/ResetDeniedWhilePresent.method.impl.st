coUnit.TEST('Cem_Reset_DeniedWhilePresent');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.axCauseIn[3] := TRUE;
fbRig.Step(tStep := T#100MS);
AssertFalse(Condition := fbRig.fbCem.stSts.xResetPermitted, Message := 'reset not permitted');
AssertEquals_UINT(Expected := 3, Actual := fbRig.fbCem.stSts.uiResetBlocker, Message := 'blocker cause 3');
fbRig.PressReset();
stEv := fbRig.fbLog.GetEvent(uiBack := 0);
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.ResetDenied), Actual := TO_INT(stEv.eKind),
    Message := 'ResetDenied');
AssertEquals_UINT(Expected := 3, Actual := stEv.uiCause, Message := 'ResetDenied: cause 3');
AssertEquals_WORD(Expected := 16#0004, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := 'still latched');
AssertFalse(Condition := fbRig.Out(uiEffect := 2), Message := 'effect 2 still tripped');
coUnit.TEST_FINISHED();
