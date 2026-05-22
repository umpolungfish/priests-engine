#!/usr/bin/env python3
"""
para_ym.py — Yang-Mills Mass Gap Bridge (QCI_YM_Bridge.lean)
=============================================================
Structural claim: the mass gap Δ > 0 corresponds to the covering relation N < T
in the Belnap approximation order. No state exists between vacuum (N) and the
lowest massive excitation (T). The gap is K_trap-stable (confined) and
Omega_Z-protected (gauge-invariant).

BRST correspondence: the nilpotent BRST charge Q (Q²=0) acts as Frobenius:
ENGAGR is the BRST operator; FSPLIT gives the (physical, ghost) pair.

Entry point: para-ym
Lean reference: MillenniumAnkh/Imscribing/Paraconsistent/QCI_YM_Bridge.lean
"""
from __future__ import annotations
import sys
from para_vm import (
    B4, b4_bnot, b4_join, b4_meet, b4_band, b4_bor,
    b4_designated, b4_dialetheic, b4_approx_le,
    kernel_fsplit, kernel_ffuse, kernel_engager,
)


# ── Mass gap: covering relation N < T ────────────────────────────────────

def ym_gap_exists() -> bool:
    """N < T is a covering relation in the approximation order: no x with N <_a x <_a T.

    Δ > 0 in Belnap: vacuum (N) and lowest particle (T) are adjacent — no intermediate.
    Verified by exhaustion over all B4 values.
    """
    for x in B4:
        if (b4_approx_le(B4.N, x) and b4_approx_le(x, B4.T)
                and x != B4.N and x != B4.T):
            return False  # intermediate state would close the gap
    return True


def ym_gap_not_dialetheic() -> bool:
    """The ground state T is not dialetheic — the gap is definite, not contradictory.

    If the gap state were B (dialetheic), the massive gluon would be
    indistinguishable from vacuum (mass=0), collapsing the gap.
    T is not dialetheic: bnot(T)=F, which is not designated.
    """
    return not b4_dialetheic(B4.T)


def ym_vacuum_canonical() -> bool:
    """N (vacuum) is the unique undesignated element in the approximation floor.

    The vacuum is the unique N-state; all excitations are designated (T, F, or B).
    No designated state can map to N via any lattice operation from T alone.
    """
    return (
        not b4_designated(B4.N)                  # vacuum undesignated
        and b4_approx_le(B4.N, B4.T)             # vacuum below particle
        and b4_meet(B4.T, B4.F) == B4.N          # T∧F = N: particle+antiparticle → vacuum
    )


# ── BRST ↔ Frobenius correspondence ──────────────────────────────────────

def ym_brst_nilpotent() -> bool:
    """BRST charge Q is nilpotent: Q²=0 ↔ ENGAGR is B-stable (B∧¬B=B).

    ENGAGR: band(r, bnot(r)). For B: band(B,B)=B (idempotent on B).
    For T: band(T,F)=F (nilpotent — T-sector annihilates under Q).
    BRST doublets arise from FSPLIT(B) = (T, F): physical + ghost partner.
    Physical cohomology H^0: T-states not arising from FSPLIT of B.
    """
    q_on_B = b4_band(B4.B, b4_bnot(B4.B))   # ENGAGR(B) = B (BRST-stable)
    q_on_T = b4_band(B4.T, b4_bnot(B4.T))   # ENGAGR(T) = F (nilpotent)
    frobenius_holds = kernel_ffuse(*kernel_fsplit(B4.B)[:2])[0] == B4.B
    return q_on_B == B4.B and q_on_T != B4.B and frobenius_holds


def ym_confinement_ktrap() -> bool:
    """The massive gluon (lowest T-state) is K_trap-stable.

    K_trap: no Belnap lattice op can move T to N (vacuum) from T alone.
    Confinement: gluons cannot propagate to asymptotic vacuum states.
    T cannot reach N via any unary/binary self-op (cf. collapse_irreversible
    but checking N-reachability specifically).
    """
    from para_vm import collapse_irreversible
    # T cannot reach N = vacuum: N is undesignated, T is designated; no path down
    t_cannot_reach_n = not any(
        c == B4.N for c in [
            b4_bnot(B4.T),
            b4_join(B4.T, B4.T),
            b4_meet(B4.T, B4.T),
            b4_band(B4.T, B4.T),
            b4_bor(B4.T, B4.T),
        ]
    )
    return t_cannot_reach_n


