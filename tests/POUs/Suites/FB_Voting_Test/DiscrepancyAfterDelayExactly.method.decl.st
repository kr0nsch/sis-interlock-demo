// Разброс 1.5 при допуске 1.0 и задержке 5 с: на t0 + 4,9 с тревоги нет, на t0 + 5,0 с — есть,
// событие DiscrepancyOn с разбросом
METHOD PRIVATE DiscrepancyAfterDelayExactly
VAR
    fbRig : FB_VotingRig;   // стенд
    stEv  : ST_SisEvent;    // событие
END_VAR
