coUnit.TEST('Sis_AiToEu_Scale');
AssertEquals_REAL(Expected := 0.0, Actual := F_SisAiToEu(rIn_mA := 4.0, rLo_eu := 0.0, rHi_eu := 1.6),
    Delta := 1.0E-6, Message := '4 mA: 0.0');
AssertEquals_REAL(Expected := 1.6, Actual := F_SisAiToEu(rIn_mA := 20.0, rLo_eu := 0.0, rHi_eu := 1.6),
    Delta := 1.0E-6, Message := '20 mA: 1.6');
AssertEquals_REAL(Expected := 75.0, Actual := F_SisAiToEu(rIn_mA := 12.0, rLo_eu := 0.0, rHi_eu := 150.0),
    Delta := 1.0E-4, Message := '12 mA: middle of 0..150');
AssertEquals_REAL(Expected := -15.0, Actual := F_SisAiToEu(rIn_mA := 2.4, rLo_eu := 0.0, rHi_eu := 150.0),
    Delta := 1.0E-4, Message := '2.4 mA: below scale, not clamped');
AssertEquals_REAL(Expected := 2.0, Actual := F_SisAiToEu(rIn_mA := 12.0, rLo_eu := 4.0, rHi_eu := 0.0),
    Delta := 1.0E-5, Message := 'reversed scale');
coUnit.TEST_FINISHED();
