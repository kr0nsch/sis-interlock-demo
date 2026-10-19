// Без источника времени (itfTime = 0) — встроенный PL.FB_SystemTime: причина без задержки фиксируется,
// метка первопричины не нулевая
METHOD PRIVATE NoTimeSourceUsesSystemTime
VAR
    fbCem     : FB_CauseEffect;                                    // ФБ без источника времени
    stCfg     : ST_CemCfg;                                         // конфигурация
    stCmd     : ST_CemCmd;                                         // команды
    axCauseIn : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF BOOL;        // требования
END_VAR
