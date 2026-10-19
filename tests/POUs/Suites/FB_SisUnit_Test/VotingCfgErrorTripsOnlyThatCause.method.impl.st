coUnit.TEST('Unit_VotingCfgError_TripsOnlyThatCause');
Setup(fbRig := fbRig);
fbRig.astVoteCfg[1] := stDef;
fbRig.Cycle();                                                  // t0
AssertTrue(Condition := fbRig.fbUnit.astVoteSts[1].xCfgError, Message := 'group 1 config error');
AssertEquals_WORD(Expected := 16#0001, Actual := fbRig.fbUnit.stCemSts.wCausePresent, Message := 'cause 1 demand');
AssertFalse(Condition := fbRig.fbUnit.stCemSts.xCfgError, Message := 'matrix itself is fine');
fbRig.Run(tDuration := T#1S900MS, tStep := T#100MS);
AssertTrue(Condition := fbRig.fbUnit.axEffectOut[1], Message := 't0 + 1.9 s: effect 1 still energized');
fbRig.Step(tStep := T#100MS);
AssertFalse(Condition := fbRig.fbUnit.axEffectOut[1], Message := 't0 + 2 s: effect 1 tripped');
AssertTrue(Condition := fbRig.fbUnit.axEffectOut[2], Message := 'effect 2 unaffected');
AssertEquals_WORD(Expected := 16#0001, Actual := fbRig.fbUnit.stCemSts.wCauseLatched,
    Message := 'only cause 1 latched');
coUnit.TEST_FINISHED();
