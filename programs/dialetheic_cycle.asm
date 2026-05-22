; dialetheic_cycle.asm
; Demonstrates the dialetheic cycle from DialetheicAlignment.lean:
;   only B is dialetheic (designated ∧ ¬-designated simultaneously).
;   The cycle T→B→T is the Frobenius loop; F→B→F is the dual.
;
; Register layout:
;   %r0  — probe value (cycles through N T F B)
;   %r1  — designated flag (T if designated, F otherwise)
;   %r2  — dialetheic flag (B iff %r0 is dialetheic, N otherwise)
;   %r3  — loop counter (FFUSE accumulates)

; Init
    CLEAR %r0
    CLEAR %r1
    CLEAR %r2
    CLEAR %r3
    IFIX %r1       ; %r1 = T (will be overwritten, just marks "classical probe start")

; --- probe N ---
.probe_N:
    CLEAR %r0
    EMIT %r0       ; print N
    CLEAR %r2      ; not dialetheic
    EMIT %r2
    FFUSE %r3 %r3 %r3  ; accumulate N (join with self = N)

; --- probe T ---
.probe_T:
    IFIX %r0       ; %r0 = T
    EMIT %r0
    CLEAR %r2
    EMIT %r2

; --- probe F ---
.probe_F:
    ENGAGR %r4     ; %r4 = B (will FSPLIT to get F? No — use IFIX + FFUSE trick)
    ; F cannot be directly set via IFIX (which gives T). Use: FSPLIT B → T,F,B via pair.
    ; Practical approach: the VM's FSPLIT %r0 %r5 %r6 sets all three to B.
    ; Real F requires reading from stdin or classical complement.
    ; We signal "F probe" symbolically: ENGAGR %r0, then T-bias annotation comment.
    CLEAR %r2
    EMIT %r2

; --- probe B: the dialetheic value ---
.probe_B:
    ENGAGR %r0     ; %r0 = B (superposition, both T and F)
    EMIT %r0       ; print B
    ENGAGR %r2     ; %r2 = B (dialetheic flag — B is dialetheic)
    EMIT %r2       ; print B

; Frobenius loop: δ then μ = identity (Frobenius identity μ∘δ=id)
.frob_loop:
    FSPLIT %r0 %r5 %r6  ; δ: co-multiply r0 → (r5, r6), all B
    FFUSE %r5 %r6 %r0   ; μ: join r5,r6 → r0 (B∨B = B, identity confirmed)
    JB %r0 .frob_done
    JMP .frob_loop

.frob_done:
    EMIT %r0       ; still B: Frobenius identity holds
    HALT
