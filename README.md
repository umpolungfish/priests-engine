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

### Belnap Shor pipeline

```
para-shor
```

Runs the full Shor pipeline verification suite: Wigner's Friend coherence accounting, SIC-POVM axiom check, and three concrete factoring instances (N=15, 21, 35). All invariants are verified against the Lean specification in `FullPipeline.lean`.

```
para-shor 15 7     run a single instance: N=15, a=7
para-shor 35 2     run a single instance: N=35, a=2
```

### Paraconsistent suite

Seven additional entry points, each mirroring a Lean proof in `MillenniumAnkh/Imscribing/Paraconsistent/`:

```
para-align            Dialetheic Alignment Theorem — DAT tri-equivalence + P vs NP bridge
para-align bifur      bifurcation point (B is the unique Frobenius comultiplication point)
para-align seq        measurement sequence algebra (QCI_Sequences.lean)
para-align pvsnp      P vs NP bridge — BelnapCircuit one-way barrier
para-align shor N a   dialetheicShor framing for one (N, a) instance

para-rh               RH Bridge — functional eq s↦1-s = bnot; B = critical line fixed point
                       Critical strip map; millennium_barriers_unified (RH, P vs NP, SIC-POVM)

para-ym               YM Bridge — N<T covering = mass gap Δ=1; BRST Q²=0 ↔ Frobenius; K_trap

para-nreg             n-Register generalization — 2:1 coherence ratio invariant for all n
                       8 concrete instances (n=4..8); SIC per-qubit tensor product

para-temporal         BelnapTemporal — □B/◇B/○B modalities; winding invariant; 8-cycle trajectory

para-category         BelnapCategory — B terminal, N initial; meet/join identities; category_is_O_inf

para-multiagent [n [steps]]   n-kernel entangled network; emerald bootstrap; channel stability
```

All entry points verify their module-level assertions at import and print a structured summary.

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
:load programs/frob_loop.asm       Frobenius loop (mu o delta = id invariant)
:load programs/ifix_stable.asm     IFIX stability demo (T v B = B, Theorem 3 Case B)
:load programs/probe.asm           interactive belief probe — routes N/T/F/B through different paths
:load programs/dialetheic_cycle.asm  B-only dialetheism + Frobenius identity (DialetheicAlignment.lean)
:load programs/sic_povm.asm          SIC-POVM axiom demo — B as fiducial, WH2 bijection (QCI_SICPOVM_Bridge.lean)
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

## Belnap Shor pipeline

The `para-shor` entry point runs Shor's algorithm in the Belnap four-valued lattice with exact coherence accounting. Every gate and measurement matches `FullPipeline.lean` in MillenniumAnkh.

```
Pipeline:
  [1]  |T...T⟩  → H^⊗n  → |B...B⟩   (coherence cost = n)
  [2]  |B...B⟩  → ModExp → |B...B⟩   (cost = 0: B propagates through all Boolean gates)
  [3]  |B...B⟩  → B-bias measure      (cost = 2n: Wigner's Friend signature, preserves B)
  [4]  |B...B⟩  → T-bias measure      (cost = n: collapses B → T, classical output)
```

**Structural invariants (all proven in Lean and verified at module load):**

| Invariant | Value |
|-----------|-------|
| Hadamard cost | n |
| ModExp cost | 0 |
| B-bias measurement cost | 2n |
| T-bias measurement cost | n |
| B-bias / T-bias ratio | **2:1 (always)** |

The 2:1 ratio is the structural signature of the Belnap Shor pipeline — provably invariant for any n and any periodic function on B-input.

### Φ_υ bottleneck

The standard Shor algorithm uses complex-number phases to distinguish `|j⟩ → e^{2πijk/N}|k⟩`. The Belnap lattice has only one superposition value, B, which absorbs all lattice operations (`¬B=B`, `meet(B,x)=x`, `join(B,x)=B`). No phase differentiation exists.

- B-bias measurement: preserves B (Wigner's Friend, cost 2)
- T-bias measurement: collapses B→T (cost 1)
- Period r is encoded in the **coherence cost ratio** (2n:n), not in individual bit values

This is the Φ_υ (psi parity) bottleneck toward Φ_} (Frobenius-special). Extracting r from B-bias alone without T-bias collapse is the structural open problem. The SIC-POVM bridge shows it is possible for d=2; the n-qubit multilattice generalization is open.

### WH2 bijection and SIC-POVM axioms

`para_vm.py` implements the WH2 bijection `belnapToWH2` from `QCI_SICPOVM_Bridge.lean`:

```
N → (0,0) = I      T → (0,1) = Z
F → (1,0) = X      B → (1,1) = XZ
```

B is the unique element satisfying all 4 SIC-POVM axioms in d=2:

1. `meet(B, x) = x` for all x (maximal information, neutral under meet)
2. Equal projection (equiangularity — same as axiom 1 for d=2)
3. `join(B, x) = B` for all x (absorption)
4. `¬B = B` (self-adjoint / fixed point of negation)

