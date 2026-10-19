coUnit.TEST('Voting_Discrepancy_NoTripImpact');
fbRig.stCfg := CfgAi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
fbRig.stCfg.rDiscrepancyMax_eu := 1.0;
fbRig.SetAi(r1 := 10.0, r2 := 30.0, r3 := 45.0);
fbRig.Cycle();
AssertTrue(Condition := fbRig.fbVote.stSts.xDiscrepancy, Message := 'alarm on');
AssertFalse(Condition := fbRig.fbVote.xTrip, Message := 'discrepancy does not trip');
AssertFalse(Condition := fbRig.fbVote.stSts.xDegraded, Message := 'discrepancy is not degradation');
coUnit.TEST_FINISHED();
