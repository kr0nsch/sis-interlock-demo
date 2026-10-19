// F_SisLogEvent: без приёмника — FALSE; с приёмником — TRUE, поля записи переданы, номер — от журнала
METHOD PRIVATE LogEventNoSinkReturnsFalse
VAR
    fbLog   : FB_SisEventLog;   // журнал
    itfNone : I_SisEventSink;   // пустая ссылка
    xRes    : BOOL;             // результат
    stEv    : ST_SisEvent;      // последнее событие
END_VAR
