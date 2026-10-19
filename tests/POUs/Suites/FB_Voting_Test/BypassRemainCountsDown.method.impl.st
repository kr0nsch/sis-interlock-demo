coUnit.TEST('Voting_Bypass_RemainCountsDown');
fbRig.stCfg := CfgDi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
fbRig.SetDi(x1 := TRUE, x2 := TRUE, x3 := TRUE);
fbRig.stCmd.axBypassReq[3] := TRUE;
fbRig.Cycle();
AssertEquals_TIME(Expected := T#10S, Actual := fbRig.fbVote.stSts.atBypassRemain[3], Message := 't0: 10 s left');
fbRig.Run(tDuration := T#3S, tStep := T#1S);
AssertEquals_TIME(Expected := T#7S, Actual := fbRig.fbVote.stSts.atBypassRemain[3], Message := 't0 + 3 s: 7 s left');
AssertEquals_TIME(Expected := T#0S, Actual := fbRig.fbVote.stSts.atBypassRemain[1], Message := 'channel 1: 0');
fbRig.stCmd.axBypassReq[3] := FALSE;
fbRig.Cycle();
AssertEquals_INT(Expected := TO_INT(E_BypassState.Off), Actual := fbRig.BypassOf(uiCh := 3),
    Message := 'request released: Off');
AssertEquals_TIME(Expected := T#0S, Actual := fbRig.fbVote.stSts.atBypassRemain[3], Message := 'Off: 0 left');
coUnit.TEST_FINISHED();
