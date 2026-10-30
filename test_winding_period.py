"""
test_winding_period.py — verification of the winding-based period finder.

Tests:
  1. Known-answer corpus (stream1_rsa_bounty_web_map.md §5.2-5.4): 12 exact
     (N, a, r) triples from the shipped engine's own suite.
  2. Brute-force vs winding at the 28-bit wall (record: r=95,360,438, 5.872s).
  3. Wall push: random semiprimes at 32/36/40 bits, self-verified (closure +
     minimality).
  4. closure_gcd: p-1 smoothness winding closure (Pollard p-1).
"""
from winding_period import winding_order, minimal_winding, closure_gcd
from math import gcd
import random, time
import sympy


def brute_period(a, N):
    cur = 1 % N
    for r in range(1, N + 1):
        cur = cur * a % N
        if cur == 1:
            return r
    return None


ok = True

# 1. Known-answer corpus
corpus = [
    (15, 7, 4), (21, 5, 6), (35, 2, 12), (143, 79, 10), (899, 53, 210),
    (2537, 1721, 58), (12319, 8563, 336), (44503, 11239, 2204),
    (156263, 74959, 25908), (622121, 3407, 77568),
    (1666633, 240041, 832010), (2556751, 1581311, 106398),
]
print("=== 1. KNOWN-ANSWER CORPUS ===")
for N, a, expect in corpus:
    t0 = time.perf_counter()
    r = winding_order(a, N)
    dt = time.perf_counter() - t0
    good = r == expect
    ok &= good
    print(f"N={N:9d} a={a:9d} expect {expect:9d} got {r} {dt*1000:8.1f}ms {'OK' if good else 'FAIL'}")

# 2. Brute vs winding at the 28-bit wall
print("\n=== 2. BRUTE vs WINDING at 28 bits (record: r=95,360,438 took 5.872s) ===")
N28 = 190748629
best = (0, None)
for cand in range(2, 200):
    if gcd(cand, N28) == 1:
        r = winding_order(cand, N28)
        if r and r > best[0]:
            best = (r, cand)
r28, a28 = best
print(f"N={N28} a={a28} r={r28}")
t0 = time.perf_counter()
rb = brute_period(a28, N28)
tb = time.perf_counter() - t0
t0 = time.perf_counter()
rw = winding_order(a28, N28)
tw = time.perf_counter() - t0
print(f"brute:  r={rb} {tb:.3f}s")
print(f"winding(BSGS): r={rw} {tw*1000:.1f}ms")
print(f"speedup: {tb/tw:.0f}x   match: {rb == rw}")
ok &= (rb == rw)

# 3. Wall push
print("\n=== 3. WALL PUSH (32/36/40 bits) ===")
for bits in (32, 36, 40):
    while True:
        p = sympy.randprime(2 ** (bits // 2 - 1), 2 ** (bits // 2))
        q = sympy.randprime(2 ** (bits // 2 - 1), 2 ** (bits // 2))
        N = p * q
        a = random.randrange(2, N)
        if gcd(a, N) == 1:
            break
    t0 = time.perf_counter()
    r = winding_order(a, N)
    dt = time.perf_counter() - t0
    closes = pow(a, r, N) == 1
    minimal = minimal_winding(a, N, r) == r
    good = closes and minimal
    ok &= good
    print(f"N~{N.bit_length()} bits  r={r} ({r.bit_length()} bits)  {dt:.2f}s  "
          f"closes={closes} minimal={minimal} {'OK' if good else 'FAIL'}")

# 4. closure_gcd — p-1 smoothness winding closure
print("\n=== 4. closure_gcd (p-1 smoothness) ===")
# p = 2311, p-1 = 2310 = 2·3·5·7·11  (11-smooth; factors 7,11 above the B=6 bound)
p = 2311
assert sympy.isprime(p), "2311 must be prime"
pm1 = p - 1
q2 = sympy.nextprime(10**9 + 1)
N = p * q2
g = closure_gcd(N, 11)
print(f"p={p}  p-1={pm1} = {sympy.factorint(pm1)}")
print(f"q={q2}  N={N}")
print(f"closure B=11 -> {g}   {'OK' if g == p else 'FAIL'}")
g2 = closure_gcd(N, 6)
print(f"closure B=6  -> {g2}   {'OK (None: 7,11 in p-1 not ≤6)' if g2 is None else 'FAIL'}")
ok &= (g == p and g2 is None)

print("\nOVERALL:", "PASS" if ok else "FAIL")
