tLeft := tDuration;
uiIter := 0;
WHILE tLeft > T#0S AND tStep > T#0S AND uiIter < 1500 DO
    tNow := MIN(tStep, tLeft);
    Step(tStep := tNow);
    tLeft := tLeft - tNow;
    uiIter := uiIter + 1;
END_WHILE
