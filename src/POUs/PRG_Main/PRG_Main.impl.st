// в демо без ввода-вывода — нормальные значения входов в первом цикле
IF xFirstCycle AND GVL_Const.DEMO_IO_SIMULATION THEN
    F_SisIoNormal(stIo := GVL_SisIo.stIo);
END_IF
xFirstCycle := FALSE;
PRG_Sis();
