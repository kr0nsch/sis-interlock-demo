coUnit.TEST('Cem_FirstOut_RecordsEarliest');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.axCauseIn[3] := TRUE;
fbRig.Step(tStep := T#100MS);                                   // t0
ltT0 := fbRig.Now();
fbRig.axCauseIn[1] := TRUE;
fbRig.Run(tDuration := T#3S, tStep := T#100MS);
AssertEquals_UINT(Expected := 3, Actual := fbRig.fbCem.stSts.uiFirstOut, Message := 'first-out cause 3');
AssertEquals_WORD(Expected := 16#0004, Actual := fbRig.fbCem.stSts.wFirstOutMask, Message := 'first-out mask: 3 only');
AssertEquals_LTIME(Expected := ltT0, Actual := fbRig.fbCem.stSts.ltFirstOut, Message := 'first-out time t0');
AssertEquals_WORD(Expected := 16#0005, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := 'causes 1 and 3 latched');
AssertEquals_UDINT(Expected := 1, Actual := fbRig.fbCem.stSts.udiTripCount, Message := 'one first-out');
AssertEquals_UINT(Expected := 1, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.FirstOut),
    Message := 'one FirstOut event');
coUnit.TEST_FINISHED();
