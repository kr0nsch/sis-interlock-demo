// Умолчания ST_VotingCfg и ST_CemCfg — ошибка конфигурации (схема None, 0 причин)
METHOD PRIVATE DefaultCfgFailsSafe
VAR
    stVoteCfg : ST_VotingCfg;   // конфигурация группы по умолчанию
    stCemCfg  : ST_CemCfg;      // конфигурация матрицы по умолчанию
    wErr      : WORD;           // биты ошибок матрицы
END_VAR
