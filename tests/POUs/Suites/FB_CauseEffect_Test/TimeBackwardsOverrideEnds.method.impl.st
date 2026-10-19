coUnit.TEST('Cem_TimeBackwards_OverrideEnds');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.stCmd.wOverrideReq := 16#0002;
fbRig.axCauseIn[2] := TRUE;
fbRig.Step(tStep := T#100MS);                                   // t1: обход причины 2 (15 мин) и требование
ltT1 := fbRig.Now();
fbRig.Run(tDuration := T#1M, tStep := T#10S);
AssertEquals_WORD(Expected := 16#0002, Actual := fbRig.fbCem.stSts.wOverridden,
    Message := 't1 + 1 min: override active');
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := 't1 + 1 min: not latched');
fbRig.SetNow(ltValue := ltT1 - LTIME#1S);
fbRig.Cycle();                                                  // время назад
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wOverridden, Message := 'time back: override ended');
AssertEquals_TIME(Expected := T#0S, Actual := fbRig.fbCem.stSts.atOverrideRemain[2],
    Message := 'time back: no override left');
AssertEquals_UINT(Expected := 1, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.OverrideExpired),
    Message := 'time back: OverrideExpired logged');
AssertEquals_WORD(Expected := 16#0002, Actual := fbRig.fbCem.stSts.wCauseLatched,
    Message := 'time back: cause 2 latched in the same call');
AssertFalse(Condition := fbRig.Out(uiEffect := 1), Message := 'time back: effect 1 tripped');
coUnit.TEST_FINISHED();
