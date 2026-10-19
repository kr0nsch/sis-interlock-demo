// Назначение: конфигурация группы голосования. Значения по умолчанию дают ошибку конфигурации
//             (eArch = None) — срабатывание группы (fail-safe, раздел 3.4).
// Автор:      <ИМЯ ФАМИЛИЯ>
// Версия:     0.1.0
// Документ:   docs/DESIGN.md, раздел «4.2 Структуры»
// ВНИМАНИЕ:   код демонстрационный и не предназначен для систем безопасности. Реальная ПАЗ
//             требует определения SIL, сертифицированных аппаратных и программных средств
//             и валидации по ГОСТ Р МЭК 61511.
{attribute 'qualified_only'}
TYPE ST_VotingCfg :
STRUCT
    eArch              : E_VoteArch := E_VoteArch.None;                  // None — ошибка (fail-safe)
    ePolicy            : E_DegradePolicy := E_DegradePolicy.VoteTrip;    // политика деградации
    eInput             : E_SisInputKind := E_SisInputKind.Discrete;      // вид входов
    xDiHealthy         : BOOL := TRUE;     // значение дискретного канала в норме; другое — требование
    eLimitDir          : E_LimitDir := E_LimitDir.High;                  // направление уставки (Analog)
    rTripLimit_eu      : REAL := 0.0;      // уставка срабатывания, инж. ед. (включительно)
    rHyst_eu           : REAL := 0.0;      // гистерезис снятия требования, >= 0
    rDiscrepancyMax_eu : REAL := 0.0;      // допустимый разброс каналов; 0.0 — контроль выключен
    tDiscrepancyDelay  : TIME := T#0S;     // задержка тревоги рассогласования
    tBypassMax         : TIME := T#0S;     // максимальная длительность байпаса; T#0S — байпас запрещён
    uiMaxBypass        : UINT := 0;        // одновременных байпасов в группе, 0..N-1
END_STRUCT
END_TYPE
