// Порядок тела — раздел 5.5. Порядок событий в вызове: CfgError/CfgOk → TimeFault → достоверность →
// окончания байпасов → включения байпасов → рассогласование

// 1. Время: действующий источник — один раз за вызов, он же — во все вложенные FB_Delay
IF itfTime <> 0 THEN
    itfTimeAct := itfTime;
ELSE
    itfTimeAct := fbSysTime;
END_IF
ltNow := itfTimeAct.Now();
// «Время назад» — неисправность источника (3.3, D-19): сроки байпасов недостоверны. Перезапуск отсчёта
// в PL.FB_Delay продлил бы байпас на полный срок, поэтому байпасы заканчиваются (пункт 5.2)
xTimeBack := ltNow < ltPrev;
ltPrev := ltNow;

// 2. Конфигурация (5.9): события по смене признака ошибки, начальное состояние — «ошибки нет»
wErr := F_VoteCheckCfg(stCfg := stCfg);
xCfgErr := wErr <> 0;
IF xCfgErr AND NOT xCfgErrPrev THEN
    F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.CfgError, uiCause := uiCause,
        uiEffect := 0, uiChannel := 0, rValue := WORD_TO_REAL(wErr));
ELSIF xCfgErrPrev AND NOT xCfgErr THEN
    F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.CfgOk, uiCause := uiCause,
        uiEffect := 0, uiChannel := 0, rValue := 0.0);
END_IF
xCfgErrPrev := xCfgErr;
IF xTimeBack THEN
    F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.TimeFault, uiCause := uiCause,
        uiEffect := 0, uiChannel := 0, rValue := 0.0);
END_IF

rSpread := 0.0;
xDisc := FALSE;

