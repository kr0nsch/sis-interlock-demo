coUnit.TEST('Cem_Events_OrderInCall');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
udiSeq := fbRig.fbLog.LastSeq;
fbRig.stCmd.xReset := TRUE;
fbRig.stCmd.wOverrideReq := 16#0002;
fbRig.axCauseIn[2] := TRUE;
fbRig.axCauseIn[3] := TRUE;
fbRig.Step(tStep := T#100MS);
AssertEquals_UDINT(Expected := udiSeq + 8, Actual := fbRig.fbLog.LastSeq, Message := '8 events in the call');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.CauseDemand), Actual := fbRig.fbLog.KindAt(uiBack := 7),
    Message := '1: CauseDemand(2)');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.CauseDemand), Actual := fbRig.fbLog.KindAt(uiBack := 6),
    Message := '2: CauseDemand(3)');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.OverrideOn), Actual := fbRig.fbLog.KindAt(uiBack := 5),
    Message := '3: OverrideOn(2)');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.ResetDenied), Actual := fbRig.fbLog.KindAt(uiBack := 4),
    Message := '4: ResetDenied(3)');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.FirstOut), Actual := fbRig.fbLog.KindAt(uiBack := 3),
    Message := '5: FirstOut(3)');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.CauseTrip), Actual := fbRig.fbLog.KindAt(uiBack := 2),
    Message := '6: CauseTrip(3)');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.EffectTrip), Actual := fbRig.fbLog.KindAt(uiBack := 1),
    Message := '7: EffectTrip(2)');
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.EffectTrip), Actual := fbRig.fbLog.KindAt(uiBack := 0),
    Message := '8: EffectTrip(3)');
stEv := fbRig.fbLog.GetEvent(uiBack := 7);
AssertEquals_UINT(Expected := 2, Actual := stEv.uiCause, Message := 'CauseDemand ascending: 2 first');
stEv := fbRig.fbLog.GetEvent(uiBack := 4);
AssertEquals_UINT(Expected := 3, Actual := stEv.uiCause, Message := 'ResetDenied: blocker 3');
stEv := fbRig.fbLog.GetEvent(uiBack := 1);
AssertEquals_UINT(Expected := 2, Actual := stEv.uiEffect, Message := 'EffectTrip ascending: effect 2 first');
stLast := fbRig.fbLog.GetEvent(uiBack := 0);
stEv := fbRig.fbLog.GetEvent(uiBack := 7);
AssertEquals_LTIME(Expected := stLast.ltTime, Actual := stEv.ltTime, Message := 'one timestamp per call');
AssertEquals_UDINT(Expected := stEv.udiSeq + 7, Actual := stLast.udiSeq, Message := 'consecutive seq');
coUnit.TEST_FINISHED();
