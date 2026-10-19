// Контрольное значение CRC-16/CCITT-FALSE: ASCII «123456789» → 16#29B1
METHOD PRIVATE Crc16CheckValue
VAR
    wCrc : WORD;    // регистр CRC
    uiCh : UINT;    // код очередного символа
END_VAR
