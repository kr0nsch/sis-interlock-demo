// Порядок тела — раздел 6.3; порядок событий в вызове — 6.9. Внутри вида — по возрастанию индекса

// 1. Время: действующий источник — один раз за вызов, он же — во все вложенные FB_Delay
IF itfTime <> 0 THEN
    itfTimeAct := itfTime;
ELSE
    itfTimeAct := fbSysTime;
END_IF
ltNow := itfTimeAct.Now();
// «Время назад» — неисправность источника (3.3, D-19): сроки обходов и идущие задержки недостоверны.
// Перезапуск отсчёта в PL.FB_Delay продлил бы обход и отложил бы срабатывание, поэтому обходы
// снимаются (пункт 4), а причины с идущей задержкой срабатывают сразу (пункт 3)
xTimeBack := ltNow < ltPrev;
ltPrev := ltNow;

// 2. Конфигурация (6.8) и старт (6.10)
wErr := F_CemCheckCfg(stCfg := stCfg);
xCfgErr := wErr <> 0;
uiFoNew := GVL_Const.SIS_FIRST_OUT_NONE;
IF xCfgErr AND NOT xCfgErrPrev THEN
    F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.CfgError, uiCause := 0,
        uiEffect := 0, uiChannel := 0, rValue := WORD_TO_REAL(wErr));
    xCfgLatch := TRUE;
    IF uiFirstOut = GVL_Const.SIS_FIRST_OUT_NONE THEN
        uiFoNew := GVL_Const.SIS_FIRST_OUT_CFG;
    END_IF
ELSIF xCfgErrPrev AND NOT xCfgErr THEN
    F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.CfgOk, uiCause := 0,
        uiEffect := 0, uiChannel := 0, rValue := 0.0);
END_IF
xCfgErrPrev := xCfgErr;
IF xFirstCall AND NOT xCfgErr AND stCfg.xStartTripped THEN
    xStartLatch := TRUE;
    F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.StartTrip,
        uiCause := GVL_Const.SIS_FIRST_OUT_START, uiEffect := 0, uiChannel := 0, rValue := 0.0);
    IF uiFirstOut = GVL_Const.SIS_FIRST_OUT_NONE THEN
        uiFoNew := GVL_Const.SIS_FIRST_OUT_START;
    END_IF
END_IF
IF uiFoNew <> GVL_Const.SIS_FIRST_OUT_NONE THEN
    uiFirstOut := uiFoNew;
    ltFirstOut := ltNow;
    wFirstOutMask := 0;
    udiTripCount := udiTripCount + 1;
    F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.FirstOut, uiCause := uiFirstOut,
        uiEffect := 0, uiChannel := 0, rValue := 0.0);
END_IF
IF xTimeBack THEN
    F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.TimeFault, uiCause := 0,
        uiEffect := 0, uiChannel := 0, rValue := 0.0);
END_IF

IF xCfgErr THEN
    uiNc := 0;
    uiNe := 0;
ELSE
    uiNc := MIN(stCfg.uiCauseCount, GVL_Const.SIS_CAUSES_MAX);
    uiNe := MIN(stCfg.uiEffectCount, GVL_Const.SIS_EFFECTS_MAX);
END_IF

// 3. Причины: требование, задержка, события по смене требования; при «времени назад» идущая
//    задержка завершается: причина с требованием активна в этом вызове
wPresent := 0;
wActive := 0;
FOR uiI := 1 TO GVL_Const.SIS_CAUSES_MAX DO
    wBit := F_SisBitMask(uiIdx := uiI);
    stCause := stCfg.astCause[uiI];
    xPresent := (uiI <= uiNc) AND stCause.xEnable AND axCauseIn[uiI];
    IF uiI <= uiNc THEN
        tDelay := stCause.tDelay;
    ELSE
        tDelay := T#0S;
    END_IF
    IF xTimeBack AND xPresent THEN
        afbDelay[uiI].Preset(xValue := TRUE);
    END_IF
    afbDelay[uiI](xIn := xPresent, tOnDelay := tDelay, tOffDelay := T#0S, itfTime := itfTimeAct);
    IF xPresent THEN
        wPresent := wPresent OR wBit;
    END_IF
    IF afbDelay[uiI].xOut THEN
        wActive := wActive OR wBit;
    END_IF
    IF xPresent AND NOT F_SisBit(wMask := wPresentPrev, uiIdx := uiI) THEN
        F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.CauseDemand, uiCause := uiI,
            uiEffect := 0, uiChannel := 0, rValue := 0.0);
    ELSIF NOT xPresent AND F_SisBit(wMask := wPresentPrev, uiIdx := uiI) THEN
        F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.CauseClear, uiCause := uiI,
            uiEffect := 0, uiChannel := 0, rValue := 0.0);
    END_IF
    stSts.atDelayRemain[uiI] := afbDelay[uiI].tRemaining;
