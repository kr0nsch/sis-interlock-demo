// Предел одного байпаса, запросы каналов 2 и 3 в одном вызове: канал 2 — Active, канал 3 — Denied;
// Denied держится до снятия запроса, даже когда место освободилось
METHOD PRIVATE BypassLimitLowestChannelWins
VAR
    fbRig : FB_VotingRig;   // стенд
    stEv  : ST_SisEvent;    // событие
END_VAR
