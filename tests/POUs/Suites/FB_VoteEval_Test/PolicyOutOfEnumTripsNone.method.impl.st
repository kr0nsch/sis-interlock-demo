coUnit.TEST('Vote_PolicyOutOfEnum_TripsNone');
aeCh[1] := E_ChannelState.Normal;
aeCh[2] := E_ChannelState.Normal;
aeCh[3] := E_ChannelState.Normal;
uBad.iValue := 7;
stRes := F_VoteEval(eArch := E_VoteArch.Vote2oo3, ePolicy := uBad.ePolicy, aeCh := aeCh);
AssertTrue(Condition := stRes.xTrip, Message := 'policy 7: trip');
AssertEquals_INT(Expected := TO_INT(E_VoteArch.None), Actual := TO_INT(stRes.eArchEff),
    Message := 'policy 7: effective None');
AssertEquals_UINT(Expected := 0, Actual := stRes.uiNormal, Message := 'policy 7: counters 0');
uBad.iValue := 0;
stRes := F_VoteEval(eArch := E_VoteArch.Vote1oo1, ePolicy := uBad.ePolicy, aeCh := aeCh);
AssertTrue(Condition := stRes.xTrip, Message := 'policy 0: trip');
coUnit.TEST_FINISHED();
