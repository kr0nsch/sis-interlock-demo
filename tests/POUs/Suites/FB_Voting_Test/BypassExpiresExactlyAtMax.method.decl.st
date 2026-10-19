// Байпас 10 с недостоверного канала 1: на t0 + 9,9 с действует (канал Bypassed), на t0 + 10,0 с —
// Expired и BypassExpired, канал в том же вызове снова голосует (Invalid)
METHOD PRIVATE BypassExpiresExactlyAtMax
VAR
    fbRig : FB_VotingRig;   // стенд
    stEv  : ST_SisEvent;    // событие
END_VAR
