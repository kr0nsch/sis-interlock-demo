coUnit.TEST('Vote_ArchHelpers_ChannelsAndRequired');
AssertEquals_UINT(Expected := 1, Actual := F_VoteArchChannels(eArch := E_VoteArch.Vote1oo1), Message := 'N 1oo1');
AssertEquals_UINT(Expected := 2, Actual := F_VoteArchChannels(eArch := E_VoteArch.Vote1oo2), Message := 'N 1oo2');
AssertEquals_UINT(Expected := 2, Actual := F_VoteArchChannels(eArch := E_VoteArch.Vote2oo2), Message := 'N 2oo2');
AssertEquals_UINT(Expected := 3, Actual := F_VoteArchChannels(eArch := E_VoteArch.Vote2oo3), Message := 'N 2oo3');
AssertEquals_UINT(Expected := 0, Actual := F_VoteArchChannels(eArch := E_VoteArch.None), Message := 'N None');
AssertEquals_UINT(Expected := 0, Actual := F_VoteArchChannels(eArch := E_VoteArch.ForcedTrip),
    Message := 'N ForcedTrip');
AssertEquals_UINT(Expected := 1, Actual := F_VoteArchRequired(eArch := E_VoteArch.Vote1oo1), Message := 'M 1oo1');
AssertEquals_UINT(Expected := 1, Actual := F_VoteArchRequired(eArch := E_VoteArch.Vote1oo2), Message := 'M 1oo2');
AssertEquals_UINT(Expected := 2, Actual := F_VoteArchRequired(eArch := E_VoteArch.Vote2oo2), Message := 'M 2oo2');
AssertEquals_UINT(Expected := 2, Actual := F_VoteArchRequired(eArch := E_VoteArch.Vote2oo3), Message := 'M 2oo3');
AssertEquals_UINT(Expected := 0, Actual := F_VoteArchRequired(eArch := E_VoteArch.None), Message := 'M None');
AssertEquals_UINT(Expected := 0, Actual := F_VoteArchRequired(eArch := E_VoteArch.ForcedTrip),
    Message := 'M ForcedTrip');
uBad.iValue := 13;
AssertEquals_UINT(Expected := 0, Actual := F_VoteArchChannels(eArch := uBad.eArch), Message := 'N of code 13');
AssertEquals_UINT(Expected := 0, Actual := F_VoteArchRequired(eArch := uBad.eArch), Message := 'M of code 13');
coUnit.TEST_FINISHED();
