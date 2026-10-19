// Маска следствия с причиной сверх uiCauseCount, непустая маска неиспользуемого следствия и пустая маска
// используемого — ошибка CEM_CFG_EFFECT (CRC пересчитан)
METHOD PRIVATE MaskBeyondCountCfgError
VAR
    fbRig : FB_CemRig;   // стенд
    stCfg : ST_CemCfg;   // проверяемая конфигурация
END_VAR
