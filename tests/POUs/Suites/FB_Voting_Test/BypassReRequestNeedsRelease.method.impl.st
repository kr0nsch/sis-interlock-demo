coUnit.TEST('Voting_Bypass_ReRequestNeedsRelease');
fbRig.stCfg := CfgDi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
fbRig.SetDi(x1 := TRUE, x2 := TRUE, x3 := TRUE);
fbRig.stCmd.axBypassReq[2] := TRUE;
fbRig.Cycle();
fbRig.Run(tDuration := T#10S, tStep := T#1S);
AssertEquals_INT(Expected := TO_INT(E_BypassState.Expired), Actual := fbRig.BypassOf(uiCh := 2),
    Message := 'after 10 s: Expired');
fbRig.Run(tDuration := T#5S, tStep := T#1S);
AssertEquals_INT(Expected := TO_INT(E_BypassState.Expired), Actual := fbRig.BypassOf(uiCh := 2),
    Message := 'request held: stays Expired');
fbRig.stCmd.axBypassReq[2] := FALSE;
fbRig.Cycle();
AssertEquals_INT(Expected := TO_INT(E_BypassState.Off), Actual := fbRig.BypassOf(uiCh := 2),
    Message := 'request released: Off');
fbRig.stCmd.axBypassReq[2] := TRUE;
fbRig.Cycle();
AssertEquals_INT(Expected := TO_INT(E_BypassState.Active), Actual := fbRig.BypassOf(uiCh := 2),
    Message := 'new request: Active');
AssertEquals_TIME(Expected := T#10S, Actual := fbRig.fbVote.stSts.atBypassRemain[2],
    Message := 'new bypass: full 10 s');
coUnit.TEST_FINISHED();
