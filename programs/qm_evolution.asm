; qm_evolution.asm — Quantum Mechanics on Belnap FOUR
;
; Demonstrates the structural QM-to-Belnap bridge:
;   [1] B = quantum superposition (both |0⟩ and |1⟩)
;   [2] FSPLIT B → (T, F) = wavefunction splitting into branches
;   [3] FFUSE (T, F) → B = coherent recombination (unitary evolution)
;   [4] IFIX = measurement collapse (project onto T)
;
; The Frobenius identity μ∘δ=id IS unitary evolution in structural form.
;
; Register map:
;   %r0 = quantum state (B = superposition, T = spin-up, F = spin-down)
;   %r1 = branch 1 (T-branch)
;   %r2 = branch 2 (F-branch)
;   %r3 = measurement apparatus
;   %r4 = Wigner's Friend register (coherent tracking)

; ── Initialize: create superposition ──
.loop:
  ENGAGR %r0            ; seed B — quantum superposition of |0⟩ and |1⟩
  EMIT  %r0             ; print system state: should be B

; ── Unitary evolution step (Frobenius kernel) ──
; FSPLIT = δ = copy + bifurcation: B → (T, F) distinct branches
  FSPLIT %r0 %r1 %r2   ; δ: split superposition into (T, F) branches
  EMIT  %r1             ; print branch 1 (T)
  EMIT  %r2             ; print branch 2 (F)

; Branch 1: |0⟩ precesses
  ENGAGR %r1            ; refresh: keeps B in branch (Wigner rotation)
  EMIT  %r1

; Branch 2: |1⟩ precesses
  ENGAGR %r2            ; refresh: keeps B in other branch
  EMIT  %r2

; FFUSE = μ = join: recombine T ∨ F = B
  FFUSE  %r1 %r2 %r0    ; μ: coherent recombination — back to B
  EMIT  %r0             ; print: should be B (unitary preserved)

; ── Measurement branch (optional) ──
; IFIX collapses to T (measurement outcome)
; Uncomment the lines below to see measurement:
; IFIX   %r0             ; collapse superposition to T
; EMIT  %r0             ; print collapsed state

; ── Tensor product demo (entanglement) ──
; Copy state to register 4 (second qubit)
  MOVE   %r0 %r4        ; copy state — tensor product |ψ⟩⊗|ψ⟩
  EMIT  %r4             ; print second qubit

; Wigner's Friend: FFUSE preserves B (coherent tracking)
  FFUSE  %r4 %r0 %r3    ; join both qubits → maximally entangled Bell state
  EMIT  %r3             ; print: should be B (maximally entangled)

  JMP    .loop          ; repeat — indefinite unitary evolution
