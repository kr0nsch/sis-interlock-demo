// Последняя (самая новая) запись вида eKind; нет такой — пустая запись (eKind = None)
METHOD LastOfKind : ST_SisEvent
VAR_INPUT
    eKind : E_SisEventKind;   // вид события
END_VAR
VAR
    uiBack  : UINT;           // сколько записей назад
    xFound  : BOOL;           // запись найдена
    stEv    : ST_SisEvent;    // запись
    stFound : ST_SisEvent;    // результат
END_VAR
