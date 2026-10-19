// TRUE — после MarkEvents в журнале есть событие eKind причины uiCause (порядок внутри вызова не важен).
METHOD HasEvent : BOOL
VAR_INPUT
    eKind   : E_SisEventKind;   // вид события
    uiCause : UINT;             // номер причины
END_VAR
VAR
    uiBack : UINT;              // сколько событий назад
    stEv   : ST_SisEvent;       // событие журнала
    xNewer : BOOL;              // событие новее отметки
END_VAR
