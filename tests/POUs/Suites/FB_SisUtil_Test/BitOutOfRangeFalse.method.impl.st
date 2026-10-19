coUnit.TEST('Sis_Bit_OutOfRangeFalse');
AssertFalse(Condition := F_SisBit(wMask := 16#FFFF, uiIdx := 0), Message := 'index 0: FALSE');
AssertFalse(Condition := F_SisBit(wMask := 16#FFFF, uiIdx := 17), Message := 'index 17: FALSE');
AssertTrue(Condition := F_SisBit(wMask := 16#0001, uiIdx := 1), Message := 'index 1 = bit 0');
AssertTrue(Condition := F_SisBit(wMask := 16#8000, uiIdx := 16), Message := 'index 16 = bit 15');
AssertFalse(Condition := F_SisBit(wMask := 16#FFFE, uiIdx := 1), Message := 'bit 0 clear');
coUnit.TEST_FINISHED();
