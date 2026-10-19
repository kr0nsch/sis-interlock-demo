coUnit.TEST('Cem_Override_StartupMaskAllowedOnly');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.stCmd.xStartupOverride := TRUE;
fbRig.Cycle();
AssertEquals_WORD(Expected := 16#0006, Actual := fbRig.fbCem.stSts.wOverridden, Message := 'causes 2 and 3 overridden');
AssertEquals_UINT(Expected := 2, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.OverrideOn),
    Message := 'two OverrideOn');
AssertEquals_UINT(Expected := 0, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.OverrideDenied),
    Message := 'no OverrideDenied');
AssertEquals_TIME(Expected := T#10S, Actual := fbRig.fbCem.stSts.atOverrideRemain[3], Message := 'cause 3: 10 s');
coUnit.TEST_FINISHED();
