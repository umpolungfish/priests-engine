"""
para_qm_fix.py — Fixed meet/join/tensor for StructuralType

Provides corrected meet, join, and tensor_product operations
on StructuralType with proper imports from para_qm.

Usage:
    from para_qm_fix import meet, join, tensor_product
"""
from para_qm import StructuralType, ordinal


def _lesser(p1: str, p2: str, cat: str) -> str:
    """Helper: return the lesser primitive value on the ordinal scale."""
    return p1 if ordinal(p1, cat) <= ordinal(p2, cat) else p2


def _greater(p1: str, p2: str, cat: str) -> str:
    """Helper: return the greater primitive value on the ordinal scale."""
    return p1 if ordinal(p1, cat) >= ordinal(p2, cat) else p2


def meet(st1: StructuralType, st2: StructuralType) -> StructuralType:
    """Greatest lower bound (shared structural floor).

    Takes the lesser of each primitive value on the ordinal scale.
    meet(O_∞, Hilbert) = quantum-like type (no Frobenius, no self-modeling)
    """
    cats = ['D','T','R','P','F','K','G','Gamma','Phi','H','S','Omega']
    prims1 = st1.to_tuple()
    prims2 = st2.to_tuple()
    vals = [_lesser(p1, p2, c) for p1, p2, c in zip(prims1, prims2, cats)]
    return StructuralType(*vals)


def join(st1: StructuralType, st2: StructuralType) -> StructuralType:
    """Least upper bound (minimal ceiling containing both).

    Takes the greater of each primitive value.
    join(O_∞, Hilbert) = O_∞ (Hilbert is a proper subset)
    """
    cats = ['D','T','R','P','F','K','G','Gamma','Phi','H','S','Omega']
    prims1 = st1.to_tuple()
    prims2 = st2.to_tuple()
    vals = [_greater(p1, p2, c) for p1, p2, c in zip(prims1, prims2, cats)]
    return StructuralType(*vals)


def tensor_product(st1: StructuralType, st2: StructuralType) -> StructuralType:
    """Composite type: max on union primitives, min on P and F.

    The composite of two systems takes the union of their structural
    capacities — except for P (parity/symmetry) and F (fidelity),
    which are bottlenecks: the composite is limited by the weaker.
    """
    def tensor_combine(p1: str, p2: str, cat: str) -> str:
        if cat == 'P':  # bottleneck: weaker symmetry limits both
            return _lesser(p1, p2, cat)
        if cat == 'F':  # bottleneck: weaker fidelity limits coherence
            return _lesser(p1, p2, cat)
        if cat == 'Phi':  # ⊙_3 absorption rule
            # If either is EP, composite is EP
            if p1 == 'φ̂_3' or p2 == 'φ̂_3':
                return 'φ̂_3'
            # If both are self-modeling, preserve
            if p1 == 'φ̂_ÿ' and p2 == 'φ̂_ÿ':
                return 'φ̂_ÿ'
            # Otherwise take the weakest
            return _lesser(p1, p2, cat)
        return _greater(p1, p2, cat)  # union

    cats = ['D','T','R','P','F','K','G','Gamma','Phi','H','S','Omega']
    prims1 = st1.to_tuple()
    prims2 = st2.to_tuple()
    vals = [tensor_combine(p1, p2, c) for p1, p2, c in zip(prims1, prims2, cats)]
    return StructuralType(*vals)
