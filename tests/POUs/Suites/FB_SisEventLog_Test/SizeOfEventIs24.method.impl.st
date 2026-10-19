coUnit.TEST('Log_SizeOfEvent_Is24');
AssertEquals_UDINT(Expected := 24, Actual := TO_UDINT(SIZEOF(stEv)), Message := 'SIZEOF(ST_SisEvent) = 24');
coUnit.TEST_FINISHED();
