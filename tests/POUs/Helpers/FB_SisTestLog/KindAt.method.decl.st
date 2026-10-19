// Код вида записи uiBack назад (0 — последняя); вне журнала — 0 (None)
METHOD KindAt : INT
VAR_INPUT
    uiBack : UINT;            // сколько записей назад
END_VAR
VAR
    stEv : ST_SisEvent;       // запись
END_VAR
