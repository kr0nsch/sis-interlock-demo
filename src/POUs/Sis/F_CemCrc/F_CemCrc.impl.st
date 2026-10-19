wCrc := GVL_Const.CRC16_INIT;

// Слова — младшим байтом вперёд
wVal := UINT_TO_WORD(stCfg.uiCauseCount);
wCrc := F_SisCrc16Byte(wCrc := wCrc, bData := WORD_TO_BYTE(wVal AND GVL_Const.WORD_LOW_BYTE));
wCrc := F_SisCrc16Byte(wCrc := wCrc, bData := WORD_TO_BYTE(SHR(wVal, GVL_Const.BITS_PER_BYTE)));
wVal := UINT_TO_WORD(stCfg.uiEffectCount);
wCrc := F_SisCrc16Byte(wCrc := wCrc, bData := WORD_TO_BYTE(wVal AND GVL_Const.WORD_LOW_BYTE));
wCrc := F_SisCrc16Byte(wCrc := wCrc, bData := WORD_TO_BYTE(SHR(wVal, GVL_Const.BITS_PER_BYTE)));

FOR uiJ := 1 TO GVL_Const.SIS_EFFECTS_MAX DO
    stEffect := stCfg.astEffect[uiJ];
    wVal := stEffect.wCauseMask;
    wCrc := F_SisCrc16Byte(wCrc := wCrc, bData := WORD_TO_BYTE(wVal AND GVL_Const.WORD_LOW_BYTE));
    wCrc := F_SisCrc16Byte(wCrc := wCrc, bData := WORD_TO_BYTE(SHR(wVal, GVL_Const.BITS_PER_BYTE)));
END_FOR

F_CemCrc := wCrc;