IF xCfgErr THEN
    // Ошибка конфигурации: байпасы снимаются, таймеры вызываются со снятым входом (иначе после
    // исправления конфигурации FB_Delay не увидел бы смены входа и новый байпас истёк бы сразу)
    FOR uiK := 1 TO GVL_Const.SIS_VOTE_CH_MAX DO
        IF aeBypass[uiK] = E_BypassState.Active THEN
            F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.BypassOff, uiCause := uiCause,
                uiEffect := 0, uiChannel := uiK, rValue := 0.0);
        END_IF
        aeBypass[uiK] := E_BypassState.Off;
        afbBypass[uiK](xIn := FALSE, tOnDelay := stCfg.tBypassMax, itfTime := itfTimeAct);
        aeChState[uiK] := E_ChannelState.NotUsed;
        atRemain[uiK] := T#0S;
    END_FOR
    fbDisc(xIn := FALSE, tOnDelay := stCfg.tDiscrepancyDelay, tOffDelay := T#0S, itfTime := itfTimeAct);
    stRes.xTrip := TRUE;
    stRes.xDegraded := FALSE;
    stRes.eArchEff := E_VoteArch.None;
    stRes.uiDemand := 0;
    stRes.uiInvalid := 0;
    stRes.uiBypassed := 0;
    stRes.uiNormal := 0;
ELSE
    uiN := F_VoteArchChannels(eArch := stCfg.eArch);

    // 3. Сырые состояния каналов 1..N (5.6); для k > N память гистерезиса сбрасывается
    FOR uiK := 1 TO GVL_Const.SIS_VOTE_CH_MAX DO
        IF uiK <= uiN THEN
            IF stCfg.eInput = E_SisInputKind.Discrete THEN
                axValid[uiK] := stIn.axDiValid[uiK];
                axDem[uiK] := stIn.axDi[uiK] <> stCfg.xDiHealthy;
            ELSE
                // Analog: уставка включительна, требование снимается строго за полосой гистерезиса;
                // память считается и у байпасированного канала
                rVal := stIn.arAi_eu[uiK];
                axValid[uiK] := stIn.axAiValid[uiK] AND PL.F_IsFinite(rIn := rVal);
                IF NOT axValid[uiK] THEN
                    axDemMem[uiK] := FALSE;
                ELSIF stCfg.eLimitDir = E_LimitDir.High THEN
                    axDemMem[uiK] := (rVal >= stCfg.rTripLimit_eu)
                        OR (axDemMem[uiK] AND (rVal >= stCfg.rTripLimit_eu - stCfg.rHyst_eu));
                ELSE
                    axDemMem[uiK] := (rVal <= stCfg.rTripLimit_eu)
                        OR (axDemMem[uiK] AND (rVal <= stCfg.rTripLimit_eu + stCfg.rHyst_eu));
                END_IF
                axDem[uiK] := axDemMem[uiK];
            END_IF
        ELSE
            axValid[uiK] := FALSE;
            axDem[uiK] := FALSE;
            axDemMem[uiK] := FALSE;
        END_IF
    END_FOR

    // 4. События достоверности (k по возрастанию)
    FOR uiK := 1 TO uiN DO
        IF axValid[uiK] <> axValidPrev[uiK] THEN
            IF stCfg.eInput = E_SisInputKind.Analog THEN
                rVal := stIn.arAi_eu[uiK];
            ELSE
                rVal := 0.0;
            END_IF
            IF axValid[uiK] THEN
                eKind := E_SisEventKind.ChannelValid;
            ELSE
                eKind := E_SisEventKind.ChannelInvalid;
            END_IF
            F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := eKind, uiCause := uiCause,
                uiEffect := 0, uiChannel := uiK, rValue := rVal);
            axValidPrev[uiK] := axValid[uiK];
        END_IF
    END_FOR

    // 5. Байпасы (5.7)
    // 5.1 Таймеры: вход — «байпас действует»
    FOR uiK := 1 TO GVL_Const.SIS_VOTE_CH_MAX DO
        afbBypass[uiK](xIn := aeBypass[uiK] = E_BypassState.Active, tOnDelay := stCfg.tBypassMax,
            itfTime := itfTimeAct);
    END_FOR
    // 5.2 Окончания: запрос снят, ключ снят, срок истёк или недостоверен («время назад»); Expired и Denied
    //     ждут снятия запроса
    FOR uiK := 1 TO uiN DO
        xReq := stCmd.axBypassReq[uiK];
        CASE aeBypass[uiK] OF
            E_BypassState.Active:
                IF NOT xReq THEN
                    aeBypass[uiK] := E_BypassState.Off;
                    F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.BypassOff,
                        uiCause := uiCause, uiEffect := 0, uiChannel := uiK, rValue := 0.0);
                ELSIF NOT xBypassPermit THEN
                    aeBypass[uiK] := E_BypassState.Denied;
                    F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.BypassOff,
                        uiCause := uiCause, uiEffect := 0, uiChannel := uiK, rValue := 0.0);
                ELSIF afbBypass[uiK].xOut OR xTimeBack THEN
                    aeBypass[uiK] := E_BypassState.Expired;
                    F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.BypassExpired,
                        uiCause := uiCause, uiEffect := 0, uiChannel := uiK, rValue := 0.0);
                ELSE
                    // байпас продолжается
                    aeBypass[uiK] := E_BypassState.Active;
                END_IF
            E_BypassState.Expired, E_BypassState.Denied:
                IF NOT xReq THEN
                    aeBypass[uiK] := E_BypassState.Off;
                END_IF
        ELSE
            // Off: включения — в пункте 5.3
            aeBypass[uiK] := E_BypassState.Off;
        END_CASE
    END_FOR
    // 5.3 Включения: действующих байпасов меньше предела; при одновременных запросах сверх
    //     предела выигрывает младший канал. Отсчёт — с ltNow этого вызова (второй вызов таймера)
    uiActive := 0;
    FOR uiK := 1 TO uiN DO
        IF aeBypass[uiK] = E_BypassState.Active THEN
            uiActive := uiActive + 1;
        END_IF
    END_FOR
    FOR uiK := 1 TO uiN DO
        IF aeBypass[uiK] = E_BypassState.Off AND stCmd.axBypassReq[uiK] THEN
            IF xBypassPermit AND stCfg.tBypassMax > T#0S AND uiActive < stCfg.uiMaxBypass THEN
                aeBypass[uiK] := E_BypassState.Active;
                uiActive := uiActive + 1;
                F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.BypassOn,
                    uiCause := uiCause, uiEffect := 0, uiChannel := uiK, rValue := 0.0);
                afbBypass[uiK](xIn := TRUE, tOnDelay := stCfg.tBypassMax, itfTime := itfTimeAct);
            ELSE
                aeBypass[uiK] := E_BypassState.Denied;
                F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.BypassDenied,
                    uiCause := uiCause, uiEffect := 0, uiChannel := uiK, rValue := 0.0);
            END_IF
        END_IF
    END_FOR
    // 5.4 Каналы k > N: байпаса нет, запросы не действуют; 5.5 остаток — только у Active
    FOR uiK := 1 TO GVL_Const.SIS_VOTE_CH_MAX DO
        IF uiK > uiN THEN
            aeBypass[uiK] := E_BypassState.Off;
        END_IF
        IF aeBypass[uiK] = E_BypassState.Active THEN
            atRemain[uiK] := afbBypass[uiK].tRemaining;
        ELSE
            atRemain[uiK] := T#0S;
        END_IF
    END_FOR

    // 6. Состояния каналов по старшинству таблицы 5.1
    FOR uiK := 1 TO GVL_Const.SIS_VOTE_CH_MAX DO
        IF uiK > uiN THEN
            aeChState[uiK] := E_ChannelState.NotUsed;
        ELSIF aeBypass[uiK] = E_BypassState.Active THEN
            aeChState[uiK] := E_ChannelState.Bypassed;
        ELSIF NOT axValid[uiK] THEN
            aeChState[uiK] := E_ChannelState.Invalid;
        ELSIF axDem[uiK] THEN
            aeChState[uiK] := E_ChannelState.Demand;
        ELSE
            aeChState[uiK] := E_ChannelState.Normal;
        END_IF
    END_FOR

    // 7. Голосование
    stRes := F_VoteEval(eArch := stCfg.eArch, ePolicy := stCfg.ePolicy, aeCh := aeChState);

    // 8. Рассогласование (5.8): только Analog, участвуют каналы Normal и Demand, порог строгий
    uiPart := 0;
    rMin := 0.0;
    rMax := 0.0;
    IF stCfg.eInput = E_SisInputKind.Analog AND stCfg.rDiscrepancyMax_eu > 0.0 THEN
        FOR uiK := 1 TO uiN DO
            IF aeChState[uiK] = E_ChannelState.Normal OR aeChState[uiK] = E_ChannelState.Demand THEN
                rVal := stIn.arAi_eu[uiK];
                IF uiPart = 0 THEN
                    rMin := rVal;
                    rMax := rVal;
                ELSE
                    rMin := MIN(rMin, rVal);
                    rMax := MAX(rMax, rVal);
                END_IF
                uiPart := uiPart + 1;
            END_IF
        END_FOR
    END_IF
    IF uiPart >= 2 THEN
        rSpread := rMax - rMin;
        xCond := rSpread > stCfg.rDiscrepancyMax_eu;
    ELSE
        rSpread := 0.0;
        xCond := FALSE;
    END_IF
    fbDisc(xIn := xCond, tOnDelay := stCfg.tDiscrepancyDelay, tOffDelay := T#0S, itfTime := itfTimeAct);
    xDisc := fbDisc.xOut;
END_IF

// События рассогласования — по смене тревоги (при ошибке конфигурации тревога снимается)
IF xDisc AND NOT xDiscPrev THEN
    F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.DiscrepancyOn, uiCause := uiCause,
        uiEffect := 0, uiChannel := 0, rValue := rSpread);
ELSIF xDiscPrev AND NOT xDisc THEN
    F_SisLogEvent(itfLog := itfLog, ltTime := ltNow, eKind := E_SisEventKind.DiscrepancyOff, uiCause := uiCause,
        uiEffect := 0, uiChannel := 0, rValue := 0.0);
END_IF
xDiscPrev := xDisc;

// 9. Состояние
xTrip := stRes.xTrip;
stSts.xTrip := xTrip;
stSts.eArchEff := stRes.eArchEff;
stSts.xDegraded := stRes.xDegraded;
stSts.xCfgError := xCfgErr;
stSts.wCfgErr := wErr;
stSts.xDiscrepancy := xDisc;
stSts.rSpread_eu := rSpread;
stSts.uiDemand := stRes.uiDemand;
stSts.uiInvalid := stRes.uiInvalid;
stSts.uiBypassed := stRes.uiBypassed;
stSts.uiNormal := stRes.uiNormal;
stSts.aeChState := aeChState;
stSts.aeBypass := aeBypass;
stSts.atBypassRemain := atRemain;
