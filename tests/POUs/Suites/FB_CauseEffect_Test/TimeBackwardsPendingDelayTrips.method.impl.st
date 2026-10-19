coUnit.TEST('Cem_TimeBackwards_PendingDelayTrips');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.axCauseIn[1] := TRUE;
fbRig.Step(tStep := T#100MS);                                   // t0: требование причины 1 (задержка 2 с)
ltT0 := fbRig.Now();
fbRig.Run(tDuration := T#1S500MS, tStep := T#100MS);
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := '1.5 s: pending, not latched');
fbRig.SetNow(ltValue := ltT0 - LTIME#1S);
fbRig.Cycle();                                                  // время назад
AssertEquals_UINT(Expected := 1, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.TimeFault),
    Message := 'time back: one TimeFault event');
AssertEquals_WORD(Expected := 16#0001, Actual := fbRig.fbCem.stSts.wCauseLatched,
    Message := 'time back: pending cause 1 latched at once, cause 2 without demand not');
AssertEquals_UINT(Expected := 1, Actual := fbRig.fbCem.stSts.uiFirstOut, Message := 'time back: first-out cause 1');
AssertFalse(Condition := fbRig.Out(uiEffect := 1), Message := 'time back: effect 1 tripped');
AssertTrue(Condition := fbRig.Out(uiEffect := 2), Message := 'time back: effect 2 energized');
fbRig.Step(tStep := T#100MS);
AssertEquals_UINT(Expected := 1, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.TimeFault),
    Message := 'time forward again: no new TimeFault');
coUnit.TEST_FINISHED();
