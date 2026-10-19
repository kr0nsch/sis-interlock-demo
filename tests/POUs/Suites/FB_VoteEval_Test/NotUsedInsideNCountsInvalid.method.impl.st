coUnit.TEST('Vote_NotUsedInsideN_CountsInvalid');
aeCh[1] := E_ChannelState.NotUsed;
aeCh[2] := E_ChannelState.Normal;
aeCh[3] := E_ChannelState.Normal;
stRes := F_VoteEval(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip, aeCh := aeCh);
AssertEquals_UINT(Expected := 1, Actual := stRes.uiInvalid, Message := 'NotUsed in N: counted invalid');
AssertTrue(Condition := stRes.xDegraded, Message := 'NotUsed in N: degraded');
AssertEquals_INT(Expected := TO_INT(E_VoteArch.Vote1oo2), Actual := TO_INT(stRes.eArchEff),
    Message := 'NotUsed in N, VoteTrip: 2oo3 -> 1oo2');
uBad.iValue := 9;
aeCh[1] := uBad.eChState;
aeCh[2] := E_ChannelState.NotUsed;
stRes := F_VoteEval(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip, aeCh := aeCh);
AssertEquals_UINT(Expected := 2, Actual := stRes.uiInvalid, Message := 'state 9 and NotUsed: 2 invalid');
AssertTrue(Condition := stRes.xTrip, Message := 'two invalid, VoteTrip: trip');
AssertEquals_INT(Expected := TO_INT(E_VoteArch.ForcedTrip), Actual := TO_INT(stRes.eArchEff),
    Message := 'two invalid, VoteTrip: ForcedTrip');
coUnit.TEST_FINISHED();
