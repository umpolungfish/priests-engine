#!/usr/bin/env python3
"""
para_category.py — Belnap Lattice as Category (BelnapCategory.lean)
====================================================================
The Belnap FOUR lattice is a category where:
  Objects: N, T, F, B
  Morphisms: the approximation order (approx_le defines unique arrows)
  Terminal object: B (every object has a unique arrow → B)
  Initial object:  N (N has a unique arrow to every object)

Key results (BelnapCategory.lean):
  band_B_idempotent: band(B, B) = B
  B_meet_is_id:      meet(B, x) = x ∀x  (B acts as identity on meet)
  B_join_absorbs:    join(B, x) = B ∀x
  category_is_O_inf

Entry point: para-category
Lean reference: MillenniumAnkh/Imscribing/Paraconsistent/BelnapCategory.lean
"""
from __future__ import annotations
import sys
from para_vm import (
    B4, b4_meet, b4_join, b4_bnot, b4_band, b4_bor,
    b4_designated, b4_dialetheic, b4_approx_le,
    kernel_fsplit, kernel_ffuse,
)


# ── Category structure ────────────────────────────────────────────────────

def category_terminal() -> bool:
    """B is the terminal object: every x has a unique morphism x → B.
    Uniqueness follows from the approximation order being a partial order.
    """
    return all(b4_approx_le(x, B4.B) for x in B4)


def category_initial() -> bool:
    """N is the initial object: there is a unique morphism N → x for every x."""
    return all(b4_approx_le(B4.N, x) for x in B4)


def category_no_other_terminal() -> bool:
    """B is the UNIQUE terminal object (no other x has arrows from all objects)."""
    for candidate in B4:
        if candidate == B4.B:
            continue
        if all(b4_approx_le(x, candidate) for x in B4):
            return False  # another terminal found
    return True


def category_no_other_initial() -> bool:
    """N is the UNIQUE initial object."""
    for candidate in B4:
        if candidate == B4.N:
            continue
        if all(b4_approx_le(candidate, x) for x in B4):
            return False  # another initial found
    return True


# ── Key theorems ──────────────────────────────────────────────────────────

def band_B_idempotent() -> bool:
    """band(B, B) = B: the B-endomorphism is idempotent."""
    return b4_band(B4.B, B4.B) == B4.B


def b_meet_is_id() -> bool:
    """meet(B, x) = x ∀x: B is the identity on the meet operation.
    This is the SIC equiangular projection: B acts as the identity morphism
    on the meet-semilattice (B is the top → meet(top, x) = x always).
    """
    return all(b4_meet(B4.B, x) == x for x in B4)


def b_join_absorbs() -> bool:
    """join(B, x) = B ∀x: B absorbs everything under join."""
    return all(b4_join(B4.B, x) == B4.B for x in B4)


def n_meet_annihilates() -> bool:
    """meet(N, x) = N ∀x: N is the identity on meet from below (annihilator).
    N (initial) acts as the zero morphism on meets.
    """
    return all(b4_meet(B4.N, x) == B4.N for x in B4)


def b_is_dagger_terminal() -> bool:
    """B is self-adjoint (bnot(B)=B): the terminal object equals its own dual.
    In a dagger category, terminal = initial for self-dual objects.
    But B ≠ N, so the dagger structure is non-trivial.
    """
    return b4_bnot(B4.B) == B4.B and b4_bnot(B4.N) == B4.N


def frobenius_as_terminal_morphism() -> bool:
    """μ∘δ(B) = B: the Frobenius condition is the terminal morphism roundtrip.
    δ: B → (T, F) — the comultiplication splits B into its two components.
    μ: (T, F) → B — the multiplication reassembles them.
    The roundtrip δ then μ is the identity on B (Frobenius = id at terminal).
    """
    return kernel_ffuse(*kernel_fsplit(B4.B)[:2])[0] == B4.B


def category_is_O_inf() -> bool:
    """The category structure has Phi_c (B terminal = criticality) and P_pm_sym (Frobenius)."""
    return frobenius_as_terminal_morphism() and b4_bnot(B4.B) == B4.B and b4_designated(B4.B)


assert category_terminal(),              "category_terminal violated"
assert category_initial(),               "category_initial violated"
assert category_no_other_terminal(),     "category_no_other_terminal violated"
assert category_no_other_initial(),      "category_no_other_initial violated"
assert band_B_idempotent(),              "band_B_idempotent violated"
assert b_meet_is_id(),                   "B_meet_is_id violated"
assert b_join_absorbs(),                 "B_join_absorbs violated"
assert n_meet_annihilates(),             "n_meet_annihilates violated"
assert b_is_dagger_terminal(),           "b_is_dagger_terminal violated"
assert frobenius_as_terminal_morphism(), "frobenius_as_terminal_morphism violated"
assert category_is_O_inf(),             "category_is_O_inf violated"


# ── CLI display ───────────────────────────────────────────────────────────

def main() -> None:
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  para-category — Belnap Lattice as Category                ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    mark = lambda ok: "✓" if ok else "✗"

    print("  ┌──────────────────────────────────────────────────────────┐")
    print("  │  Category structure (BelnapCategory.lean)                │")
    print("  ├──────────────────────────────────────────────────────────┤")
    print(f"  │  {mark(category_terminal())}  B is terminal: approx_le(x, B) ∀x            │")
    print(f"  │  {mark(category_initial())}  N is initial:  approx_le(N, x) ∀x            │")
    print(f"  │  {mark(category_no_other_terminal())}  B is the unique terminal object               │")
    print(f"  │  {mark(category_no_other_initial())}  N is the unique initial object                │")
    print("  ├──────────────────────────────────────────────────────────┤")
    print("  │  Approximation order (morphism arrows):                  │")
    for src in B4:
        targets = [t for t in B4 if b4_approx_le(src, t)]
        print(f"  │    {src.value} → {', '.join(t.value for t in targets)}")
    print("  ├──────────────────────────────────────────────────────────┤")
    print("  │  Key theorems                                             │")
    print("  ├──────────────────────────────────────────────────────────┤")
    print(f"  │  {mark(band_B_idempotent())}  band_B_idempotent: band(B,B)=B                │")
    print(f"  │  {mark(b_meet_is_id())}  B_meet_is_id: meet(B,x)=x ∀x               │")
    print(f"  │       B is the meet-identity (SIC equiangular projection)│")
    print(f"  │  {mark(b_join_absorbs())}  B_join_absorbs: join(B,x)=B ∀x             │")
    print(f"  │  {mark(n_meet_annihilates())}  N_meet_annihilates: meet(N,x)=N ∀x           │")
    print(f"  │  {mark(b_is_dagger_terminal())}  B self-adjoint (dagger): bnot(B)=B            │")
    print(f"  │  {mark(frobenius_as_terminal_morphism())}  Frobenius = terminal roundtrip: μ∘δ(B)=B    │")
    print(f"  │  {mark(category_is_O_inf())}  category_is_O_inf: Phi_c ∧ P_pm_sym          │")
    print("  └──────────────────────────────────────────────────────────┘")
    print()
    print("  ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
