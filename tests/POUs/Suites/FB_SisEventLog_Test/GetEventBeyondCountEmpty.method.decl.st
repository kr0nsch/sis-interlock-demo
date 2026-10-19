// GetEvent(uiBack >= Count) — пустая запись: все поля 0
METHOD PRIVATE GetEventBeyondCountEmpty
VAR
    fbLog : FB_SisEventLog;   // журнал
    stEv  : ST_SisEvent;      // событие
END_VAR
