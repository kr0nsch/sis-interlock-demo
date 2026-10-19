// Первопричина — причина, зафиксированная первой (3 в t0); причина 1, зафиксированная позже, — только
// в wCauseLatched; метка и маска первопричины не меняются
METHOD PRIVATE FirstOutRecordsEarliest
VAR
    fbRig : FB_CemRig;   // стенд
    ltT0  : LTIME;       // момент первой фиксации
END_VAR
