coUnit.TEST('Voting_NoTimeSource_UsesSystemTime');
stCfg := CfgDi(eArch := E_VoteArch.Vote1oo2, ePolicy := E_DegradePolicy.VoteTrip);
stIn.axDi[1] := TRUE;
stIn.axDi[2] := TRUE;
stIn.axDiValid[1] := TRUE;
stIn.axDiValid[2] := TRUE;
stCmd.axBypassReq[2] := TRUE;
fbVote(stIn := stIn, stCmd := stCmd, stCfg := stCfg, xBypassPermit := TRUE, uiCause := 1);
AssertFalse(Condition := fbVote.xTrip, Message := 'system time: healthy group, no trip');
AssertFalse(Condition := fbVote.stSts.xCfgError, Message := 'system time: no config error');
AssertEquals_INT(Expected := TO_INT(E_BypassState.Active), Actual := TO_INT(fbVote.stSts.aeBypass[2]),
    Message := 'system time: bypass Active');
AssertTrue(Condition := fbVote.stSts.atBypassRemain[2] > T#9S, Message := 'system time: nearly full remain');
stIn.axDi[1] := FALSE;
fbVote(stIn := stIn, stCmd := stCmd, stCfg := stCfg, xBypassPermit := TRUE, uiCause := 1);
AssertTrue(Condition := fbVote.xTrip, Message := 'system time: demand on channel 1 trips 1oo1');
coUnit.TEST_FINISHED();
