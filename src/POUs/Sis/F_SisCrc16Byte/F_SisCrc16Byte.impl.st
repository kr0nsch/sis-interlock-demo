wReg := wCrc XOR SHL(BYTE_TO_WORD(bData), GVL_Const.BITS_PER_BYTE);
FOR uiBit := 1 TO GVL_Const.BITS_PER_BYTE DO
    IF (wReg AND GVL_Const.CRC16_MSB) <> 0 THEN
        wReg := SHL(wReg, 1) XOR GVL_Const.CRC16_POLY;
    ELSE
        wReg := SHL(wReg, 1);
    END_IF
END_FOR
F_SisCrc16Byte := wReg;
