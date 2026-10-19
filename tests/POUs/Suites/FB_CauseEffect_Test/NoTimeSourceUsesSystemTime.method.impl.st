coUnit.TEST('Cem_NoTimeSource_UsesSystemTime');
stCfg := CfgBase();
fbCem(axCauseIn := axCauseIn, xOverridePermit := FALSE, xResetHw := FALSE, stCmd := stCmd, stCfg := stCfg);
AssertTrue(Condition := fbCem.axEffectOut[1], Message := 'system time: effect 1 energized');
axCauseIn[3] := TRUE;
fbCem(axCauseIn := axCauseIn, xOverridePermit := FALSE, xResetHw := FALSE, stCmd := stCmd, stCfg := stCfg);
AssertEquals_WORD(Expected := 16#0004, Actual := fbCem.stSts.wCauseLatched, Message := 'system time: cause 3 latched');
AssertTrue(Condition := fbCem.stSts.ltFirstOut > LTIME#0S, Message := 'system time: first-out time set');
coUnit.TEST_FINISHED();
