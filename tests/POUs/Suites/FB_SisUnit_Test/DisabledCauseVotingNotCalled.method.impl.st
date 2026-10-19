coUnit.TEST('Unit_DisabledCause_VotingNotCalled');
Setup(fbRig := fbRig);
fbRig.astIn[3].axDi[1] := FALSE;
fbRig.astIn[3].axDiValid[1] := FALSE;
fbRig.Cycle();
fbRig.Run(tDuration := T#5S, tStep := T#1S);
AssertEquals_INT(Expected := TO_INT(E_VoteArch.None), Actual := TO_INT(fbRig.fbUnit.astVoteSts[3].eArchEff),
    Message := 'disabled cause: group status default (not called)');
AssertEquals_INT(Expected := TO_INT(E_ChannelState.NotUsed),
    Actual := TO_INT(fbRig.fbUnit.astVoteSts[3].aeChState[1]), Message := 'disabled cause: channel NotUsed');
AssertEquals_UINT(Expected := 0, Actual := fbRig.fbLog.CountKind(eKind := E_SisEventKind.ChannelInvalid),
    Message := 'disabled cause: no group events');
AssertTrue(Condition := fbRig.fbUnit.axEffectOut[2], Message := 'effect 2 energized');
AssertEquals_WORD(Expected := 0, Actual := fbRig.fbUnit.stCemSts.wCausePresent, Message := 'no demand');
coUnit.TEST_FINISHED();
