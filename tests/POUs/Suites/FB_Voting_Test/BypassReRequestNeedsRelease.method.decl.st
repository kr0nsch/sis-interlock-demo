// После истечения байпаса удержанный запрос его не возобновляет (Expired); снять запрос и подать
// снова — новый байпас на полный срок
METHOD PRIVATE BypassReRequestNeedsRelease
VAR
    fbRig : FB_VotingRig;   // стенд
END_VAR
