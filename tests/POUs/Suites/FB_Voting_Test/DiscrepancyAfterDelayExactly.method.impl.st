coUnit.TEST('Voting_Discrepancy_AfterDelayExactly');
fbRig.stCfg := CfgAi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
fbRig.stCfg.rDiscrepancyMax_eu := 1.0;
fbRig.stCfg.tDiscrepancyDelay := T#5S;
fbRig.SetAi(r1 := 40.0, r2 := 41.5, r3 := 40.5);
fbRig.Cycle();                                                  // t0
AssertEquals_REAL(Expected := 1.5, Actual := fbRig.fbVote.stSts.rSpread_eu, Delta := 1.0E-5, Message := 'spread 1.5');
AssertFalse(Condition := fbRig.fbVote.stSts.xDiscrepancy, Message := 't0: no alarm yet');
fbRig.Run(tDuration := T#4S900MS, tStep := T#100MS);            // t0 + 4,9 с
AssertFalse(Condition := fbRig.fbVote.stSts.xDiscrepancy, Message := 't0 + 4.9 s: no alarm');
fbRig.Step(tStep := T#100MS);                                   // t0 + 5,0 с
AssertTrue(Condition := fbRig.fbVote.stSts.xDiscrepancy, Message := 't0 + 5.0 s: alarm');
stEv := fbRig.fbLog.GetEvent(uiBack := 0);
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.DiscrepancyOn), Actual := TO_INT(stEv.eKind),
    Message := 'event DiscrepancyOn');
AssertEquals_REAL(Expected := 1.5, Actual := stEv.rValue, Delta := 1.0E-5, Message := 'DiscrepancyOn: spread');
AssertEquals_UINT(Expected := 0, Actual := stEv.uiChannel, Message := 'DiscrepancyOn: no channel');
fbRig.SetAi(r1 := 40.0, r2 := 40.5, r3 := 40.5);
fbRig.Step(tStep := T#100MS);
AssertFalse(Condition := fbRig.fbVote.stSts.xDiscrepancy, Message := 'spread 0.5: alarm off at once');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.DiscrepancyOff), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := 'event DiscrepancyOff');
coUnit.TEST_FINISHED();
