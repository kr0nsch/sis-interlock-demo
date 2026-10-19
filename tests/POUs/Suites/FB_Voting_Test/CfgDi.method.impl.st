stCfg.eArch := eArch;
stCfg.ePolicy := ePolicy;
stCfg.eInput := E_SisInputKind.Discrete;
stCfg.xDiHealthy := TRUE;
stCfg.tBypassMax := T#10S;
IF F_VoteArchChannels(eArch := eArch) > 1 THEN
    stCfg.uiMaxBypass := 1;
ELSE
    stCfg.uiMaxBypass := 0;
END_IF
CfgDi := stCfg;
