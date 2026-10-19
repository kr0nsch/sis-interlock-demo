coUnit.TEST('Cem_Override_DeniedNotAllowed');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.stCmd.wOverrideReq := 16#0009;
fbRig.Cycle();
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wOverridden, Message := 'no override');
AssertEquals_UINT(Expected := 2, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.OverrideDenied),
    Message := 'two OverrideDenied (causes 1, 4)');
stEv := fbRig.fbLog.GetEvent(uiBack := 1);
AssertEquals_UINT(Expected := 1, Actual := stEv.uiCause, Message := 'first denied: cause 1');
stEv := fbRig.fbLog.GetEvent(uiBack := 0);
AssertEquals_UINT(Expected := 4, Actual := stEv.uiCause, Message := 'then denied: cause 4 (disabled)');
coUnit.TEST_FINISHED();
