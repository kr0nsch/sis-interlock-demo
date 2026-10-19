coUnit.TEST('Cem_Override_DeniedWithoutPermit');
fbRig.stCfg := CfgBase();
fbRig.xOverridePermit := FALSE;
fbRig.Cycle();
fbRig.stCmd.wOverrideReq := 16#0002;
fbRig.Cycle();
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wOverridden, Message := 'no permit: no override');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.OverrideDenied), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := 'OverrideDenied');
coUnit.TEST_FINISHED();
