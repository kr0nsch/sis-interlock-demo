coUnit.TEST('Voting_Bypass_DeniedWithoutPermit');
fbRig.stCfg := CfgDi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
fbRig.SetDi(x1 := TRUE, x2 := TRUE, x3 := TRUE);
fbRig.xBypassPermit := FALSE;
fbRig.stCmd.axBypassReq[1] := TRUE;
fbRig.Cycle();
AssertEquals_INT(Expected := TO_INT(E_BypassState.Denied), Actual := fbRig.BypassOf(uiCh := 1),
    Message := 'no permit: Denied');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.BypassDenied), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := 'event BypassDenied');
fbRig.xBypassPermit := TRUE;
fbRig.Cycle();
AssertEquals_INT(Expected := TO_INT(E_BypassState.Denied), Actual := fbRig.BypassOf(uiCh := 1),
    Message := 'permit while request held: still Denied');
coUnit.TEST_FINISHED();
