stCem.uiCauseCount := 3;
stCem.uiEffectCount := 2;
stCem.xStartTripped := FALSE;
stCem.astCause[1].xEnable := TRUE;
stCem.astCause[1].eSource := E_CauseSource.Voting;
stCem.astCause[1].tDelay := T#2S;
stCem.astCause[2].xEnable := TRUE;
stCem.astCause[2].eSource := E_CauseSource.External;
stCem.astCause[3].xEnable := FALSE;
stCem.astCause[3].eSource := E_CauseSource.Voting;
stCem.astEffect[1].eSafeState := E_SafeState.Closed;
stCem.astEffect[1].wCauseMask := 16#0001;
stCem.astEffect[2].eSafeState := E_SafeState.Stopped;
stCem.astEffect[2].wCauseMask := 16#0006;
stCem.wMatrixCrc := F_CemCrc(stCfg := stCem);
fbRig.stCemCfg := stCem;

stVote.eArch := E_VoteArch.Vote1oo2;
stVote.ePolicy := E_DegradePolicy.VoteTrip;
stVote.eInput := E_SisInputKind.Discrete;
stVote.xDiHealthy := TRUE;
stVote.tBypassMax := T#10S;
stVote.uiMaxBypass := 1;
fbRig.astVoteCfg[1] := stVote;
stVote.eArch := E_VoteArch.Vote1oo1;
stVote.uiMaxBypass := 0;
fbRig.astVoteCfg[3] := stVote;

FOR uiK := 1 TO GVL_Const.SIS_VOTE_CH_MAX DO
    fbRig.astIn[1].axDi[uiK] := TRUE;
    fbRig.astIn[1].axDiValid[uiK] := TRUE;
    fbRig.astIn[3].axDi[uiK] := TRUE;
    fbRig.astIn[3].axDiValid[uiK] := TRUE;
END_FOR
