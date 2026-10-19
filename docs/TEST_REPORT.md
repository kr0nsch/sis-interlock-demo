# Отчёт о тестировании

> **Внимание.** Код демонстрационный и не предназначен для систем безопасности. Реальная ПАЗ
> требует определения SIL, сертифицированных аппаратных и программных средств и валидации по
> ГОСТ Р МЭК 61511.

Результаты тестов coUnit (CfUnit 1.2.0.0) в CODESYS Control Win V3, сборки и проверок без CODESYS.
«Проверено в CODESYS» пишется только после реального прогона. Раздел «Последний прогон в CODESYS»
обновляет `python tools/codesys/cds.py report` по итогам `cds.py test` (`build/test-results.json`);
правки внутри него вручную перезаписываются. Те же результаты по шагам протокола испытаний —
[FAT_REPORT.md](FAT_REPORT.md) (`python -m cemgen fat-report`).

<!-- cds:test-report:begin (раздел обновляет `python tools/codesys/cds.py report`) -->
## Последний прогон в CODESYS

Проверено в CODESYS 3.5.17.30 / CODESYS Control Win V3 (пользовательский процесс) — 2026-10-19 11:58:19. Итог: **все тесты пройдены**.

| Параметр | Значение |
|---|---|
| Дата прогона | 2026-10-19 11:58:19 |
| Коммит | 03bd1d0-dirty |
| CODESYS | 3.5.17.30 (профиль `CODESYS V3.5 SP17 Patch 3`) |
| Устройство в проекте | CODESYS Control Win V3 (4096 / 0000 0001 / 3.5.17.30) |
| Рантайм | CODESYS Control Win V3 (пользовательский процесс) |
| Фреймворк тестов | coUnit (CfUnit) 1.2.0.0 |
| Сборка | ошибок 0, предупреждений 0 |
| Способ запуска | `python tools/codesys/cds.py test` |

| Набор | Тестов | Пройдено | Упало | Пропущено | Итог |
|---|---|---|---|---|---|
| `GVL_TestsSis.fbVoteEvalTest` | 7 | 7 | 0 | 0 | пройдено |
| `GVL_TestsSis.fbVotingTest` | 27 | 27 | 0 | 0 | пройдено |
| `GVL_TestsSis.fbCauseEffectTest` | 42 | 42 | 0 | 0 | пройдено |
| `GVL_TestsSis.fbSisEventLogTest` | 6 | 6 | 0 | 0 | пройдено |
| `GVL_TestsSis.fbSisUnitTest` | 5 | 5 | 0 | 0 | пройдено |
| `GVL_TestsSis.fbSisUtilTest` | 9 | 9 | 0 | 0 | пройдено |
| `GVL_TestsSis.fbCommonTest` | 4 | 4 | 0 | 0 | пройдено |
| `GVL_TestsTruthTables.fbVoteTableEvalTest` | 12 | 12 | 0 | 0 | пройдено |
| `GVL_TestsTruthTables.fbVoteTable2oo3VTDITest` | 1 | 1 | 0 | 0 | пройдено |
| `GVL_TestsTruthTables.fbVoteTable2oo3VTAITest` | 1 | 1 | 0 | 0 | пройдено |
| `GVL_TestsTruthTables.fbVoteTable2oo3DSDITest` | 1 | 1 | 0 | 0 | пройдено |
| `GVL_TestsTruthTables.fbVoteTable2oo3DSAITest` | 1 | 1 | 0 | 0 | пройдено |
| `GVL_TestsTruthTables.fbVoteTable2oo3DADITest` | 1 | 1 | 0 | 0 | пройдено |
| `GVL_TestsTruthTables.fbVoteTable2oo3DAAITest` | 1 | 1 | 0 | 0 | пройдено |
| `GVL_TestsTruthTables.fbVoteTableFbSmallTest` | 18 | 18 | 0 | 0 | пройдено |
| `GVL_TestsGenerated.fbVoteTruthTest` | 36 | 36 | 0 | 0 | пройдено |
| `GVL_TestsGenerated.fbCemGen01Test` | 40 | 40 | 0 | 0 | пройдено |
| `GVL_TestsGenerated.fbCemGen02Test` | 40 | 40 | 0 | 0 | пройдено |
| `GVL_TestsGenerated.fbCemGen03Test` | 3 | 3 | 0 | 0 | пройдено |
| **Всего** | 255 | 255 | 0 | 0 | **пройдено** |

