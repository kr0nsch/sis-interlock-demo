coUnit.TEST('Cem_Override_RepeatIgnored');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.stCmd.wOverrideReq := 16#0002;
fbRig.Step(tStep := T#100MS);
fbRig.Step(tStep := T#1M);
uiEvents := fbRig.fbLog.Count;
fbRig.stCmd.wOverrideReq := 16#0002;
fbRig.Step(tStep := T#100MS);
AssertEquals_UINT(Expected := uiEvents, Actual := fbRig.fbLog.Count, Message := 'repeat request: no event');
AssertEquals_TIME(Expected := T#13M59S900MS, Actual := fbRig.fbCem.stSts.atOverrideRemain[2],
    Message := 'repeat request: not extended');
coUnit.TEST_FINISHED();
