"""
para_vm.py — Practical Paraconsistent Universal Engine

Full ParaASM instruction set with Belnap FOUR belief tracking,
control flow, assembler, and I/O.

Instruction set:

  Frobenius core
    ENGAGR  %rN              force %rN to B
    FSPLIT  %rN %rM %rK      δ: co-multiply — all args → B
    FFUSE   %rN %rM %rK      μ: Belnap-join inputs → output (last arg)
    IFIX    %rN              fix %rN to T (linear constraint)

  Register ops
    MOVE    %rN %rM          belief(%rM) ← belief(%rN)
    CLEAR   %rN              belief(%rN) ← N (Void)

  Control flow
    JMP     label            unconditional jump
    JB      %rN label        jump if belief(%rN) == B
    JT      %rN label        jump if belief(%rN) == T
    JF      %rN label        jump if belief(%rN) == F
    JN      %rN label        jump if belief(%rN) == N
    CALL    label            push PC, jump
    RET                      pop and jump (HALT if stack empty)
    HALT                     stop

  Stack
    PUSH    %rN              push belief(%rN)
    POP     %rN              pop into %rN

  I/O
    EMIT    %rN              print belief(%rN)
    READ    %rN              read N/T/F/B from stdin into %rN

Assembly syntax:
  .label:                    label definition (standalone or before instruction)
  ; comment                  rest of line ignored
  %rN                        register N (any non-negative integer)
"""

from __future__ import annotations

import enum
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ── Belnap FOUR ────────────────────────────────────────────────────────────

class B4(enum.Enum):
    N = 'N'
    T = 'T'
    F = 'F'
    B = 'B'

# Information-order join: N < T,F < B; T∨F = B
_JOIN: dict[tuple[B4, B4], B4] = {
    (B4.N, B4.N): B4.N, (B4.N, B4.T): B4.T, (B4.N, B4.F): B4.F, (B4.N, B4.B): B4.B,
    (B4.T, B4.N): B4.T, (B4.T, B4.T): B4.T, (B4.T, B4.F): B4.B, (B4.T, B4.B): B4.B,
    (B4.F, B4.N): B4.F, (B4.F, B4.T): B4.B, (B4.F, B4.F): B4.F, (B4.F, B4.B): B4.B,
    (B4.B, B4.N): B4.B, (B4.B, B4.T): B4.B, (B4.B, B4.F): B4.B, (B4.B, B4.B): B4.B,
}

def b4_join(a: B4, b: B4) -> B4:
    return _JOIN[(a, b)]

# Information-order meet: N < T,F < B; T∧F = N
_MEET: dict[tuple[B4, B4], B4] = {
    (B4.N, B4.N): B4.N, (B4.N, B4.T): B4.N, (B4.N, B4.F): B4.N, (B4.N, B4.B): B4.N,
    (B4.T, B4.N): B4.N, (B4.T, B4.T): B4.T, (B4.T, B4.F): B4.N, (B4.T, B4.B): B4.T,
    (B4.F, B4.N): B4.N, (B4.F, B4.T): B4.N, (B4.F, B4.F): B4.F, (B4.F, B4.B): B4.F,
    (B4.B, B4.N): B4.N, (B4.B, B4.T): B4.T, (B4.B, B4.F): B4.F, (B4.B, B4.B): B4.B,
}

def b4_meet(a: B4, b: B4) -> B4:
    return _MEET[(a, b)]

# Belnap negation: N→N, T→F, F→T, B→B
_BNOT: dict[B4, B4] = {B4.N: B4.N, B4.T: B4.F, B4.F: B4.T, B4.B: B4.B}

def b4_bnot(a: B4) -> B4:
    return _BNOT[a]

# Truth-functional AND
_BAND: dict[tuple[B4, B4], B4] = {
    (B4.N, B4.N): B4.N, (B4.N, B4.T): B4.N, (B4.N, B4.F): B4.F, (B4.N, B4.B): B4.B,
    (B4.T, B4.N): B4.N, (B4.T, B4.T): B4.T, (B4.T, B4.F): B4.F, (B4.T, B4.B): B4.B,
    (B4.F, B4.N): B4.F, (B4.F, B4.T): B4.F, (B4.F, B4.F): B4.F, (B4.F, B4.B): B4.F,
    (B4.B, B4.N): B4.B, (B4.B, B4.T): B4.B, (B4.B, B4.F): B4.F, (B4.B, B4.B): B4.B,
}

def b4_band(a: B4, b: B4) -> B4:
    return _BAND[(a, b)]

