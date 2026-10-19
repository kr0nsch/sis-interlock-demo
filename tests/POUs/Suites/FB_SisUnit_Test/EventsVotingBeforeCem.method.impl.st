coUnit.TEST('Unit_Events_VotingBeforeCem');
Setup(fbRig := fbRig);
fbRig.Cycle();
fbRig.astIn[1].axDiValid[2] := FALSE;
fbRig.Step(tStep := T#100MS);
stEv := fbRig.fbLog.GetEvent(uiBack := 1);
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.ChannelInvalid), Actual := TO_INT(stEv.eKind),
    Message := 'first: ChannelInvalid of group 1');
AssertEquals_UINT(Expected := 1, Actual := stEv.uiCause, Message := 'ChannelInvalid: cause 1');
AssertEquals_UINT(Expected := 2, Actual := stEv.uiChannel, Message := 'ChannelInvalid: channel 2');
stEv := fbRig.fbLog.GetEvent(uiBack := 0);
AssertEquals_INT(Expected := TO_INT(E_SisEventKind.CauseDemand), Actual := TO_INT(stEv.eKind),
    Message := 'then: CauseDemand of the matrix');
AssertEquals_UINT(Expected := 1, Actual := stEv.uiCause, Message := 'CauseDemand: cause 1');
coUnit.TEST_FINISHED();
