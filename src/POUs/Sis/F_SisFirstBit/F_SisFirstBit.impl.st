uiFound := 0;
FOR uiIdx := 1 TO GVL_Const.WORD_BITS DO
    IF uiFound = 0 AND F_SisBit(wMask := wMask, uiIdx := uiIdx) THEN
        uiFound := uiIdx;
    END_IF
END_FOR
F_SisFirstBit := uiFound;
