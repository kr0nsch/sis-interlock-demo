// 70 событий в кольцо на 64: Count = 64, последнее — номер 70, самое старое — номер 7
METHOD PRIVATE RingOverwritesOldest
VAR
    fbLog  : FB_SisEventLog;   // журнал
    stEv   : ST_SisEvent;      // событие
    uiI    : UINT;             // счётчик
    xAdded : BOOL;             // результат записи
    xAll   : BOOL := TRUE;     // все записи приняты
END_VAR
