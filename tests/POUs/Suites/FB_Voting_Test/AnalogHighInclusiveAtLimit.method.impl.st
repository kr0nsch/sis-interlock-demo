coUnit.TEST('Voting_AnalogHigh_InclusiveAtLimit');
fbRig.stCfg := CfgAi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
fbRig.stCfg.rHyst_eu := 0.0;
fbRig.SetAi(r1 := 49.99, r2 := 49.99, r3 := 49.99);
fbRig.Cycle();
AssertFalse(Condition := fbRig.fbVote.xTrip, Message := '49.99 < 50: no trip');
AssertEquals_INT(Expected := TO_INT(E_ChannelState.Normal), Actual := fbRig.StateOf(uiCh := 1),
    Message := '49.99: channel Normal');
fbRig.SetAi(r1 := 50.0, r2 := 50.0, r3 := 49.0);
fbRig.Cycle();
AssertTrue(Condition := fbRig.fbVote.xTrip, Message := 'exactly 50.0 on two channels: trip');
AssertEquals_INT(Expected := TO_INT(E_ChannelState.Demand), Actual := fbRig.StateOf(uiCh := 1),
    Message := '50.0: channel Demand');
AssertEquals_INT(Expected := TO_INT(E_ChannelState.Normal), Actual := fbRig.StateOf(uiCh := 3),
    Message := '49.0: channel Normal');
AssertEquals_UINT(Expected := 2, Actual := fbRig.fbVote.stSts.uiDemand, Message := 'two demands');
coUnit.TEST_FINISHED();
