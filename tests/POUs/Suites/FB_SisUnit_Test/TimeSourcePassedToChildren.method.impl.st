coUnit.TEST('Unit_TimeSource_PassedToChildren');
Setup(fbRig := fbRig);
fbRig.stCmd.astVote[1].axBypassReq[1] := TRUE;
fbRig.Cycle();
AssertEquals_INT(Expected := TO_INT(E_BypassState.Active), Actual := TO_INT(fbRig.fbUnit.astVoteSts[1].aeBypass[1]),
    Message := 'bypass Active');
fbRig.Run(tDuration := T#9S900MS, tStep := T#100MS);
AssertEquals_INT(Expected := TO_INT(E_BypassState.Active), Actual := TO_INT(fbRig.fbUnit.astVoteSts[1].aeBypass[1]),
    Message := 'fake time 9.9 s: bypass Active');
fbRig.Step(tStep := T#100MS);
AssertEquals_INT(Expected := TO_INT(E_BypassState.Expired), Actual := TO_INT(fbRig.fbUnit.astVoteSts[1].aeBypass[1]),
    Message := 'fake time 10 s: bypass Expired');
fbRig.astIn[1].axDi[2] := FALSE;
fbRig.Step(tStep := T#100MS);                                   // t0
fbRig.Run(tDuration := T#1S900MS, tStep := T#100MS);
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbUnit.stCemSts.wCauseLatched,
    Message := 'fake time 1.9 s: not latched');
fbRig.Step(tStep := T#100MS);
AssertEquals_WORD(Expected := 16#0001, Actual := fbRig.fbUnit.stCemSts.wCauseLatched,
    Message := 'fake time 2 s: latched');
coUnit.TEST_FINISHED();
