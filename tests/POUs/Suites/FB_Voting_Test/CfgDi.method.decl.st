// Конфигурация дискретной группы для тестов: норма канала TRUE, байпас до 10 с, один байпас
// (для 1oo1 — ни одного)
METHOD CfgDi : ST_VotingCfg
VAR_INPUT
    eArch   : E_VoteArch;        // схема
    ePolicy : E_DegradePolicy;   // политика
END_VAR
VAR
    stCfg : ST_VotingCfg;        // результат
END_VAR
