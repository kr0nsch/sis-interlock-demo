coUnit.TEST('Cem_TimeBackwards_DuringConfirmEndsOverride');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.stCmd.wOverrideReq := 16#0002;
fbRig.axCauseIn[2] := TRUE;
fbRig.Step(tStep := T#100MS);                                   // t1: обход причины 2 и требование
fbRig.Run(tDuration := T#10S, tStep := T#1S);
fbRig.axCauseIn[2] := FALSE;
fbRig.Step(tStep := T#100MS);                                   // t2: требование ушло
ltT2 := fbRig.Now();
fbRig.Run(tDuration := T#20S, tStep := T#1S);                   // t2 + 20 с
AssertEquals_TIME(Expected := T#10S, Actual := fbRig.fbCem.stSts.atOverrideClearRemain[2],
    Message := 't2 + 20 s: 10 s of confirm left');
fbRig.SetNow(ltValue := ltT2 - LTIME#1S);
fbRig.Cycle();                                                  // время назад
AssertEquals_UINT(Expected := 1, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.TimeFault),
    Message := 'time back: TimeFault');
AssertEquals_UINT(Expected := 1, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.OverrideExpired),
    Message := 'time back: override ended as OverrideExpired');
AssertEquals_UINT(Expected := 0, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.OverrideCleared),
    Message := 'time back: not reported as OverrideCleared');
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wOverridden, Message := 'time back: override ended');
AssertEquals_TIME(Expected := T#0S, Actual := fbRig.fbCem.stSts.atOverrideClearRemain[2],
    Message := 'time back: confirm reset');
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := 'time back: no latch');
AssertTrue(Condition := fbRig.Out(uiEffect := 1), Message := 'time back: effect 1 energized');
fbRig.Run(tDuration := T#40S, tStep := T#1S);
AssertEquals_UINT(Expected := 0, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.OverrideCleared),
    Message := 'no late OverrideCleared');
fbRig.axCauseIn[2] := TRUE;
fbRig.Step(tStep := T#100MS);                                   // t3: новое требование
fbRig.Run(tDuration := T#4S900MS, tStep := T#100MS);
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := 't3 + 4.9 s: delay running');
fbRig.Step(tStep := T#100MS);
AssertEquals_WORD(Expected := 16#0002, Actual := fbRig.fbCem.stSts.wCauseLatched,
    Message := 't3 + 5 s: protection active, latched');
coUnit.TEST_FINISHED();
