coUnit.TEST('Cem_CfgErrorRecovered_NeedsReset');
fbRig.stCfg := CfgBase();
fbRig.stCfg.wMatrixCrc := fbRig.stCfg.wMatrixCrc XOR 16#0001;
fbRig.Cycle();
AssertTrue(Condition := fbRig.fbCem.stSts.xCfgError, Message := 'config error');
fbRig.stCfg := CfgBase();
fbRig.Step(tStep := T#1S);
AssertFalse(Condition := fbRig.fbCem.stSts.xCfgError, Message := 'config fixed');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.CfgOk), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := 'event CfgOk');
AssertTrue(Condition := fbRig.fbCem.xTripped, Message := 'still tripped until reset');
AssertFalse(Condition := fbRig.Out(uiEffect := 1), Message := 'effect 1 still de-energized');
AssertEquals_UINT(Expected := GVL_Const.SIS_FIRST_OUT_CFG, Actual := fbRig.fbCem.stSts.uiFirstOut,
    Message := 'first-out CFG kept');
AssertTrue(Condition := fbRig.fbCem.stSts.xResetPermitted, Message := 'reset permitted after fix');
fbRig.PressReset();
AssertFalse(Condition := fbRig.fbCem.xTripped, Message := 'after reset: not tripped');
AssertTrue(Condition := fbRig.Out(uiEffect := 1), Message := 'after reset: effect 1 energized');
AssertTrue(Condition := fbRig.Out(uiEffect := 3), Message := 'after reset: effect 3 energized');
AssertEquals_UINT(Expected := 0, Actual := fbRig.fbCem.stSts.uiFirstOut, Message := 'after reset: no first-out');
AssertEquals_UINT(Expected := 3, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.EffectRestore),
    Message := 'EffectRestore for 3 effects');
coUnit.TEST_FINISHED();
