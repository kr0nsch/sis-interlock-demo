// F_CemCheckCfg: каждое правило таблицы 4.3 даёт свой бит; при CEM_CFG_COUNT причины и следствия не
// проверяются, CRC — всегда
METHOD PRIVATE CfgCheckDetectsEachRule
VAR
    stCfg : ST_CemCfg;      // проверяемая конфигурация
    uBad  : U_SisEnumInt;   // значение вне перечисления
END_VAR