END_FOR
wPresentPrev := wPresent;

// 4. Пусковые обходы (6.4)
IF xCfgErr THEN
    // 4.1 Ошибка конфигурации: обходы снимаются, запросы не обрабатываются
    FOR uiI := 1 TO GVL_Const.SIS_CAUSES_MAX DO
        IF F_SisBit(wMask := wOverridden, uiIdx := uiI) THEN
            wOverridden := wOverridden AND NOT F_SisBitMask(uiIdx := uiI);
            F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.OverrideOff, uiCause := uiI,
                uiEffect := 0, uiChannel := 0, rValue := 0.0);
        END_IF
    END_FOR
ELSE
    // 4.1 Время назад: срок обходов недостоверен — обходы снимаются (D-19)
    IF xTimeBack THEN
        FOR uiI := 1 TO GVL_Const.SIS_CAUSES_MAX DO
            IF F_SisBit(wMask := wOverridden, uiIdx := uiI) THEN
                wOverridden := wOverridden AND NOT F_SisBitMask(uiIdx := uiI);
                F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.OverrideExpired,
                    uiCause := uiI, uiEffect := 0, uiChannel := 0, rValue := 0.0);
            END_IF
        END_FOR
    END_IF
    // 4.2 Снятие командой
    FOR uiI := 1 TO uiNc DO
        IF F_SisBit(wMask := stCmd.wOverrideCancel, uiIdx := uiI) AND F_SisBit(wMask := wOverridden, uiIdx := uiI) THEN
            wOverridden := wOverridden AND NOT F_SisBitMask(uiIdx := uiI);
            F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.OverrideOff, uiCause := uiI,
                uiEffect := 0, uiChannel := 0, rValue := 0.0);
        END_IF
    END_FOR
    // 4.3 Запросы: маска HMI и общий пусковой обход; запрос действующего обхода игнорируется (D-13)
    wReq := stCmd.wOverrideReq;
    IF stCmd.xStartupOverride THEN
        FOR uiI := 1 TO uiNc DO
            stCause := stCfg.astCause[uiI];
            IF stCause.xEnable AND stCause.xOverrideAllowed THEN
                wReq := wReq OR F_SisBitMask(uiIdx := uiI);
            END_IF
        END_FOR
    END_IF
    FOR uiI := 1 TO uiNc DO
        IF F_SisBit(wMask := wReq, uiIdx := uiI) AND NOT F_SisBit(wMask := wOverridden, uiIdx := uiI) THEN
            stCause := stCfg.astCause[uiI];
            IF stCause.xEnable AND stCause.xOverrideAllowed AND stCause.tOverrideMax > T#0S AND xOverridePermit THEN
                wOverridden := wOverridden OR F_SisBitMask(uiIdx := uiI);
                // срок нового обхода и подтверждение нормы — от ltNow этого вызова, даже если прежний
                // истёк в прошлом вызове или снят в этом: иначе таймеры не увидели бы смены входа
                // (6.4, п. 3; D-13)
                afbOverride[uiI].Preset(xValue := FALSE);
                afbOvrClear[uiI].Preset(xValue := FALSE);
                F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.OverrideOn,
                    uiCause := uiI, uiEffect := 0, uiChannel := 0, rValue := 0.0);
            ELSE
                F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.OverrideDenied,
                    uiCause := uiI, uiEffect := 0, uiChannel := 0, rValue := 0.0);
            END_IF
        END_IF
    END_FOR
