// Назначение: экземпляры наборов тестов логики ПАЗ, написанных вручную (граничные случаи, раздел
//             12.3). Объявление экземпляра регистрирует набор в coUnit; PRG_Tests их не перечисляет.
//             {attribute 'linkalways'} обязателен: на GVL никто не ссылается, и без атрибута CODESYS
//             3.5.17 не включает её в приложение — наборы молча не выполняются.
// Автор:      <ИМЯ ФАМИЛИЯ>
// Версия:     0.1.0
// Документ:   docs/DESIGN.md, раздел «12.3 Граничные случаи (вручную, команда A)»
// ВНИМАНИЕ:   код демонстрационный и не предназначен для систем безопасности. Реальная ПАЗ
//             требует определения SIL, сертифицированных аппаратных и программных средств
//             и валидации по ГОСТ Р МЭК 61511.
{attribute 'qualified_only'}
{attribute 'linkalways'}
VAR_GLOBAL
    fbVoteEvalTest    : FB_VoteEval_Test;      // F_VoteEval, F_VoteArchChannels, F_VoteArchRequired
    fbVotingTest      : FB_Voting_Test;        // FB_Voting, F_VoteCheckCfg
    fbCauseEffectTest : FB_CauseEffect_Test;   // FB_CauseEffect, F_CemCheckCfg
    fbSisEventLogTest : FB_SisEventLog_Test;   // FB_SisEventLog, I_SisEventSink
    fbSisUnitTest     : FB_SisUnit_Test;       // FB_SisUnit
    fbSisUtilTest     : FB_SisUtil_Test;       // CRC, биты, NE 43, масштабирование, F_SisLogEvent
    fbCommonTest      : FB_Common_Test;        // пределы, умолчания, коды перечислений, размеры
END_VAR
