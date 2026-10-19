coUnit.TEST('Cem_StartTripped_RequiresReset');
fbRig.stCfg := CfgBase();
fbRig.stCfg.xStartTripped := TRUE;
fbRig.Cycle();
AssertFalse(Condition := fbRig.Out(uiEffect := 1), Message := 'start: effect 1 de-energized');
AssertFalse(Condition := fbRig.Out(uiEffect := 2), Message := 'start: effect 2 de-energized');
AssertEquals_WORD(Expected := 16#0007, Actual := fbRig.fbCem.stSts.wEffectTripped,
    Message := 'start: 3 effects tripped');
AssertEquals_UINT(Expected := GVL_Const.SIS_FIRST_OUT_START, Actual := fbRig.fbCem.stSts.uiFirstOut,
    Message := 'start: first-out START');
AssertEquals_LTIME(Expected := fbRig.Now(), Actual := fbRig.fbCem.stSts.ltFirstOut, Message := 'start: first-out time');
stEv := fbRig.fbLog.GetEvent(uiBack := 1);
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.StartTrip), Actual := TO_INT(stEv.eKind), Message := 'StartTrip');
AssertEquals_UINT(Expected := GVL_Const.SIS_FIRST_OUT_START, Actual := stEv.uiCause, Message := 'StartTrip: code');
stEv := fbRig.fbLog.GetEvent(uiBack := 0);
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.FirstOut), Actual := TO_INT(stEv.eKind), Message := 'FirstOut');
AssertEquals_UINT(Expected := GVL_Const.SIS_FIRST_OUT_START, Actual := stEv.uiCause, Message := 'FirstOut: START');
fbRig.Run(tDuration := T#10S, tStep := T#1S);
AssertTrue(Condition := fbRig.fbCem.xTripped, Message := 'no reset: still tripped');
fbRig.PressReset();
AssertTrue(Condition := fbRig.Out(uiEffect := 1), Message := 'after reset: effect 1 energized');
AssertFalse(Condition := fbRig.fbCem.xTripped, Message := 'after reset: not tripped');
AssertEquals_UDINT(Expected := 1, Actual := fbRig.fbCem.stSts.udiTripCount, Message := 'one first-out since start');
coUnit.TEST_FINISHED();
