coUnit.TEST('Voting_DefaultCfg_TripsCfgError');
fbRig.SetDi(x1 := TRUE, x2 := TRUE, x3 := TRUE);
fbRig.Cycle();
AssertTrue(Condition := fbRig.fbVote.xTrip, Message := 'default cfg: trip');
AssertTrue(Condition := fbRig.fbVote.stSts.xCfgError, Message := 'default cfg: config error');
AssertEquals_WORD(Expected := GVL_Const.VOTE_CFG_ARCH, Actual := fbRig.fbVote.stSts.wCfgErr,
    Message := 'default cfg: VOTE_CFG_ARCH');
AssertEquals_INT(Expected := TO_INT(E_VoteArch.None), Actual := TO_INT(fbRig.fbVote.stSts.eArchEff),
    Message := 'default cfg: effective None');
AssertEquals_INT(Expected := TO_INT(E_ChannelState.NotUsed), Actual := fbRig.StateOf(uiCh := 1),
    Message := 'default cfg: channels NotUsed');
stEv := fbRig.fbLog.GetEvent(uiBack := 0);
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.CfgError), Actual := TO_INT(stEv.eKind),
    Message := 'event CfgError');
AssertEquals_UINT(Expected := 7, Actual := stEv.uiCause, Message := 'CfgError: cause number');
AssertEquals_REAL(Expected := 1.0, Actual := stEv.rValue, Delta := 0.0, Message := 'CfgError: value = wCfgErr');
fbRig.Cycle();
AssertEquals_UINT(Expected := 1, Actual := fbRig.fbLog.Count, Message := 'CfgError only once');
coUnit.TEST_FINISHED();
