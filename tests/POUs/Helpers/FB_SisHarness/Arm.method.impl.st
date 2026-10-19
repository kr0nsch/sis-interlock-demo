SetNormal();
Cycle();
PressReset();
Arm := fbApp.stCemSts.wEffectTripped = 0 AND fbApp.stCemSts.wCauseLatched = 0 AND NOT fbApp.xTripped;
