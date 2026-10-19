// Записать событие. stEvent — VAR_INPUT (копия 24 байт), а не VAR_IN_OUT CONSTANT: так нет
// ограничений RuSTy на вызов метода. TRUE — событие записано. В контракте метод называется Add:
// это имя CODESYS 3.5.17 для метода не принимает (оператор ADD) — отступление A-01
METHOD AddEvent : BOOL
VAR_INPUT
    stEvent : ST_SisEvent;   // событие; udiSeq заполняет приёмник
END_VAR