### Результаты тестов

| Набор | Тест | Итог |
|---|---|---|
| `GVL_TestsSis.fbVoteEvalTest` | `Vote_ArchNone_TripsReportsNone` | пройден |
| `GVL_TestsSis.fbVoteEvalTest` | `Vote_PolicyOutOfEnum_TripsNone` | пройден |
| `GVL_TestsSis.fbVoteEvalTest` | `Vote_NotUsedInsideN_CountsInvalid` | пройден |
| `GVL_TestsSis.fbVoteEvalTest` | `Vote_ArchHelpers_ChannelsAndRequired` | пройден |
| `GVL_TestsSis.fbVoteEvalTest` | `Vote_TwoOfThree_TripsOnSecondDemand` | пройден |
| `GVL_TestsSis.fbVoteEvalTest` | `Vote_ChannelsBeyondN_Ignored` | пройден |
| `GVL_TestsSis.fbVoteEvalTest` | `Vote_Counters_ReportStates` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_DefaultCfg_TripsCfgError` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_AnalogHigh_InclusiveAtLimit` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_AnalogLow_InclusiveAtLimit` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_Hysteresis_ReleasesBeyondBand` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_AnalogNaN_Invalid` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_AnalogInf_Invalid` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_DiHealthyFalse_InvertsDemand` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_ChannelValidity_EventsOnChange` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_Bypass_ExpiresExactlyAtMax` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_Bypass_RemainCountsDown` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_Bypass_LimitLowestChannelWins` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_Bypass_DeniedWithoutPermit` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_Bypass_PermitLostEnds` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_Bypass_ReRequestNeedsRelease` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_Bypass_ZeroTimeDenied` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_Bypass_EventsWithChannel` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_Discrepancy_AfterDelayExactly` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_Discrepancy_AtLimitNoAlarm` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_Discrepancy_IgnoresBypassedAndInvalid` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_Discrepancy_ZeroDisables` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_Discrepancy_NoTripImpact` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_CfgError_RemovesBypasses` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_UnusedChannels_Ignored` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_TimeBackwards_BypassEnds` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_NoTimeSource_UsesSystemTime` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_CfgCheck_DetectsEachRule` | пройден |
| `GVL_TestsSis.fbVotingTest` | `Voting_DegradeAvailable_TwoOfThreeAsTwoOfTwo` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_DefaultCfg_AllTripped` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_CrcMismatch_AllTripped` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_MaskBeyondCount_CfgError` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_CfgErrorRecovered_NeedsReset` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_StartTripped_RequiresReset` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_StartNotTripped_EnergizedFirstCall` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_Delay_TripsExactlyAtDelay` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_ShortPulse_NoTrip` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_ZeroDelay_SameCall` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_Latch_HeldAfterClear` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_Reset_DeniedWhilePresent` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_Reset_DeniedWhilePending` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_Reset_AllowedWhenOverridden` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_ResetHw_EdgeOnly` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_ResetHw_HeldAtStartIgnored` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_FirstOut_RecordsEarliest` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_FirstOut_SimultaneousLowestAndMask` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_FirstOut_TimestampFromSource` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_FirstOut_ClearedByReset` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_Override_ExpiresExactly` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_Override_DeniedNotAllowed` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_Override_DeniedWithoutPermit` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_Override_CancelRestoresTrip` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_Override_RepeatIgnored` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_Override_StartupMaskAllowedOnly` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_Override_DelayRunsDuringOverride` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_DisabledCause_NeverTrips` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_UnusedEffects_Deenergized` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_CmdBits_Cleared` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_Events_OrderInCall` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_EffectTripEvent_CarriesCause` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_CfgCheck_DetectsEachRule` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_TimeBackwards_PendingDelayTrips` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_TimeBackwards_OverrideEnds` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_Override_ReRequestAfterExpiryFullTime` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_Override_CancelAndRequestRestarts` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_NoTimeSource_UsesSystemTime` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_Override_ClearsExactlyAtConfirm` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_Override_ChatteringNotCleared` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_Override_ReRequestRestartsConfirm` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_TimeBackwards_DuringConfirmEndsOverride` | пройден |
| `GVL_TestsSis.fbCauseEffectTest` | `Cem_Override_ExpiryWinsTieWithConfirm` | пройден |
| `GVL_TestsSis.fbSisEventLogTest` | `Log_Ring_OverwritesOldest` | пройден |
| `GVL_TestsSis.fbSisEventLogTest` | `Log_Seq_IncrementsAndWraps` | пройден |
| `GVL_TestsSis.fbSisEventLogTest` | `Log_GetEventBeyondCount_Empty` | пройден |
| `GVL_TestsSis.fbSisEventLogTest` | `Log_Clear_KeepsSeq` | пройден |
| `GVL_TestsSis.fbSisEventLogTest` | `Log_SizeOfEvent_Is24` | пройден |
| `GVL_TestsSis.fbSisEventLogTest` | `Log_ViaInterface_KeepsFields` | пройден |
| `GVL_TestsSis.fbSisUnitTest` | `Unit_ExternalCause_UsesExtDemand` | пройден |
| `GVL_TestsSis.fbSisUnitTest` | `Unit_DisabledCause_VotingNotCalled` | пройден |
| `GVL_TestsSis.fbSisUnitTest` | `Unit_VotingCfgError_TripsOnlyThatCause` | пройден |
| `GVL_TestsSis.fbSisUnitTest` | `Unit_TimeSource_PassedToChildren` | пройден |
| `GVL_TestsSis.fbSisUnitTest` | `Unit_Events_VotingBeforeCem` | пройден |
| `GVL_TestsSis.fbSisUtilTest` | `Sis_Crc16_CheckValue` | пройден |
| `GVL_TestsSis.fbSisUtilTest` | `Sis_CemCrc_DemoMatrixValue` | пройден |
| `GVL_TestsSis.fbSisUtilTest` | `Sis_Bit_OutOfRangeFalse` | пройден |
| `GVL_TestsSis.fbSisUtilTest` | `Sis_BitMask_OutOfRangeZero` | пройден |
| `GVL_TestsSis.fbSisUtilTest` | `Sis_LowMask_Bounds` | пройден |
| `GVL_TestsSis.fbSisUtilTest` | `Sis_FirstBit_LowestIndex` | пройден |
| `GVL_TestsSis.fbSisUtilTest` | `Sis_Ne43Valid_Limits` | пройден |
| `GVL_TestsSis.fbSisUtilTest` | `Sis_AiToEu_Scale` | пройден |
| `GVL_TestsSis.fbSisUtilTest` | `Sis_LogEvent_NoSinkReturnsFalse` | пройден |
| `GVL_TestsSis.fbCommonTest` | `Common_SizeLimits_MasksFitWord` | пройден |
| `GVL_TestsSis.fbCommonTest` | `Common_DefaultCfg_FailsSafe` | пройден |
| `GVL_TestsSis.fbCommonTest` | `Common_EnumCodes_MatchContract` | пройден |
| `GVL_TestsSis.fbCommonTest` | `Common_DefaultSts_FailSafe` | пройден |
| `GVL_TestsTruthTables.fbVoteTableEvalTest` | `VoteTable_Eval1oo1VT_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableEvalTest` | `VoteTable_Eval1oo1DS_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableEvalTest` | `VoteTable_Eval1oo1DA_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableEvalTest` | `VoteTable_Eval1oo2VT_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableEvalTest` | `VoteTable_Eval1oo2DS_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableEvalTest` | `VoteTable_Eval1oo2DA_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableEvalTest` | `VoteTable_Eval2oo2VT_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableEvalTest` | `VoteTable_Eval2oo2DS_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableEvalTest` | `VoteTable_Eval2oo2DA_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableEvalTest` | `VoteTable_Eval2oo3VT_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableEvalTest` | `VoteTable_Eval2oo3DS_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableEvalTest` | `VoteTable_Eval2oo3DA_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTable2oo3VTDITest` | `VoteTable_Fb2oo3VTDI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTable2oo3VTAITest` | `VoteTable_Fb2oo3VTAI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTable2oo3DSDITest` | `VoteTable_Fb2oo3DSDI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTable2oo3DSAITest` | `VoteTable_Fb2oo3DSAI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTable2oo3DADITest` | `VoteTable_Fb2oo3DADI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTable2oo3DAAITest` | `VoteTable_Fb2oo3DAAI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableFbSmallTest` | `VoteTable_Fb1oo1VTDI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableFbSmallTest` | `VoteTable_Fb1oo1VTAI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableFbSmallTest` | `VoteTable_Fb1oo1DSDI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableFbSmallTest` | `VoteTable_Fb1oo1DSAI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableFbSmallTest` | `VoteTable_Fb1oo1DADI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableFbSmallTest` | `VoteTable_Fb1oo1DAAI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableFbSmallTest` | `VoteTable_Fb1oo2VTDI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableFbSmallTest` | `VoteTable_Fb1oo2VTAI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableFbSmallTest` | `VoteTable_Fb1oo2DSDI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableFbSmallTest` | `VoteTable_Fb1oo2DSAI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableFbSmallTest` | `VoteTable_Fb1oo2DADI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableFbSmallTest` | `VoteTable_Fb1oo2DAAI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableFbSmallTest` | `VoteTable_Fb2oo2VTDI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableFbSmallTest` | `VoteTable_Fb2oo2VTAI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableFbSmallTest` | `VoteTable_Fb2oo2DSDI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableFbSmallTest` | `VoteTable_Fb2oo2DSAI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableFbSmallTest` | `VoteTable_Fb2oo2DADI_MatchesModel` | пройден |
| `GVL_TestsTruthTables.fbVoteTableFbSmallTest` | `VoteTable_Fb2oo2DAAI_MatchesModel` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Eval1oo1VT_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Eval1oo1DS_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Eval1oo1DA_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Eval1oo2VT_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Eval1oo2DS_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Eval1oo2DA_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Eval2oo2VT_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Eval2oo2DS_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Eval2oo2DA_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Eval2oo3VT_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Eval2oo3DS_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Eval2oo3DA_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb1oo1VTDI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb1oo1VTAI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb1oo1DSDI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb1oo1DSAI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb1oo1DADI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb1oo1DAAI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb1oo2VTDI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb1oo2VTAI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb1oo2DSDI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb1oo2DSAI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb1oo2DADI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb1oo2DAAI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb2oo2VTDI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb2oo2VTAI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb2oo2DSDI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb2oo2DSAI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb2oo2DADI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb2oo2DAAI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb2oo3VTDI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb2oo3VTAI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb2oo3DSDI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb2oo3DSAI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb2oo3DADI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbVoteTruthTest` | `VoteTruth_Fb2oo3DAAI_MatchesTable` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_PSHH101Demand_TripsOwnEffects` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_PSHH101Delay_TripsExactlyAtDelay` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_PSHH101Override_Denied` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_PSHH101Reset_OnlyAfterClear` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_PSHH101ChannelInvalid_MatchesPolicy` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_PSHH101Bypass_ExpiresBackToVoting` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_PSLL101Demand_TripsOwnEffects` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_PSLL101Delay_TripsExactlyAtDelay` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_PSLL101Override_ExpiresThenTrips` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_PSLL101Override_ClearsAfterConfirm` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_PSLL101Override_DemandBackRestartsConfirm` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_PSLL101Override_ExpiryBoundsConfirm` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_PSLL101Override_ClearedThenDelayTrips` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_PSLL101Reset_OnlyAfterClear` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_PSLL101ChannelInvalid_MatchesPolicy` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_PSLL101Bypass_ExpiresBackToVoting` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_LSHH102Demand_TripsOwnEffects` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_LSHH102Delay_TripsExactlyAtDelay` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_LSHH102Override_Denied` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_LSHH102Reset_OnlyAfterClear` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_LSHH102ChannelInvalid_MatchesPolicy` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_LSHH102Bypass_ExpiresBackToVoting` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_LSLL102Demand_TripsOwnEffects` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_LSLL102Delay_TripsExactlyAtDelay` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_LSLL102Override_ExpiresThenTrips` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_LSLL102Override_ClearsAfterConfirm` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_LSLL102Override_DemandBackRestartsConfirm` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_LSLL102Override_ExpiryBoundsConfirm` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_LSLL102Override_ClearedThenDelayTrips` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_LSLL102Reset_OnlyAfterClear` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_LSLL102ChannelInvalid_MatchesPolicy` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_LSLL102Bypass_ExpiresBackToVoting` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_TSHH103Demand_TripsOwnEffects` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_TSHH103Delay_TripsExactlyAtDelay` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_TSHH103Override_Denied` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_TSHH103Reset_OnlyAfterClear` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_TSHH103ChannelInvalid_MatchesPolicy` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_TSHH103Bypass_ExpiresBackToVoting` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_ASHH104Demand_TripsOwnEffects` | пройден |
| `GVL_TestsGenerated.fbCemGen01Test` | `Matrix_ASHH104Delay_TripsExactlyAtDelay` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_ASHH104Override_Denied` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_ASHH104Reset_OnlyAfterClear` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_ASHH104ChannelInvalid_MatchesPolicy` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_ASHH104Bypass_ExpiresBackToVoting` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_BSH105Demand_TripsOwnEffects` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_BSH105Override_Denied` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_BSH105Reset_OnlyAfterClear` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_BSH105ChannelInvalid_MatchesPolicy` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_BSH105Bypass_ExpiresBackToVoting` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_HS106Demand_TripsOwnEffects` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_HS106Override_Denied` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_HS106Reset_OnlyAfterClear` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_HS106ChannelInvalid_MatchesPolicy` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_HS106Bypass_Denied` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_PSLL108Demand_TripsOwnEffects` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_PSLL108Delay_TripsExactlyAtDelay` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_PSLL108Override_ExpiresThenTrips` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_PSLL108Override_ClearsAfterConfirm` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_PSLL108Override_DemandBackRestartsConfirm` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_PSLL108Override_ExpiryBoundsConfirm` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_PSLL108Override_ClearedThenDelayTrips` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_PSLL108Reset_OnlyAfterClear` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_PSLL108ChannelInvalid_MatchesPolicy` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_PSLL108Bypass_ExpiresBackToVoting` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_ESL109Demand_TripsOwnEffects` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_ESL109Delay_TripsExactlyAtDelay` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_ESL109Override_Denied` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_ESL109Reset_OnlyAfterClear` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_ESL109ChannelInvalid_MatchesPolicy` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_ESL109Bypass_Denied` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_FirstOutPSHH101ThenPSLL101_RecordsFirst` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_FirstOutPSLL101ThenLSHH102_RecordsFirst` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_FirstOutLSHH102ThenLSLL102_RecordsFirst` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_FirstOutLSLL102ThenTSHH103_RecordsFirst` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_FirstOutTSHH103ThenASHH104_RecordsFirst` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_FirstOutASHH104ThenBSH105_RecordsFirst` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_FirstOutBSH105ThenHS106_RecordsFirst` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_FirstOutHS106ThenPSLL108_RecordsFirst` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_FirstOutPSLL108ThenESL109_RecordsFirst` | пройден |
| `GVL_TestsGenerated.fbCemGen02Test` | `Matrix_FirstOutESL109ThenPSHH101_RecordsFirst` | пройден |
| `GVL_TestsGenerated.fbCemGen03Test` | `Matrix_Start_TrippedUntilReset` | пройден |
| `GVL_TestsGenerated.fbCemGen03Test` | `Matrix_FirstOutSimultaneous_LowestIndex` | пройден |
| `GVL_TestsGenerated.fbCemGen03Test` | `Matrix_GeneratedCfg_PassesChecks` | пройден |

