// Источник времени узла передаётся группам и матрице: байпас группы 1 истекает ровно через 10 с
// подменного времени, задержка причины — ровно через 2 с
METHOD PRIVATE TimeSourcePassedToChildren
VAR
    fbRig : FB_UnitRig;   // стенд
END_VAR
