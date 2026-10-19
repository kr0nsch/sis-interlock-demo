coUnit.TEST('Voting_AnalogInf_Invalid');
fbRig.stCfg := CfgAi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
uPlus.dwValue := 16#7F800000;
uMinus.dwValue := 16#FF800000;
fbRig.SetAi(r1 := uPlus.rValue, r2 := uMinus.rValue, r3 := 1.0E31);
fbRig.Cycle();
AssertEquals_INT(Expected := TO_INT(E_ChannelState.Invalid), Actual := fbRig.StateOf(uiCh := 1),
    Message := '+Inf: Invalid');
AssertEquals_INT(Expected := TO_INT(E_ChannelState.Invalid), Actual := fbRig.StateOf(uiCh := 2),
    Message := '-Inf: Invalid');
AssertEquals_INT(Expected := TO_INT(E_ChannelState.Invalid), Actual := fbRig.StateOf(uiCh := 3),
    Message := '1.0E31: Invalid');
AssertTrue(Condition := fbRig.fbVote.xTrip, Message := 'three invalid: trip');
AssertEquals_INT(Expected := TO_INT(E_VoteArch.ForcedTrip), Actual := TO_INT(fbRig.fbVote.stSts.eArchEff),
    Message := 'three invalid: ForcedTrip');
AssertEquals_UINT(Expected := 3, Actual := fbRig.fbVote.stSts.uiInvalid, Message := 'three invalid counted');
coUnit.TEST_FINISHED();
