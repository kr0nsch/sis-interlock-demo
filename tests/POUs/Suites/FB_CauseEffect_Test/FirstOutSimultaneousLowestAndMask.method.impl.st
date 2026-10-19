coUnit.TEST('Cem_FirstOut_SimultaneousLowestAndMask');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.axCauseIn[1] := TRUE;
fbRig.Step(tStep := T#100MS);                                   // t0: задержка причины 1 пошла
fbRig.Run(tDuration := T#1S900MS, tStep := T#100MS);            // t0 + 1,9 с
fbRig.axCauseIn[3] := TRUE;
fbRig.Step(tStep := T#100MS);                                   // t0 + 2,0 с: обе
AssertEquals_UINT(Expected := 1, Actual := fbRig.fbCem.stSts.uiFirstOut, Message := 'first-out: lowest index 1');
AssertEquals_WORD(Expected := 16#0005, Actual := fbRig.fbCem.stSts.wFirstOutMask, Message := 'first-out mask: 1 and 3');
stEv := fbRig.fbLog.LastOfKind(eKind := E_SisEventKind.CauseTrip);
AssertEquals_UINT(Expected := 3, Actual := stEv.uiCause, Message := 'last CauseTrip: cause 3');
AssertEquals_UINT(Expected := 2, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.CauseTrip),
    Message := 'two CauseTrip');
coUnit.TEST_FINISHED();
