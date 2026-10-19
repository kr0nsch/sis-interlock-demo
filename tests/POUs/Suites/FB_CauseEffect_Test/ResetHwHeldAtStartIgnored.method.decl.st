// Кнопка, зажатая при старте ПЛК, — не фронт: срабатывание при старте не сбрасывается
METHOD PRIVATE ResetHwHeldAtStartIgnored
VAR
    fbRig : FB_CemRig;   // стенд
END_VAR
