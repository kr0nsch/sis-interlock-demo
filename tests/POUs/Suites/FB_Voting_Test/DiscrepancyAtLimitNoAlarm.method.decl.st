// Порог рассогласования строгий: разброс ровно 1.0 при допуске 1.0 — тревоги нет, 1.25 — есть
METHOD PRIVATE DiscrepancyAtLimitNoAlarm
VAR
    fbRig : FB_VotingRig;   // стенд
END_VAR
