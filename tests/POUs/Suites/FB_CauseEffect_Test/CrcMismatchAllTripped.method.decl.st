// Ручная правка конфигурации без пересчёта CRC: ошибка CEM_CFG_CRC (только она), все выходы обесточены,
// событие CfgError с кодом ошибки
METHOD PRIVATE CrcMismatchAllTripped
VAR
    fbRig : FB_CemRig;     // стенд
    stEv  : ST_SisEvent;   // событие
END_VAR
