// 1. Первый цикл: нормальные значения входов (как PRG_Main в демо без ввода-вывода)
ltNow := GVL_Sis.fbTime.Now();
IF xInit THEN
    F_SisIoNormal(stIo := GVL_SisIo.stIo);
    ltStart := ltNow;
    ltPrev := ltNow;
    lrP_MPa := P_NORMAL_MPA;
    lrSpan_MPa := REAL_TO_LREAL(GVL_SisCfg.AI_PT101A_HI_EU - GVL_SisCfg.AI_PT101A_LO_EU);
    xInit := FALSE;
END_IF
lrT_s := ULINT_TO_LREAL(LTIME_TO_ULINT(ltNow - ltStart)) / NS_PER_S;
lrDt_s := ULINT_TO_LREAL(LTIME_TO_ULINT(ltNow - ltPrev)) / NS_PER_S;
ltPrev := ltNow;

// 2. Модель давления: рост при открытом ESDV101, падение к P_SINK_MPA при закрытом
IF lrT_s >= T_RISE_S THEN
    IF GVL_SisIo.stIo.xQESDV101 THEN
        lrP_MPa := MIN(P_MAX_MPA, lrP_MPa + P_RISE_MPA_S * lrDt_s);
    ELSE
        lrP_MPa := lrP_MPa + (P_SINK_MPA - lrP_MPa) * MIN(1.0, lrDt_s / TAU_DECAY_S);
    END_IF
END_IF
lrPB_MPa := lrP_MPa + OFFSET_B_MPA;
lrPC_MPa := lrP_MPa + OFFSET_C_MPA;

// 3. Входы ПАЗ: токи 4–20 мА; PT101C — обрыв линии с T_WIRE_BREAK_S
GVL_SisIo.stIo.rPT101A_mA := LREAL_TO_REAL(MA_ZERO + MA_SPAN * lrP_MPa / lrSpan_MPa);
GVL_SisIo.stIo.rPT101B_mA := LREAL_TO_REAL(MA_ZERO + MA_SPAN * lrPB_MPa / lrSpan_MPa);
IF lrT_s >= T_WIRE_BREAK_S THEN
    GVL_SisIo.stIo.rPT101C_mA := MA_WIRE_BREAK;
ELSE
    GVL_SisIo.stIo.rPT101C_mA := LREAL_TO_REAL(MA_ZERO + MA_SPAN * lrPC_MPa / lrSpan_MPa);
END_IF
GVL_SisIo.stIo.xHS120 := (lrT_s >= T_RESET_1_S AND lrT_s < T_RESET_1_S + T_PULSE_S)
    OR (lrT_s >= T_RESET_2_S AND lrT_s < T_RESET_2_S + T_PULSE_S);

// 4. Логика ПАЗ — та же программа, что в приложении (PRG_Main → PRG_Sis)
PRG_Sis();

// 5. Отсчёт трассировки каждые T_SAMPLE_S
IF NOT GVL_TripTrace.xDone AND lrT_s >= lrNextSample_s THEN
    IF GVL_TripTrace.uiCount < GVL_TripTrace.TRACE_LEN THEN
        uiIdx := GVL_TripTrace.uiCount + 1;
        wOut := 0;
        wOut.0 := GVL_SisIo.stIo.xQESDV101;
        wOut.1 := GVL_SisIo.stIo.xQBDV101;
        wOut.2 := GVL_SisIo.stIo.xQESDV102;
        wOut.3 := GVL_SisIo.stIo.xQP101A;
        wOut.4 := GVL_SisIo.stIo.xQP101B;
        wOut.5 := GVL_SisIo.stIo.xQH101;
        wOut.6 := GVL_SisIo.stIo.xQUA110;
        GVL_TripTrace.arT_s[uiIdx] := LREAL_TO_REAL(lrT_s);
        GVL_TripTrace.arPA_MPa[uiIdx] := LREAL_TO_REAL(lrP_MPa);
        GVL_TripTrace.arPB_MPa[uiIdx] := LREAL_TO_REAL(lrPB_MPa);
        GVL_TripTrace.arPC_mA[uiIdx] := GVL_SisIo.stIo.rPT101C_mA;
        GVL_TripTrace.aiArchPshh[uiIdx] := TO_INT(GVL_Sis.fbApp.astVoteSts[GVL_SisCfg.CAUSE_PSHH101].eArchEff);
        GVL_TripTrace.aiArchPsll[uiIdx] := TO_INT(GVL_Sis.fbApp.astVoteSts[GVL_SisCfg.CAUSE_PSLL101].eArchEff);
        GVL_TripTrace.aiChStateC[uiIdx] := TO_INT(GVL_Sis.fbApp.astVoteSts[GVL_SisCfg.CAUSE_PSHH101].aeChState[3]);
        GVL_TripTrace.awCausePresent[uiIdx] := GVL_Sis.fbApp.stCemSts.wCausePresent;
        GVL_TripTrace.awCauseActive[uiIdx] := GVL_Sis.fbApp.stCemSts.wCauseActive;
        GVL_TripTrace.awCauseLatched[uiIdx] := GVL_Sis.fbApp.stCemSts.wCauseLatched;
        GVL_TripTrace.awEffectTripped[uiIdx] := GVL_Sis.fbApp.stCemSts.wEffectTripped;
        GVL_TripTrace.auiFirstOut[uiIdx] := GVL_Sis.fbApp.stCemSts.uiFirstOut;
        GVL_TripTrace.awFirstOutMask[uiIdx] := GVL_Sis.fbApp.stCemSts.wFirstOutMask;
        GVL_TripTrace.axResetPermitted[uiIdx] := GVL_Sis.fbApp.stCemSts.xResetPermitted;
        GVL_TripTrace.auiResetBlocker[uiIdx] := GVL_Sis.fbApp.stCemSts.uiResetBlocker;
        GVL_TripTrace.axResetButton[uiIdx] := GVL_SisIo.stIo.xHS120;
        GVL_TripTrace.awOutputs[uiIdx] := wOut;
        GVL_TripTrace.uiCount := uiIdx;
    END_IF
    lrNextSample_s := lrNextSample_s + T_SAMPLE_S;
END_IF
IF lrT_s >= T_END_S THEN
    GVL_TripTrace.xDone := TRUE;
END_IF
