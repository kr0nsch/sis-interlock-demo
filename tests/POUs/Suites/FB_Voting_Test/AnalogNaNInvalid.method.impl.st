coUnit.TEST('Voting_AnalogNaN_Invalid');
fbRig.stCfg := CfgAi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
fbRig.SetAi(r1 := 60.0, r2 := 40.0, r3 := 40.0);
fbRig.Cycle();
AssertEquals_INT(Expected := TO_INT(E_ChannelState.Demand), Actual := fbRig.StateOf(uiCh := 1),
    Message := 'channel 1 demand before NaN');
uBits.dwValue := 16#7FC00000;
fbRig.stIn.arAi_eu[1] := uBits.rValue;
fbRig.Cycle();
AssertEquals_INT(Expected := TO_INT(E_ChannelState.Invalid), Actual := fbRig.StateOf(uiCh := 1),
    Message := 'NaN: channel Invalid');
AssertEquals_INT(Expected := TO_INT(E_VoteArch.Vote1oo2), Actual := TO_INT(fbRig.fbVote.stSts.eArchEff),
    Message := 'NaN, VoteTrip: 2oo3 -> 1oo2');
AssertTrue(Condition := fbRig.fbVote.stSts.xDegraded, Message := 'NaN: degraded');
stEv := fbRig.fbLog.LastOfKind(eKind := E_SisEventKind.ChannelInvalid);
AssertEquals_UINT(Expected := 1, Actual := stEv.uiChannel, Message := 'ChannelInvalid: channel 1');
fbRig.stIn.arAi_eu[1] := 49.0;
fbRig.Cycle();
AssertEquals_INT(Expected := TO_INT(E_ChannelState.Normal), Actual := fbRig.StateOf(uiCh := 1),
    Message := '49.0 after NaN: Normal (hysteresis memory cleared)');
coUnit.TEST_FINISHED();
