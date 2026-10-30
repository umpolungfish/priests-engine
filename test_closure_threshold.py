"""Sharp threshold theorem: closure_gcd(N,B) isolates p iff
max_prime_power(ord_p(2)) <= B < max_prime_power(ord_q(2)).
Prediction derived from group theory, matched against the engine."""
import sys
sys.path.insert(0, '/home/mrnob0dy666/imsgct/priests-engine')
from winding_period import closure_gcd

def factor(n):
    f = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f

def max_prime_power(m):
    f = factor(m)
    return max(p ** e for p, e in f.items()) if f else 1

def order_mod(a, p):
    f = factor(p - 1)
    d = p - 1
    for q in f:
        while d % q == 0 and pow(a, d // q, p) == 1:
            d //= q
    return d

primes = [73, 127, 257, 2311, 2521, 2593, 2689, 2731, 2857,
          2971, 3001, 3089, 3121, 3217, 3361, 3433, 3529, 3571]

# sharpen: order threshold vs p-1 smoothness bound
print("--- order-vs-p-1 sharpening (ord threshold is the true closure time) ---")
for p in primes:
    op = order_mod(2, p)
    print(f"p={p}: p-1={p-1}={factor(p-1)}, ord_p(2)={op}, "
          f"T_ord={max_prime_power(op)}, T_p-1={max_prime_power(p-1)}")

fails = tests = 0
for i in range(len(primes)):
    for j in range(i + 1, len(primes)):
        p, q = primes[i], primes[j]
        N = p * q
        Tp = max_prime_power(order_mod(2, p))
        Tq = max_prime_power(order_mod(2, q))
        lo, hi = min(Tp, Tq), max(Tp, Tq)
        Bs = {2}
        for T in (Tp, Tq):
            for d in (-1, 0, 1):
                if T + d >= 2:
                    Bs.add(T + d)
        Bs.add(hi + 1)
        if hi > lo + 2:
            Bs.add((lo + hi) // 2)
        for B in sorted(Bs):
            tests += 1
            g = closure_gcd(N, B)
            if B < lo:
                pred = None
            elif B < hi:
                pred = p if Tp == lo else q
            else:
                pred = None
            if g != pred:
                fails += 1
                print(f"FAIL N={p}*{q} B={B}: got {g} pred {pred} "
                      f"(Tp={Tp} Tq={Tq} ord_p={order_mod(2,p)} ord_q={order_mod(2,q)})")
print(f"\nthreshold corpus: {tests} tests, {fails} fails")
print("THEOREM CONFIRMED" if fails == 0 else "THEOREM REFUTED")
