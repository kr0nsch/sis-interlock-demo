// xStartTripped = FALSE: в первом вызове используемые следствия под напряжением (EffectRestore,
// начальное состояние — «сработало»), неиспользуемые обесточены, первопричины нет
METHOD PRIVATE StartNotTrippedEnergizedFirstCall
VAR
    fbRig : FB_CemRig;   // стенд
END_VAR
