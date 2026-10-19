coUnit.TEST('Vote_Counters_ReportStates');
aeCh[1] := E_ChannelState.Bypassed;
aeCh[2] := E_ChannelState.Demand;
aeCh[3] := E_ChannelState.Invalid;
stRes := F_VoteEval(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.DegradeSafe, aeCh := aeCh);
AssertEquals_UINT(Expected := 1, Actual := stRes.uiBypassed, Message := 'B = 1');
AssertEquals_UINT(Expected := 1, Actual := stRes.uiDemand, Message := 'D = 1');
AssertEquals_UINT(Expected := 1, Actual := stRes.uiInvalid, Message := 'F = 1');
AssertEquals_UINT(Expected := 0, Actual := stRes.uiNormal, Message := 'H = 0');
AssertTrue(Condition := stRes.xTrip, Message := 'DegradeSafe B=1 F=1: 1oo1 with demand trips');
AssertEquals_INT(Expected := TO_INT(E_VoteArch.Vote1oo1), Actual := TO_INT(stRes.eArchEff),
    Message := 'DegradeSafe B=1 F=1: effective 1oo1');
coUnit.TEST_FINISHED();