END_IF
// 4.4 Срок (таймеры вызываются и при ошибке конфигурации — со снятым входом); обход, принятый в
//     этом вызове, отсчитывается от ltNow этого вызова и в нём же не истекает. Срок — верхняя
//     граница: в одном вызове он проверяется раньше подтверждения нормы
FOR uiI := 1 TO GVL_Const.SIS_CAUSES_MAX DO
    stCause := stCfg.astCause[uiI];
    afbOverride[uiI](xIn := F_SisBit(wMask := wOverridden, uiIdx := uiI), tOnDelay := stCause.tOverrideMax,
        itfTime := itfTimeAct);
    IF F_SisBit(wMask := wOverridden, uiIdx := uiI) AND afbOverride[uiI].xOut THEN
        wOverridden := wOverridden AND NOT F_SisBitMask(uiIdx := uiI);
        F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.OverrideExpired, uiCause := uiI,
            uiEffect := 0, uiChannel := 0, rValue := 0.0);
    END_IF
END_FOR
// 4.5 Автоснятие при норме (R-12, D-20): сырого требования нет непрерывно tOverrideClear; каждое
//     появление требования перезапускает отсчёт. Обход, принятый в этом вызове, в нём же не
//     снимается (tOverrideClear > T#0S проверяет F_CemCheckCfg)
FOR uiI := 1 TO GVL_Const.SIS_CAUSES_MAX DO
    stCause := stCfg.astCause[uiI];
    afbOvrClear[uiI](
        xIn := F_SisBit(wMask := wOverridden, uiIdx := uiI) AND NOT F_SisBit(wMask := wPresent, uiIdx := uiI),
        tOnDelay := stCause.tOverrideClear, tOffDelay := T#0S, itfTime := itfTimeAct);
    IF F_SisBit(wMask := wOverridden, uiIdx := uiI) AND afbOvrClear[uiI].xOut THEN
        wOverridden := wOverridden AND NOT F_SisBitMask(uiIdx := uiI);
        F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.OverrideCleared, uiCause := uiI,
            uiEffect := 0, uiChannel := 0, rValue := 0.0);
    END_IF
END_FOR
// 4.6 Импульсы HMI обработаны; 4.7 остаток обходов и подтверждения нормы
stCmd.wOverrideReq := 0;
stCmd.wOverrideCancel := 0;
stCmd.xStartupOverride := FALSE;
FOR uiI := 1 TO GVL_Const.SIS_CAUSES_MAX DO
    IF F_SisBit(wMask := wOverridden, uiIdx := uiI) THEN
        stSts.atOverrideRemain[uiI] := afbOverride[uiI].tRemaining;
        stSts.atOverrideClearRemain[uiI] := afbOvrClear[uiI].tRemaining;
    ELSE
        stSts.atOverrideRemain[uiI] := T#0S;
        stSts.atOverrideClearRemain[uiI] := T#0S;
    END_IF
END_FOR

// 5. Сброс (6.5): только вручную и только при снятых причинах — по сырому требованию (D-07)
xResetReq := stCmd.xReset OR (xResetHw AND NOT xResetHwPrev);
xResetHwPrev := xResetHw;
stCmd.xReset := FALSE;
IF xCfgErr THEN
    uiBlocker := GVL_Const.SIS_FIRST_OUT_CFG;
ELSE
    uiBlocker := 0;
    FOR uiI := 1 TO uiNc DO
        IF uiBlocker = 0 AND F_SisBit(wMask := wPresent, uiIdx := uiI)
            AND NOT F_SisBit(wMask := wOverridden, uiIdx := uiI)
        THEN
            uiBlocker := uiI;
        END_IF
    END_FOR
END_IF
xResetPermitted := uiBlocker = 0;
IF xResetReq THEN
    IF xResetPermitted THEN
        wLatched := 0;
        xCfgLatch := FALSE;
        xStartLatch := FALSE;
        uiFirstOut := GVL_Const.SIS_FIRST_OUT_NONE;
        ltFirstOut := LTIME#0S;
        wFirstOutMask := 0;
        F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.ResetDone, uiCause := 0,
            uiEffect := 0, uiChannel := 0, rValue := 0.0);
    ELSE
        F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.ResetDenied,
            uiCause := uiBlocker, uiEffect := 0, uiChannel := 0, rValue := 0.0);
    END_IF
END_IF

