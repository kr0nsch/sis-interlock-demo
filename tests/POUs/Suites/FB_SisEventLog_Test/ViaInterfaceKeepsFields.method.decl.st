// Запись через I_SisEventSink: все поля, кроме номера, сохраняются как есть
METHOD PRIVATE ViaInterfaceKeepsFields
VAR
    fbLog  : FB_SisEventLog;   // журнал
    itfLog : I_SisEventSink;   // журнал как приёмник
    stEv   : ST_SisEvent;      // событие
    stGot  : ST_SisEvent;      // прочитанное событие
    xAdded : BOOL;             // результат записи
END_VAR
