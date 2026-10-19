coUnit.TEST('Voting_UnusedChannels_Ignored');
fbRig.stCfg := CfgDi(eArch := E_VoteArch.Vote1oo2, ePolicy := E_DegradePolicy.VoteTrip);
fbRig.SetDi(x1 := TRUE, x2 := TRUE, x3 := FALSE);
fbRig.stIn.axDiValid[3] := FALSE;
fbRig.stCmd.axBypassReq[3] := TRUE;
fbRig.Cycle();
AssertFalse(Condition := fbRig.fbVote.xTrip, Message := 'channel 3 demand ignored');
AssertFalse(Condition := fbRig.fbVote.stSts.xDegraded, Message := 'channel 3 invalid ignored');
AssertEquals_INT(Expected := TO_INT(E_ChannelState.NotUsed), Actual := fbRig.StateOf(uiCh := 3),
    Message := 'channel 3 NotUsed');
AssertEquals_INT(Expected := TO_INT(E_BypassState.Off), Actual := fbRig.BypassOf(uiCh := 3),
    Message := 'channel 3 bypass request ignored');
AssertEquals_UINT(Expected := 0, Actual := fbRig.fbLog.Count, Message := 'no events for channel 3');
coUnit.TEST_FINISHED();
