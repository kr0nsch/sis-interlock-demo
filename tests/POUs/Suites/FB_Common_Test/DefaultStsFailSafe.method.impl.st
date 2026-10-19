coUnit.TEST('Common_DefaultSts_FailSafe');
AssertTrue(Condition := stRes.xTrip, Message := 'ST_VoteResult default: trip');
AssertEquals_INT(Expected := TO_INT(E_VoteArch.None), Actual := TO_INT(stRes.eArchEff),
    Message := 'ST_VoteResult default: arch None');
AssertTrue(Condition := stSts.xTrip, Message := 'ST_VotingSts default: trip');
AssertTrue(Condition := fbVote.xTrip, Message := 'FB_Voting before first call: trip');
AssertTrue(Condition := fbCem.xTripped, Message := 'FB_CauseEffect before first call: tripped');
xAnyOn := FALSE;
FOR uiJ := 1 TO GVL_Const.SIS_EFFECTS_MAX DO
    xAnyOn := xAnyOn OR fbCem.axEffectOut[uiJ];
END_FOR
AssertFalse(Condition := xAnyOn, Message := 'FB_CauseEffect before first call: all outputs de-energized');
coUnit.TEST_FINISHED();
