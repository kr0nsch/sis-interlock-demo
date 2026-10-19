coUnit.TEST('Voting_Discrepancy_ZeroDisables');
fbRig.stCfg := CfgAi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
fbRig.SetAi(r1 := 10.0, r2 := 45.0, r3 := 30.0);
fbRig.Cycle();
AssertFalse(Condition := fbRig.fbVote.stSts.xDiscrepancy, Message := 'limit 0: no alarm');
AssertEquals_REAL(Expected := 0.0, Actual := fbRig.fbVote.stSts.rSpread_eu, Delta := 0.0,
    Message := 'limit 0: spread 0');
coUnit.TEST_FINISHED();
