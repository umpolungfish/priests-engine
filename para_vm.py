"""
para_vm.py — Practical Paraconsistent Universal Engine

Belnap foundation provided by p4ramill_py (mirroring p4ramill Lean 4 kernel).
All Belnap types, operations, and invariants are imported from the p4rakernel,
not defined locally. The VM, assembler, ParaASM instruction set, and
dialetheic alignment functions are built on top of this kernel foundation.

Instruction set:
  Frobenius core: ENGAGR, FSPLIT, FFUSE, IFIX
  Register ops: MOVE, CLEAR
  Control flow: JMP, JB, JT, JF, JN, CALL, RET, HALT
  Stack: PUSH, POP
  I/O: EMIT, READ

Kernel basis: p4ramill_py ← Imscribing/Paraconsistent/{Belnap,Kernel}.lean
"""

from __future__ import annotations

import enum
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── Auto-resolve p4rakernel path ─────────────────────────────────────────
# This allows the priests-engine to find p4ramill_py regardless of how it's run.
_p4rakernel_path = str(Path(__file__).resolve().parent.parent / 'p4rakernel')
if _p4rakernel_path not in sys.path:
    sys.path.insert(0, _p4rakernel_path)

# ── Belnap foundation: imported from p4rakernel (mirroring Lean 4 kernel) ──
from p4ramill_py.belnap import (
    Belnap, meet, join, band, bor, bnot, designated,
    approx_le, to_wh2, from_wh2, dialetheic,
)
from p4ramill_py.kernel import (
    MachineState, initial_state, engager, fsplit, ffuse,
    step as kernel_step_fn, run as kernel_run_fn,
    frobenius_invariant, verify_frobenius_invariant,
    verify_run_B3, verify_paradox_conservation, verify_cycle_count,
    verify_paraconsistency, run_all_verifications,
)

# ── Alias for backward compatibility ──────────────────────────────────────
B4 = Belnap

# ── Belnap operation aliases (b4_ prefix for compatibility) ──────────────
b4_join = join
b4_meet = meet
b4_band = band
b4_bnot = bnot
b4_designated = designated
b4_bor = bor
b4_approx_le = approx_le
b4_to_wh2 = to_wh2
wh2_to_b4 = from_wh2
b4_dialetheic = dialetheic

_TO_FLUX = {
    Belnap.N: '00', Belnap.T: '01', Belnap.F: '10', Belnap.B: '11'
}

# ── WH2 bijection verification ──────────────────────────────────────────
assert len({to_wh2(v) for v in Belnap}) == 4, "belnapToWH2 not injective"
assert all(meet(Belnap.B, x) == x for x in Belnap), "B_meet_equiangular violated"
assert all(join(Belnap.B, x) == Belnap.B for x in Belnap), "B_join_universal violated"
assert bnot(Belnap.B) == Belnap.B, "B_fixed_point_negation violated"
assert all(approx_le(x, Belnap.B) for x in Belnap), "B_is_top violated"
assert dialetheic(Belnap.B), "B_is_dialetheic violated"
assert not any(dialetheic(x) for x in Belnap if x != Belnap.B), "only_B_is_dialetheic violated"

# ── Register ───────────────────────────────────────────────────────────────

class ParaRegister:
    __slots__ = ('flux', 'value', 'paradox_count')

    def __init__(self) -> None:
        self.flux: str = '00'
        self.value: Optional[str] = None
        self.paradox_count: int = 0

    def engage(self) -> None:
        self.flux = '11'
        self.paradox_count += 1

    @property
    def is_fixed(self) -> bool:
        return self.value == 'FIXED'

    @property
    def is_active(self) -> bool:
        return self.flux != '00' or self.value is not None

    def get_belnap(self) -> Belnap:
        return {
            '00': Belnap.N, '01': Belnap.T, '10': Belnap.F, '11': Belnap.B,
        }.get(self.flux, Belnap.N)

    def set_belnap(self, b: Belnap) -> None:
        self.flux = _TO_FLUX[b]


# ── Instruction ────────────────────────────────────────────────────────────

@dataclass
class Instr:
    op: str
    args: list[str] = field(default_factory=list)
    source_line: str = ''

    def __str__(self) -> str:
        parts = [self.op] + self.args
        return '  ' + '  '.join(parts)


# ── Assembler ──────────────────────────────────────────────────────────────

