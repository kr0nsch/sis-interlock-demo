// В EffectTrip — младшая зафиксированная причина из маски следствия; уже сработавшее следствие
// нового события не даёт
METHOD PRIVATE EffectTripEventCarriesCause
VAR
    fbRig : FB_CemRig;     // стенд
    stEv  : ST_SisEvent;   // событие
END_VAR
