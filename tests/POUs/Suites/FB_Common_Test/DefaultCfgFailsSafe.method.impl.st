coUnit.TEST('Common_DefaultCfg_FailsSafe');
AssertEquals_WORD(Expected := GVL_Const.VOTE_CFG_ARCH, Actual := F_VoteCheckCfg(stCfg := stVoteCfg),
    Message := 'default voting cfg: arch error only');
wErr := F_CemCheckCfg(stCfg := stCemCfg);
AssertEquals_WORD(Expected := GVL_Const.CEM_CFG_COUNT, Actual := wErr AND GVL_Const.CEM_CFG_COUNT,
    Message := 'default matrix cfg: count error');
AssertTrue(Condition := stCemCfg.xStartTripped, Message := 'default matrix: start tripped');
coUnit.TEST_FINISHED();
