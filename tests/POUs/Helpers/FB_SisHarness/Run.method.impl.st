tLeft := tDuration;
uiIter := 0;
WHILE tLeft > T#0S AND uiIter < RUN_MAX_ITERATIONS DO
    IF tStep > T#0S AND tStep < tLeft THEN
        tThis := tStep;
    ELSE
        tThis := tLeft;
    END_IF
    Step(tStep := tThis);
    tLeft := tLeft - tThis;
    uiIter := uiIter + 1;
END_WHILE
