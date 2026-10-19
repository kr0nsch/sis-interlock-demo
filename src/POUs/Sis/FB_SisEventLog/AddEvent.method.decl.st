// Записать событие с очередным номером (I_SisEventSink). Всегда TRUE: при заполнении кольца
// затирается самая старая запись
METHOD AddEvent : BOOL
VAR_INPUT
    stEvent : ST_SisEvent;   // событие; udiSeq заполняет журнал
END_VAR
VAR
    stRec : ST_SisEvent;     // запись с номером
END_VAR
