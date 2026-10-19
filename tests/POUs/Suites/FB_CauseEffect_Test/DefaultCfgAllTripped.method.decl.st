// Конфигурация по умолчанию (0 причин): до и после вызова все 16 выходов обесточены, ошибка
// CEM_CFG_COUNT, первопричина SIS_FIRST_OUT_CFG, сброс запрещён
METHOD PRIVATE DefaultCfgAllTripped
VAR
    fbRig  : FB_CemRig;   // стенд
    uiJ    : UINT;        // индекс следствия
    xAnyOn : BOOL;        // хотя бы один выход под напряжением
END_VAR
