wErr := 0;
uiN := F_VoteArchChannels(eArch := stCfg.eArch);

// Схема: только 1oo1, 1oo2, 2oo2, 2oo3 (None и ForcedTrip — ошибка)
IF uiN = 0 THEN
    wErr := wErr OR GVL_Const.VOTE_CFG_ARCH;
END_IF

IF NOT (stCfg.ePolicy = E_DegradePolicy.VoteTrip OR stCfg.ePolicy = E_DegradePolicy.DegradeSafe
    OR stCfg.ePolicy = E_DegradePolicy.DegradeAvailable)
THEN
    wErr := wErr OR GVL_Const.VOTE_CFG_POLICY;
END_IF

IF NOT (stCfg.eInput = E_SisInputKind.Discrete OR stCfg.eInput = E_SisInputKind.Analog) THEN
    wErr := wErr OR GVL_Const.VOTE_CFG_INPUT;
END_IF

// Поля аналога проверяются только для Analog; для Discrete они не действуют
IF stCfg.eInput = E_SisInputKind.Analog THEN
    IF NOT PL.F_IsFinite(rIn := stCfg.rTripLimit_eu) OR NOT PL.F_IsFinite(rIn := stCfg.rHyst_eu)
        OR stCfg.rHyst_eu < 0.0
        OR NOT (stCfg.eLimitDir = E_LimitDir.High OR stCfg.eLimitDir = E_LimitDir.Low)
    THEN
        wErr := wErr OR GVL_Const.VOTE_CFG_LIMIT;
    END_IF
    IF NOT PL.F_IsFinite(rIn := stCfg.rDiscrepancyMax_eu) OR stCfg.rDiscrepancyMax_eu < 0.0
        OR stCfg.tDiscrepancyDelay > GVL_Const.SIS_DELAY_MAX
    THEN
        wErr := wErr OR GVL_Const.VOTE_CFG_DISCREPANCY;
    END_IF
END_IF

// Байпасов — не больше N − 1 (хотя бы один канал голосует); при неверной схеме — ни одного
IF uiN = 0 THEN
    xBypassBad := stCfg.uiMaxBypass > 0;
ELSE
    xBypassBad := stCfg.uiMaxBypass > uiN - 1;
END_IF
IF xBypassBad OR stCfg.tBypassMax > GVL_Const.SIS_BYPASS_MAX THEN
    wErr := wErr OR GVL_Const.VOTE_CFG_BYPASS;
END_IF

F_VoteCheckCfg := wErr;
