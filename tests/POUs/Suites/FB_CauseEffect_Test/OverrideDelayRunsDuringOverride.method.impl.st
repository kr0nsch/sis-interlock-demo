coUnit.TEST('Cem_Override_DelayRunsDuringOverride');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.stCmd.wOverrideReq := 16#0002;
fbRig.axCauseIn[2] := TRUE;
fbRig.Step(tStep := T#100MS);
fbRig.Run(tDuration := T#4S900MS, tStep := T#100MS);
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wCauseActive, Message := '4.9 s: delay still running');
fbRig.Step(tStep := T#100MS);
AssertEquals_WORD(Expected := 16#0002, Actual := fbRig.fbCem.stSts.wCauseActive,
    Message := '5 s: active under override');
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := '5 s: not latched');
fbRig.stCmd.wOverrideCancel := 16#0002;
fbRig.Step(tStep := T#100MS);
AssertEquals_WORD(Expected := 16#0002, Actual := fbRig.fbCem.stSts.wCauseLatched, Message := 'cancel: latched at once');
coUnit.TEST_FINISHED();
