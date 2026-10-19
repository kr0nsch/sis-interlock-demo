coUnit.TEST('Cem_Override_ChatteringNotCleared');
fbRig.stCfg := CfgBase();
fbRig.Cycle();
fbRig.stCmd.wOverrideReq := 16#0004;
fbRig.axCauseIn[3] := TRUE;
fbRig.Step(tStep := T#100MS);                                   // t1: обход причины 3 и требование
// 4 периода по 2,1 с: норма в 20 вызовах (подтверждение доходит до 1,9 с), требование — в одном
FOR uiK := 1 TO 4 DO
    fbRig.axCauseIn[3] := FALSE;
    fbRig.Run(tDuration := T#2S, tStep := T#100MS);
    AssertEquals_TIME(Expected := T#100MS, Actual := fbRig.fbCem.stSts.atOverrideClearRemain[3],
        Message := 'chatter: 100 ms of confirm left');
    fbRig.axCauseIn[3] := TRUE;
    fbRig.Step(tStep := T#100MS);
    AssertEquals_TIME(Expected := T#0S, Actual := fbRig.fbCem.stSts.atOverrideClearRemain[3],
        Message := 'chatter: demand resets confirm');
END_FOR
AssertEquals_WORD(Expected := 16#0004, Actual := fbRig.fbCem.stSts.wOverridden,
    Message := 't1 + 8.4 s: override still active');
AssertEquals_UINT(Expected := 0, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.OverrideCleared),
    Message := 'chatter: never cleared');
fbRig.axCauseIn[3] := FALSE;
fbRig.Run(tDuration := T#1S500MS, tStep := T#100MS);            // t1 + 9,9 с
AssertEquals_WORD(Expected := 16#0004, Actual := fbRig.fbCem.stSts.wOverridden,
    Message := 't1 + 9.9 s: override still active');
AssertEquals_TIME(Expected := T#100MS, Actual := fbRig.fbCem.stSts.atOverrideRemain[3],
    Message := 't1 + 9.9 s: 100 ms of override left');
fbRig.axCauseIn[3] := TRUE;
fbRig.Step(tStep := T#100MS);                                   // t1 + 10 с: срок
AssertEquals_UINT(Expected := 1, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.OverrideExpired),
    Message := 't1 + 10 s: OverrideExpired by max time');
AssertEquals_UINT(Expected := 0, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.OverrideCleared),
    Message := 't1 + 10 s: no OverrideCleared');
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbCem.stSts.wOverridden, Message := 't1 + 10 s: no override');
AssertEquals_WORD(Expected := 16#0004, Actual := fbRig.fbCem.stSts.wCauseLatched,
    Message := 't1 + 10 s: demand at expiry latched');
AssertFalse(Condition := fbRig.Out(uiEffect := 2), Message := 't1 + 10 s: effect 2 tripped');
coUnit.TEST_FINISHED();
