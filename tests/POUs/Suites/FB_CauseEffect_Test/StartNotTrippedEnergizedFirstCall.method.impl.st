coUnit.TEST('Cem_StartNotTripped_EnergizedFirstCall');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
AssertTrue(Condition := fbRig.Out(uiEffect := 1), Message := 'effect 1 energized');
AssertTrue(Condition := fbRig.Out(uiEffect := 2), Message := 'effect 2 energized');
AssertTrue(Condition := fbRig.Out(uiEffect := 3), Message := 'effect 3 energized');
AssertFalse(Condition := fbRig.Out(uiEffect := 4), Message := 'unused effect 4 de-energized');
AssertFalse(Condition := fbRig.fbCem.xTripped, Message := 'not tripped');
AssertEquals_UINT(Expected := 0, Actual := fbRig.fbCem.stSts.uiFirstOut, Message := 'no first-out');
AssertEquals_UINT(Expected := 3, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.EffectRestore),
    Message := 'EffectRestore for 3 used effects');
coUnit.TEST_FINISHED();
