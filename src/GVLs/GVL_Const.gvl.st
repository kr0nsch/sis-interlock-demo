// Назначение: константы проекта ПАЗ: пределы матрицы и групп голосования, коды первопричины,
//             CRC-16/CCITT-FALSE, биты ошибок конфигурации. В логике нет «магических чисел» —
//             только имена отсюда. Обращение — GVL_Const.X; константы библиотеки — PL.GVL_Const.X.
// Автор:      <ИМЯ ФАМИЛИЯ>
// Версия:     0.1.0
// Документ:   docs/DESIGN.md, раздел «4.3 GVL_Const»
// ВНИМАНИЕ:   код демонстрационный и не предназначен для систем безопасности. Реальная ПАЗ
//             требует определения SIL, сертифицированных аппаратных и программных средств
//             и валидации по ГОСТ Р МЭК 61511.
{attribute 'qualified_only'}
VAR_GLOBAL CONSTANT
    // Пределы матрицы и групп (маски — WORD, поэтому не больше 16 причин и 16 следствий, D-12)
    SIS_CAUSES_MAX : UINT := 16;              // причин в матрице = разрядность масок
    SIS_EFFECTS_MAX : UINT := 16;             // следствий
    SIS_VOTE_CH_MAX : UINT := 3;              // каналов в группе голосования
    SIS_LOG_SIZE : UINT := 64;                // ёмкость кольцевого журнала событий

    // Пределы длительностей
    SIS_DELAY_MAX : TIME := T#10M;            // предел задержки причины и задержки рассогласования
    SIS_OVERRIDE_MAX : TIME := T#2H;          // предел пускового обхода
    SIS_BYPASS_MAX : TIME := T#12H;           // предел байпаса канала

    // Коды первопричины (uiFirstOut, uiCause событий)
    SIS_FIRST_OUT_NONE : UINT := 0;           // первопричины нет
    SIS_FIRST_OUT_START : UINT := 16#FFFE;    // срабатывание при старте ПЛК
    SIS_FIRST_OUT_CFG : UINT := 16#FFFF;      // ошибка конфигурации матрицы

    // CRC-16/CCITT-FALSE (раздел 6.8) и работа с битами
    CRC16_INIT : WORD := 16#FFFF;             // начальное значение
    CRC16_POLY : WORD := 16#1021;             // полином
    CRC16_MSB : WORD := 16#8000;              // старший бит
    BITS_PER_BYTE : UINT := 8;                // бит в байте
    WORD_BIT0 : WORD := 16#0001;              // бит 0 (маски строятся сдвигом)
    WORD_LOW_BYTE : WORD := 16#00FF;          // младший байт слова
    WORD_ALL : WORD := 16#FFFF;               // все биты слова (wEffectTripped при ошибке конфигурации)
    WORD_BITS : UINT := 16;                   // разрядность WORD: индексы битов 1..16
    UDINT_MAX : UDINT := 16#FFFFFFFF;         // после него номер события журнала — снова 1

    // Схемы голосования: каналов N и голосов M (таблица 5.1); 1 и 2 — литералы
    VOTE_2OO3_CHANNELS : UINT := 3;           // N схемы 2oo3

    // Биты ошибок конфигурации группы голосования (F_VoteCheckCfg, ST_VotingSts.wCfgErr)
    VOTE_CFG_ARCH : WORD := 16#0001;          // eArch вне {1oo1, 1oo2, 2oo2, 2oo3}
    VOTE_CFG_POLICY : WORD := 16#0002;        // ePolicy вне перечисления
    VOTE_CFG_INPUT : WORD := 16#0004;         // eInput вне перечисления
    VOTE_CFG_LIMIT : WORD := 16#0008;         // Analog: уставка не конечна, гистерезис < 0 или не конечен, eLimitDir
    VOTE_CFG_DISCREPANCY : WORD := 16#0010;   // Analog: rDiscrepancyMax_eu < 0 или не конечен, задержка > предела
    VOTE_CFG_BYPASS : WORD := 16#0020;        // uiMaxBypass > N − 1 или tBypassMax > SIS_BYPASS_MAX

    // Биты ошибок конфигурации матрицы (F_CemCheckCfg, ST_CauseEffectSts.wCfgErr)
    CEM_CFG_COUNT : WORD := 16#0001;          // uiCauseCount или uiEffectCount вне 1..MAX
    CEM_CFG_CAUSE : WORD := 16#0002;          // используемая причина: источник, задержка, обход
    CEM_CFG_EFFECT : WORD := 16#0004;         // используемое следствие: состояние, маска; маска неиспользуемого
    CEM_CFG_CRC : WORD := 16#0008;            // F_CemCrc(stCfg) <> stCfg.wMatrixCrc

    // Демонстрация без ввода-вывода: PRG_Main в первом цикле ставит нормальные значения входов
    DEMO_IO_SIMULATION : BOOL := TRUE;
END_VAR
