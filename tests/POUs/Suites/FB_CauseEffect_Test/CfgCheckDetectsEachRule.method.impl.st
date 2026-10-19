coUnit.TEST('Cem_CfgCheck_DetectsEachRule');
stCfg := CfgBase();
AssertEquals_WORD(Expected := 0, Actual := F_CemCheckCfg(stCfg := stCfg), Message := 'base cfg valid');
stCfg.uiCauseCount := 17;
stCfg.wMatrixCrc := F_CemCrc(stCfg := stCfg);
AssertEquals_WORD(Expected := GVL_Const.CEM_CFG_COUNT, Actual := F_CemCheckCfg(stCfg := stCfg), Message := '17 causes');
stCfg := CfgBase();
stCfg.uiEffectCount := 0;
stCfg.astCause[1].tDelay := T#1H;
AssertEquals_WORD(Expected := GVL_Const.CEM_CFG_COUNT OR GVL_Const.CEM_CFG_CRC, Actual := F_CemCheckCfg(stCfg := stCfg),
    Message := '0 effects, stale CRC: COUNT and CRC, causes not checked');
stCfg := CfgBase();
stCfg.astCause[1].tDelay := T#10M1S;
AssertEquals_WORD(Expected := GVL_Const.CEM_CFG_CAUSE, Actual := F_CemCheckCfg(stCfg := stCfg),
    Message := 'delay > 10 min');
stCfg.astCause[1].tDelay := T#10M;
AssertEquals_WORD(Expected := 0, Actual := F_CemCheckCfg(stCfg := stCfg), Message := 'delay = 10 min valid');
stCfg := CfgBase();
stCfg.astCause[2].tOverrideMax := T#0S;
AssertEquals_WORD(Expected := GVL_Const.CEM_CFG_CAUSE, Actual := F_CemCheckCfg(stCfg := stCfg),
    Message := 'override 0 s');
stCfg.astCause[2].tOverrideMax := T#2H1S;
AssertEquals_WORD(Expected := GVL_Const.CEM_CFG_CAUSE, Actual := F_CemCheckCfg(stCfg := stCfg),
    Message := 'override > 2 h');
stCfg := CfgBase();
stCfg.astCause[2].tOverrideClear := T#0S;
AssertEquals_WORD(Expected := GVL_Const.CEM_CFG_CAUSE, Actual := F_CemCheckCfg(stCfg := stCfg),
    Message := 'override clear 0 s');
stCfg.astCause[2].tOverrideClear := T#15M;
AssertEquals_WORD(Expected := GVL_Const.CEM_CFG_CAUSE, Actual := F_CemCheckCfg(stCfg := stCfg),
    Message := 'override clear = override time');
stCfg.astCause[2].tOverrideClear := T#14M59S999MS;
AssertEquals_WORD(Expected := 0, Actual := F_CemCheckCfg(stCfg := stCfg),
    Message := 'override clear just below override time valid');
stCfg := CfgBase();
stCfg.astCause[1].tOverrideClear := T#1H;
AssertEquals_WORD(Expected := 0, Actual := F_CemCheckCfg(stCfg := stCfg),
    Message := 'override clear not checked when override not allowed');
stCfg := CfgBase();
uBad.iValue := 3;
stCfg.astCause[4].eSource := uBad.eSource;
AssertEquals_WORD(Expected := GVL_Const.CEM_CFG_CAUSE, Actual := F_CemCheckCfg(stCfg := stCfg),
    Message := 'source 3 in used (disabled) cause 4');
stCfg := CfgBase();
stCfg.astCause[5].tDelay := T#1H;
AssertEquals_WORD(Expected := 0, Actual := F_CemCheckCfg(stCfg := stCfg),
    Message := 'cause 5 beyond count not checked');
stCfg := CfgBase();
uBad.iValue := 6;
stCfg.astEffect[3].eSafeState := uBad.eSafeState;
AssertEquals_WORD(Expected := GVL_Const.CEM_CFG_EFFECT, Actual := F_CemCheckCfg(stCfg := stCfg),
    Message := 'safe state 6');
coUnit.TEST_FINISHED();
