coUnit.TEST('Sis_BitMask_OutOfRangeZero');
AssertEquals_WORD(Expected := 0, Actual := F_SisBitMask(uiIdx := 0), Message := 'index 0: 0');
AssertEquals_WORD(Expected := 0, Actual := F_SisBitMask(uiIdx := 17), Message := 'index 17: 0');
AssertEquals_WORD(Expected := 16#0001, Actual := F_SisBitMask(uiIdx := 1), Message := 'index 1');
AssertEquals_WORD(Expected := 16#0200, Actual := F_SisBitMask(uiIdx := 10), Message := 'index 10');
AssertEquals_WORD(Expected := 16#8000, Actual := F_SisBitMask(uiIdx := 16), Message := 'index 16');
coUnit.TEST_FINISHED();
