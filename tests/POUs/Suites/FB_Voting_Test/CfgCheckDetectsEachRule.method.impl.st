coUnit.TEST('Voting_CfgCheck_DetectsEachRule');
uNaN.dwValue := 16#7FC00000;
stCfg := CfgAi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
AssertEquals_WORD(Expected := 0, Actual := F_VoteCheckCfg(stCfg := stCfg), Message := 'valid analog cfg: 0');
stCfg.eArch := E_VoteArch.ForcedTrip;
AssertEquals_WORD(Expected := GVL_Const.VOTE_CFG_ARCH OR GVL_Const.VOTE_CFG_BYPASS,
    Actual := F_VoteCheckCfg(stCfg := stCfg), Message := 'arch ForcedTrip with 1 bypass: ARCH and BYPASS');
stCfg := CfgAi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
uBad.iValue := 4;
stCfg.ePolicy := uBad.ePolicy;
AssertEquals_WORD(Expected := GVL_Const.VOTE_CFG_POLICY, Actual := F_VoteCheckCfg(stCfg := stCfg),
    Message := 'policy 4');
stCfg := CfgAi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
uBad.iValue := 3;
stCfg.eInput := uBad.eInput;
AssertEquals_WORD(Expected := GVL_Const.VOTE_CFG_INPUT, Actual := F_VoteCheckCfg(stCfg := stCfg), Message := 'input 3');
stCfg := CfgAi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
stCfg.rTripLimit_eu := uNaN.rValue;
AssertEquals_WORD(Expected := GVL_Const.VOTE_CFG_LIMIT, Actual := F_VoteCheckCfg(stCfg := stCfg),
    Message := 'limit NaN');
stCfg := CfgAi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
stCfg.rHyst_eu := -0.1;
AssertEquals_WORD(Expected := GVL_Const.VOTE_CFG_LIMIT, Actual := F_VoteCheckCfg(stCfg := stCfg),
    Message := 'hyst < 0');
stCfg := CfgAi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
uBad.iValue := 0;
stCfg.eLimitDir := uBad.eLimitDir;
AssertEquals_WORD(Expected := GVL_Const.VOTE_CFG_LIMIT, Actual := F_VoteCheckCfg(stCfg := stCfg), Message := 'dir 0');
stCfg := CfgAi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
stCfg.rDiscrepancyMax_eu := -1.0;
AssertEquals_WORD(Expected := GVL_Const.VOTE_CFG_DISCREPANCY, Actual := F_VoteCheckCfg(stCfg := stCfg),
    Message := 'discrepancy < 0');
stCfg := CfgAi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
stCfg.tDiscrepancyDelay := T#10M1S;
AssertEquals_WORD(Expected := GVL_Const.VOTE_CFG_DISCREPANCY, Actual := F_VoteCheckCfg(stCfg := stCfg),
    Message := 'discrepancy delay > 10 min');
stCfg.tDiscrepancyDelay := T#10M;
AssertEquals_WORD(Expected := 0, Actual := F_VoteCheckCfg(stCfg := stCfg), Message := 'discrepancy delay = 10 min');
stCfg := CfgAi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
stCfg.uiMaxBypass := 3;
AssertEquals_WORD(Expected := GVL_Const.VOTE_CFG_BYPASS, Actual := F_VoteCheckCfg(stCfg := stCfg),
    Message := '2oo3: 3 bypasses > N - 1');
stCfg.uiMaxBypass := 2;
stCfg.tBypassMax := T#12H1S;
AssertEquals_WORD(Expected := GVL_Const.VOTE_CFG_BYPASS, Actual := F_VoteCheckCfg(stCfg := stCfg),
    Message := 'bypass time > 12 h');
stCfg := CfgDi(eArch := E_VoteArch.Vote1oo1, ePolicy := E_DegradePolicy.VoteTrip);
stCfg.rTripLimit_eu := uNaN.rValue;
stCfg.rHyst_eu := -5.0;
AssertEquals_WORD(Expected := 0, Actual := F_VoteCheckCfg(stCfg := stCfg),
    Message := 'discrete: analog fields ignored');
stCfg.uiMaxBypass := 1;
AssertEquals_WORD(Expected := GVL_Const.VOTE_CFG_BYPASS, Actual := F_VoteCheckCfg(stCfg := stCfg),
    Message := '1oo1: any bypass is too many');
coUnit.TEST_FINISHED();