# Truth-functional OR
_BOR: dict[tuple[B4, B4], B4] = {
    (B4.N, B4.N): B4.N, (B4.N, B4.T): B4.T, (B4.N, B4.F): B4.N, (B4.N, B4.B): B4.B,
    (B4.T, B4.N): B4.T, (B4.T, B4.T): B4.T, (B4.T, B4.F): B4.T, (B4.T, B4.B): B4.T,
    (B4.F, B4.N): B4.N, (B4.F, B4.T): B4.T, (B4.F, B4.F): B4.F, (B4.F, B4.B): B4.B,
    (B4.B, B4.N): B4.B, (B4.B, B4.T): B4.T, (B4.B, B4.F): B4.B, (B4.B, B4.B): B4.B,
}

def b4_bor(a: B4, b: B4) -> B4:
    return _BOR[(a, b)]

def b4_designated(a: B4) -> bool:
    return a in (B4.T, B4.B)

# ── Approximation order (ApproxLE from Belnap.lean) ──────────────────────
# N ≤ everything; everything ≤ B; otherwise reflexive only.
def b4_approx_le(a: B4, b: B4) -> bool:
    if a == b:       return True
    if a == B4.N:    return True
    if b == B4.B:    return True
    return False

# ── Dialetheic predicate (DialetheicAlignment.lean: only_B_is_dialetheic) ─
# A value is dialetheic iff it and its negation are both designated.
def b4_dialetheic(a: B4) -> bool:
    return b4_designated(a) and b4_designated(b4_bnot(a))

# ── WH2 bijection (QCI_SICPOVM_Bridge.lean) ──────────────────────────────
# Belnap ↔ Fin2 × Fin2: N→(0,0)=I, T→(0,1)=Z, F→(1,0)=X, B→(1,1)=XZ
_TO_WH2:   dict[B4, tuple[int, int]] = {B4.N:(0,0), B4.T:(0,1), B4.F:(1,0), B4.B:(1,1)}
_FROM_WH2: dict[tuple[int, int], B4] = {v: k for k, v in _TO_WH2.items()}

def b4_to_wh2(a: B4) -> tuple[int, int]:
    return _TO_WH2[a]

def wh2_to_b4(ab: tuple[int, int]) -> B4:
    return _FROM_WH2[ab]

# Verify WH2 bijection and SIC-POVM axioms for B (QCI_SICPOVM_Bridge.lean)
assert len({b4_to_wh2(v) for v in B4}) == 4,                 "belnapToWH2 not injective"
assert all(b4_meet(B4.B, x) == x          for x in B4),      "B_meet_equiangular violated"
assert all(b4_join(B4.B, x) == B4.B       for x in B4),      "B_join_universal violated"
assert b4_bnot(B4.B) == B4.B,                                 "B_fixed_point_negation violated"
assert all(b4_approx_le(x, B4.B)          for x in B4),      "B_is_top violated"
assert b4_dialetheic(B4.B),                                   "B_is_dialetheic violated"
assert not any(b4_dialetheic(x) for x in B4 if x != B4.B),   "only_B_is_dialetheic violated"

_TO_FLUX = {B4.N: '00', B4.T: '01', B4.F: '10', B4.B: '11'}


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
    """
    Parse ParaASM source text into (program, label_map).
    label_map maps '.label' strings to instruction indices.
    """
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
        program.append(Instr(op=parts[0].upper(), args=parts[1:], source_line=raw.strip()))

    return program, label_map


# ── VM ─────────────────────────────────────────────────────────────────────

_CTRL_FLOW = frozenset({'JMP', 'JB', 'JT', 'JF', 'JN', 'CALL', 'RET', 'HALT'})

