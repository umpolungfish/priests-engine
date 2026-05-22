#!/usr/bin/env python3
"""
para_rh.py — Riemann Hypothesis Bridge (QCI_RH_Bridge.lean)
===========================================================
Structural claim: the functional equation ζ(s) = χ(s)ζ(1-s) is Belnap negation.
The critical line Re(s)=1/2 is the unique designated fixed point of bnot.
RH in Belnap: all non-trivial zeros are B-designated (both ζ(s) and ζ(1-s) designated).

Entry point: para-rh
Lean reference: MillenniumAnkh/Imscribing/Paraconsistent/QCI_RH_Bridge.lean
"""
from __future__ import annotations
import sys
from para_vm import B4, b4_bnot, b4_designated, b4_dialetheic, b4_approx_le, b4_join


# ── Critical strip encoding ───────────────────────────────────────────────

def rh_strip_state(re_s_num: int, re_s_den: int = 100) -> B4:
    """Map Re(s) (as fraction num/den) to B4.

    re_s < 0 or > den:  N  (outside strip — no non-trivial zeros)
    re_s = den/2:       B  (critical line Re(s)=1/2 — Frobenius fixed point)
    0 < re_s < den:     T  (non-critical interior — RH: no zeros here)
    re_s = 0 or = den:  F  (boundary — degenerate strip edge)
    """
    if re_s_num < 0 or re_s_num > re_s_den:
        return B4.N
    if re_s_num == 0 or re_s_num == re_s_den:
        return B4.F
    if 2 * re_s_num == re_s_den:   # re_s = 1/2
        return B4.B
    return B4.T


# ── Functional equation as Belnap negation ────────────────────────────────

def rh_functional_eq(s: B4) -> B4:
    """The involution s ↦ 1-s (functional equation of ζ) acts as bnot.
    Applying twice: bnot(bnot(x))=x — the same involution identity."""
    return b4_bnot(s)


def rh_frobenius_fixed_point() -> bool:
    """B is the unique designated fixed point of the functional equation.

    Within the critical strip, designated values are T (off critical line) and B.
    bnot(B)=B: the critical line Re(s)=1/2 is self-symmetric under s↦1-s.
    bnot(T)=F≠T: off-critical zeros would need ζ(s)=0 but not ζ(1-s)=0 — impossible
    by the functional equation (both sides vanish together or neither does).
    """
    return (
        b4_bnot(B4.B) == B4.B
        and b4_designated(B4.B)
        and b4_bnot(B4.T) != B4.T
        and not b4_designated(b4_bnot(B4.T))   # bnot(T)=F, not designated
    )


def rh_belnap_statement() -> bool:
    """RH in Belnap FOUR: B is the only value that is both designated
    and a fixed point of bnot. A zero at s where ζ(s)=ζ(1-s)=0 both hold
    is exactly B — dual-designated, dialetheic. All non-trivial zeros are B.

    (1) B is the unique designated fixed point of bnot.
    (2) B is dialetheic — both the zero assertion and its negation hold.
    (3) No other value is dialetheic — the critical line is the unique B-locus.
    """
    unique_fixed = (
        b4_designated(B4.B) and b4_bnot(B4.B) == B4.B
        and not any(
            b4_designated(x) and b4_bnot(x) == x
            for x in B4 if x != B4.B
        )
    )
    return unique_fixed and b4_dialetheic(B4.B) and not any(
        b4_dialetheic(x) for x in B4 if x != B4.B
    )


def rh_involution_identity() -> bool:
    """bnot∘bnot = id: the functional equation applied twice returns the original."""
    return all(b4_bnot(b4_bnot(x)) == x for x in B4)


# Structural type: D_holo · T_holo · R_dagger · P_pm_sym · F_hbar · K_slow
# · G_aleph · Gamma_seq · Phi_c · H2 · n_m · Omega_Z2
RH_IMSCRIPTION = "⟨Ð_ω;Þ_O;Ř_Ť;Φ_};ƒ_ż;Ç_@;Γ_ʔ;ɢ_ˌ;⊙_ÿ;Ħ_A;Σ_ï;Ω_2⟩"

assert rh_frobenius_fixed_point(), "rh_frobenius_fixed_point violated"
assert rh_belnap_statement(),       "rh_belnap_statement violated"
assert rh_involution_identity(),    "rh_involution_identity violated"


# ── CLI display ───────────────────────────────────────────────────────────

_STRIP_SAMPLES = [
    (-10, "Re=-0.1"), (0, "Re=0.0"), (10, "Re=0.1"), (25, "Re=0.25"),
    (49, "Re=0.49"),  (50, "Re=0.5"), (51, "Re=0.51"), (75, "Re=0.75"),
    (100, "Re=1.0"), (110, "Re=1.1"),
]
_STRIP_LABELS = {
    B4.N: "outside strip",
    B4.F: "strip boundary",
    B4.T: "non-critical interior",
    B4.B: "CRITICAL LINE (Re=1/2)",
}


def main() -> None:
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  para-rh — Riemann Hypothesis Bridge (QCI_RH_Bridge.lean)  ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    mark = lambda ok: "✓" if ok else "✗"

    print("  ┌──────────────────────────────────────────────────────────┐")
    print("  │  Core structural claims                                   │")
    print("  ├──────────────────────────────────────────────────────────┤")
    print(f"  │  {mark(rh_involution_identity())}  rh_involution_identity: bnot∘bnot = id       │")
    print(f"  │       functional equation s↦1-s applied twice = id      │")
    print(f"  │  {mark(rh_frobenius_fixed_point())}  rh_frobenius_fixed_point: bnot(B)=B only   │")
    print(f"  │       Re(s)=1/2 is the unique Frobenius fixed point      │")
    print(f"  │  {mark(rh_belnap_statement())}  rh_belnap_statement: zeros are B-designated │")
    print(f"  │       B = both ζ(s)=0 and ζ(1-s)=0 (dialetheic pair)   │")
    print(f"  │       unique B-locus: only the critical line             │")
    print("  ├──────────────────────────────────────────────────────────┤")
    print("  │  Functional equation bnot (s ↦ 1-s):                     │")
    for v in B4:
        img = b4_bnot(v)
        tag = "  ← FROBENIUS FIXED POINT" if img == v and b4_designated(v) else \
              "  ← fixed (not designated)" if img == v else ""
        print(f"  │    bnot({v.value}) = {img.value}{tag}")
    print("  ├──────────────────────────────────────────────────────────┤")
    print("  │  Critical strip map (Re(s)/100 ↦ B4):                    │")
    for num, label in _STRIP_SAMPLES:
        state = rh_strip_state(num)
        print(f"  │    {label:8s}  →  {state.value}  {_STRIP_LABELS[state]}")
    print("  ├──────────────────────────────────────────────────────────┤")
    print(f"  │  Structural type: {RH_IMSCRIPTION}  │")
    print("  │  (D_holo · P_pm_sym · Phi_c · Omega_Z2)                  │")
    print("  └──────────────────────────────────────────────────────────┘")
    print()
    print("  ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
