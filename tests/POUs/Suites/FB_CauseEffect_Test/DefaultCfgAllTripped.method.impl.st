coUnit.TEST('Cem_DefaultCfg_AllTripped');
AssertTrue(Condition := fbRig.fbCem.xTripped, Message := 'before first call: tripped');
fbRig.Cycle();
fbRig.PressReset();
xAnyOn := FALSE;
FOR uiJ := 1 TO GVL_Const.SIS_EFFECTS_MAX DO
    xAnyOn := xAnyOn OR fbRig.Out(uiEffect := uiJ);
END_FOR
AssertFalse(Condition := xAnyOn, Message := 'default cfg: all outputs de-energized');
AssertTrue(Condition := fbRig.fbCem.xTripped, Message := 'default cfg: tripped');
AssertTrue(Condition := fbRig.fbCem.stSts.xCfgError, Message := 'default cfg: config error');
AssertEquals_WORD(Expected := GVL_Const.CEM_CFG_COUNT,
    Actual := fbRig.fbCem.stSts.wCfgErr AND GVL_Const.CEM_CFG_COUNT, Message := 'default cfg: CEM_CFG_COUNT');
AssertEquals_UINT(Expected := GVL_Const.SIS_FIRST_OUT_CFG, Actual := fbRig.fbCem.stSts.uiFirstOut,
    Message := 'default cfg: first-out CFG');
AssertEquals_WORD(Expected := 16#FFFF, Actual := fbRig.fbCem.stSts.wEffectTripped, Message := 'all effects tripped');
AssertFalse(Condition := fbRig.fbCem.stSts.xResetPermitted, Message := 'reset not permitted');
AssertEquals_UINT(Expected := GVL_Const.SIS_FIRST_OUT_CFG, Actual := fbRig.fbCem.stSts.uiResetBlocker,
    Message := 'reset blocker CFG');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.ResetDenied), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := 'reset denied');
coUnit.TEST_FINISHED();
