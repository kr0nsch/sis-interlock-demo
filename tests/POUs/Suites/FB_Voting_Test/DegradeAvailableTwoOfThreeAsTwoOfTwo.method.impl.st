coUnit.TEST('Voting_DegradeAvailable_TwoOfThreeAsTwoOfTwo');
fbRig.stCfg := CfgAi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.DegradeAvailable);
fbRig.SetAi(r1 := 60.0, r2 := 40.0, r3 := 40.0);
fbRig.stIn.axAiValid[3] := FALSE;
fbRig.Cycle();
AssertEquals_INT(Expected := TO_INT(E_VoteArch.Vote2oo2), Actual := TO_INT(fbRig.fbVote.stSts.eArchEff),
    Message := 'one invalid, DegradeAvailable: 2oo2');
AssertFalse(Condition := fbRig.fbVote.xTrip, Message := '2oo2 with one demand: no trip');
fbRig.stIn.arAi_eu[2] := 60.0;
fbRig.Cycle();
AssertTrue(Condition := fbRig.fbVote.xTrip, Message := '2oo2 with two demands: trip');
coUnit.TEST_FINISHED();
