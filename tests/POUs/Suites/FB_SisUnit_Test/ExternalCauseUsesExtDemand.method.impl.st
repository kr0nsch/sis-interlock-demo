coUnit.TEST('Unit_ExternalCause_UsesExtDemand');
Setup(fbRig := fbRig);
fbRig.Cycle();
AssertTrue(Condition := fbRig.fbUnit.axEffectOut[2], Message := 'no external demand: effect 2 energized');
fbRig.astIn[2].xExtDemand := TRUE;
fbRig.Step(tStep := T#100MS);
AssertEquals_WORD(Expected := 16#0002, Actual := fbRig.fbUnit.stCemSts.wCauseLatched, Message := 'cause 2 latched');
AssertFalse(Condition := fbRig.fbUnit.axEffectOut[2], Message := 'effect 2 tripped');
AssertTrue(Condition := fbRig.fbUnit.axEffectOut[1], Message := 'effect 1 energized');
AssertEquals_INT(Expected := TO_INT(E_VoteArch.None), Actual := TO_INT(fbRig.fbUnit.astVoteSts[2].eArchEff),
    Message := 'external cause: group status default');
AssertTrue(Condition := fbRig.fbUnit.xTripped, Message := 'unit tripped');
coUnit.TEST_FINISHED();