### Упавшие тесты

_Нет._

Машиночитаемые результаты: `build/test-results.json`, `build/junit.xml` (не в git).
<!-- cds:test-report:end -->

## Сборка и полная проверка компиляции в CODESYS

CODESYS 3.5.17.30, профиль `CODESYS V3.5 SP17 Patch 3`, локально, 19.10.2026, после интеграции кода
логики ПАЗ и сгенерированного по матрице и после исправлений ревизии функциональной безопасности
([ASSUMPTIONS.md](ASSUMPTIONS.md), R-01…R-13; прогон 16.10.2026 после исправлений R-01, R-02 дал те же итоги) и
после автоснятия пускового обхода (R-12, DESIGN.md 1.2.0). `build` компилирует объекты, достижимые из задач; `check` —
все объекты раскладки ([MANUAL_STEPS.md](MANUAL_STEPS.md), раздел 5). Библиотеки проекта:
`#Standard` (Standard 3.5.17.0), plc-process-lib 1.0.0.0 (`plc-process-lib, 1.0.0.0 (plc-portfolio)`, версия
закреплена, собрана `cds.py` из соседнего репозитория, коммит `1e0356d`), в тестовом проекте — coUnit 1.2.0.0;
плейсхолдеры устройства `#IoStandard`, `#3SLicense`, `#CAA Device Diagnosis`, `#BreakpointLogging`.

