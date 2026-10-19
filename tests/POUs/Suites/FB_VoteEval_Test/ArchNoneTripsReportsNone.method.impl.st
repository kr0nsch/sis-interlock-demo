coUnit.TEST('Vote_ArchNone_TripsReportsNone');
aeCh[1] := E_ChannelState.Normal;
aeCh[2] := E_ChannelState.Normal;
aeCh[3] := E_ChannelState.Normal;
stRes := F_VoteEval(eArch := E_VoteArch.None, ePolicy := E_DegradePolicy.VoteTrip, aeCh := aeCh);
AssertTrue(Condition := stRes.xTrip, Message := 'arch None: trip');
AssertEquals_INT(Expected := TO_INT(E_VoteArch.None), Actual := TO_INT(stRes.eArchEff),
    Message := 'arch None: effective None');
AssertFalse(Condition := stRes.xDegraded, Message := 'arch None: not degraded');
AssertEquals_UINT(Expected := 0, Actual := stRes.uiNormal, Message := 'arch None: counters 0');
stRes := F_VoteEval(eArch := E_VoteArch.ForcedTrip, ePolicy := E_DegradePolicy.DegradeSafe, aeCh := aeCh);
AssertTrue(Condition := stRes.xTrip, Message := 'arch ForcedTrip as config: trip');
AssertEquals_INT(Expected := TO_INT(E_VoteArch.None), Actual := TO_INT(stRes.eArchEff),
    Message := 'arch ForcedTrip as config: effective None');
coUnit.TEST_FINISHED();
