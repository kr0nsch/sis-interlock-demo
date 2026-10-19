coUnit.TEST('Sis_FirstBit_LowestIndex');
AssertEquals_UINT(Expected := 0, Actual := F_SisFirstBit(wMask := 0), Message := 'empty mask: 0');
AssertEquals_UINT(Expected := 1, Actual := F_SisFirstBit(wMask := 16#FFFF), Message := 'full mask: 1');
AssertEquals_UINT(Expected := 3, Actual := F_SisFirstBit(wMask := 16#0014), Message := 'bits 2, 4: index 3');
AssertEquals_UINT(Expected := 16, Actual := F_SisFirstBit(wMask := 16#8000), Message := 'bit 15: index 16');
coUnit.TEST_FINISHED();
