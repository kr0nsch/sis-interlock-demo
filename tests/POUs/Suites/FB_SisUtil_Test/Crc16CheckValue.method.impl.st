coUnit.TEST('Sis_Crc16_CheckValue');
wCrc := GVL_Const.CRC16_INIT;
FOR uiCh := 16#31 TO 16#39 DO
    wCrc := F_SisCrc16Byte(wCrc := wCrc, bData := UINT_TO_BYTE(uiCh));
END_FOR
AssertEquals_WORD(Expected := 16#29B1, Actual := wCrc, Message := 'CRC-16/CCITT-FALSE of 123456789');
coUnit.TEST_FINISHED();
