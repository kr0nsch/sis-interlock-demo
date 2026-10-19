coUnit.TEST('Voting_Bypass_ExpiresExactlyAtMax');
fbRig.stCfg := CfgDi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
fbRig.SetDi(x1 := TRUE, x2 := TRUE, x3 := TRUE);
fbRig.stIn.axDiValid[1] := FALSE;
fbRig.stCmd.axBypassReq[1] := TRUE;
fbRig.Cycle();                                                  // t0
AssertEquals_INT(Expected := TO_INT(E_BypassState.Active), Actual := fbRig.BypassOf(uiCh := 1),
    Message := 't0: bypass Active');
AssertEquals_INT(Expected := TO_INT(E_ChannelState.Bypassed), Actual := fbRig.StateOf(uiCh := 1),
    Message := 't0: invalid channel Bypassed');
fbRig.Run(tDuration := T#9S900MS, tStep := T#100MS);            // t0 + 9,9 с
AssertEquals_INT(Expected := TO_INT(E_BypassState.Active), Actual := fbRig.BypassOf(uiCh := 1),
    Message := 't0 + 9.9 s: still Active');
fbRig.Step(tStep := T#100MS);                                   // t0 + 10,0 с
AssertEquals_INT(Expected := TO_INT(E_BypassState.Expired), Actual := fbRig.BypassOf(uiCh := 1),
    Message := 't0 + 10 s: Expired');
AssertEquals_INT(Expected := TO_INT(E_ChannelState.Invalid), Actual := fbRig.StateOf(uiCh := 1),
    Message := 't0 + 10 s: channel back in voting as Invalid');
stEv := fbRig.fbLog.GetEvent(uiBack := 0);
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.BypassExpired), Actual := TO_INT(stEv.eKind),
    Message := 'event BypassExpired');
coUnit.TEST_FINISHED();
