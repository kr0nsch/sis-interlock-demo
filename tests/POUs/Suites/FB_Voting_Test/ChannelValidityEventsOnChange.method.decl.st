// События достоверности — только по смене: исправные каналы при первом вызове событий не дают,
// повтор недостоверности не повторяет событие, возврат — ChannelValid
METHOD PRIVATE ChannelValidityEventsOnChange
VAR
    fbRig : FB_VotingRig;   // стенд
    stEv  : ST_SisEvent;    // событие
END_VAR
