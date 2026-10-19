// Порядок событий в одном вызове (6.9): CauseDemand → OverrideOn → ResetDenied → FirstOut → CauseTrip
// → EffectTrip; внутри вида — по возрастанию индекса; номера подряд, метка одна
METHOD PRIVATE EventsOrderInCall
VAR
    fbRig  : FB_CemRig;     // стенд
    stEv   : ST_SisEvent;   // событие
    stLast : ST_SisEvent;   // последнее событие
    udiSeq : UDINT;         // номер события до вызова
END_VAR
