coUnit.TEST('Cem_MaskBeyondCount_CfgError');
stCfg := CfgBase();
stCfg.astEffect[2].wCauseMask := 16#0014;
stCfg.wMatrixCrc := F_CemCrc(stCfg := stCfg);
AssertEquals_WORD(Expected := GVL_Const.CEM_CFG_EFFECT, Actual := F_CemCheckCfg(stCfg := stCfg),
    Message := 'cause 5 > count 4 in mask');
stCfg := CfgBase();
stCfg.astEffect[4].wCauseMask := 16#0001;
stCfg.wMatrixCrc := F_CemCrc(stCfg := stCfg);
AssertEquals_WORD(Expected := GVL_Const.CEM_CFG_EFFECT, Actual := F_CemCheckCfg(stCfg := stCfg),
    Message := 'unused effect 4 with mask');
stCfg := CfgBase();
stCfg.astEffect[1].wCauseMask := 0;
stCfg.wMatrixCrc := F_CemCrc(stCfg := stCfg);
AssertEquals_WORD(Expected := GVL_Const.CEM_CFG_EFFECT, Actual := F_CemCheckCfg(stCfg := stCfg),
    Message := 'used effect 1 with empty mask');
fbRig.stCfg := stCfg;
fbRig.Cycle();
AssertTrue(Condition := fbRig.fbCem.stSts.xCfgError, Message := 'FB reports config error');
AssertFalse(Condition := fbRig.Out(uiEffect := 2), Message := 'config error: effect 2 de-energized');
coUnit.TEST_FINISHED();
