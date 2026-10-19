coUnit.TEST('Cem_Delay_TripsExactlyAtDelay');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.axCauseIn[1] := TRUE;
fbRig.Step(tStep := T#100MS);                                   // t0
ltT0 := fbRig.Now();
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.CauseDemand), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := 't0: CauseDemand');
AssertEquals_TIME(Expected := T#2S, Actual := fbRig.fbCem.stSts.atDelayRemain[1], Message := 't0: 2 s left');
AssertTrue(Condition := fbRig.Out(uiEffect := 1), Message := 't0: effect 1 energized');
fbRig.Run(tDuration := T#1S900MS, tStep := T#100MS);            // t0 + 1,9 с
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := 't0 + 1.9 s: not latched');
AssertTrue(Condition := fbRig.Out(uiEffect := 1), Message := 't0 + 1.9 s: effect 1 energized');
AssertEquals_TIME(Expected := T#100MS, Actual := fbRig.fbCem.stSts.atDelayRemain[1],
    Message := 't0 + 1.9 s: 100 ms left');
fbRig.Step(tStep := T#100MS);                                   // t0 + 2,0 с
AssertEquals_WORD(Expected := 16#0001, Actual := fbRig.fbCem.stSts.wCauseLatched,
    Message := 't0 + 2 s: cause 1 latched');
AssertFalse(Condition := fbRig.Out(uiEffect := 1), Message := 't0 + 2 s: effect 1 tripped');
AssertTrue(Condition := fbRig.Out(uiEffect := 2), Message := 't0 + 2 s: effect 2 not in mask, energized');
AssertFalse(Condition := fbRig.Out(uiEffect := 3), Message := 't0 + 2 s: effect 3 tripped');
AssertEquals_UINT(Expected := 1, Actual := fbRig.fbCem.stSts.uiFirstOut, Message := 'first-out cause 1');
AssertEquals_LTIME(Expected := ltT0 + LTIME#2S, Actual := fbRig.fbCem.stSts.ltFirstOut,
    Message := 'first-out at t0 + 2 s');
AssertEquals_TIME(Expected := T#0S, Actual := fbRig.fbCem.stSts.atDelayRemain[1],
    Message := 'no countdown after delay');
coUnit.TEST_FINISHED();
