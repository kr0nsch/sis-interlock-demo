// Гистерезис 2.0 у уставки 50.0 (1oo1): требование держится до 48.0 включительно, снимается при
// 47.99; снизу без памяти 49.0 — норма
METHOD PRIVATE HysteresisReleasesBeyondBand
VAR
    fbRig : FB_VotingRig;   // стенд
END_VAR