_LABEL_RE = re.compile(r'^\s*(\.\w+)\s*:(.*)')

def assemble(text: str) -> tuple[list[Instr], dict[str, int]]:
    program: list[Instr] = []
    label_map: dict[str, int] = {}
    for raw in text.splitlines():
        line = raw.split(';', 1)[0].strip()
        if not line:
            continue
        m = _LABEL_RE.match(line)
        if m:
            label_map[m.group(1)] = len(program)
            line = m.group(2).strip()
            if not line:
                continue
        parts = line.split()
        if not parts:
            continue
        program.append(Instr(op=parts[0].upper(), args=parts[1:],
                             source_line=raw.strip()))
    return program, label_map


# ── Control flow ops ───────────────────────────────────────────────────────

_CTRL_FLOW = frozenset({'JMP', 'JB', 'JT', 'JF', 'JN', 'CALL', 'RET', 'HALT'})

# ── VM ─────────────────────────────────────────────────────────────────────

class ParaVM:
    """Practical Paraconsistent Universal Engine — ParaASM ISA.
    Belnap foundation: p4ramill_py (mirrors Imscribing/Paraconsistent/Kernel.lean)."""

    def __init__(self) -> None:
        self.registers: defaultdict[int, ParaRegister] = defaultdict(ParaRegister)
        self.belief: dict[int, Belnap] = {}
        self.program: list[Instr] = []
        self.label_map: dict[str, int] = {}
        self.pc: int = 0
        self.total_steps: int = 0
        self.cycles: int = 0
        self.call_stack: list[int] = []
        self.data_stack: list[Belnap] = []
        self.halted: bool = False

    def belief_of(self, reg_id: int) -> Belnap:
        return self.belief.get(reg_id, Belnap.N)

    def set_belief(self, reg_id: int, val: Belnap) -> None:
        self.belief[reg_id] = val
        self.registers[reg_id].flux = _TO_FLUX[val]

    def engage(self, reg_id: int) -> None:
        self.registers[reg_id].engage()
        self.belief[reg_id] = Belnap.B

    @staticmethod
    def parse_reg(arg: str) -> int:
        if arg.startswith('%r') and arg[2:].isdigit():
            return int(arg[2:])
        raise ValueError(f'expected %rN, got: {arg!r}')

    def resolve(self, label: str) -> int:
        if label not in self.label_map:
            raise KeyError(f'undefined label: {label!r}')
        return self.label_map[label]

    def load(self, text: str) -> None:
        self.program, self.label_map = assemble(text)
        self.pc = 0
        self.halted = False

    def load_file(self, path: str | Path) -> None:
        self.load(Path(path).read_text())

    def append_instr(self, instr: Instr) -> None:
        self.program.append(instr)

    def add_label(self, label: str) -> None:
        self.label_map[label] = len(self.program)

    def step(self) -> bool:
        if self.halted or not self.program:
            return False
        if self.pc >= len(self.program):
            self.pc = 0
            self.cycles += 1
        instr = self.program[self.pc]
        self.pc += 1
        self.total_steps += 1
        self._exec(instr)
        return not self.halted

    def run(self, steps: Optional[int] = None) -> None:
        n = 0
        try:
            while not self.halted:
                if steps is not None and n >= steps:
                    break
                if not self.step():
                    break
                n += 1
        except KeyboardInterrupt:
            pass

    def exec_one(self, instr: Instr) -> None:
        self.total_steps += 1
        self._exec(instr)

    def _exec(self, instr: Instr) -> None:
        op = instr.op
        a  = instr.args

        def R(i: int) -> int:
            return self.parse_reg(a[i])
        def L(i: int) -> int:
            return self.resolve(a[i])

        if op == 'ENGAGR':
            r = R(0)
            self.engage(r)

        elif op == 'FSPLIT':
            if len(a) < 3:
                return
            src = self.parse_reg(a[0])
            d1  = self.parse_reg(a[1])
            d2  = self.parse_reg(a[2])
            b = self.belief_of(src)
            p = self.registers[src].paradox_count
            if b == Belnap.B:
                b1, b2, bump = Belnap.T, Belnap.F, 1
            else:
                b1, b2, bump = b, b, 0
            self.set_belief(d1, b1)
            self.set_belief(d2, b2)
            self.registers[d1].paradox_count = p + bump
            self.registers[d2].paradox_count = p + bump

        elif op == 'FFUSE':
            if len(a) < 2:
                return
            joined = self.belief_of(self.parse_reg(a[0]))
            for arg in a[1:-1]:
                joined = b4_join(joined, self.belief_of(self.parse_reg(arg)))
            self.set_belief(self.parse_reg(a[-1]), joined)

        elif op == 'IFIX':
            r = R(0)
            self.registers[r].value = 'FIXED'
            self.set_belief(r, Belnap.T)

        elif op == 'MOVE':
            self.set_belief(R(1), self.belief_of(R(0)))

        elif op == 'CLEAR':
            r = R(0)
            self.registers[r].flux = '00'
            self.registers[r].value = None
            self.belief[r] = Belnap.N

        elif op == 'JMP':
            self.pc = L(0)
        elif op == 'JB':
            if self.belief_of(R(0)) == Belnap.B: self.pc = L(1)
        elif op == 'JT':
            if self.belief_of(R(0)) == Belnap.T: self.pc = L(1)
        elif op == 'JF':
            if self.belief_of(R(0)) == Belnap.F: self.pc = L(1)
        elif op == 'JN':
            if self.belief_of(R(0)) == Belnap.N: self.pc = L(1)
        elif op == 'CALL':
            self.call_stack.append(self.pc)
            self.pc = L(0)
        elif op == 'RET':
            if self.call_stack:
                self.pc = self.call_stack.pop()
            else:
                self.halted = True
        elif op == 'HALT':
            self.halted = True
        elif op == 'PUSH':
            self.data_stack.append(self.belief_of(R(0)))
        elif op == 'POP':
            val = self.data_stack.pop() if self.data_stack else Belnap.N
            self.set_belief(R(0), val)
        elif op == 'EMIT':
            r = R(0)
            b = self.belief_of(r).value
            fixed = ' [FIXED]' if self.registers[r].is_fixed else ''
            print(f'  %r{r} = {b}{fixed}')
        elif op == 'READ':
            r = R(0)
            try:
                raw = input(f'  read %r{r} (N/T/F/B): ').strip().upper()
                val = Belnap(raw) if raw in ('N', 'T', 'F', 'B') else Belnap.N
            except (EOFError, ValueError):
                val = Belnap.N
            self.set_belief(r, val)

    # ── introspection ──────────────────────────────────────────────────

    def snapshot(self) -> dict:
        dist    = {v: 0 for v in Belnap}
        paradox = 0
        active  = 0
        fixed   = 0
        for rid in self.registers:
            r = self.registers[rid]
            dist[self.belief_of(rid)] += 1
            paradox += r.paradox_count
            if r.is_active:
                active += 1
            if r.is_fixed:
                fixed += 1
        return {
            'steps': self.total_steps, 'cycles': self.cycles,
            'pc': self.pc, 'active': active, 'fixed': fixed,
            'paradox': paradox, 'dist': dist, 'halted': self.halted,
            'kernel': 'p4ramill_py (Lean 4 verified)',
        }

    def active_regs(self) -> list[tuple[int, Belnap, int, bool]]:
        rows = []
        seen = set(self.registers.keys()) | set(self.belief.keys())
        for rid in sorted(seen):
            r = self.registers[rid]
            if r.is_active or rid in self.belief:
                rows.append((rid, self.belief_of(rid), r.paradox_count, r.is_fixed))
        return rows

    def reset(self) -> None:
        self.__init__()