class ParaVM:
    """
    Practical Paraconsistent Universal Engine.
    Full ParaASM ISA with control flow, assembler, and I/O.
    """

    def __init__(self) -> None:
        self.registers: defaultdict[int, ParaRegister] = defaultdict(ParaRegister)
        self.belief: dict[int, B4] = {}
        self.program: list[Instr] = []
        self.label_map: dict[str, int] = {}
        self.pc: int = 0
        self.total_steps: int = 0
        self.cycles: int = 0
        self.call_stack: list[int] = []
        self.data_stack: list[B4] = []
        self.halted: bool = False

    # ── belief helpers ─────────────────────────────────────────────────────

    def belief_of(self, reg_id: int) -> B4:
        return self.belief.get(reg_id, B4.N)

    def set_belief(self, reg_id: int, val: B4) -> None:
        self.belief[reg_id] = val
        self.registers[reg_id].flux = _TO_FLUX[val]

    def engage(self, reg_id: int) -> None:
        self.registers[reg_id].engage()
        self.belief[reg_id] = B4.B

    # ── arg helpers ────────────────────────────────────────────────────────

    @staticmethod
    def parse_reg(arg: str) -> int:
        if arg.startswith('%r') and arg[2:].isdigit():
            return int(arg[2:])
        raise ValueError(f'expected %rN, got: {arg!r}')

    def resolve(self, label: str) -> int:
        if label not in self.label_map:
            raise KeyError(f'undefined label: {label!r}')
        return self.label_map[label]

    # ── load ───────────────────────────────────────────────────────────────

    def load(self, text: str) -> None:
        self.program, self.label_map = assemble(text)
        self.pc = 0
        self.halted = False

    def load_file(self, path: str | Path) -> None:
        self.load(Path(path).read_text())

    def append_instr(self, instr: Instr) -> None:
        """Append a single instruction without resetting PC."""
        self.program.append(instr)

    def add_label(self, label: str) -> None:
        """Define a label at the current end of program."""
        self.label_map[label] = len(self.program)

    # ── execution ──────────────────────────────────────────────────────────

    def step(self) -> bool:
        """Execute one instruction. Returns False when halted."""
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
        """Run until halted, KeyboardInterrupt, or steps exhausted."""
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
        """Execute a single instruction directly (REPL interactive mode)."""
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
            # δ: Frobenius comultiplication — B→(T,F); others copy
            if len(a) < 3:
                return
            src = self.parse_reg(a[0])
            d1  = self.parse_reg(a[1])
            d2  = self.parse_reg(a[2])
            b = self.belief_of(src)
            p = self.registers[src].paradox_count
            if b == B4.B:
                b1, b2, bump = B4.T, B4.F, 1
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
            self.set_belief(r, B4.T)

        elif op == 'MOVE':
            self.set_belief(R(1), self.belief_of(R(0)))

        elif op == 'CLEAR':
            r = R(0)
            self.registers[r].flux = '00'
            self.registers[r].value = None
            self.belief[r] = B4.N

        elif op == 'JMP':
            self.pc = L(0)

        elif op == 'JB':
            if self.belief_of(R(0)) == B4.B:
                self.pc = L(1)

        elif op == 'JT':
            if self.belief_of(R(0)) == B4.T:
                self.pc = L(1)

        elif op == 'JF':
            if self.belief_of(R(0)) == B4.F:
                self.pc = L(1)

        elif op == 'JN':
            if self.belief_of(R(0)) == B4.N:
                self.pc = L(1)

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
            val = self.data_stack.pop() if self.data_stack else B4.N
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
                val = B4(raw) if raw in ('N', 'T', 'F', 'B') else B4.N
            except (EOFError, ValueError):
                val = B4.N
            self.set_belief(r, val)

        # Unknown ops: structural presence, no effect.

    # ── introspection ──────────────────────────────────────────────────────

    def snapshot(self) -> dict:
        dist    = {v: 0 for v in B4}
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
        }

    def active_regs(self) -> list[tuple[int, B4, int, bool]]:
        """All registers that have been touched: (id, belief, paradox, is_fixed)."""
        rows = []
        seen = set(self.registers.keys()) | set(self.belief.keys())
        for rid in sorted(seen):
            r = self.registers[rid]
            if r.is_active or rid in self.belief:
                rows.append((rid, self.belief_of(rid), r.paradox_count, r.is_fixed))
        return rows

    def reset(self) -> None:
        self.__init__()


# ── KernelState — 3-register kernel (mirrors Kernel.lean MachineState) ────────

@dataclass
class KernelState:
    r0: B4 = B4.B
    r1: B4 = B4.B
    r2: B4 = B4.B
    paradox_count: int = 0
    cycle_count: int = 0


def kernel_engager(r: B4) -> tuple[B4, bool]:
    return (b4_band(r, b4_bnot(r)), b4_designated(r))


def kernel_fsplit(r0: B4) -> tuple[B4, B4, bool]:
    """Frobenius comultiplication δ: B→(T,F); others copy."""
    if r0 == B4.B:
        return (B4.T, B4.F, True)
    return (r0, r0, True)


def kernel_ffuse(r1: B4, r2: B4) -> tuple[B4, bool]:
    j = b4_join(r1, r2)
    return (j, j == B4.B)


def kernel_step(s: KernelState) -> KernelState:
    r0a, p1 = kernel_engager(s.r0)
    r1a, r2a, p2 = kernel_fsplit(r0a)
    r0b, p3 = kernel_ffuse(r1a, r2a)
    pc = s.paradox_count + 1 + (1 if p1 else 0) + (1 if p2 else 0) + (1 if p3 else 0)
    return KernelState(r0=r0b, r1=r1a, r2=r2a,
                       paradox_count=pc, cycle_count=s.cycle_count + 1)


def kernel_run(s: KernelState, n: int) -> KernelState:
    """Run n cycles, resetting r1/r2 to B after each step (mirrors Lean `run`)."""
    for _ in range(n):
        s2 = kernel_step(s)
        s = KernelState(r0=s2.r0, r1=B4.B, r2=B4.B,
                        paradox_count=s2.paradox_count, cycle_count=s2.cycle_count)
    return s