| Команда | Итог | Примечание |
|---|---|---|
| `cds.py build` | 0 ошибок, 0 предупреждений | рабочий проект: MainTask 20 мс → `PRG_Main` → `PRG_Sis` |
| `cds.py build --tests` | 0 ошибок, 0 предупреждений | тестовый проект: TestTask 10 мс → `PRG_Tests`; код 1,39 МБ, глобальные данные 154 МБ (замер 16.10.2026; с R-12 добавились 12 экземпляров стенда `FB_SisHarness` — по экземпляру на сценарий, размер не перемерялся) |
| `cds.py check` | 0 ошибок, 0 предупреждений | 50 объектов `src/` (включая `PRG_Main`) |
| `cds.py check --tests` | 0 ошибок, 0 предупреждений | 81 объект `src/` и `tests/` |
| `cds.py test` | 255 из 255 | раздел выше; все наборы завершились к первому опросу. До исправлений ревизии новые тесты R-01, R-02 упали — 5 из 238 (тесты сначала, 16.10.2026) |
| `cds.py roundtrip` | без диффа (747 файлов), повторный импорт — 0 изменений | импорт в чистый проект → экспорт → побайтное сравнение |
| `cemgen fat-report` | 55 шагов из 55 «соответствует» | [FAT_REPORT.md](FAT_REPORT.md) по `build/test-results.json` этого прогона |
| мутации (копия репозитория) | поймано 16 из 16 | 16 ошибок в `FB_Voting` и `FB_CauseEffect` по одной, `cds.py test` копии, 19.10.2026: эталон без мутации — 238 из 238, у мутаций упало от 1 до 47 тестов ([ASSUMPTIONS.md](ASSUMPTIONS.md), R-08) |
| мутации автоснятия обхода (копия репозитория) | поймано 6 из 6 | 6 ошибок автоснятия пускового обхода (O1–O6) в `FB_CauseEffect` и `F_CemCheckCfg` по одной, `cds.py test` копии, 19.10.2026: эталон без мутации — 255 из 255, у мутаций упало от 1 до 21 теста ([ASSUMPTIONS.md](ASSUMPTIONS.md), R-12) |
| `cds.py deps --check` | есть | plc-process-lib 1.0.0.0, собрана из `../plc-process-lib` @ `1e0356d` (19.10.2026: 81 объект, 255 из 255 на выпуске 1.0.0) |

