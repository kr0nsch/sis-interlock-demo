// 1. Время: один источник на весь вызов — для групп и матрицы (так тесты с PL.FB_FakeTime
//    детерминированы)
IF itfTime <> 0 THEN
    itfTimeAct := itfTime;
ELSE
    itfTimeAct := fbSysTime;
END_IF

// 2. Группы голосования по возрастанию индекса причины. Ошибка конфигурации группы — требование
//    только этой причины (xTrip = TRUE), она срабатывает через обычную задержку
uiNc := MIN(stCemCfg.uiCauseCount, GVL_Const.SIS_CAUSES_MAX);
FOR uiI := 1 TO GVL_Const.SIS_CAUSES_MAX DO
    stCause := stCemCfg.astCause[uiI];
    IF uiI <= uiNc AND stCause.xEnable AND stCause.eSource = E_CauseSource.Voting THEN
        afbVote[uiI](stIn := astIn[uiI], stCmd := stCmd.astVote[uiI], stCfg := astVoteCfg[uiI],
            xBypassPermit := xBypassPermit, uiCause := uiI, itfTime := itfTimeAct, itfLog := itfLog);
        axDemand[uiI] := afbVote[uiI].xTrip;
        astVoteSts[uiI] := afbVote[uiI].stSts;
    ELSIF uiI <= uiNc AND stCause.xEnable AND stCause.eSource = E_CauseSource.External THEN
        // требование — логика приложения, группа не вызывается
        axDemand[uiI] := astIn[uiI].xExtDemand;
        astVoteSts[uiI] := stVoteStsDefault;
    ELSE
        axDemand[uiI] := FALSE;
        astVoteSts[uiI] := stVoteStsDefault;
    END_IF
END_FOR

// 3. Матрица
fbCem(axCauseIn := axDemand, xOverridePermit := xOverridePermit, xResetHw := xResetHw, itfTime := itfTimeAct,
    itfLog := itfLog, stCmd := stCmd.stCem, stCfg := stCemCfg);

// 4. Выходы
axEffectOut := fbCem.axEffectOut;
xTripped := fbCem.xTripped;
stCemSts := fbCem.stSts;
