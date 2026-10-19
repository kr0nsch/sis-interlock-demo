coUnit.TEST('Cem_UnusedEffects_Deenergized');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
xAnyOn := FALSE;
FOR uiJ := 4 TO GVL_Const.SIS_EFFECTS_MAX DO
    xAnyOn := xAnyOn OR fbRig.Out(uiEffect := uiJ);
END_FOR
AssertFalse(Condition := xAnyOn, Message := 'effects 4..16 de-energized');
AssertTrue(Condition := fbRig.Out(uiEffect := 3), Message := 'used effect 3 energized');
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wEffectTripped, Message := 'unused not in wEffectTripped');
AssertFalse(Condition := fbRig.fbCem.xTripped, Message := 'unused effects do not set xTripped');
coUnit.TEST_FINISHED();
