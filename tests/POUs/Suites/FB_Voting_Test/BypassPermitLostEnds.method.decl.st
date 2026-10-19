// Снятие ключа разрешения заканчивает действующий байпас: Denied и BypassOff, канал снова голосует;
// возврат ключа при удержанном запросе байпас не возобновляет
METHOD PRIVATE BypassPermitLostEnds
VAR
    fbRig : FB_VotingRig;   // стенд
    stEv  : ST_SisEvent;    // событие
END_VAR