// 6. Фиксация и первопричина (6.6): обход маскирует только фиксацию
wNew := 0;
FOR uiI := 1 TO uiNc DO
    IF F_SisBit(wMask := wActive, uiIdx := uiI) AND NOT F_SisBit(wMask := wOverridden, uiIdx := uiI)
        AND NOT F_SisBit(wMask := wLatched, uiIdx := uiI)
    THEN
        wNew := wNew OR F_SisBitMask(uiIdx := uiI);
    END_IF
END_FOR
IF wNew <> 0 THEN
    IF uiFirstOut = GVL_Const.SIS_FIRST_OUT_NONE THEN
        // одновременные причины: первопричина — младший индекс, все — в маске (D-08)
        uiFirstOut := F_SisFirstBit(wMask := wNew);
        wFirstOutMask := wNew;
        ltFirstOut := ltNow;
        udiTripCount := udiTripCount + 1;
        F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.FirstOut, uiCause := uiFirstOut,
            uiEffect := 0, uiChannel := 0, rValue := 0.0);
    END_IF
    wLatched := wLatched OR wNew;
    FOR uiI := 1 TO uiNc DO
        IF F_SisBit(wMask := wNew, uiIdx := uiI) THEN
            F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.CauseTrip, uiCause := uiI,
                uiEffect := 0, uiChannel := 0, rValue := 0.0);
        END_IF
    END_FOR
END_IF

// 7. Следствия (6.7): обесточивание на срабатывание; неиспользуемые следствия обесточены
wEffTripped := 0;
FOR uiJ := 1 TO GVL_Const.SIS_EFFECTS_MAX DO
    stEffect := stCfg.astEffect[uiJ];
    xTripJ := (uiJ > uiNe) OR xCfgErr OR xCfgLatch OR xStartLatch OR ((wLatched AND stEffect.wCauseMask) <> 0);
    axEffectOut[uiJ] := NOT xTripJ;
    IF uiJ <= uiNe AND xTripJ THEN
        wEffTripped := wEffTripped OR F_SisBitMask(uiIdx := uiJ);
    END_IF
END_FOR
IF xCfgErr THEN
    wEffTripped := GVL_Const.WORD_ALL;
ELSE
    // События — без ошибки конфигурации, по смене состояния следствия (начально — «сработало»)
    FOR uiJ := 1 TO uiNe DO
        xTripJ := F_SisBit(wMask := wEffTripped, uiIdx := uiJ);
        xWasTripped := F_SisBit(wMask := wEffTrippedPrev, uiIdx := uiJ);
        IF xTripJ AND NOT xWasTripped THEN
            stEffect := stCfg.astEffect[uiJ];
            uiEvCause := F_SisFirstBit(wMask := wLatched AND stEffect.wCauseMask);
            IF uiEvCause = 0 THEN
                IF xCfgLatch THEN
                    uiEvCause := GVL_Const.SIS_FIRST_OUT_CFG;
                ELSIF xStartLatch THEN
                    uiEvCause := GVL_Const.SIS_FIRST_OUT_START;
                END_IF
            END_IF
            F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.EffectTrip,
                uiCause := uiEvCause, uiEffect := uiJ, uiChannel := 0, rValue := 0.0);
        ELSIF xWasTripped AND NOT xTripJ THEN
            F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.EffectRestore, uiCause := 0,
                uiEffect := uiJ, uiChannel := 0, rValue := 0.0);
        END_IF
    END_FOR
END_IF
wEffTrippedPrev := wEffTripped;

// 8. Состояние
xTripped := xCfgErr OR xCfgLatch OR xStartLatch OR (wEffTripped <> 0);
stSts.uiFirstOut := uiFirstOut;
stSts.ltFirstOut := ltFirstOut;
stSts.wFirstOutMask := wFirstOutMask;
stSts.wCausePresent := wPresent;
stSts.wCauseActive := wActive;
stSts.wCauseLatched := wLatched;
stSts.wOverridden := wOverridden;
stSts.wEffectTripped := wEffTripped;
stSts.xTripped := xTripped;
stSts.xResetPermitted := xResetPermitted;
stSts.uiResetBlocker := uiBlocker;
stSts.xCfgError := xCfgErr;
stSts.wCfgErr := wErr;
stSts.udiTripCount := udiTripCount;
xFirstCall := FALSE;
