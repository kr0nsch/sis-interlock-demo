// Шаги tStep до суммарной длительности tDuration, последний шаг — остаток; tDuration = T#0S — ничего;
// tStep = T#0S — один шаг на всю длительность. Не больше RUN_MAX_ITERATIONS шагов.
METHOD Run
VAR_INPUT
    tDuration : TIME;   // сколько времени прогнать
    tStep     : TIME;   // шаг
END_VAR
VAR
    tLeft  : TIME;      // осталось
    tThis  : TIME;      // шаг этой итерации
    uiIter : UINT;      // итераций
END_VAR
