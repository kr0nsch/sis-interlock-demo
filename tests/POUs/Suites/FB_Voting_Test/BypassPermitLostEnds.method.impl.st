coUnit.TEST('Voting_Bypass_PermitLostEnds');
fbRig.stCfg := CfgDi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
fbRig.SetDi(x1 := FALSE, x2 := TRUE, x3 := TRUE);
fbRig.stCmd.axBypassReq[1] := TRUE;
fbRig.Cycle();
AssertEquals_INT(Expected := TO_INT(E_ChannelState.Bypassed), Actual := fbRig.StateOf(uiCh := 1),
    Message := 'demand channel bypassed');
fbRig.xBypassPermit := FALSE;
fbRig.Step(tStep := T#1S);
AssertEquals_INT(Expected := TO_INT(E_BypassState.Denied), Actual := fbRig.BypassOf(uiCh := 1),
    Message := 'permit lost: Denied');
AssertEquals_INT(Expected := TO_INT(E_ChannelState.Demand), Actual := fbRig.StateOf(uiCh := 1),
    Message := 'permit lost: channel votes again');
stEv := fbRig.fbLog.GetEvent(uiBack := 0);
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.BypassOff), Actual := TO_INT(stEv.eKind),
    Message := 'permit lost: event BypassOff');
AssertEquals_UINT(Expected := 1, Actual := stEv.uiChannel, Message := 'BypassOff: channel 1');
fbRig.xBypassPermit := TRUE;
fbRig.Cycle();
AssertEquals_INT(Expected := TO_INT(E_BypassState.Denied), Actual := fbRig.BypassOf(uiCh := 1),
    Message := 'permit back, request held: still Denied');
coUnit.TEST_FINISHED();
