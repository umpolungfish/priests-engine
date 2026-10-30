"""
winding_period.py — winding-based period finding for the Belnap Shor pipeline.

Canonical law (ig-docs/unified_mesh_winding_document.md):
    Winding=2π  ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑔𐑠⊙𐑖𐑙𐑭⟩   ∮_γ A = 2πn ∧ n∈ℤ ∧ wind(γ)≠0

The period r of a^x mod N IS the winding number of the exponentiation map
x ↦ a^x on the cyclic subgroup <a>: the loop closes exactly at x = r — the
discrete winding-zero condition a^r ≡ 1 mod N.  "Closure and periodicity are
visible in the denominator": the minimal period is extracted from the group's
denominator structure, never by brute-force iteration of r.

Primitives
----------
winding_order(a, N)   BSGS order finding, O(√r). The r-cycle has diameter ~√r:
                      baby steps walk one radius out, giant steps walk the
                      other back; they meet at the winding midpoint. Replaces
                      the shipped engine's O(r) loop (belnap_shor.py:_period).
minimal_winding(a,N,r) Denominator reduction: r | r'. Strip each prime factor
                      p while a^(r'/p) ≡ 1 still closes — the minimal winding
                      is the denominator left standing.
closure_gcd(N, B)     Pollard p-1 closure: if p−1 is B-smooth, the p-component
                      of the winding closes at M = lcm(1..B) for every a
                      coprime to p while the q-component stays open;
                      gcd(a^M − 1, N) isolates p. The denominator structure of
                      p−1 IS the closure time — no search.
"""
from math import gcd, isqrt, lcm
from functools import reduce


def _closes(a, r, N):
    """Closure test: does the winding close at r?  a^r ≡ 1 mod N."""
    return pow(a, r, N) == 1


def minimal_winding(a, N, r):
    """Reduce a period multiple r to the minimal winding of a mod N."""
    if r <= 1:
        return r
    d = 2
    while d * d <= r:
        while r % d == 0 and _closes(a, r // d, N):
            r //= d
        d += 1 if d == 2 else 2
    return r


def winding_order(a, N):
    """Minimal period r of a^x mod N, O(√r) BSGS winding halving.
    Returns r, or None if a is not in the unit group (gcd(a,N)≠1)."""
    if N <= 1 or gcd(a, N) != 1:
        return None
    if a % N == 1:
        return 1
    m = isqrt(N) + 1                      # diameter of the N-circle
    baby = {}
    cur = 1 % N
    for j in range(m):                    # walk one radius out
        if cur not in baby:
            baby[cur] = j
        cur = cur * a % N
    ainv = pow(a, -1, N)
    g = pow(ainv, m, N)
    cur = 1
    for i in range(1, m + 1):             # walk the other radius back
        cur = cur * g % N                 # a^{-i·m}
        j = baby.get(cur)
        if j is not None:
            r = i * m + j                 # a^{i·m+j} ≡ 1 → r | (i·m+j)
            if r > 0 and _closes(a, r, N):
                return minimal_winding(a, N, r)
    return None


def closure_gcd(N, B):
    """Factor N by winding closure: any p | N with p−1 B-smooth is found."""
    M = reduce(lcm, range(2, B + 1))
    g = gcd(pow(2, M, N) - 1, N)
    return g if 1 < g < N else None


if __name__ == "__main__":
    import sys, time
    a, N = int(sys.argv[1]), int(sys.argv[2])
    t0 = time.perf_counter()
    r = winding_order(a, N)
    print(f"winding_order({a}, {N}) = {r}  ({time.perf_counter()-t0:.3f}s)")
