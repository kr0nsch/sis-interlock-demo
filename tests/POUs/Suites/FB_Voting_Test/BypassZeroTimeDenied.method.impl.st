coUnit.TEST('Voting_Bypass_ZeroTimeDenied');
fbRig.stCfg := CfgDi(eArch := E_VoteArch.Vote2oo3, ePolicy := E_DegradePolicy.VoteTrip);
fbRig.stCfg.tBypassMax := T#0S;
fbRig.SetDi(x1 := TRUE, x2 := TRUE, x3 := TRUE);
fbRig.stCmd.axBypassReq[1] := TRUE;
fbRig.Cycle();
AssertFalse(Condition := fbRig.fbVote.stSts.xCfgError, Message := 'T#0S is a valid config');
AssertEquals_INT(Expected := TO_INT(E_BypassState.Denied), Actual := fbRig.BypassOf(uiCh := 1),
    Message := 'tBypassMax 0: Denied');
coUnit.TEST_FINISHED();