# frobenius_invariant: ffuse(fsplit(r)).0 = r  ∀ r
assert all(kernel_ffuse(*kernel_fsplit(r)[:2])[0] == r for r in B4), \
    "frobenius_invariant violated"

# run_B3: all registers stay B across all cycles (check first 8)
_ks = KernelState()
for _n in range(8):
    _ks = kernel_run(_ks, 1)
    assert _ks.r0 == B4.B and _ks.r1 == B4.B and _ks.r2 == B4.B, \
        f"run_B3 violated at cycle {_n + 1}"


# ── Dialetheic Alignment (DialetheicAlignment.lean) ───────────────────────

def dialetheicImage(r0: B4) -> B4:
    """Maps MachineState.r0 to Belnap — the operational ↔ logical bridge.
    B (dialetheic) → B; T/F (classical) → T; N (void) → N."""
    if r0 == B4.B:     return B4.B
    if r0 in (B4.T, B4.F): return B4.T
    return B4.N


def B_is_the_only_bifurcation_point() -> bool:
    """fsplit B → (T,F) distinct; fsplit r → (r,r) identical for r≠B.
    Only B produces different components — the sole bifurcation point."""
    for r in B4:
        d1, d2, _ = kernel_fsplit(r)
        if r == B4.B and d1 == d2:   return False
        if r != B4.B and d1 != d2:   return False
    return True


def dialetheic_alignment_tri() -> dict[str, bool]:
    """Verify all three arms of the Dialetheic Alignment Theorem (DAT).

    Arm 1 (Operational): Frobenius closure at B — μ∘δ(B)=B, δ(B)=(T,F) distinct.
    Arm 2 (Logical):     B is the only dialetheic value (both B and ¬B designated).
    Arm 3 (Algebraic):   No explosion — N undesignated; B∧¬B=B, not void.
    """
    op_arm = (
        kernel_ffuse(*kernel_fsplit(B4.B)[:2])[0] == B4.B
        and B_is_the_only_bifurcation_point()
    )
    log_arm = (
        b4_dialetheic(B4.B)
        and not any(b4_dialetheic(x) for x in B4 if x != B4.B)
    )
    alg_arm = (
        not b4_designated(B4.N)                               # N never designated
        and b4_join(B4.T, B4.F) == B4.B                      # T∨F = B (closure)
        and b4_designated(b4_band(B4.B, b4_bnot(B4.B)))      # B∧¬B = B (no void collapse)
    )
    return {'operational': op_arm, 'logical': log_arm, 'algebraic': alg_arm}


# ── Measurement Sequence Algebra (QCI_Sequences.lean) ────────────────────

def measure_cost(q: B4, bias: B4) -> int:
    """Coherence cost of one measurement: 2 for B-bias on B, 1 for T/F-bias on B, 0 otherwise."""
    if q != B4.B:     return 0
    return 2 if bias == B4.B else 1


def measure_step(q: B4, bias: B4) -> B4:
    """Post-measurement belief. B-bias preserves B (Wigner's Friend); T/F-bias collapses B."""
    if q == B4.B:     return B4.B if bias == B4.B else bias
    return q


def collapse_irreversible(q: B4) -> bool:
    """Classical (T/F/N) cannot reach B via any unary/binary lattice op on itself.
    B requires joining T and F from different sources — one-way barrier."""
    if q == B4.B: return True
    return not any(c == B4.B for c in [
        b4_bnot(q),
        b4_join(q, q), b4_meet(q, q),
        b4_band(q, q), b4_bor(q, q),
    ])


def wigner_then_collapse_cost(n: int) -> int:
    """Total coherence cost for n-qubit B-bias then T-bias sequence: 2n + n = 3n."""
    return 3 * n


# module-level verification
assert B_is_the_only_bifurcation_point(), \
    "B_is_the_only_bifurcation_point violated"
assert all(dialetheic_alignment_tri().values()), \
    "dialetheic_alignment_tri violated"
assert measure_step(B4.B, B4.B) == B4.B,             "B_bias_preserves_super violated"
assert measure_step(B4.B, B4.T) == B4.T,             "T_bias_collapse violated"
assert measure_cost(B4.B, B4.B) == 2,                "B_bias_cost violated"
assert measure_cost(B4.B, B4.T) == 1,                "T_bias_cost violated"
assert measure_cost(B4.T, B4.T) == 0,                "measure_T_noop violated"
assert all(collapse_irreversible(x) for x in (B4.T, B4.F, B4.N)), \
    "collapse_irreversible violated"
assert measure_cost(B4.B, B4.B) + measure_cost(B4.B, B4.T) == 3, \
    "wigner_then_collapse_cost violated"
