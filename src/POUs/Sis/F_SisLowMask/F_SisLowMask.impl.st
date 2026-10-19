IF uiCount = 0 THEN
    F_SisLowMask := 0;
ELSIF uiCount >= GVL_Const.WORD_BITS THEN
    // сдвиг на разрядность и больше не определён — значение задаётся явно
    F_SisLowMask := GVL_Const.WORD_ALL;
ELSE
    // старшие биты 16#FFFF после сдвига влево — единицы; XOR оставляет младшие uiCount единиц
    F_SisLowMask := SHL(GVL_Const.WORD_ALL, uiCount) XOR GVL_Const.WORD_ALL;
END_IF
