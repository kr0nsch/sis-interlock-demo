coUnit.TEST('Voting_AnalogLow_InclusiveAtLimit');
fbRig.stCfg := CfgAi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
fbRig.stCfg.eLimitDir := E_LimitDir.Low;
fbRig.stCfg.rTripLimit_eu := 10.0;
fbRig.stCfg.rHyst_eu := 0.0;
fbRig.SetAi(r1 := 10.01, r2 := 10.01, r3 := 10.01);
fbRig.Cycle();
AssertFalse(Condition := fbRig.fbVote.xTrip, Message := '10.01 > 10: no trip');
fbRig.SetAi(r1 := 10.0, r2 := 11.0, r3 := 10.0);
fbRig.Cycle();
AssertTrue(Condition := fbRig.fbVote.xTrip, Message := 'exactly 10.0 on two channels: trip');
AssertEquals_INT(Expected := TO_INT(E_ChannelState.Demand), Actual := fbRig.StateOf(uiCh := 3),
    Message := '10.0: channel Demand');
AssertEquals_INT(Expected := TO_INT(E_ChannelState.Normal), Actual := fbRig.StateOf(uiCh := 2),
    Message := '11.0: channel Normal');
coUnit.TEST_FINISHED();
