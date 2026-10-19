coUnit.TEST('Cem_DisabledCause_NeverTrips');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.axCauseIn[4] := TRUE;
fbRig.Run(tDuration := T#10S, tStep := T#1S);
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wCausePresent, Message := 'disabled: not present');
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := 'disabled: not latched');
AssertTrue(Condition := fbRig.Out(uiEffect := 3), Message := 'effect 3 energized');
AssertEquals_UINT(Expected := 0, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.CauseDemand),
    Message := 'no CauseDemand');
coUnit.TEST_FINISHED();
