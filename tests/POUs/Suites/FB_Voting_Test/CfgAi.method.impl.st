stCfg.eArch := eArch;
stCfg.ePolicy := ePolicy;
stCfg.eInput := E_SisInputKind.Analog;
stCfg.eLimitDir := E_LimitDir.High;
stCfg.rTripLimit_eu := 50.0;
stCfg.rHyst_eu := 2.0;
stCfg.rDiscrepancyMax_eu := 0.0;
stCfg.tDiscrepancyDelay := T#0S;
stCfg.tBypassMax := T#10S;
IF F_VoteArchChannels(eArch := eArch) > 1 THEN
    stCfg.uiMaxBypass := 1;
ELSE
    stCfg.uiMaxBypass := 0;
END_IF
CfgAi := stCfg;
