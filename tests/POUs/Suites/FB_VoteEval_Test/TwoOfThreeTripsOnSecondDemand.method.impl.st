coUnit.TEST('Vote_TwoOfThree_TripsOnSecondDemand');
aeCh[1] := E_ChannelState.Normal;
aeCh[2] := E_ChannelState.Demand;
aeCh[3] := E_ChannelState.Normal;
stRes := F_VoteEval(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.DegradeAvailable, aeCh := aeCh);
AssertFalse(Condition := stRes.xTrip, Message := '2oo3 one demand: no trip');
AssertFalse(Condition := stRes.xDegraded, Message := '2oo3 healthy: not degraded');
AssertEquals_INT(Expected := TO_INT(E_VoteArch.Vote2oo3), Actual := TO_INT(stRes.eArchEff),
    Message := '2oo3 healthy: effective 2oo3');
aeCh[3] := E_ChannelState.Demand;
stRes := F_VoteEval(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.DegradeAvailable, aeCh := aeCh);
AssertTrue(Condition := stRes.xTrip, Message := '2oo3 two demands: trip');
coUnit.TEST_FINISHED();
