coUnit.TEST('Sis_LowMask_Bounds');
AssertEquals_WORD(Expected := 0, Actual := F_SisLowMask(uiCount := 0), Message := 'count 0');
AssertEquals_WORD(Expected := 16#0001, Actual := F_SisLowMask(uiCount := 1), Message := 'count 1');
AssertEquals_WORD(Expected := 16#03FF, Actual := F_SisLowMask(uiCount := 10), Message := 'count 10');
AssertEquals_WORD(Expected := 16#7FFF, Actual := F_SisLowMask(uiCount := 15), Message := 'count 15');
AssertEquals_WORD(Expected := 16#FFFF, Actual := F_SisLowMask(uiCount := 16), Message := 'count 16');
AssertEquals_WORD(Expected := 16#FFFF, Actual := F_SisLowMask(uiCount := 40), Message := 'count 40');
coUnit.TEST_FINISHED();
