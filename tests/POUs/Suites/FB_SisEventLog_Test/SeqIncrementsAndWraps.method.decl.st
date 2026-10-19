// Номер события растёт на 1; после 16#FFFFFFFF — снова 1 (0 не выдаётся)
METHOD PRIVATE SeqIncrementsAndWraps
VAR
    fbLog : FB_SisTestLog;    // журнал с установкой номера
    stEv  : ST_SisEvent;      // событие
END_VAR
