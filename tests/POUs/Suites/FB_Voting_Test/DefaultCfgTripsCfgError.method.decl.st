// Конфигурация по умолчанию (схема None): срабатывание, ошибка VOTE_CFG_ARCH, одно событие CfgError
// с номером причины и кодом ошибки; повторный вызов события не повторяет
METHOD PRIVATE DefaultCfgTripsCfgError
VAR
    fbRig : FB_VotingRig;   // стенд
    stEv  : ST_SisEvent;    // событие
END_VAR
