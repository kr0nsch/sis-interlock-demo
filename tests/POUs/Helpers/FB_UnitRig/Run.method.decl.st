// Шаги tStep до tDuration (последний — остаток), вызов после каждого шага; не больше 1500 шагов
METHOD Run
VAR_INPUT
    tDuration : TIME;   // сколько времени пройти
    tStep     : TIME;   // шаг
END_VAR
VAR
    tLeft  : TIME;      // осталось
    tNow   : TIME;      // этот шаг
    uiIter : UINT;      // шагов сделано
END_VAR
