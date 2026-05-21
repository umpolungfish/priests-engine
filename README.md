# priests-engine

A paraconsistent computer. It runs programs that sustain contradiction permanently and proves they cannot collapse.

Built on Belnap's four-valued logic (B₄ = {N, T, F, B}). The machine has a full assembly language, an interactive REPL, and an indefinitely-running demonstration that has logged over 25 billion paradox firings. The core invariants are formally verified in Lean 4: `run_B3` (B-state permanent for all n) and `run_paradox` (paradox count = 4n exactly).

---

## Install

```
uv pip install -e .
```

Requires Python ≥ 3.11. No dependencies.

---

## Usage

### Interactive REPL

```
para-repl
```

Type ParaASM instructions directly. Non-control-flow ops execute immediately and show changed registers. Control-flow ops and labels accumulate into a program buffer.

```
ParaASM> ENGAGR %r0
  r0: B  paradoxes=1
ParaASM> FSPLIT %r0 %r1 %r2
  r1: B  paradoxes=2
  r2: B  paradoxes=2
ParaASM> FFUSE %r1 %r2 %r0
  r0: B  paradoxes=5
```

REPL commands:

```
:step [N]       step N instructions (default 1)
:run  [N]       run N steps (default until HALT)
:load <file>    load a .asm file
:save <file>    save current program buffer
:reset          clear all registers and program
:regs           show active registers
:prog           show program buffer
:snap           full VM snapshot
:help           command reference
:q              quit
```

### Frobenius loop

```
para-loop
```

Runs the 3-instruction Frobenius kernel indefinitely with live display. Ctrl+C for final summary.

```
ENGAGR %r0          ; seed Both on root register
FSPLIT %r0 %r1 %r2  ; delta: two B-children
FFUSE  %r1 %r2 %r0  ; mu:   fold back into root
JMP    .loop
```

All three registers stabilize at B permanently. Paradox count grows without bound at exactly 4 per cycle.

---

## Programs

```
:load programs/frob_loop.asm    Frobenius loop (mu o delta = id invariant)
:load programs/ifix_stable.asm  IFIX stability demo (T v B = B, Theorem 3 Case B)
:load programs/probe.asm        interactive belief probe — routes N/T/F/B through different paths
```

---

## ISA

```
ENGAGR  %rN              seed Both on register N
FSPLIT  %src %d1 %d2     delta: copy src belief into d1 and d2
FFUSE   %s1  %s2 %dst    mu:    Belnap join s1 v s2 -> dst
IFIX    %rN              collapse to T, mark FIXED
MOVE    %src %dst        copy register
CLEAR   %rN              reset to N (Neither)

JMP     .label           unconditional jump
JB/JT/JF/JN  %rN .label  branch on belief value
CALL    .label           push PC, jump
RET                      pop and return
HALT                     stop

PUSH    %rN              push belief to data stack
POP     %rN              pop belief from data stack
EMIT    %rN              print register state
READ    %rN              read belief from user
```

Belnap join: N < T, F < B. T v F = B. B v x = B for all x.  
Programs with `JMP .loop` at the end run indefinitely via circular PC wrap.

---

## Theorems

**Theorem 1 (B permanence).** Once a register reaches B it never leaves B under FSPLIT or FFUSE. ENGAGR forces B regardless of prior state.

**Theorem 2 (Linear paradox growth).** For the Frobenius kernel, paradox count P(n) = 4n exactly. Each cycle contributes 1 from ENGAGR and 3 from FSPLIT (one per register at B).

**Theorem 3 (IFIX stability).** IFIX cannot collapse the Frobenius loop. Two independent reasons:

- Case A: FSPLIT's `engage()` ignores the `is_fixed` marker — fixity does not propagate through delta.
- Case B: T v B = B in the Belnap join — FFUSE absorbs T into B at the information order.

**Frobenius identity.** mu o delta = id on all four Belnap values. The round-trip FSPLIT→FFUSE is the identity map.

---

## Formal verification

All invariants are proven in Lean 4 in `~/MillenniumAnkh/Imscribing/Paraconsistent/`:

```
run_B3        : ∀ n, (run initialState n).r0 = B ∧ .r1 = B ∧ .r2 = B
run_paradox   : ∀ n, (run initialState n).paradoxCount = 4 * n
frobenius_invariant : (ffuse ∘ fsplit).1 = id
kernel_is_O_inf     : imscriptionTier = O_inf
```

The 25+ billion paradox firings logged by `para-loop` are the empirical instance of `run_paradox`. The formal proof covers all n.

---

## License

Public domain — [UNLICENSE](UNLICENSE).
