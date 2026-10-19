coUnit.TEST('Cem_ShortPulse_NoTrip');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.axCauseIn[1] := TRUE;
fbRig.Step(tStep := T#100MS);
fbRig.Run(tDuration := T#1S900MS, tStep := T#100MS);
fbRig.axCauseIn[1] := FALSE;
fbRig.Step(tStep := T#100MS);
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.CauseClear), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := 'CauseClear');
fbRig.axCauseIn[1] := TRUE;
fbRig.Step(tStep := T#100MS);
fbRig.Run(tDuration := T#1S900MS, tStep := T#100MS);
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wCauseLatched,
    Message := 'second pulse 1.9 s: not latched');
AssertTrue(Condition := fbRig.Out(uiEffect := 1), Message := 'effect 1 energized');
AssertEquals_UINT(Expected := 0, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.CauseTrip),
    Message := 'no CauseTrip');
coUnit.TEST_FINISHED();
