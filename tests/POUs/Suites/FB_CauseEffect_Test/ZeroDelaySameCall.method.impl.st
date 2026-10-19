coUnit.TEST('Cem_ZeroDelay_SameCall');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.axCauseIn[3] := TRUE;
fbRig.Step(tStep := T#100MS);
AssertEquals_WORD(Expected := 16#0004, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := 'cause 3 latched at once');
AssertFalse(Condition := fbRig.Out(uiEffect := 2), Message := 'effect 2 tripped');
AssertTrue(Condition := fbRig.Out(uiEffect := 1), Message := 'effect 1 not in mask: energized');
coUnit.TEST_FINISHED();