## Что проверяют тесты

| Набор | Тестов | Что проверяет |
|---|---:|---|
| `FB_VoteEval_Test` | 7 | `F_VoteEval`: схема вне перечисления и `None` — срабатывание; политика вне перечисления; `NotUsed` внутри N — недостоверен; 2oo3 срабатывает на втором требовании; каналы за пределами N не действуют; счётчики состояний; функции схем (N, M) |
| `FB_Voting_Test` | 27 | уставки включительно (High, Low), гистерезис, NaN и ±Inf — недостоверно, инверсия DI, события достоверности; байпас: истечение ровно в срок, остаток, предел числа (младший канал выигрывает), без ключа, снятие ключа, повторный запрос, нулевой срок, события; рассогласование: ровно после задержки, «на пределе» — нет, исключает байпасированные и недостоверные, отключение, не влияет на срабатывание; ошибка конфигурации снимает байпасы; неиспользуемые каналы; «время назад» заканчивает байпас (D-19); системное время по умолчанию; проверка конфигурации — каждое правило; DegradeAvailable: 2oo3 как 2oo2 |
| `FB_CauseEffect_Test` | 42 | конфигурация по умолчанию и неверная CRC — срабатывание всего; маска за пределами числа причин; восстановление конфигурации требует сброса; старт в сработавшем и без; задержка ровно, короткий импульс, нулевая задержка; фиксация; сброс: запрещён при требовании и во время отсчёта, разрешён при обходе, кнопка по фронту, зажатая при старте кнопка; первопричина: самая ранняя, одновременные (младшая и маска), метка времени от источника, очистка сбросом; обходы: истечение ровно, запрет, без ключа, отмена, повтор, новый обход сразу после истечения и после снятия в том же вызове — полный срок, пусковой по маске, задержка идёт во время обхода; выключенная причина, неиспользуемые следствия, очистка команд, порядок событий в вызове, событие срабатывания следствия с причиной; проверка конфигурации — каждое правило; «время назад»: идущая задержка срабатывает, обход снимается (D-19); системное время по умолчанию; автоснятие обхода при норме (D-20): ровно по подтверждению и полная задержка нового требования, дребезг требования не снимает обход — его снимает срок, новый обход перезапускает подтверждение (повторный запрос — нет), срок и подтверждение в одном вызове — `OverrideExpired`, «время назад» во время подтверждения — `OverrideExpired` без позднего `OverrideCleared` |
| `FB_SisEventLog_Test` | 6 | кольцо затирает самое старое, номер растёт и переходит через `16#FFFFFFFF`, чтение за пределами — пустая запись, очистка сохраняет номер, `SIZEOF(ST_SisEvent) = 24`, запись через интерфейс сохраняет поля |
| `FB_SisUnit_Test` | 5 | внешняя причина без голосования, выключенная причина не вызывает группу, ошибка конфигурации группы — срабатывает только её причина, один источник времени для всех ФБ, порядок событий (голосование раньше матрицы) |
| `FB_SisUtil_Test` | 9 | CRC-16/CCITT-FALSE: контрольное значение `16#29B1` и CRC демо-матрицы `16#CD40`; функции битов и масок за пределами; NE 43: 3,6 и 21,0 мА — недостоверно, 3,61 и 20,99 мА — достоверно, NaN; масштабирование мА → инж. ед.; младший установленный бит; запись события без приёмника |
| `FB_Common_Test` | 4 | маски помещаются в `WORD`; конфигурации и состояния по умолчанию — безопасные; коды перечислений совпадают с контрактом |
| `FB_VoteTruth_Test` (генерируется `cemgen`) | 36 | 12 таблиц `F_VoteEval` (300 строк) и 24 таблицы `FB_Voting` (3888 строк) по эталонной модели `cemgen` |
| `FB_VoteTable*_Test` (8 наборов, `tools_project`) | 36 | те же 4188 строк по независимой модели `tools_project/vote_model.py`, по ассерту на строку |
| `FB_CemGen01_Test` … `FB_CemGen03_Test` (генерируются `cemgen`) | 83 | на каждую причину V-101: требование отключает ровно свои следствия (10), задержка «до и ровно» (8), пусковой обход истекает (3) или отклонён (7), снимается ровно по подтверждению нормы (3), подтверждение перезапускается требованием (3), срок ограничивает подтверждение (3), после автоснятия новое требование — через полную задержку (3), сброс только после снятия (10), отказ канала по политике (10), байпас истекает (8) или запрещён (2); первопричина для 10 пар причин, одновременная фиксация, старт ПЛК, проверка сгенерированной конфигурации |