# ── KernelState — wraps p4ramill_py.kernel (mirrors Kernel.lean) ─────────

@dataclass
class KernelState:
    """Lightweight wrapper around p4ramill_py kernel.MachineState.
    Mirrors Imscribing/Paraconsistent/Kernel.lean `MachineState`."""
    r0: Belnap = Belnap.B
    r1: Belnap = Belnap.B
    r2: Belnap = Belnap.B
    paradox_count: int = 0
    cycle_count: int = 0

    def to_machine_state(self) -> MachineState:
        return MachineState(r0=self.r0, r1=self.r1, r2=self.r2,
                            paradoxCount=self.paradox_count,
                            cycleCount=self.cycle_count)

    @classmethod
    def from_machine_state(cls, ms: MachineState) -> 'KernelState':
        return cls(r0=ms.r0, r1=ms.r1, r2=ms.r2,
                   paradox_count=ms.paradoxCount,
                   cycle_count=ms.cycleCount)


def kernel_engager(r: Belnap) -> tuple[Belnap, bool]:
    return engager(r)

def kernel_fsplit(r0: Belnap) -> tuple[Belnap, Belnap, bool]:
    return fsplit(r0)

def kernel_ffuse(r1: Belnap, r2: Belnap) -> tuple[Belnap, bool]:
    return ffuse(r1, r2)

