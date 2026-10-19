IF udiSeq = GVL_Const.UDINT_MAX THEN
    udiSeq := 1;
ELSE
    udiSeq := udiSeq + 1;
END_IF
stRec := stEvent;
stRec.udiSeq := udiSeq;
astRing[uiNext] := stRec;
uiNext := (uiNext + 1) MOD GVL_Const.SIS_LOG_SIZE;
IF uiUsed < GVL_Const.SIS_LOG_SIZE THEN
    uiUsed := uiUsed + 1;
END_IF
AddEvent := TRUE;
