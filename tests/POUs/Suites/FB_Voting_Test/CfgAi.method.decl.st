// Конфигурация аналоговой группы для тестов: уставка 50.0 (High), гистерезис 2.0, рассогласование
// выключено, байпас до 10 с, один байпас (для 1oo1 — ни одного)
METHOD CfgAi : ST_VotingCfg
VAR_INPUT
    eArch   : E_VoteArch;        // схема
    ePolicy : E_DegradePolicy;   // политика
END_VAR
VAR
    stCfg : ST_VotingCfg;        // результат
END_VAR
