// Назначение: состояние исполнителя матрицы для HMI, журнала и тестов (раздел 6.3, шаг 8).
// Автор:      kr0nsch
// Версия:     0.2.0
// Документ:   docs/DESIGN.md, раздел «4.2 Структуры»
// ВНИМАНИЕ:   код демонстрационный и не предназначен для систем безопасности. Реальная ПАЗ
//             требует определения SIL, сертифицированных аппаратных и программных средств
//             и валидации по ГОСТ Р МЭК 61511.
{attribute 'qualified_only'}
TYPE ST_CauseEffectSts :
STRUCT
    uiFirstOut       : UINT;        // SIS_FIRST_OUT_NONE, 1..N, SIS_FIRST_OUT_START или SIS_FIRST_OUT_CFG
    ltFirstOut       : LTIME;       // момент фиксации первопричины (I_TimeSource); LTIME#0S — нет
    wFirstOutMask    : WORD;        // все причины, зафиксированные в вызове первопричины
    wCausePresent    : WORD;        // требование есть сейчас (до задержки), причина включена
    wCauseActive     : WORD;        // требование после задержки (без учёта обхода)
    wCauseLatched    : WORD;        // причина зафиксирована, до сброса
    wOverridden      : WORD;        // пусковой обход действует
    wEffectTripped   : WORD;        // следствие сработало (выход обесточен), j <= uiEffectCount
    xTripped         : BOOL;        // хотя бы одно следствие сработало
    xResetPermitted  : BOOL;        // сброс сейчас разрешён
    uiResetBlocker   : UINT;        // 0 — нет; первая мешающая причина; SIS_FIRST_OUT_CFG — ошибка конфигурации
    xCfgError        : BOOL;        // ошибка конфигурации матрицы
    wCfgErr          : WORD;        // биты CEM_CFG_*
    udiTripCount     : UDINT;       // фиксаций первопричины с запуска
    atOverrideRemain : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF TIME;   // остаток обхода; T#0S — обхода нет
    atDelayRemain    : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF TIME;   // остаток задержки; T#0S — отсчёта нет
    // остаток подтверждения нормы до автоснятия обхода (6.4, п. 5); T#0S — обхода нет или требование есть
    atOverrideClearRemain : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF TIME;
END_STRUCT
END_TYPE
