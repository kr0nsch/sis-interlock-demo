coUnit.TEST('Voting_Discrepancy_IgnoresBypassedAndInvalid');
fbRig.stCfg := CfgAi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.DegradeSafe);
fbRig.stCfg.rDiscrepancyMax_eu := 1.0;
fbRig.SetAi(r1 := 10.0, r2 := 45.0, r3 := 40.0);
fbRig.stIn.axAiValid[1] := FALSE;
fbRig.stCmd.axBypassReq[2] := TRUE;
fbRig.Cycle();
AssertEquals_REAL(Expected := 0.0, Actual := fbRig.fbVote.stSts.rSpread_eu, Delta := 0.0,
    Message := 'one participant: spread 0');
AssertFalse(Condition := fbRig.fbVote.stSts.xDiscrepancy, Message := 'invalid and bypassed ignored: no alarm');
fbRig.stIn.axAiValid[1] := TRUE;
fbRig.Cycle();
AssertEquals_REAL(Expected := 30.0, Actual := fbRig.fbVote.stSts.rSpread_eu, Delta := 1.0E-4,
    Message := 'channel 1 valid again: spread 30 (bypassed channel 2 still ignored)');
AssertTrue(Condition := fbRig.fbVote.stSts.xDiscrepancy, Message := 'spread 30: alarm');
coUnit.TEST_FINISHED();
