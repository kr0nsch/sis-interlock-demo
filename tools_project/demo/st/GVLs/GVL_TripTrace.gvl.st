// Назначение: буфер трассировки демо-сценария PRG_TripDemo: отсчёт каждые 100 мс — давление,
//             состояние канала PT101C, действующие схемы голосования, причины, следствия,
//             первопричина и сброс. После xDone буфер читает tools_project/demo/trip_trace.py.
//             В библиотеку и приложение ПАЗ не входит (только демо-проект build/demo-trip/).
// Автор:      <ИМЯ ФАМИЛИЯ>
// Версия:     0.1.0
// Документ:   tools_project/demo/README.md; docs/DESIGN.md, раздел «8.4 PRG_Main»
// ВНИМАНИЕ:   код демонстрационный и не предназначен для систем безопасности. Реальная ПАЗ
//             требует определения SIL, сертифицированных аппаратных и программных средств
//             и валидации по ГОСТ Р МЭК 61511.
{attribute 'qualified_only'}
VAR_GLOBAL CONSTANT
    TRACE_LEN : UINT := 600;                                // ёмкость: 60 с при шаге 100 мс
END_VAR
VAR_GLOBAL
    xDone            : BOOL;                                // сценарий завершён, буфер заполнен
    uiCount          : UINT;                                // записано отсчётов
    arT_s            : ARRAY[1..GVL_TripTrace.TRACE_LEN] OF REAL;    // время от первого цикла, с
    arPA_MPa         : ARRAY[1..GVL_TripTrace.TRACE_LEN] OF REAL;    // давление модели у PT101A, МПа
    arPB_MPa         : ARRAY[1..GVL_TripTrace.TRACE_LEN] OF REAL;    // давление модели у PT101B, МПа
    arPC_mA          : ARRAY[1..GVL_TripTrace.TRACE_LEN] OF REAL;    // ток PT101C на входе ПАЗ, мА
    aiArchPshh       : ARRAY[1..GVL_TripTrace.TRACE_LEN] OF INT;     // действующая схема PSHH101 (E_VoteArch)
    aiArchPsll       : ARRAY[1..GVL_TripTrace.TRACE_LEN] OF INT;     // действующая схема PSLL101 (E_VoteArch)
    aiChStateC       : ARRAY[1..GVL_TripTrace.TRACE_LEN] OF INT;     // канал 3 группы PSHH101 (E_ChannelState)
    awCausePresent   : ARRAY[1..GVL_TripTrace.TRACE_LEN] OF WORD;    // требование до задержки
    awCauseActive    : ARRAY[1..GVL_TripTrace.TRACE_LEN] OF WORD;    // требование после задержки
    awCauseLatched   : ARRAY[1..GVL_TripTrace.TRACE_LEN] OF WORD;    // причина зафиксирована до сброса
    awEffectTripped  : ARRAY[1..GVL_TripTrace.TRACE_LEN] OF WORD;    // следствие сработало
    auiFirstOut      : ARRAY[1..GVL_TripTrace.TRACE_LEN] OF UINT;    // первопричина
    awFirstOutMask   : ARRAY[1..GVL_TripTrace.TRACE_LEN] OF WORD;    // причины в вызове первопричины
    axResetPermitted : ARRAY[1..GVL_TripTrace.TRACE_LEN] OF BOOL;    // сброс сейчас разрешён
    auiResetBlocker  : ARRAY[1..GVL_TripTrace.TRACE_LEN] OF UINT;    // первая мешающая сбросу причина
    axResetButton    : ARRAY[1..GVL_TripTrace.TRACE_LEN] OF BOOL;    // кнопка HS120 нажата
    awOutputs        : ARRAY[1..GVL_TripTrace.TRACE_LEN] OF WORD;    // выходы xQ*: бит j-1 — следствие j
END_VAR