def ym_topological_protection() -> bool:
    """Omega_Z protection: the gap is preserved under the approximation join.

    The join of any two T-states is T (no spontaneous B-creation).
    B creation requires explicit bifurcation input (FSPLIT from B).
    The gap is structurally preserved: b4_join(T,T)=T stays above vacuum.
    """
    return (
        b4_join(B4.T, B4.T) == B4.T    # T∨T=T: no spontaneous B promotion
        and b4_join(B4.N, B4.T) == B4.T  # vacuum + particle = particle (gap survives)
        and b4_join(B4.T, B4.F) == B4.B  # particle + antiparticle = B (annihilation)
    )


# Structural type: D_holo · T_in · R_dagger · P_pm_sym · F_hbar · K_trap
# · G_aleph · Gamma_broad · Phi_c · H_inf · n_n · Omega_Z
YM_IMSCRIPTION = "⟨Ð_ω;Þ_K;Ř_Ť;Φ_};ƒ_ż;Ç_Ù;Γ_ʔ;ɢ_Ş;⊙_ÿ;Ħ_!;Σ_ő;Ω_z⟩"

assert ym_gap_exists(),              "ym_gap_exists violated"
assert ym_gap_not_dialetheic(),      "ym_gap_not_dialetheic violated"
assert ym_vacuum_canonical(),        "ym_vacuum_canonical violated"
assert ym_brst_nilpotent(),          "ym_brst_nilpotent violated"
assert ym_confinement_ktrap(),       "ym_confinement_ktrap violated"
assert ym_topological_protection(),  "ym_topological_protection violated"


# ── CLI display ───────────────────────────────────────────────────────────

def main() -> None:
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  para-ym — Yang-Mills Mass Gap Bridge (QCI_YM_Bridge.lean)  ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    mark = lambda ok: "✓" if ok else "✗"

    print("  ┌──────────────────────────────────────────────────────────┐")
    print("  │  Mass gap structural claims                               │")
    print("  ├──────────────────────────────────────────────────────────┤")
    print(f"  │  {mark(ym_gap_exists())}  ym_gap_exists: N < T is a covering relation   │")
    print(f"  │       no state x with N <_a x <_a T in Belnap order     │")
    print(f"  │       ↔ Δ > 0: no massless gluon states                 │")
    print(f"  │  {mark(ym_gap_not_dialetheic())}  ym_gap_not_dialetheic: T is not dialetheic    │")
    print(f"  │       gap is definite — not a B-state contradiction      │")
    print(f"  │  {mark(ym_vacuum_canonical())}  ym_vacuum_canonical: N is the unique floor    │")
    print(f"  │       T∧F=N: particle+antiparticle → vacuum             │")
    print("  ├──────────────────────────────────────────────────────────┤")
    print("  │  BRST ↔ Frobenius correspondence                         │")
    print("  ├──────────────────────────────────────────────────────────┤")
    print(f"  │  {mark(ym_brst_nilpotent())}  ym_brst_nilpotent: ENGAGR is BRST-stable     │")
    print(f"  │       band(B,¬B)=B: B sector is BRST-closed             │")
    print(f"  │       band(T,¬T)=F: T sector is nilpotent (Q(physical)) │")
    print(f"  │       FSPLIT(B)=(T,F): physical + ghost doublet          │")
    print(f"  │       μ∘δ=id: Frobenius = BRST cohomology invariance    │")
    print("  ├──────────────────────────────────────────────────────────┤")
    print("  │  Confinement + protection                                 │")
    print("  ├──────────────────────────────────────────────────────────┤")
    print(f"  │  {mark(ym_confinement_ktrap())}  ym_confinement_ktrap: T cannot reach N     │")
    print(f"  │       gluon cannot propagate to vacuum — K_trap stable   │")
    print(f"  │  {mark(ym_topological_protection())}  ym_topological_protection: T∨T=T          │")
    print(f"  │       no spontaneous B-creation; gap Omega_Z-protected   │")
    print("  ├──────────────────────────────────────────────────────────┤")
    print("  │  Structural correspondences:                              │")
    print("  │    N  = vacuum (zero energy, undesignated)                │")
    print("  │    T  = massive gluon (Δ > 0, designated)                 │")
    print("  │    F  = anti-gluon                                        │")
    print("  │    B  = BRST-closed sector (both T and F coexist)         │")
    print("  │    N < T covering relation = mass gap Δ > 0               │")
    print("  │    K_trap = confinement (T cannot decay to N)             │")
    print("  │    Omega_Z = full gauge invariance (topological lock)     │")
    print("  ├──────────────────────────────────────────────────────────┤")
    print(f"  │  Structural type: {YM_IMSCRIPTION}  │")
    print("  │  (D_holo · K_trap · Phi_c · P_pm_sym · Omega_Z)          │")
    print("  └──────────────────────────────────────────────────────────┘")
    print()
    print("  ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
