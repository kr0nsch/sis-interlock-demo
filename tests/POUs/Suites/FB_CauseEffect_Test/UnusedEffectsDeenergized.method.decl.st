// Следствия с номером больше uiEffectCount всегда обесточены
METHOD PRIVATE UnusedEffectsDeenergized
VAR
    fbRig  : FB_CemRig;   // стенд
    uiJ    : UINT;        // индекс следствия
    xAnyOn : BOOL;        // хотя бы один неиспользуемый выход под напряжением
END_VAR
