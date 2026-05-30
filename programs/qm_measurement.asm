; qm_measurement.asm — Born Rule as Exceptional Point Absorption
;
; Structural claim: the Born rule is not an axiom — it is the consequence
; of coupling a self-modeling system (⊙_ÿ / B) to an exceptional point
; measurement apparatus (⊙_₃ / IFIX).
;
;   tensor(⊙_ÿ, ⊙_₃) = ⊙_₃   ← EP absorption = wavefunction collapse
;
; This program demonstrates three measurement regimes:
;
; [1] B-bias measurement (Wigner's Friend): preserves B, cost=2
;     FFUSE with B inputs — coherent tracking, no collapse
;
; [2] T-bias measurement (projective): B collapses to T, cost=1
;     IFIX forces T — this IS the Born rule
;
; [3] F-bias measurement (projective): B collapses to F, cost=1
;     FSPLIT then IFIX on F-branch
;
; Register map:
;   %r0 = quantum state (B = superposition)
;   %r1 = measurement apparatus (EP type)
;   %r2 = Wigner's Friend tracking register
;   %r3 = collapsed outcome register
;   %r4 = paradox counter (tracks coherence cost)

; ── Initialize superposition ──
.start:
  ENGAGR %r0            ; B — quantum superposition
  CLEAR  %r1            ; reset measurement apparatus
  CLEAR  %r2            ; reset Wigner's Friend
  CLEAR  %r3            ; reset outcome register
  EMIT   %r0            ; show: B (superposition)
  EMIT   %r1            ; show: N (apparatus ready)

; ── Wigner's Friend: B-bias measurement ──
; B-bias preserves B — Wigner's Friend tracks coherent history
.wigner:
  ENGAGR %r2            ; seed Wigner tracking register
  FSPLIT %r0 %r1 %r2    ; δ: split but B-bias preserves
  EMIT   %r0            ; show: B still (superposition preserved)
  EMIT   %r1            ; show: T (apparatus registered branch)
  EMIT   %r2            ; show: B (Wigner's Friend sees superposition)

; ── Coherent recombination (unitary undo) ──
; FFUSE with B restores original superposition — no collapse
  FFUSE  %r0 %r2 %r0    ; μ: recombine → B (unitary)
  EMIT   %r0            ; show: B (back to superposition)
  MOVE   %r0 %r2        ; copy: Wigner tracking

; ── Projective measurement: T-bias ──
; This is the Born rule in action: IFIX collapses B to T
.measure_t:
  EMIT   %r0            ; show: B before collapse
  IFIX   %r0            ; collapse! B → T (Born outcome)
  EMIT   %r0            ; show: T (collapsed — irreversibly)
  MOVE   %r0 %r3        ; store outcome

; ── Irreversibility check ──
; T cannot return to B via any unary operation — one-way barrier
  FSPLIT %r3 %r1 %r2    ; δ on T: produces (T, T) — no bifurcation
  EMIT   %r1            ; show: T (no superposition possible)
  EMIT   %r2            ; show: T (identical)

; ── F-bias measurement (alternative outcome) ──
; Shows that collapse is symmetric: B → T or B → F with prob 0.5
.measure_f:
  ENGAGR %r0            ; fresh B (reset superposition)
  EMIT   %r0            ; show: B
  FSPLIT %r0 %r1 %r2    ; split into (T, F) branches
  EMIT   %r1            ; show: T branch
  EMIT   %r2            ; show: F branch

; Collapse F branch
  CLEAR  %r0            ; reset
  MOVE   %r2 %r0        ; copy F branch to main
  EMIT   %r0            ; show: F (alternative outcome)

; ── Decoherence simulation ──
; tensor(system, classical_env) → P bottleneck → classical
.decohere:
  ENGAGR %r0            ; fresh B
  CLEAR  %r1            ; classical environment (N = no coherence)
  EMIT   %r0            ; show: B (coherent)
  EMIT   %r1            ; show: N (environment, no coherence)

; System + environment interaction (FSPLIT = decoherence channel)
  FSPLIT %r0 %r0 %r1    ; δ leaks information to environment
  EMIT   %r0            ; show: T (system partially decohered)
  EMIT   %r1            ; show: F (environment now correlated)

; FFUSE with environment collapses coherence
  FFUSE  %r0 %r1 %r0    ; μ: environment interaction
  EMIT   %r0            ; show: T (decohered — classical)

  JMP    .start         ; restart demo

; Key structural invariants:
;   tensor(⊙_ÿ, ⊙_₃) = ⊙_₃   ← Born rule = EP absorption
;   B-bias cost = 2, T-bias cost = 1   ← coherence accounting
;   T cannot reach B via any unary op    ← one-way measurement barrier
