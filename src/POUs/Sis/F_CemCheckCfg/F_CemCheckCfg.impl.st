wErr := 0;
xCauseBad := FALSE;
xEffectBad := FALSE;

IF stCfg.uiCauseCount < 1 OR stCfg.uiCauseCount > GVL_Const.SIS_CAUSES_MAX
    OR stCfg.uiEffectCount < 1 OR stCfg.uiEffectCount > GVL_Const.SIS_EFFECTS_MAX
THEN
    wErr := wErr OR GVL_Const.CEM_CFG_COUNT;
ELSE
    // Причины: источник, предел задержки, срок разрешённого обхода и подтверждение нормы для его
    // автоснятия — короче срока, иначе обход не снимется при норме раньше срока (6.4)
    FOR uiI := 1 TO stCfg.uiCauseCount DO
        stCause := stCfg.astCause[uiI];
        xSourceOk := stCause.eSource = E_CauseSource.Voting OR stCause.eSource = E_CauseSource.External;
        xOvrTimeOk := stCause.tOverrideMax > T#0S AND stCause.tOverrideMax <= GVL_Const.SIS_OVERRIDE_MAX;
        xOvrClrOk := stCause.tOverrideClear > T#0S AND stCause.tOverrideClear < stCause.tOverrideMax;
        IF NOT xSourceOk OR stCause.tDelay > GVL_Const.SIS_DELAY_MAX
            OR (stCause.xOverrideAllowed AND NOT (xOvrTimeOk AND xOvrClrOk))
        THEN
            xCauseBad := TRUE;
        END_IF
    END_FOR

    // Следствия: используемые — состояние из перечисления, маска не пуста и без причин сверх
    // uiCauseCount; неиспользуемые — пустая маска
    wUsedMask := F_SisLowMask(uiCount := stCfg.uiCauseCount);
    FOR uiJ := 1 TO GVL_Const.SIS_EFFECTS_MAX DO
        stEffect := stCfg.astEffect[uiJ];
        IF uiJ <= stCfg.uiEffectCount THEN
            xSafeOk := stEffect.eSafeState = E_SafeState.Closed OR stEffect.eSafeState = E_SafeState.Open
                OR stEffect.eSafeState = E_SafeState.Stopped OR stEffect.eSafeState = E_SafeState.Off
                OR stEffect.eSafeState = E_SafeState.Alarm;
            IF NOT xSafeOk OR stEffect.wCauseMask = 0 OR (stEffect.wCauseMask AND NOT wUsedMask) <> 0 THEN
                xEffectBad := TRUE;
            END_IF
        ELSIF stEffect.wCauseMask <> 0 THEN
            xEffectBad := TRUE;
        END_IF
    END_FOR

    IF xCauseBad THEN
        wErr := wErr OR GVL_Const.CEM_CFG_CAUSE;
    END_IF
    IF xEffectBad THEN
        wErr := wErr OR GVL_Const.CEM_CFG_EFFECT;
    END_IF
END_IF

// CRC — всегда
IF F_CemCrc(stCfg := stCfg) <> stCfg.wMatrixCrc THEN
    wErr := wErr OR GVL_Const.CEM_CFG_CRC;
END_IF

F_CemCheckCfg := wErr;
