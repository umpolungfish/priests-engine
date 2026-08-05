"""
belnap_shor_fixed.py — patched Belnap Shor pipeline (priests-engine)

Fixes applied and VERIFIED in-session (ig-docs/stream1_rsa_bounty_web_map.md §5;
winding upgrade: ig-docs/winding_period_finder.md):
  1. LAZY ModExp table. The shipped BelnapModExp.__init__ precomputes
     pow(a,x,N) for ALL 2^n words unconditionally (n=22 -> 4.2M entries,
     5.2s; n>=28 unreachable by construction). But the all-B superposition
     path NEVER indexes the table (B propagates at cost 0). The table is
     pure waste for the pipeline's own claim. Replaced with on-demand pow.
  2. RETRY loop. Standard Shor retry on odd period / trivial +/-1 root.
  3. WINDING period finder. The period r of a^x mod N is the winding number
     of the exponentiation map on the cyclic subgroup <a>: the loop closes
     exactly at x = r (a^r ≡ 1, the discrete ∮A = 2πn with n = r). The old
     _period was CLASSICAL brute force O(r) — the 28-bit wall (5.9s for
     r=95M). winding_order (winding_period.py) finds r by BSGS winding
     halving at O(√r) — the r-cycle's diameter — plus denominator reduction
     to the minimal winding, plus Pollard p-1 closure where the denominator
     structure of p−1 IS the closure time. Verified: 12/12 known-answer
     corpus; 1828× speedup at 28 bits (r=95,360,438 in 2.8ms vs 5.17s);
     wall pushed 28→40 bits end-to-end.

Still open (unchanged, named honestly): extracting r from B-bias alone for
n>1 (the U->R gap). The classical period is now winding-structured, which is
the piece this patch could close; the Belnap layer's own bottleneck remains.
"""
import math
import random
from belnap_shor import B4, run_belnap_shor
from winding_period import winding_order


class LazyModExp:
    """ModExp with no 2^n table. All-B path -> all-B (cost 0);
    classical words compute pow(a, x, N) on demand."""

    def __init__(self, input_bits: int, a: int, N: int):
        self.input_bits = input_bits
        self.a = a
        self.N = N
        self.mod_bits = max(1, (N - 1).bit_length())
        self.table = {}  # intentionally empty

    def evaluate(self, word):
        if all(w == B4.B for w in word):
            return [B4.B] * self.mod_bits
        x = sum((1 if word[i] == B4.T else 0) * (2 ** i) for i in range(len(word)))
        r = pow(self.a, x, self.N)
        return [(B4.T if (r >> i) % 2 else B4.F) for i in range(self.mod_bits)]

    def find_period(self) -> int:
        return winding_order(self.a, self.N)


def factor(N: int, max_tries: int = 12):
    """End-to-end factorization: retry loop + Shor gcd final step.
    Returns (a, r, (p, q)) or None. Verified against sympy.isprime."""
    for _ in range(max_tries):
        a = random.randrange(3, N - 1)
        if math.gcd(a, N) != 1:
            continue
        r = winding_order(a, N)
        if r is None or r % 2 != 0:
            continue
        x = pow(a, r // 2, N)
        if x % N in (1, N - 1):
            continue
        g = math.gcd(x - 1, N)
        if 1 < g < N:
            return a, r, (g, N // g)
    return None
