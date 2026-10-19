coUnit.TEST('Voting_CfgError_RemovesBypasses');
fbRig.stCfg := CfgDi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
fbRig.SetDi(x1 := TRUE, x2 := TRUE, x3 := TRUE);
fbRig.stCmd.axBypassReq[1] := TRUE;
fbRig.Cycle();
AssertEquals_INT(Expected := TO_INT(E_BypassState.Active), Actual := fbRig.BypassOf(uiCh := 1),
    Message := 'bypass Active');
fbRig.stCfg.eArch := E_VoteArch.None;
fbRig.Step(tStep := T#1S);
AssertTrue(Condition := fbRig.fbVote.xTrip, Message := 'config error: trip');
AssertEquals_INT(Expected := TO_INT(E_BypassState.Off), Actual := fbRig.BypassOf(uiCh := 1),
    Message := 'config error: bypass Off');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.CfgError), Actual := fbRig.fbLog.KindAt(uiBack := 1),
    Message := 'first CfgError');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.BypassOff), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := 'then BypassOff');
fbRig.Run(tDuration := T#20S, tStep := T#1S);
fbRig.stCfg.eArch := E_VoteArch.Vote2oo3;
fbRig.Step(tStep := T#1S);
AssertFalse(Condition := fbRig.fbVote.xTrip, Message := 'config fixed: no trip');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.CfgOk), Actual := fbRig.fbLog.KindAt(uiBack := 1),
    Message := 'CfgOk');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.BypassOn), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := 'held request: new BypassOn');
AssertEquals_TIME(Expected := T#10S, Actual := fbRig.fbVote.stSts.atBypassRemain[1],
    Message := 'new bypass: full 10 s, not expired');
coUnit.TEST_FINISHED();
