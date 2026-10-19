"""Сценарные тесты coUnit по матрице (DESIGN.md, 12.4).

Каждый тест строится :class:`Scenario`: одно и то же действие выполняется на стенде эталонной
модели (:class:`cemgen.refmodel.Harness`) и записывается строкой ST для ``FB_SisHarness``.
Ожидаемые значения ассертов берутся из состояния модели в этой точке сценария, а не
выписываются вручную, — поэтому ST и модель проходят ровно один и тот же путь.

Генератор проверяет и предпосылки сценария (причина действительно срабатывает, обход
действует до конца срока и т. п.): если модель им противоречит, это ошибка матрицы или
генератора, и файлы не пишутся.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from cemgen import limits
from cemgen.model import Cause, Matrix, Signal, format_dec
from cemgen.refmodel import (
    CauseEffectSts,
    Harness,
    IoValue,
    VotingSts,
    channel_demand,
    channel_invalid,
    demand_values,
    normal_values,
)
from cemgen.sisdefs import BypassState, ChannelState, EventKind, VoteArch, st_enum, st_member
from cemgen.stfmt import (
    GenerationError,
    HeaderInfo,
    join_lines,
    st_bool,
    st_header,
    st_ltime,
    st_real,
    st_time,
    st_word,
)
from cemgen.values import format_duration_ru, format_float_ru

TESTS_GVL = "tests/GVLs/Generated"
TESTS_POU = "tests/POUs/Generated"
NS_PER_MS = 1_000_000

Files = dict[str, str]


@dataclass
class TestCase:
    """Сгенерированный тест: имя coUnit, метод, описание, локальные переменные и тело."""

    name: str
    method: str
    description: str
    kind: str  # вид теста для протокола FAT: demand, delay, override, reset, invalid, bypass, first_out, start, cfg
    cause: Cause | None = None
    locals: dict[str, tuple[str, str]] = field(default_factory=dict)
    body: list[str] = field(default_factory=list)
    harness: str = "fbH001"
    iterations: int = 0


def run_step(total_ms: int, delta_ms: int) -> int:
    """Шаг перехода к моменту ``T − Δ``: не крупнее T/50, не мельче Δ, кратен Δ, ≤ 100 итераций."""
    step = max(delta_ms, (total_ms // limits.RUN_STEP_DIVISOR) // delta_ms * delta_ms)
    while -(-total_ms // step) > limits.RUN_MAX_ITERATIONS:
        step += delta_ms
    return step


class Scenario:
    """Пишет тело теста и одновременно ведёт стенд эталонной модели."""

    def __init__(self, matrix: Matrix, case: TestCase) -> None:
        self.m = matrix
        self.case = case
        self.h = Harness(matrix)
        self.v = case.harness
        self.delta = matrix.header.test_step_ms
        self.t0: int | None = None
        self.emit(f"coUnit.TEST('{case.name}');")

    # --- служебное ---------------------------------------------------------------------------
    def emit(self, line: str) -> None:
        self.case.body.append(line)

    def local(self, name: str, st_type: str, comment: str) -> None:
        self.case.locals.setdefault(name, (st_type, comment))

    def fail(self, message: str) -> GenerationError:
        return GenerationError(f"{self.case.name}: {message}")

    def _at(self) -> str:
        if self.t0 is None:
            return ""
        delta = (self.h.now() - self.t0) // NS_PER_MS
        return "// t0" if delta == 0 else f"// t0 + {format_duration_ru(delta)}"

    def finish(self) -> TestCase:
        self.emit("coUnit.TEST_FINISHED();")
        self.case.iterations = self.h.iterations
        if self.h.iterations > limits.HARNESS_MAX_ITERATIONS:
            raise self.fail(f"итераций стенда {self.h.iterations} > {limits.HARNESS_MAX_ITERATIONS}")
        return self.case

    @staticmethod
    def literal(value: IoValue) -> str:
        return st_bool(value) if isinstance(value, bool) else st_real(value)

    # --- действия ----------------------------------------------------------------------------------
    def arm(self) -> None:
        if not self.h.arm():
            raise self.fail("стенд модели не взводится: следствия не под напряжением после сброса")
        self.local("xArmed", "BOOL", "стенд взведён: все следствия под напряжением после сброса")
        self.emit(f"xArmed := {self.v}.Arm();")
        self.emit("AssertTrue(Condition := xArmed, Message := 'armed: all effects energized after reset');")

    def set_io(self, pairs: list[tuple[str, IoValue]], note: Callable[[str], str] | None = None) -> None:
        for name, value in pairs:
            self.h.io[name] = value
            comment = note(name) if note is not None else ""
            line = f"{self.v}.stIo.{name} := {self.literal(value)};"
            self.emit(f"{line}   // {comment}" if comment else line)

    def _ai_note(self, cause: Cause) -> Callable[[str], str]:
        def note(name: str) -> str:
            if cause.analog is None or not name.startswith("r"):
                return ""
            ma = float(self.h.io[name])
            if ma < limits.NE43_FAIL_LOW_MA:
                return "обрыв: недостоверно по NE 43"
            eu = float(cause.analog.range_lo) + (ma - limits.MA_ZERO) / limits.MA_SPAN * float(cause.analog.span)
            return f"{format_float_ru(ma)} мА = {format_float_ru(eu, 3)} {cause.analog.units}"

        return note

    def demand(self, cause: Cause) -> None:
        self.set_io(demand_values(cause), self._ai_note(cause))

    def normal(self, cause: Cause) -> None:
        self.set_io(normal_values(cause), self._ai_note(cause))

    def channel_demand(self, cause: Cause, channel: int) -> None:
        self.set_io([channel_demand(cause, channel)], self._ai_note(cause))

    def channel_invalid(self, cause: Cause, channel: int) -> None:
        self.set_io([channel_invalid(cause, channel)], self._ai_note(cause))

    def cycle(self, mark_t0: bool = False) -> None:
        self.h.cycle()
        if mark_t0:
            self.t0 = self.h.now()
        self.emit(f"{self.v}.Cycle();   {self._at()}".rstrip())

    def capture_t0(self) -> None:
        self.local("ltT0", "LTIME", "момент t0 по подменному времени стенда")
        self.t0 = self.h.now()
        self.emit(f"ltT0 := {self.v}.Now();")

    def run(self, duration_ms: int, step_ms: int | None = None) -> None:
        if duration_ms == 0:
            return
        step = step_ms if step_ms is not None else run_step(duration_ms, self.delta)
        count = self.h.run(duration_ms, step)
        if count > limits.RUN_MAX_ITERATIONS:
            raise self.fail(f"Run: {count} итераций > {limits.RUN_MAX_ITERATIONS}")
        self.emit(f"{self.v}.Run(tDuration := {st_time(duration_ms)}, tStep := {st_time(step)});   {self._at()}")

    def run_until_before(self, total_ms: int) -> None:
        """Переход к моменту ``T − Δ`` шагами не крупнее T/50."""
        self.run(total_ms - self.delta, run_step(total_ms, self.delta))

    def step(self) -> None:
        self.h.step(self.delta)
        self.emit(f"{self.v}.Step(tStep := {st_time(self.delta)});   {self._at()}")

    def keys(self, bypass: bool, override: bool) -> None:
        self.h.keys(bypass, override)
        self.emit(f"{self.v}.Keys(xBypass := {st_bool(bypass)}, xOverride := {st_bool(override)});")

    def press_reset(self) -> None:
        self.h.press_reset()
        self.emit(f"{self.v}.PressReset();   {self._at()}".rstrip())

    def set_normal(self) -> None:
        self.h.set_normal()
        self.emit(f"{self.v}.SetNormal();")

    def override_request(self, cause: Cause) -> None:
        self.h.cmd.cem.override_req = cause.bit
        self.emit(f"{self.v}.stCmd.stCem.wOverrideReq := {st_word(cause.bit)};   // пусковой обход {cause.tag}")

    def bypass_request(self, cause: Cause, channel: int) -> None:
        self.h.cmd.vote[cause.no - 1].bypass_req[channel - 1] = True
        self.emit(
            f"{self.v}.stCmd.astVote[GVL_SisCfg.{cause.const_name}].axBypassReq[{channel}] := TRUE;"
            f"   // байпас {cause.sources[channel - 1]}"
        )

    def mark_events(self) -> None:
        self.h.mark_events()
        self.emit(f"{self.v}.MarkEvents();")

    # --- чтение модели -------------------------------------------------------------------------------
    @property
    def sts(self) -> CauseEffectSts:
        return self.h.app.cem_sts

    def vote_sts(self, cause: Cause) -> VotingSts:
        return self.h.app.vote_sts[cause.no - 1]

    def load_vote_sts(self, cause: Cause) -> None:
        self.local("stVs", "ST_VotingSts", "копия состояния группы голосования")
        self.emit(f"stVs := {self.v}.fbApp.astVoteSts[GVL_SisCfg.{cause.const_name}];")

    def load_last_event(self) -> None:
        self.local("stEv", "ST_SisEvent", "последнее событие журнала")
        self.emit(f"stEv := {self.v}.fbLog.GetEvent(uiBack := 0);")

    # --- ассерты -----------------------------------------------------------------------------------
    def assert_bool(self, actual: str, value: bool, message: str) -> None:
        fn = "AssertTrue" if value else "AssertFalse"
        self.emit(f"{fn}(Condition := {actual}, Message := '{message}');")

    def assert_effects(
        self, tag: str, only: list[int] | None = None, phase: str = "", *, restored: bool = False
    ) -> None:
        """Выходы следствий по модели: обесточен — «must be tripped», под напряжением — «energized»."""
        for effect in self.m.effects:
            if only is not None and effect.no not in only:
                continue
            value = bool(self.h.io[effect.io_field])
            energized = "must be energized" if restored else "must stay energized"
            state = energized if value else "must be tripped"
            text = f"{tag}: {effect.tag} {state}{phase}"
            self.assert_bool(f"{self.v}.stIo.{effect.io_field}", value, text)

    def assert_word(self, actual: str, value: int, message: str) -> None:
        self.emit(f"AssertEquals_WORD(Expected := {st_word(value)}, Actual := {actual},")
        self.emit(f"    Message := '{message}');")

    def cause_code(self, value: int) -> str:
        if value == limits.SIS_FIRST_OUT_NONE:
            return "GVL_Const.SIS_FIRST_OUT_NONE"
        if value == limits.SIS_FIRST_OUT_START:
            return "GVL_Const.SIS_FIRST_OUT_START"
        if value == limits.SIS_FIRST_OUT_CFG:
            return "GVL_Const.SIS_FIRST_OUT_CFG"
        return f"GVL_SisCfg.{self.m.cause(value).const_name}"

    def assert_cause(self, actual: str, value: int, message: str) -> None:
        self.emit(f"AssertEquals_UINT(Expected := {self.cause_code(value)}, Actual := {actual},")
        self.emit(f"    Message := '{message}');")

    def assert_uint(self, actual: str, value: int, message: str) -> None:
        self.emit(f"AssertEquals_UINT(Expected := {value}, Actual := {actual}, Message := '{message}');")

    def assert_enum(self, actual: str, value: VoteArch | ChannelState | BypassState | EventKind, message: str) -> None:
        self.emit(f"AssertEquals_INT(Expected := TO_INT({st_enum(value)}), Actual := TO_INT({actual}),")
        self.emit(f"    Message := '{message}');")

    def assert_time(self, actual: str, value_ms: int, message: str) -> None:
        self.emit(f"AssertEquals_TIME(Expected := {st_time(value_ms)}, Actual := {actual},")
        self.emit(f"    Message := '{message}');")

    def assert_since_t0(self, actual: str, value_ns: int, message: str) -> None:
        if self.t0 is None:
            raise self.fail("нет отметки t0")
        diff = (value_ns - self.t0) // NS_PER_MS
        expected = "ltT0" if diff == 0 else f"ltT0 + {st_ltime(diff)}"
        self.emit(f"AssertEquals_LTIME(Expected := {expected}, Actual := {actual},")
        self.emit(f"    Message := '{message}');")

    def assert_event_since_mark(self, kind: EventKind, cause: Cause, message: str) -> None:
        found = self.h.has_event(kind, cause.no)
        if not found:
            raise self.fail(f"модель: нет события {kind.name} причины {cause.tag}")
        self.emit(f"AssertTrue(Condition := {self.v}.HasEvent(eKind := {st_enum(kind)},")
        self.emit(f"    uiCause := GVL_SisCfg.{cause.const_name}), Message := '{message}');")

    # --- общие проверки ------------------------------------------------------------------------------
    def assert_latched(self, tag: str, phase: str) -> None:
        self.assert_word(f"{self.v}.fbApp.stCemSts.wCauseLatched", self.sts.latched, f"{tag}: latched causes{phase}")

    def assert_first_out(self, tag: str, phase: str = "") -> None:
        self.assert_cause(f"{self.v}.fbApp.stCemSts.uiFirstOut", self.sts.first_out, f"{tag}: first-out{phase}")


# --- тесты на причину ------------------------------------------------------------------------------------
def _new(matrix: Matrix, name: str, description: str, kind: str, cause: Cause | None) -> Scenario:
    method = "".join(name.split("_")[1:])
    return Scenario(matrix, TestCase(name, method, description, kind, cause))


def _effects_text(matrix: Matrix, cause: Cause) -> str:
    return ", ".join(matrix.effect(j).tag for j in sorted(cause.effects))


def _stimulus_text(cause: Cause) -> str:
    if cause.signal is Signal.AI and cause.analog is not None:
        a = cause.analog
        sign = "≥" if a.high else "≤"
        return (
            f"{', '.join(cause.sources)} = {format_float_ru(a.demand_ma)} мА ({format_dec(a.demand_value)} {a.units}; "
            f"уставка {sign} {format_dec(a.setpoint)} {a.units})"
        )
    level = "1" if cause.trip_on == 1 else "0"
    return f"{', '.join(cause.sources)} = {level}"


def test_demand(m: Matrix, c: Cause) -> TestCase:
    s = _new(
        m,
        f"Matrix_{c.tag}Demand_TripsOwnEffects",
        f"Причина {c.no} {c.tag} ({c.vote_text}, задержка {format_duration_ru(c.delay_ms)}): требование "
        f"{_stimulus_text(c)} отключает {_effects_text(m, c)}; остальные следствия под напряжением; "
        f"первопричина {c.tag}.",
        "demand",
        c,
    )
    s.arm()
    s.demand(c)
    s.cycle(mark_t0=True)
    s.run(c.delay_ms)
    if not s.sts.latched & c.bit:
        raise s.fail("модель: причина не зафиксирована после задержки")
    s.assert_effects(c.tag)
    s.assert_first_out(c.tag)
    s.assert_latched(c.tag, " after delay")
    return s.finish()


def test_delay(m: Matrix, c: Cause) -> TestCase:
    s = _new(
        m,
        f"Matrix_{c.tag}Delay_TripsExactlyAtDelay",
        f"Причина {c.no} {c.tag}: требование в t0; на t0 + {format_duration_ru(c.delay_ms)} − шаг не "
        f"зафиксирована, следствия под напряжением; ровно на t0 + {format_duration_ru(c.delay_ms)} — "
        "зафиксирована, ltFirstOut = t0 + задержка.",
        "delay",
        c,
    )
    s.arm()
    s.demand(c)
    s.cycle(mark_t0=True)
    s.capture_t0()
    s.run_until_before(c.delay_ms)
    if s.sts.latched & c.bit:
        raise s.fail("модель: причина зафиксирована раньше задержки")
    s.assert_latched(c.tag, " before delay")
    s.assert_time(
        f"{s.v}.fbApp.stCemSts.atDelayRemain[GVL_SisCfg.{c.const_name}]",
        s.sts.delay_remain_ms[c.no - 1],
        f"{c.tag}: one step of delay left",
    )
    s.assert_effects(c.tag, sorted(c.effects), " before delay")
    s.step()
    if not s.sts.latched & c.bit:
        raise s.fail("модель: причина не зафиксирована ровно на задержке")
    s.assert_latched(c.tag, " exactly at delay")
    s.assert_since_t0(f"{s.v}.fbApp.stCemSts.ltFirstOut", s.sts.lt_first_out, f"{c.tag}: first-out at t0 + delay")
    s.assert_effects(c.tag, sorted(c.effects), " at delay")
    return s.finish()


def test_override_expires(m: Matrix, c: Cause) -> TestCase:
    s = _new(
        m,
        f"Matrix_{c.tag}Override_ExpiresThenTrips",
        f"Причина {c.no} {c.tag}: ключ разрешения обходов, запрос пускового обхода и требование в одном "
        f"вызове t0; до t0 + {format_duration_ru(c.override_time_ms)} − шаг обход действует, причина не "
        f"зафиксирована; ровно на t0 + {format_duration_ru(c.override_time_ms)} — OverrideExpired, фиксация, "
        f"первопричина {c.tag}.",
        "override",
        c,
    )
    s.arm()
    s.keys(False, True)
    s.override_request(c)
    s.demand(c)
    s.cycle(mark_t0=True)
    s.assert_word(f"{s.v}.fbApp.stCemSts.wOverridden", s.sts.overridden, f"{c.tag}: override accepted")
    s.run_until_before(c.override_time_ms)
    if not s.sts.overridden & c.bit or s.sts.latched & c.bit:
        raise s.fail("модель: обход не действует до конца срока")
    s.assert_word(f"{s.v}.fbApp.stCemSts.wOverridden", s.sts.overridden, f"{c.tag}: override still active")
    s.assert_time(
        f"{s.v}.fbApp.stCemSts.atOverrideRemain[GVL_SisCfg.{c.const_name}]",
        s.sts.override_remain_ms[c.no - 1],
        f"{c.tag}: one step of override left",
    )
    s.assert_latched(c.tag, " while overridden")
    s.assert_effects(c.tag, sorted(c.effects), " while overridden")
    s.mark_events()
    s.step()
    s.assert_event_since_mark(EventKind.OVERRIDE_EXPIRED, c, f"{c.tag}: OverrideExpired logged")
    if not s.sts.latched & c.bit:
        raise s.fail("модель: причина не зафиксирована после окончания обхода")
    s.assert_latched(c.tag, " after override expired")
    s.assert_first_out(c.tag)
    s.assert_effects(c.tag, sorted(c.effects), " after override expired")
    return s.finish()


def test_override_denied(m: Matrix, c: Cause) -> TestCase:
    s = _new(
        m,
        f"Matrix_{c.tag}Override_Denied",
        f"Причина {c.no} {c.tag} без разрешённого обхода: ключ разрешения обходов, запрос → последнее "
        "событие OverrideDenied, обхода нет; требование → срабатывание после задержки.",
        "override",
        c,
    )
    s.arm()
    s.keys(False, True)
    s.override_request(c)
    s.cycle()
    s.load_last_event()
    last = s.h.log.get(0)
    if last.kind != EventKind.OVERRIDE_DENIED or last.cause != c.no:
        raise s.fail("модель: последнее событие не OverrideDenied")
    s.assert_enum("stEv.eKind", EventKind.OVERRIDE_DENIED, f"{c.tag}: last event OverrideDenied")
    s.assert_cause("stEv.uiCause", c.no, f"{c.tag}: OverrideDenied carries cause")
    s.assert_word(f"{s.v}.fbApp.stCemSts.wOverridden", s.sts.overridden, f"{c.tag}: no override")
    s.demand(c)
    s.cycle(mark_t0=True)
    s.run(c.delay_ms)
    if not s.sts.latched & c.bit:
        raise s.fail("модель: причина не зафиксирована")
    s.assert_latched(c.tag, " after delay")
    s.assert_first_out(c.tag)
    return s.finish()


def test_reset(m: Matrix, c: Cause) -> TestCase:
    s = _new(
        m,
        f"Matrix_{c.tag}Reset_OnlyAfterClear",
        f"Причина {c.no} {c.tag}: срабатывание; сброс при требовании → ResetDenied, блокирует {c.tag}, "
        "следствия обесточены; норма → следствия всё ещё обесточены (фиксация); сброс → все следствия под "
        "напряжением.",
        "reset",
        c,
    )
    s.arm()
    s.demand(c)
    s.cycle(mark_t0=True)
    s.run(c.delay_ms)
    s.press_reset()
    last = s.h.log.get(0)
    if last.kind != EventKind.RESET_DENIED:
        raise s.fail("модель: сброс при требовании не отклонён")
    s.load_last_event()
    s.assert_enum("stEv.eKind", EventKind.RESET_DENIED, f"{c.tag}: reset denied while demand present")
    s.assert_cause(f"{s.v}.fbApp.stCemSts.uiResetBlocker", s.sts.reset_blocker, f"{c.tag}: reset blocker")
    s.assert_effects(c.tag, sorted(c.effects), " after denied reset")
    s.normal(c)
    s.cycle()
    s.assert_bool(f"{s.v}.fbApp.stCemSts.xResetPermitted", s.sts.reset_permitted, f"{c.tag}: reset permitted")
    s.assert_effects(c.tag, sorted(c.effects), " until reset")
    s.press_reset()
    if s.sts.effect_tripped != 0:
        raise s.fail("модель: после сброса не все следствия под напряжением")
    s.assert_effects(c.tag, None, " after reset", restored=True)
    s.assert_first_out(c.tag, " cleared by reset")
    return s.finish()


def test_channel_invalid(m: Matrix, c: Cause) -> TestCase:
    s = _new(
        m,
        f"Matrix_{c.tag}ChannelInvalid_MatchesPolicy",
        f"Причина {c.no} {c.tag} ({c.vote_text}, {st_member(c.policy) if c.policy else ''}): канал "
        f"{c.sources[0]} недостоверен → действующая схема и срабатывание по политике деградации; если не "
        f"сработало — требование на {c.sources[1] if len(c.sources) > 1 else 'втором канале'} → по эталонной "
        "модели.",
        "invalid",
        c,
    )
    s.arm()
    s.channel_invalid(c, 1)
    s.cycle(mark_t0=True)
    s.run(c.delay_ms)
    vs = s.vote_sts(c)
    s.load_vote_sts(c)
    s.assert_enum("stVs.aeChState[1]", vs.ch_state[0], f"{c.tag}: channel 1 state")
    s.assert_enum("stVs.eArchEff", vs.arch_eff, f"{c.tag}: effective scheme with channel 1 invalid")
    s.assert_latched(c.tag, " with channel 1 invalid")
    if not s.sts.latched & c.bit and c.channels >= 2:
        s.channel_demand(c, 2)
        s.cycle(mark_t0=True)
        s.run(c.delay_ms)
        s.assert_latched(c.tag, " with channel 2 demand")
        s.assert_effects(c.tag, sorted(c.effects), " with channel 2 demand")
    else:
        s.assert_effects(c.tag, sorted(c.effects), " with channel 1 invalid")
    return s.finish()


def test_bypass_expires(m: Matrix, c: Cause) -> TestCase:
    s = _new(
        m,
        f"Matrix_{c.tag}Bypass_ExpiresBackToVoting",
        f"Причина {c.no} {c.tag}: ключ разрешения байпасов, байпас {c.sources[0]} → Active; канал недостоверен "
        f"→ Bypassed, не сработало; на t0 + {format_duration_ru(c.bypass_time_ms)} − шаг — Active; ровно на "
        f"t0 + {format_duration_ru(c.bypass_time_ms)} — Expired, BypassExpired, канал Invalid; далее — по "
        "эталонной модели.",
        "bypass",
        c,
    )
    s.arm()
    s.keys(True, False)
    s.bypass_request(c, 1)
    s.cycle(mark_t0=True)
    s.load_vote_sts(c)
    if s.vote_sts(c).bypass[0] != BypassState.ACTIVE:
        raise s.fail("модель: байпас не включился")
    s.assert_enum("stVs.aeBypass[1]", BypassState.ACTIVE, f"{c.tag}: bypass channel 1 active")
    s.channel_invalid(c, 1)
    s.cycle()
    vs = s.vote_sts(c)
    s.load_vote_sts(c)
    s.assert_enum("stVs.aeChState[1]", vs.ch_state[0], f"{c.tag}: bypassed channel state")
    s.assert_bool("stVs.xTrip", vs.trip, f"{c.tag}: voting with bypassed channel")
    s.run_until_before(c.bypass_time_ms)
    vs = s.vote_sts(c)
    if vs.bypass[0] != BypassState.ACTIVE:
        raise s.fail("модель: байпас истёк раньше срока")
    s.load_vote_sts(c)
    s.assert_enum("stVs.aeBypass[1]", BypassState.ACTIVE, f"{c.tag}: bypass active one step before max")
    s.assert_time("stVs.atBypassRemain[1]", vs.bypass_remain_ms[0], f"{c.tag}: one step of bypass left")
    s.assert_latched(c.tag, " while bypassed")
    s.mark_events()
    s.step()
    vs = s.vote_sts(c)
    if vs.bypass[0] != BypassState.EXPIRED:
        raise s.fail("модель: байпас не истёк ровно на сроке")
    s.assert_event_since_mark(EventKind.BYPASS_EXPIRED, c, f"{c.tag}: BypassExpired logged")
    s.load_vote_sts(c)
    s.assert_enum("stVs.aeBypass[1]", BypassState.EXPIRED, f"{c.tag}: bypass expired exactly at max")
    s.assert_enum("stVs.aeChState[1]", vs.ch_state[0], f"{c.tag}: channel back to voting")
    s.run(c.delay_ms)
    s.assert_latched(c.tag, " after bypass expired")
    s.assert_effects(c.tag, sorted(c.effects), " after bypass expired")
    return s.finish()


def test_bypass_denied(m: Matrix, c: Cause) -> TestCase:
    s = _new(
        m,
        f"Matrix_{c.tag}Bypass_Denied",
        f"Причина {c.no} {c.tag}: байпас запрещён (bypass_max = 0); ключ разрешения байпасов, запрос байпаса "
        f"{c.sources[0]} → Denied, событие BypassDenied с номером канала.",
        "bypass",
        c,
    )
    s.arm()
    s.keys(True, False)
    s.bypass_request(c, 1)
    s.cycle()
    vs = s.vote_sts(c)
    last = s.h.log.get(0)
    if vs.bypass[0] != BypassState.DENIED or last.kind != EventKind.BYPASS_DENIED:
        raise s.fail("модель: запрос байпаса не отклонён")
    s.load_vote_sts(c)
    s.assert_enum("stVs.aeBypass[1]", BypassState.DENIED, f"{c.tag}: bypass denied")
    s.load_last_event()
    s.assert_enum("stEv.eKind", EventKind.BYPASS_DENIED, f"{c.tag}: last event BypassDenied")
    s.assert_cause("stEv.uiCause", c.no, f"{c.tag}: BypassDenied carries cause")
    s.assert_uint("stEv.uiChannel", last.channel, f"{c.tag}: BypassDenied carries channel")
    return s.finish()


# --- общие тесты -----------------------------------------------------------------------------------------
def test_first_out_pair(m: Matrix, a: Cause, b: Cause) -> TestCase:
    s = _new(
        m,
        f"Matrix_FirstOut{a.tag}Then{b.tag}_RecordsFirst",
        f"Первопричина: требование {a.tag}, фиксация через {format_duration_ru(a.delay_ms)}; затем требование "
        f"{b.tag}, фиксация через {format_duration_ru(b.delay_ms)} → первопричина {a.tag}, в маске первопричины "
        f"только {a.tag}, ltFirstOut — момент фиксации {a.tag}, {b.tag} — среди зафиксированных.",
        "first_out",
        a,
    )
    s.arm()
    s.demand(a)
    s.cycle(mark_t0=True)
    s.capture_t0()
    s.run(a.delay_ms)
    s.demand(b)
    s.cycle()
    s.run(b.delay_ms)
    if s.sts.first_out != a.no or not s.sts.latched & b.bit:
        raise s.fail("модель: первопричина или фиксация второй причины не по сценарию")
    s.assert_first_out(a.tag)
    s.assert_word(f"{s.v}.fbApp.stCemSts.wFirstOutMask", s.sts.first_out_mask, f"{a.tag}: first-out mask")
    s.assert_since_t0(f"{s.v}.fbApp.stCemSts.ltFirstOut", s.sts.lt_first_out, f"{a.tag}: first-out timestamp")
    s.assert_latched(f"{a.tag} then {b.tag}", "")
    return s.finish()


def _shares_channels(a: Cause, b: Cause) -> bool:
    return bool({t.casefold() for t in a.sources} & {t.casefold() for t in b.sources})


def test_first_out_simultaneous(m: Matrix) -> TestCase | None:
    enabled = m.enabled_causes
    pair = next(((a, b) for i, a in enumerate(enabled) for b in enabled[i + 1 :] if not _shares_channels(a, b)), None)
    if pair is None:
        return None
    a, b = pair
    s = _new(
        m,
        "Matrix_FirstOutSimultaneous_LowestIndex",
        f"Одновременная фиксация {a.tag} и {b.tag} (без общих каналов) в одном вызове: требования подаются "
        "со сдвигом на разницу задержек → первопричина — младшая причина, в маске первопричины обе.",
        "first_out",
        a,
    )
    s.arm()
    first, second = (a, b) if a.delay_ms >= b.delay_ms else (b, a)
    # вторая причина должна впервые получить требование в момент t0 + d1 − d2
    s.demand(first)
    if first.delay_ms == 0:
        s.demand(second)  # обе без задержки — один вызов
        s.cycle(mark_t0=True)
    elif second.delay_ms > 0:
        s.cycle(mark_t0=True)
        s.run(first.delay_ms - second.delay_ms)
        s.demand(second)
        s.cycle()
        s.run(second.delay_ms)
    else:
        s.cycle(mark_t0=True)
        s.run(first.delay_ms - s.delta)
        s.demand(second)  # без задержки: требование видит вызов на t0 + d1
        s.step()
    if s.sts.first_out_mask != (a.bit | b.bit) or s.sts.first_out != a.no:
        raise s.fail("модель: причины зафиксированы не в одном вызове")
    s.assert_first_out(a.tag)
    s.assert_word(f"{s.v}.fbApp.stCemSts.wFirstOutMask", s.sts.first_out_mask, f"{a.tag} and {b.tag} in mask")
    return s.finish()


def test_start(m: Matrix) -> TestCase:
    tripped = m.header.start_tripped
    name = "Matrix_Start_TrippedUntilReset" if tripped else "Matrix_Start_EnergizedWithoutReset"
    text = (
        "старт ПЛК: первый вызов с нормальными входами — все следствия обесточены, первопричина "
        "SIS_FIRST_OUT_START; сброс → все под напряжением."
        if tripped
        else "старт ПЛК без срабатывания (start_tripped = no): первый вызов — все следствия под напряжением."
    )
    s = _new(m, name, text[0].upper() + text[1:], "start", None)
    s.set_normal()
    s.cycle(mark_t0=True)
    s.assert_effects("start", None, " on first call")
    s.assert_first_out("start")
    if tripped:
        s.press_reset()
        s.assert_effects("start", None, " after reset", restored=True)
        s.assert_first_out("start", " cleared by reset")
    return s.finish()


def test_generated_cfg(m: Matrix) -> TestCase:
    s = _new(
        m,
        "Matrix_GeneratedCfg_PassesChecks",
        f"Сгенерированная конфигурация: F_CemCrc(CEM_CFG) = {st_word(m.crc)} = CEM_CFG.wMatrixCrc, F_CemCheckCfg "
        "без ошибок; после взвода нет ошибок конфигурации у матрицы и у групп голосования.",
        "cfg",
        None,
    )
    s.local("stCfg", "ST_CemCfg", "копия GVL_SisCfg.CEM_CFG")
    s.local("wCrc", "WORD", "CRC сгенерированной матрицы")
    s.local("wErr", "WORD", "биты ошибок конфигурации матрицы")
    s.emit("stCfg := GVL_SisCfg.CEM_CFG;")
    s.emit("wCrc := F_CemCrc(stCfg := stCfg);")
    s.assert_word("wCrc", m.crc, "CRC of generated CEM_CFG")
    s.emit(
        "AssertEquals_WORD(Expected := stCfg.wMatrixCrc, Actual := wCrc, Message := 'CRC matches CEM_CFG.wMatrixCrc');"
    )
    s.emit("wErr := F_CemCheckCfg(stCfg := stCfg);")
    s.assert_word("wErr", 0, "generated CEM_CFG passes F_CemCheckCfg")
    s.arm()
    s.assert_bool(f"{s.v}.fbApp.stCemSts.xCfgError", s.sts.cfg_error, "matrix cfg error after arm")
    for cause in m.enabled_causes:
        if not cause.is_voting:
            continue
        s.load_vote_sts(cause)
        s.assert_word("stVs.wCfgErr", s.vote_sts(cause).cfg_err, f"{cause.tag}: voting cfg ok")
    return s.finish()


def build_cases(matrix: Matrix) -> list[TestCase]:
    """Все сценарные тесты в порядке: по причинам, затем первопричина и общие."""
    cases: list[TestCase] = []
    for c in matrix.enabled_causes:
        cases.append(test_demand(matrix, c))
        if c.delay_ms > 0:
            cases.append(test_delay(matrix, c))
        cases.append(test_override_expires(matrix, c) if c.override else test_override_denied(matrix, c))
        cases.append(test_reset(matrix, c))
        if c.is_voting:
            cases.append(test_channel_invalid(matrix, c))
            cases.append(test_bypass_expires(matrix, c) if c.bypass_max > 0 else test_bypass_denied(matrix, c))
    enabled = matrix.enabled_causes
    if len(enabled) > 1:
        for index, a in enumerate(enabled):
            cases.append(test_first_out_pair(matrix, a, enabled[(index + 1) % len(enabled)]))
    cases.append(test_start(matrix))
    simultaneous = test_first_out_simultaneous(matrix)
    if simultaneous is not None:
        cases.append(simultaneous)
    cases.append(test_generated_cfg(matrix))
    return cases


# --- файлы наборов ---------------------------------------------------------------------------------------
def _wrap(text: str, width: int = 100) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if current and len(current) + 1 + len(word) > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}" if current else word
    if current:
        lines.append(current)
    return lines


def suites(cases: list[TestCase]) -> list[list[TestCase]]:
    """Разбиение на наборы не больше ``TESTS_PER_SUITE_MAX`` тестов."""
    size = limits.TESTS_PER_SUITE_MAX
    return [cases[i : i + size] for i in range(0, len(cases), size)]


def suite_name(index: int) -> str:
    return f"FB_CemGen{index:02d}_Test"


def _method_files(info: HeaderInfo, suite: str, case: TestCase) -> Files:
    decl = st_header(info, f"тест {case.name} набора {suite} (сценарий по матрице, DESIGN.md, 12.4).")
    decl += [f"// {line}" for line in _wrap(case.description)]
    decl.append(f"METHOD PRIVATE {case.method}")
    entries = list(case.locals.items())
    if entries:
        width = max(len(name) for name, _ in entries)
        type_width = max(len(st_type) for _, (st_type, _) in entries)
        decl.append("VAR")
        for name, (st_type, comment) in entries:
            decl.append(f"    {name.ljust(width)} : {(st_type + ';').ljust(type_width + 1)}   // {comment}")
        decl.append("END_VAR")
    impl = st_header(info, "", declaration=False) + case.body
    base = f"{TESTS_POU}/{suite}/{case.method}"
    return {f"{base}.method.decl.st": join_lines(decl), f"{base}.method.impl.st": join_lines(impl)}


def generate_tests(matrix: Matrix) -> tuple[Files, list[TestCase]]:
    """Наборы ``FB_CemGenNN_Test`` и ``GVL_TestsGenerated``."""
    info = HeaderInfo.of(matrix)
    cases = build_cases(matrix)
    files: Files = {}
    groups = suites(cases)
    first = 1
    for index, group in enumerate(groups, 1):
        suite = suite_name(index)
        for number, case in enumerate(group, 1):
            harness = f"fbH{number:03d}"
            case.harness = harness
            case.body = [line.replace("fbH001", harness) for line in case.body]
        last = first + len(group) - 1
        decl = st_header(
            info,
            f"набор coUnit: сценарии по матрице {matrix.header.document}, тесты {first}–{last} (DESIGN.md, "
            "12.4). Ожидаемые значения — эталонная модель cemgen. Стенд FB_SisHarness — по экземпляру на тест.",
        )
        decl += [f"FUNCTION_BLOCK {suite} EXTENDS coUnit.FB_TestSuite", "VAR"]
        width = max(len(case.harness) for case in group)
        for case in group:
            decl.append(f"    {case.harness.ljust(width)} : FB_SisHarness;   // {case.name}")
        decl.append("END_VAR")
        impl = st_header(info, "", declaration=False)
        impl.append("// Тесты выполняются за один вызов; coUnit сам отмечает завершённые")
        impl += [f"{case.method}();" for case in group]
        files[f"{TESTS_POU}/{suite}/{suite}.decl.st"] = join_lines(decl)
        files[f"{TESTS_POU}/{suite}/{suite}.impl.st"] = join_lines(impl)
        for case in group:
            files.update(_method_files(info, suite, case))
        first = last + 1
    # регистрация наборов
    lines = st_header(
        info,
        "экземпляры сгенерированных наборов coUnit: таблицы истинности голосования и сценарии по "
        "матрице. {attribute 'linkalways'} обязателен: без него CODESYS выбрасывает GVL, на которую никто "
        "не ссылается, и наборы молча пропадают.",
    )
    lines += ["{attribute 'qualified_only'}", "{attribute 'linkalways'}", "VAR_GLOBAL"]
    entries = [("fbVoteTruthTest", "FB_VoteTruth_Test", "таблицы истинности голосования (36 тестов)")]
    start = 1
    for index, group in enumerate(groups, 1):
        end = start + len(group) - 1
        entries.append((f"fbCemGen{index:02d}Test", suite_name(index), f"сценарии по матрице, тесты {start}–{end}"))
        start = end + 1
    width = max(len(name) for name, _, _ in entries)
    type_width = max(len(st_type) for _, st_type, _ in entries)
    for name, st_type, comment in entries:
        lines.append(f"    {name.ljust(width)} : {(st_type + ';').ljust(type_width + 1)}   // {comment}")
    lines.append("END_VAR")
    files[f"{TESTS_GVL}/GVL_TestsGenerated.gvl.st"] = join_lines(lines)
    return files, cases
