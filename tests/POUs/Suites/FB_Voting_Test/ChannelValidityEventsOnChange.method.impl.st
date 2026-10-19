coUnit.TEST('Voting_ChannelValidity_EventsOnChange');
fbRig.stCfg := CfgDi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
fbRig.SetDi(x1 := TRUE, x2 := TRUE, x3 := TRUE);
fbRig.Cycle();
AssertEquals_UINT(Expected := 0, Actual := fbRig.fbLog.Count, Message := 'healthy first call: no events');
fbRig.stIn.axDiValid[2] := FALSE;
fbRig.Cycle();
fbRig.Cycle();
AssertEquals_UINT(Expected := 1, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.ChannelInvalid),
    Message := 'ChannelInvalid once');
stEv := fbRig.fbLog.LastOfKind(eKind := E_SisEventKind.ChannelInvalid);
AssertEquals_UINT(Expected := 2, Actual := stEv.uiChannel, Message := 'ChannelInvalid: channel 2');
AssertEquals_UINT(Expected := 7, Actual := stEv.uiCause, Message := 'ChannelInvalid: cause number');
fbRig.stIn.axDiValid[2] := TRUE;
fbRig.Cycle();
stEv := fbRig.fbLog.GetEvent(uiBack := 0);
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.ChannelValid), Actual := TO_INT(stEv.eKind),
    Message := 'ChannelValid on return');
AssertEquals_UINT(Expected := 2, Actual := stEv.uiChannel, Message := 'ChannelValid: channel 2');
coUnit.TEST_FINISHED();