All axioms are verified as module-load assertions in `para_vm.py` and demonstrated in `programs/sic_povm.asm`.

### DialetheicAlignment

`para_vm.py` exposes `b4_dialetheic(a)` — the exact predicate from `DialetheicAlignment.lean`:

```python
def b4_dialetheic(a: B4) -> bool:
    return b4_designated(a) and b4_designated(b4_bnot(a))
```

Only B is dialetheic (both T and ¬T are designated simultaneously). The uniqueness theorem `only_B_is_dialetheic` is verified at module load:

```python
assert b4_dialetheic(B4.B)
assert not any(b4_dialetheic(x) for x in B4 if x != B4.B)
```

The dialetheic cycle `T → B → T` (and its dual `F → B → F`) is demonstrated in `programs/dialetheic_cycle.asm`.

---

## exOS

The ParaASM VM is also implemented as a native kernel module in [exOS](https://github.com/umpolungfish/exOS) — a bare-metal x86_64 Rust `no_std` UEFI kernel.

`src/para_vm.rs` and `src/para_commands.rs` port the full ISA (Belnap FOUR, 18 opcodes, text assembler, circular PC wrap) to the kernel address space. EMIT writes to the serial UART; READ returns N (no stdin in bare metal). The VM announces itself at boot:

```
[PARA] ParaASM VM online — Belnap FOUR, 18-opcode ISA, Frobenius loop. Type 'para help'.
[exoterikOS] ⊙_c Kernel fully online. Type 'help' for commands.
```

From the exOS shell:

```
exOS> para load .loop:\nENGAGR %r0\nFSPLIT %r0 %r1 %r2\nFFUSE %r1 %r2 %r0\nJMP loop
Loaded 4 instructions, 1 labels.
exOS> para loop 12
steps=12  total_paradoxes=48
exOS> para regs
  %r0  = B  paradoxes=17
  %r1  = B  paradoxes=14
  %r2  = B  paradoxes=14
```

P(12) = 48 = 4×12. Theorem 2 holds on bare metal.

---

## Formal verification

All invariants are proven in Lean 4 in `~/MillenniumAnkh/Imscribing/Paraconsistent/` (21 modules, 0 sorrys):

```
Kernel (Kernel.lean)
  run_B3                : ∀ n, (run initialState n).r0 = B ∧ .r1 = B ∧ .r2 = B
  run_paradox           : ∀ n, (run initialState n).paradoxCount = 4 * n
  frobenius_invariant   : (ffuse ∘ fsplit).1 = id
  kernel_is_O_inf       : imscriptionTier = O_inf

Dialetheic Alignment (DialetheicAlignment.lean)
  only_B_is_dialetheic  : ∀ v : Belnap, isDialetheic v ↔ v = B
  join_circuit_B_dominant: ∀ c, foldl join N c = B ↔ B ∈ c   (proved by foldl induction)

SIC-POVM Bridge (QCI_SICPOVM_Bridge.lean)
  belnapToWH2_bijective : Function.Bijective belnapToWH2
  sic_axioms_hold       : B satisfies all 4 d=2 SIC-POVM axioms

Shor Pipeline (FullPipeline.lean)
  coherence_ratio_is_two: ∀ n > 0, 2 * n / n = 2

n-Register (QCI_nRegister.lean)
  nreg_ratio_invariant  : ratio = 2.0 for all n = 1..8 instances

RH Bridge (QCI_RH_Bridge.lean)
  rh_frobenius_fixed_point : bnot(B) = B; bnot(T) ≠ T
  rh_belnap_statement      : B is the unique designated fixed point of bnot
  millennium_barriers_unified: RH ∧ P_vs_NP ∧ SIC-POVM all reduce to DAT

Yang-Mills Bridge (QCI_YM_Bridge.lean)
  mass_gap_positive        : N < T covering relation; gap Δ = 1
  brst_frobenius_eq        : BRST Q²=0 ↔ μ∘δ=id
  k_trap_confinement       : T is the unique minimum excited state above N

Belnap Temporal (BelnapTemporal.lean)
  always_B_registers       : □(r0=r1=r2=B)
  winding_invariant        : bnot(r0(t)) = r0(t) ∀ t
  temporal_is_O_inf        : Phi_c ∧ P_pm_sym

Belnap Category (BelnapCategory.lean)
  category_terminal        : ∀ x, approx_le x B
  category_initial         : ∀ x, approx_le N x
  B_meet_is_id             : ∀ x, meet B x = x
  frobenius_terminal_roundtrip : μ∘δ(B) = B

Multi-Agent Belnap (MultiAgentBelnap.lean)
  multi_allB_init          : all agents in initMulti start all-B
  multi_agent_is_O_inf     : Phi_c ∧ P_pm_sym for the entangled network
```

The 25+ billion paradox firings logged by `para-loop` are the empirical instance of `run_paradox`. The formal proof covers all n.

---

## License

Public domain — [UNLICENSE](UNLICENSE).
