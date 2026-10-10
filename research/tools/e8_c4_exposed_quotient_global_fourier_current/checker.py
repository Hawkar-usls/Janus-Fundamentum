#!/usr/bin/env python3
"""Exact v8.5.2 checker: 18->12 decision quotient + global F3 Fourier-current identity."""

from collections import Counter, defaultdict
from itertools import permutations, product

D = range(3)
S3 = list(permutations(D))
REPS4 = {
    0: (0, 1, 0, 1),
    1: (0, 1, 0, 2),
    2: (0, 1, 2, 1),
}
PI = {0: 1, 1: 0, 2: 2}
H = {
    0: (0, 2, 1),
    1: (0, 2, 1),
    2: (1, 2, 0),
}
FREE = (0, 2, 3)


def comp(p, q):
    return tuple(p[q[i]] for i in D)


def inv(p):
    out = [0, 0, 0]
    for i, v in enumerate(p):
        out[v] = i
    return tuple(out)


def applyg(g, xs):
    return tuple(g[x] for x in xs)


OMEGA18 = [(tau, g) for tau in D for g in S3]


def F18(state):
    tau, g = state
    return (PI[tau], comp(g, inv(H[tau])))


def colors4(state):
    tau, g = state
    return applyg(g, REPS4[tau])


def exposed(state):
    c = colors4(state)
    return tuple(c[p] for p in FREE)


def T(x):
    a, b, c = x
    if a == b:
        return x
    assert len({a, b, c}) == 3
    return (b, c, a)


B = sorted({exposed(s) for s in OMEGA18})
assert len(B) == 12
fibers = defaultdict(list)
for s in OMEGA18:
    fibers[exposed(s)].append(s)
assert Counter(len(v) for v in fibers.values()) == Counter({2: 6, 1: 6})
assert len({F18(s) for s in OMEGA18}) == 18

# Exact compositional quotient conditions.
for s in OMEGA18:
    assert exposed(F18(s)) == T(exposed(s))

pos = {p: i for i, p in enumerate(FREE)}
for a in OMEGA18:
    for b in OMEGA18:
        ca = colors4(F18(a))
        eb = exposed(b)
        ta = T(exposed(a))
        for p in FREE:
            for q in FREE:
                full_pred = ca[p] != colors4(b)[q]
                quot_pred = ta[pos[p]] != eb[pos[q]]
                assert full_pred == quot_pred

# The 12-state graph-of-T wire tensor on six ports.
WIRE6 = [x + T(x) for x in B]
assert len(set(WIRE6)) == 12

# Equivalent affine parameterization used in v8.3/v8.4.
def mod3(x):
    return x % 3


def wire_state(c, s, q):
    # Port order: L0,L2,L3,R0,R2,R3
    return (
        mod3(c + s),
        mod3(c + s * q),
        mod3(c),
        mod3(c + s * q),
        mod3(c - s * (1 + q)),
        mod3(c + s * (q - 1)),
    )

AFFINE_WIRE6 = {
    wire_state(c, s, q)
    for c in range(3)
    for s in (1, 2)
    for q in (1, 2)
}
assert set(WIRE6) == AFFINE_WIRE6

VP = (1, 1, 0, 1, 1, 0)
VM = (1, 2, 0, 2, 0, 1)


def h(t):
    return 2 if t % 3 == 0 else -1


def dot(k, x):
    return sum(a * b for a, b in zip(k, x)) % 3


def dotv(k, v):
    return dot(k, v)


def wire_reduced_amplitude(k):
    return h(dotv(k, VP)) + h(dotv(k, VM))


# Exact cyclotomic Fourier check for the wire tensor.
outside_zero = amp12 = amp3 = ampm6 = 0
for k in product(D, repeat=6):
    sigma = sum(k) % 3
    n = [0, 0, 0]
    for x in WIRE6:
        n[dot(k, x)] += 1
    if sigma != 0:
        assert n == [4, 4, 4]
        outside_zero += 1
        continue
    assert n[1] == n[2]
    exact_amp = n[0] - n[1]
    predicted = 3 * wire_reduced_amplitude(k)
    assert exact_amp == predicted
    lp = dotv(k, VP)
    lm = dotv(k, VM)
    if lp == 0 and lm == 0:
        assert exact_amp == 12
        amp12 += 1
    elif (lp == 0) != (lm == 0):
        assert exact_amp == 3
        amp3 += 1
    else:
        assert exact_amp == -6
        ampm6 += 1
assert (outside_zero, amp12, amp3, ampm6) == (486, 27, 108, 108)

# Exact 2-variable Fourier tensor for NEQ_3:
# \hat N(a,b)=3*delta[a+b=0]*h(a).
for a, b in product(D, repeat=2):
    n = [0, 0, 0]
    for x, y in product(D, repeat=2):
        if x != y:
            n[(a * x + b * y) % 3] += 1
    if (a + b) % 3:
        assert n == [2, 2, 2]
    else:
        assert n[1] == n[2]
        exact_amp = n[0] - n[1]
        assert exact_amp == 3 * h(a)

# Global closed-network identity for two wires joined by all six ports.
# For every permutation pi of the second wire's ports:
#   Z = 3^{-4} * sum_{k: sum k=0} A(k) A(k2) prod_e h(k_e),
# where k2[pi(j)] = -k[j] and A=h(k.v+)+h(k.v-).
def direct_closed_count(pi):
    z = 0
    for x in WIRE6:
        for y in WIRE6:
            if all(x[j] != y[pi[j]] for j in range(6)):
                z += 1
    return z


def dual_closed_count(pi):
    s = 0
    for k in product(D, repeat=6):
        if sum(k) % 3:
            continue
        k2 = [0] * 6
        edge_weight = 1
        for j in range(6):
            k2[pi[j]] = (-k[j]) % 3
            edge_weight *= h(k[j])
        assert sum(k2) % 3 == 0
        s += wire_reduced_amplitude(k) * wire_reduced_amplitude(tuple(k2)) * edge_weight
    assert s % 81 == 0
    return s // 81


count_profile = Counter()
for pi in permutations(range(6)):
    direct = direct_closed_count(pi)
    dual = dual_closed_count(pi)
    assert direct == dual
    count_profile[direct] += 1

assert sum(count_profile.values()) == 720
assert set(count_profile) == {0, 6, 12, 18, 24, 30, 36}

print("PASS: 18 full C4 states quotient exactly to 12 exposed states with fibers 6x2 + 6x1")
print("PASS: F18 descends to T and every exposed-port NEQ predicate is fiber-invariant")
print("PASS: arbitrary compositions of wire maps and exposed-port NEQ splices are decision-liftable 12->18")
print("PASS: exact wire Fourier identity holds on all 3^6=729 frequencies")
print("PASS: exact NEQ_3 Fourier tensor holds on all 3^2=9 dual frequencies")
print("PASS: global two-wire closed Fourier-current contraction matches direct count for all 6!=720 port matchings")
print("DIRECT_COUNT_SUPPORT=0,6,12,18,24,30,36")
print("VERDICT: EXACT_DECISION_QUOTIENT_AND_GLOBAL_F3_CURRENT_CONTRACTION_ESTABLISHED")
print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")
