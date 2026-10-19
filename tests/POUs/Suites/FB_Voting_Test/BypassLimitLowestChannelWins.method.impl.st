coUnit.TEST('Voting_Bypass_LimitLowestChannelWins');
fbRig.stCfg := CfgDi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
fbRig.SetDi(x1 := TRUE, x2 := TRUE, x3 := TRUE);
fbRig.stCmd.axBypassReq[2] := TRUE;
fbRig.stCmd.axBypassReq[3] := TRUE;
fbRig.Cycle();
AssertEquals_INT(Expected := TO_INT(E_BypassState.Active), Actual := fbRig.BypassOf(uiCh := 2),
    Message := 'lower channel 2: Active');
AssertEquals_INT(Expected := TO_INT(E_BypassState.Denied), Actual := fbRig.BypassOf(uiCh := 3),
    Message := 'channel 3 over limit: Denied');
stEv := fbRig.fbLog.LastOfKind(eKind := E_SisEventKind.BypassDenied);
AssertEquals_UINT(Expected := 3, Actual := stEv.uiChannel, Message := 'BypassDenied: channel 3');
fbRig.stCmd.axBypassReq[2] := FALSE;
fbRig.Cycle();
AssertEquals_INT(Expected := TO_INT(E_BypassState.Denied), Actual := fbRig.BypassOf(uiCh := 3),
    Message := 'channel 3 stays Denied while request held');
fbRig.stCmd.axBypassReq[3] := FALSE;
fbRig.Cycle();
fbRig.stCmd.axBypassReq[3] := TRUE;
fbRig.Cycle();
AssertEquals_INT(Expected := TO_INT(E_BypassState.Active), Actual := fbRig.BypassOf(uiCh := 3),
    Message := 'channel 3 re-requested: Active');
coUnit.TEST_FINISHED();
