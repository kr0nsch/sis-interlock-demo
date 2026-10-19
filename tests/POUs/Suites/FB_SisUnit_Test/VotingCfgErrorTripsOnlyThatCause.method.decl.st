// Ошибка конфигурации группы 1 — требование только причины 1: она срабатывает через обычную задержку
// 2 с, следствие 2 и причина 2 работают как обычно
METHOD PRIVATE VotingCfgErrorTripsOnlyThatCause
VAR
    fbRig : FB_UnitRig;     // стенд
    stDef : ST_VotingCfg;   // конфигурация по умолчанию (ошибка)
END_VAR
