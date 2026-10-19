// Сколько записей кольца имеют вид eKind
METHOD CountKind : UINT
VAR_INPUT
    eKind : E_SisEventKind;   // вид события
END_VAR
VAR
    uiBack : UINT;            // сколько записей назад
    uiHits : UINT;            // найдено
    stEv   : ST_SisEvent;     // запись
END_VAR
