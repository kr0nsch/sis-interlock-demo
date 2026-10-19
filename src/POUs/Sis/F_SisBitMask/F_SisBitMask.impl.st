IF uiIdx >= 1 AND uiIdx <= GVL_Const.WORD_BITS THEN
    F_SisBitMask := SHL(GVL_Const.WORD_BIT0, uiIdx - 1);
ELSE
    F_SisBitMask := 0;
END_IF
