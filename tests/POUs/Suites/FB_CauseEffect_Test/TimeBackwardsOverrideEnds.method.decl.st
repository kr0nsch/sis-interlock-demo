// «Время назад» во время пускового обхода (D-19): срок обхода недостоверен — обход снимается в том же
// вызове (OverrideExpired), и причина, задержка которой прошла под обходом, сразу фиксируется
METHOD PRIVATE TimeBackwardsOverrideEnds
VAR
    fbRig : FB_CemRig;   // стенд
    ltT1  : LTIME;       // момент включения обхода
END_VAR
