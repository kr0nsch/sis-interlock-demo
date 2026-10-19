coUnit.TEST('Cem_ResetHw_HeldAtStartIgnored');
fbRig.stCfg := CfgBase();
fbRig.stCfg.xStartTripped := TRUE;
fbRig.xResetHw := TRUE;
fbRig.Cycle();
fbRig.Step(tStep := T#100MS);
AssertTrue(Condition := fbRig.fbCem.xTripped, Message := 'button held at start: still tripped');
AssertEquals_UINT(Expected := 0, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.ResetDone),
    Message := 'no ResetDone');
fbRig.xResetHw := FALSE;
fbRig.Step(tStep := T#100MS);
fbRig.xResetHw := TRUE;
fbRig.Step(tStep := T#100MS);
AssertFalse(Condition := fbRig.fbCem.xTripped, Message := 'press after release: reset');
coUnit.TEST_FINISHED();
