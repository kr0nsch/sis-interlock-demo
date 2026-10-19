// Обозначения — как в псевдокоде раздела 5.2; целые со знаком (DINT)
diN := UINT_TO_DINT(F_VoteArchChannels(eArch := eArch));
diM := UINT_TO_DINT(F_VoteArchRequired(eArch := eArch));
diN2oo3 := UINT_TO_DINT(GVL_Const.VOTE_2OO3_CHANNELS);
xPolicyOk := ePolicy = E_DegradePolicy.VoteTrip OR ePolicy = E_DegradePolicy.DegradeSafe
    OR ePolicy = E_DegradePolicy.DegradeAvailable;
diB := 0;
diF := 0;
diD := 0;
diH := 0;

// По умолчанию — срабатывание без схемы: так заканчивается ветка «N = 0 или политика вне перечисления»
stRes.xTrip := TRUE;
stRes.xDegraded := FALSE;
stRes.eArchEff := E_VoteArch.None;
stRes.uiDemand := 0;
stRes.uiInvalid := 0;
stRes.uiBypassed := 0;
stRes.uiNormal := 0;

IF diN > 0 AND xPolicyOk THEN
    // Счёт состояний каналов 1..N: B — Bypassed, F — Invalid (и NotUsed), D — Demand, H — Normal.
    // Значение вне перечисления считается недостоверным каналом (безопасная сторона)
    FOR uiK := 1 TO DINT_TO_UINT(diN) DO
        CASE aeCh[uiK] OF
            E_ChannelState.Bypassed:
                diB := diB + 1;
            E_ChannelState.Demand:
                diD := diD + 1;
            E_ChannelState.Normal:
                diH := diH + 1;
        ELSE
            diF := diF + 1;
        END_CASE
    END_FOR
    stRes.uiDemand := DINT_TO_UINT(diD);
    stRes.uiInvalid := DINT_TO_UINT(diF);
    stRes.uiBypassed := DINT_TO_UINT(diB);
    stRes.uiNormal := DINT_TO_UINT(diH);
    stRes.xDegraded := (diB + diF) > 0;

    // Байпасированный канал исключается всегда; недостоверный — голосует «на останов» (VoteTrip)
    // или исключается (DegradeSafe, DegradeAvailable)
    IF ePolicy = E_DegradePolicy.VoteTrip THEN
        diX := diB;
        diFv := diF;
    ELSE
        diX := diB + diF;
        diFv := 0;
    END_IF
    diR := diN - diX;

    IF diR > 0 THEN
        IF ePolicy = E_DegradePolicy.DegradeAvailable THEN
            diMeff := MIN(diM, diR);
        ELSE
            diMeff := MAX(1, diM - diX);
        END_IF
        diMh := diMeff - diFv;
        diRh := diR - diFv;
        IF diMh > 0 THEN
            stRes.xTrip := diD >= diMh;
            IF diMh = 1 AND diRh = 1 THEN
                stRes.eArchEff := E_VoteArch.Vote1oo1;
            ELSIF diMh = 1 AND diRh = 2 THEN
                stRes.eArchEff := E_VoteArch.Vote1oo2;
            ELSIF diMh = 2 AND diRh = 2 THEN
                stRes.eArchEff := E_VoteArch.Vote2oo2;
            ELSIF diMh = 2 AND diRh = diN2oo3 THEN
                stRes.eArchEff := E_VoteArch.Vote2oo3;
            ELSE
                // недостижимо для схем таблицы 5.1 — защитная ветвь
                stRes.eArchEff := E_VoteArch.None;
                stRes.xTrip := TRUE;
            END_IF
        ELSE
            // недостоверные каналы уже дают требуемое число голосов
            stRes.xTrip := TRUE;
            stRes.eArchEff := E_VoteArch.ForcedTrip;
        END_IF
    ELSE
        // голосовать некем: все каналы исключены
        stRes.xTrip := TRUE;
        stRes.eArchEff := E_VoteArch.ForcedTrip;
    END_IF
END_IF

F_VoteEval := stRes;
