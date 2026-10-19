// Назначение: исполнитель матрицы причин и следствий: задержки причин, фиксация до ручного
//             сброса при снятых причинах, первопричина с меткой времени, пусковые обходы со сроком
//             и автоснятием после подтверждения нормы (D-20), следствия с обесточиванием на
//             срабатывание, журнал. Fail-safe: до первого вызова и при ошибке конфигурации все
//             выходы FALSE (обесточено); «время назад» — неисправность источника времени: обходы
//             снимаются, идущие задержки завершаются (D-19).
// Автор:      kr0nsch
// Версия:     0.3.0
// Документ:   docs/DESIGN.md, раздел «6. FB_CauseEffect — исполнитель матрицы»
// ВНИМАНИЕ:   код демонстрационный и не предназначен для систем безопасности. Реальная ПАЗ
//             требует определения SIL, сертифицированных аппаратных и программных средств
//             и валидации по ГОСТ Р МЭК 61511.
FUNCTION_BLOCK FB_CauseEffect
VAR_INPUT
    axCauseIn       : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF BOOL;   // TRUE — требование причины (после голосования)
    xOverridePermit : BOOL;                 // ключ разрешения пусковых обходов
    xResetHw        : BOOL;                 // кнопка «Сброс ПАЗ», действует фронт
    itfTime         : PL.I_TimeSource;      // 0 — встроенный PL.FB_SystemTime
    itfLog          : I_SisEventSink;       // 0 — без журнала
END_VAR
VAR_IN_OUT
    stCmd : ST_CemCmd;                      // импульсы HMI, ФБ сбрасывает
END_VAR
VAR_IN_OUT CONSTANT
    stCfg : ST_CemCfg;                      // конфигурация матрицы
END_VAR
VAR_OUTPUT
    axEffectOut : ARRAY[1..GVL_Const.SIS_EFFECTS_MAX] OF BOOL;   // TRUE — под напряжением (норма), FALSE — сработало
    xTripped    : BOOL := TRUE;             // хотя бы одно следствие сработало
    stSts       : ST_CauseEffectSts;        // состояние матрицы
END_VAR
VAR
    fbSysTime       : PL.FB_SystemTime;     // запасной источник времени
    itfTimeAct      : PL.I_TimeSource;      // действующий источник этого вызова
    ltNow           : LTIME;                // время этого вызова
    afbDelay        : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF PL.FB_Delay;   // задержки причин
    afbOverride     : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF PL.FB_Delay;   // таймеры пусковых обходов
    afbOvrClear     : ARRAY[1..GVL_Const.SIS_CAUSES_MAX] OF PL.FB_Delay;   // подтверждение нормы для автоснятия
    wLatched        : WORD;                 // зафиксированные причины
    wOverridden     : WORD;                 // действующие пусковые обходы
    xCfgLatch       : BOOL;                 // ошибка конфигурации была, сброса ещё не было
    xStartLatch     : BOOL;                 // срабатывание при старте, сброса ещё не было
    xFirstCall      : BOOL := TRUE;         // первый вызов
    xResetHwPrev    : BOOL := TRUE;         // кнопка, зажатая при старте, — не фронт
    xCfgErrPrev     : BOOL;                 // ошибка конфигурации прошлого вызова
    wPresentPrev    : WORD;                 // требования прошлого вызова
    wEffTrippedPrev : WORD := 16#FFFF;      // следствия прошлого вызова; начально — «сработало»
    uiFirstOut      : UINT;                 // первопричина
    ltFirstOut      : LTIME;                // момент фиксации первопричины
    wFirstOutMask   : WORD;                 // причины, зафиксированные в вызове первопричины
    udiTripCount    : UDINT;                // фиксаций первопричины с запуска
    ltPrev          : LTIME;                // время прошлого вызова: «время назад» — неисправность (D-19)
END_VAR
VAR_TEMP
    wErr            : WORD;                 // биты CEM_CFG_*
    xCfgErr         : BOOL;                 // ошибка конфигурации
    xTimeBack       : BOOL;                 // время источника меньше времени прошлого вызова
    uiNc            : UINT;                 // используемых причин (0 при ошибке конфигурации)
    uiNe            : UINT;                 // используемых следствий (0 при ошибке конфигурации)
    uiI             : UINT;                 // индекс причины
    uiJ             : UINT;                 // индекс следствия
    wBit            : WORD;                 // маска индекса
    uiFoNew         : UINT;                 // первопричина старта или конфигурации этого вызова
    xPresent        : BOOL;                 // требование причины (до задержки)
    wPresent        : WORD;                 // требования до задержки
    wActive         : WORD;                 // требования после задержки
    wReq            : WORD;                 // запросы обходов этого вызова
    wNew            : WORD;                 // причины, которые фиксируются в этом вызове
    tDelay          : TIME;                 // задержка причины
    uiBlocker       : UINT;                 // причина, которая мешает сбросу
    xResetReq       : BOOL;                 // запрос сброса
    xResetPermitted : BOOL;                 // сброс разрешён
    xTripJ          : BOOL;                 // следствие сработало
    wEffTripped     : WORD;                 // сработавшие следствия
    uiEvCause       : UINT;                 // причина для события EffectTrip
    xWasTripped     : BOOL;                 // следствие было сработавшим
    stCause         : ST_CauseCfg;          // копия строки матрицы
    stEffect        : ST_EffectCfg;         // копия столбца матрицы
END_VAR
