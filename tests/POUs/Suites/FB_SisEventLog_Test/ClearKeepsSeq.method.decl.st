// Clear: записей 0, номер последнего события сохраняется, следующее событие — следующий номер
METHOD PRIVATE ClearKeepsSeq
VAR
    fbLog : FB_SisEventLog;   // журнал
    stEv  : ST_SisEvent;      // событие
END_VAR