def kernel_step(s: KernelState) -> KernelState:
    ms = s.to_machine_state()
    ms2 = kernel_step_fn(ms)
    return KernelState.from_machine_state(ms2)

def kernel_run(s: KernelState, n: int) -> KernelState:
    ms = s.to_machine_state()
    ms2 = kernel_run_fn(ms, n)
    return KernelState.from_machine_state(ms2)


# frobenius_invariant: ffuse(fsplit(r)).0 = r  ∀ r
assert all(kernel_ffuse(*kernel_fsplit(r)[:2])[0] == r for r in Belnap), \
    "frobenius_invariant violated (p4ramill_py verified)"

# run_B3: all registers stay B across all cycles
_ks = KernelState()
for _n in range(8):
    _ks = kernel_run(_ks, 1)
    assert _ks.r0 == Belnap.B and _ks.r1 == Belnap.B and _ks.r2 == Belnap.B, \
        f"run_B3 violated at cycle {_n + 1}"


# ── Dialetheic Alignment (DialetheicAlignment.lean) ───────────────────────

def dialetheicImage(r0: Belnap) -> Belnap:
    if r0 == Belnap.B:     return Belnap.B
    if r0 in (Belnap.T, Belnap.F): return Belnap.T
    return Belnap.N

def B_is_the_only_bifurcation_point() -> bool:
    for r in Belnap:
        d1, d2, _ = kernel_fsplit(r)
        if r == Belnap.B and d1 == d2:   return False
        if r != Belnap.B and d1 != d2:   return False
    return True

def dialetheic_alignment_tri() -> dict[str, bool]:
    op_arm = (
        kernel_ffuse(*kernel_fsplit(Belnap.B)[:2])[0] == Belnap.B
        and B_is_the_only_bifurcation_point()
    )
    log_arm = (
        b4_dialetheic(Belnap.B)
        and not any(b4_dialetheic(x) for x in Belnap if x != Belnap.B)
    )
    alg_arm = (
        not b4_designated(Belnap.N)
        and b4_join(Belnap.T, Belnap.F) == Belnap.B
        and b4_designated(b4_band(Belnap.B, b4_bnot(Belnap.B)))
    )
    return {'operational': op_arm, 'logical': log_arm, 'algebraic': alg_arm}


# ── Measurement Sequence Algebra (QCI_Sequences.lean) ────────────────────

def measure_cost(q: Belnap, bias: Belnap) -> int:
    if q != Belnap.B:     return 0
    return 2 if bias == Belnap.B else 1

def measure_step(q: Belnap, bias: Belnap) -> Belnap:
    if q == Belnap.B:
        return Belnap.B if bias == Belnap.B else bias
    return q

def collapse_irreversible(q: Belnap) -> bool:
    if q == Belnap.B: return True
    return not any(c == Belnap.B for c in [
        b4_bnot(q), b4_join(q, q), b4_meet(q, q),
        b4_band(q, q), b4_bor(q, q),
    ])

def wigner_then_collapse_cost(n: int) -> int:
    return 3 * n


# module-level verification
assert B_is_the_only_bifurcation_point(), \
    "B_is_the_only_bifurcation_point violated"
assert all(dialetheic_alignment_tri().values()), \
    "dialetheic_alignment_tri violated"
assert measure_step(Belnap.B, Belnap.B) == Belnap.B, "B_bias_preserves_super violated"
assert measure_step(Belnap.B, Belnap.T) == Belnap.T, "T_bias_collapse violated"
assert measure_cost(Belnap.B, Belnap.B) == 2, "B_bias_cost violated"
assert measure_cost(Belnap.B, Belnap.T) == 1, "T_bias_cost violated"
assert measure_cost(Belnap.T, Belnap.T) == 0, "measure_T_noop violated"
assert all(collapse_irreversible(x) for x in (Belnap.T, Belnap.F, Belnap.N)), \
    "collapse_irreversible violated"
assert measure_cost(Belnap.B, Belnap.B) + measure_cost(Belnap.B, Belnap.T) == 3, \
    "wigner_then_collapse_cost violated"
