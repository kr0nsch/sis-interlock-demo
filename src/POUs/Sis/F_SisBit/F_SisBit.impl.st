IF uiIdx >= 1 AND uiIdx <= GVL_Const.WORD_BITS THEN
    F_SisBit := (wMask AND SHL(GVL_Const.WORD_BIT0, uiIdx - 1)) <> 0;
ELSE
    F_SisBit := FALSE;
END_IF