## Проверки без CODESYS

Локально, 19.10.2026, Windows, Python 3.12.10 (CI GitHub Actions — те же команды на Linux).

| Проверка | Итог | Примечание |
|---|---|---|
| `ruff check`, `ruff format --check`, `mypy` | пройдено | 77 файлов Python; mypy (strict) — 58 модулей без замечаний |
| `pytest` | 858 пройдено | `tools/tests` 528, `tools/project_checks` 107, `tools_project` 13, `pytests` (cemgen) 210; интеграционные — с настоящими iec_checker 0.4 и RuSTy 1.0.6 |
| `cemgen validate --strict` (CSV и XLSX) | 0 ошибок, 0 предупреждений | `SIS-V101-CEM`, ревизия B, 10 причин, 7 следствий, CRC `16#CD40` |
| `cemgen generate --check` | совпадает (277 файлов) | ST, тесты, документы по матрице и раздел 3 `SRS.md` |
| `gen_voting_tests.py --check` | совпадает | 8 наборов, 36 тестов, 4188 ассертов |
| `tools/assemble.py --tests` | пройдено | 81 объект |
| `tools/check/st_lint.py --strict` | пройдено | 747 файлов, 0 замечаний |
| iec_checker 0.4 (`run_iec_checker.py --tests`) | пройдено | 81 объект, ошибок разбора нет; необоснованных находок 0 (обоснованных 2195) — разбор в [STATIC_ANALYSIS.md](STATIC_ANALYSIS.md) |
| RuSTy 1.0.6 (`run_rusty.py`) | пройдено | 47 файлов, 35 исключены (`tools/check/rusty_exclude.txt`: зависят от `PL.*`), 0 ошибок |
