coUnit.TEST('Voting_TimeBackwards_BypassEnds');
fbRig.stCfg := CfgDi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
fbRig.SetDi(x1 := TRUE, x2 := TRUE, x3 := TRUE);
fbRig.stCmd.axBypassReq[1] := TRUE;
fbRig.Cycle();
ltT0 := fbRig.Now();
fbRig.Run(tDuration := T#6S, tStep := T#1S);
AssertEquals_INT(Expected := TO_INT(E_BypassState.Active), Actual := fbRig.BypassOf(uiCh := 1),
    Message := 't0 + 6 s: Active');
fbRig.SetNow(ltValue := ltT0 - LTIME#1S);
fbRig.Cycle();                                                  // время назад
AssertEquals_INT(Expected := TO_INT(E_BypassState.Expired), Actual := fbRig.BypassOf(uiCh := 1),
    Message := 'time back: bypass ended');
AssertEquals_INT(Expected := TO_INT(E_ChannelState.Normal), Actual := fbRig.StateOf(uiCh := 1),
    Message := 'time back: channel 1 votes again');
AssertEquals_TIME(Expected := T#0S, Actual := fbRig.fbVote.stSts.atBypassRemain[1],
    Message := 'time back: no bypass left');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.TimeFault), Actual := fbRig.fbLog.KindAt(uiBack := 1),
    Message := 'time back: TimeFault');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.BypassExpired), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := 'time back: then BypassExpired');
stEv := fbRig.fbLog.GetEvent(uiBack := 0);
AssertEquals_UINT(Expected := 1, Actual := stEv.uiChannel, Message := 'BypassExpired: channel 1');
fbRig.Step(tStep := T#1S);
AssertEquals_INT(Expected := TO_INT(E_BypassState.Expired), Actual := fbRig.BypassOf(uiCh := 1),
    Message := 'request held: stays Expired');
fbRig.stCmd.axBypassReq[1] := FALSE;
fbRig.Cycle();
fbRig.stCmd.axBypassReq[1] := TRUE;
fbRig.Cycle();
AssertEquals_INT(Expected := TO_INT(E_BypassState.Active), Actual := fbRig.BypassOf(uiCh := 1),
    Message := 'new request: Active');
AssertEquals_TIME(Expected := T#10S, Actual := fbRig.fbVote.stSts.atBypassRemain[1],
    Message := 'new bypass: full 10 s');
coUnit.TEST_FINISHED();
