// В контроле рассогласования — только каналы Normal и Demand: недостоверный и байпасированный каналы
// не участвуют, при одном участнике разброс 0.0
METHOD PRIVATE DiscrepancyIgnoresBypassedAndInvalid
VAR
    fbRig : FB_VotingRig;   // стенд
END_VAR
