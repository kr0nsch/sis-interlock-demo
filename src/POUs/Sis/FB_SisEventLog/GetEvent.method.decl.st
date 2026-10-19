// Событие uiBack записей назад (0 — последнее); uiBack >= Count — пустая запись (все поля 0)
METHOD GetEvent : ST_SisEvent
VAR_INPUT
    uiBack : UINT;           // сколько записей назад
END_VAR
VAR
    stEmpty : ST_SisEvent;   // пустая запись
    uiIdx   : UINT;          // индекс в кольце
END_VAR
