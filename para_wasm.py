# para_wasm.py — Self-Verifying WASM Runtime
# Belnap-tagged WebAssembly execution with Frobenius checkpoint/verify protocol.
# Matches SelfVerifyingWASM.lean exactly.

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from para_vm import B4

# ── Types ─────────────────────────────────────────────────────────────────────

class WasmType(Enum):
    i32 = "i32"
    i64 = "i64"

@dataclass
class WasmValue:
    ty: WasmType
    val: int

@dataclass
class TaggedValue:
    value: WasmValue
    tag: B4

    def designated(self) -> bool:
        return self.tag in (B4.T, B4.B)

Stack = list[TaggedValue]

# ── Frobenius tag operations (frobTagBin = meet in approx order) ──────────────

_MEET: dict[tuple[B4, B4], B4] = {
    (B4.N, B4.N): B4.N, (B4.N, B4.T): B4.N, (B4.N, B4.F): B4.N, (B4.N, B4.B): B4.N,
    (B4.T, B4.N): B4.N, (B4.T, B4.T): B4.T, (B4.T, B4.F): B4.N, (B4.T, B4.B): B4.T,
    (B4.F, B4.N): B4.N, (B4.F, B4.T): B4.N, (B4.F, B4.F): B4.F, (B4.F, B4.B): B4.F,
    (B4.B, B4.N): B4.N, (B4.B, B4.T): B4.T, (B4.B, B4.F): B4.F, (B4.B, B4.B): B4.B,
}

def frob_tag_bin(t1: B4, t2: B4) -> B4:
    return _MEET[(t1, t2)]

# frobenius_mu_delta_id_tag: frob_tag_bin(t, B) = t  ∀ t
assert all(frob_tag_bin(t, B4.B) == t for t in B4), "Frobenius identity violated"

# ── WasmState ─────────────────────────────────────────────────────────────────

@dataclass
class WasmState:
    stack:                 Stack = field(default_factory=list)
    ip:                    int   = 0
    frob_snapshot:         Stack = field(default_factory=list)
    frob_invariant_holds:  B4    = B4.N
    verified_steps:        int   = 0
    total_steps:           int   = 0

# ── Instructions ──────────────────────────────────────────────────────────────

class WasmInstr(Enum):
    i32_const       = "i32_const"
    i64_const       = "i64_const"
    drop            = "drop"
    select          = "select"
    nop             = "nop"
    unreachable     = "unreachable"
    verify          = "verify"
    checkpoint      = "checkpoint"
    assert_invariant = "assert_invariant"

def exec_one(s: WasmState, instr: WasmInstr, arg: Optional[int] = None) -> WasmState:
    from copy import deepcopy
    s = deepcopy(s)
    s.ip += 1
    s.total_steps += 1

    if instr == WasmInstr.i32_const:
        s.stack.insert(0, TaggedValue(WasmValue(WasmType.i32, arg or 0), B4.T))

    elif instr == WasmInstr.i64_const:
        s.stack.insert(0, TaggedValue(WasmValue(WasmType.i64, arg or 0), B4.T))

    elif instr == WasmInstr.drop:
        if s.stack:
            s.stack.pop(0)

    elif instr == WasmInstr.nop:
        pass

    elif instr == WasmInstr.unreachable:
        s.frob_invariant_holds = B4.F

    elif instr == WasmInstr.checkpoint:
        s.frob_snapshot = list(s.stack)

    elif instr == WasmInstr.verify:
        all_designated = all(tv.designated() for tv in s.stack)
        if all_designated:
            s.frob_invariant_holds = B4.B
            s.verified_steps += 1
        else:
            s.frob_invariant_holds = B4.F

    elif instr == WasmInstr.assert_invariant:
        rhs = B4.F if s.frob_invariant_holds == B4.F else B4.B
        s.frob_invariant_holds = frob_tag_bin(s.frob_invariant_holds, rhs)

    elif instr == WasmInstr.select:
        pass  # requires 3-operand form; no-op in this runtime

    return s

# ── Runtime ───────────────────────────────────────────────────────────────────

class SelfVerifyingWASM:
    def __init__(self):
        self.state = WasmState()
        self.program: list[tuple[WasmInstr, Optional[int]]] = []

    def load(self, program: list[tuple[WasmInstr, Optional[int]]]):
        self.program = program
        self.state = WasmState()

    def step(self) -> bool:
        if self.state.ip >= len(self.program):
            return False
        instr, arg = self.program[self.state.ip]
        self.state = exec_one(self.state, instr, arg)
        return True

    def run(self) -> WasmState:
        while self.step():
            pass
        return self.state

    def snapshot(self) -> str:
        s = self.state
        inv = s.frob_invariant_holds.name
        lines = [
            f"ip={s.ip}  steps={s.total_steps}  verified={s.verified_steps}",
            f"frob_invariant={inv}  snapshot_depth={len(s.frob_snapshot)}",
            f"stack ({len(s.stack)} items):",
        ]
        for tv in s.stack:
            lines.append(f"  {tv.value.ty.value}({tv.value.val}) [{tv.tag.name}]")
        if not s.stack:
            lines.append("  (empty)")
        return "\n".join(lines)

# ── Demo: frobenius_empty_stack theorem as runtime ────────────────────────────
# checkpoint + i32_const n + verify → frob_invariant_holds = B

def demo_frobenius_empty_stack(n: int = 42) -> WasmState:
    runtime = SelfVerifyingWASM()
    runtime.load([
        (WasmInstr.checkpoint, None),
        (WasmInstr.i32_const, n),
        (WasmInstr.verify, None),
    ])
    return runtime.run()

# ── REPL entry point ──────────────────────────────────────────────────────────

def repl():
    import sys
    print("ParaWASM REPL — Belnap-tagged WebAssembly")
    print("Instructions: i32_const <n>  i64_const <n>  drop  nop  unreachable")
    print("              checkpoint  verify  assert_invariant")
    print("Commands: :snap  :reset  :demo  :run  :q")
    print()

    runtime = SelfVerifyingWASM()
    _INSTR_MAP = {i.value: i for i in WasmInstr}

    while True:
        try:
            line = input("ParaWASM> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        if line == ":q":
            break
        if line == ":snap":
            print(runtime.snapshot())
            continue
        if line == ":reset":
            runtime = SelfVerifyingWASM()
            print("reset.")
            continue
        if line == ":demo":
            s = demo_frobenius_empty_stack()
            print(f"checkpoint + i32_const 42 + verify → frob_invariant={s.frob_invariant_holds.name}")
            print("frobenius_empty_stack: OK" if s.frob_invariant_holds == B4.B else "FAIL")
            continue
        if line == ":run":
            runtime.run()
            print(runtime.snapshot())
            continue

        tokens = line.split()
        op_str = tokens[0]
        arg = int(tokens[1]) if len(tokens) > 1 else None
        instr = _INSTR_MAP.get(op_str)
        if instr is None:
            print(f"unknown: {op_str}")
            continue

        runtime.state = exec_one(runtime.state, instr, arg)
        print(runtime.snapshot())


if __name__ == "__main__":
    repl()
