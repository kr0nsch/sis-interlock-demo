// F_VoteCheckCfg: каждое правило таблицы 4.3 даёт свой бит; верная конфигурация — 0
METHOD PRIVATE CfgCheckDetectsEachRule
VAR
    stCfg : ST_VotingCfg;    // проверяемая конфигурация
    uBad  : U_SisEnumInt;    // значение вне перечисления
    uNaN  : PL.U_RealBits;   // NaN
END_VAR
