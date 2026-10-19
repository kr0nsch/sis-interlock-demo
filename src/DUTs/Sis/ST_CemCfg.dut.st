// Назначение: конфигурация матрицы причин и следствий с CRC. Значения по умолчанию дают ошибку
//             конфигурации (uiCauseCount = 0) — срабатывание всех следствий (раздел 6.8).
// Автор:      kr0nsch
// Версия:     0.1.0
// Документ:   docs/DESIGN.md, раздел «4.2 Структуры»
// ВНИМАНИЕ:   код демонстрационный и не предназначен для систем безопасности. Реальная ПАЗ
//             требует определения SIL, сертифицированных аппаратных и программных средств
//             и валидации по ГОСТ Р МЭК 61511.
{attribute 'qualified_only'}
TYPE ST_CemCfg :
STRUCT
    uiCauseCount  : UINT := 0;      // используемых причин, 1..SIS_CAUSES_MAX; 0 — ошибка (fail-safe)
    uiEffectCount : UINT := 0;      // используемых следствий, 1..SIS_EFFECTS_MAX
    xStartTripped : BOOL := TRUE;   // после старта ПЛК все следствия сработали до первого сброса
    astCause      : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF ST_CauseCfg;     // строки матрицы
    astEffect     : ARRAY[1..GVL_Const.SIS_EFFECTS_MAX] OF ST_EffectCfg;   // столбцы матрицы
    wMatrixCrc    : WORD := 0;      // CRC-16/CCITT-FALSE матрицы (раздел 6.8), считает генератор
END_STRUCT
END_TYPE
