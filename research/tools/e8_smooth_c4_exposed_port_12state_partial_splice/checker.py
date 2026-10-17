#!/usr/bin/env python3
"""Exact replay for v8.2 exposed-port 12-state quotient and partial-splice catalog."""

from collections import Counter, defaultdict
from itertools import combinations, permutations

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
RHO = {
    0: (0, 0, 1),  # E sector
    1: (0, 1, 2),  # A sector
}
R = (1, 2, 0)


def comp(p, q):
    """p after q."""
    return tuple(p[q[i]] for i in D)


def inv(p):
    out = [0, 0, 0]
    for i, v in enumerate(p):
        out[v] = i
    return tuple(out)


def applyg(g, xs):
    return tuple(g[x] for x in xs)


OMEGA18 = [(tau, g) for tau in D for g in S3]
IDX18 = {s: i for i, s in enumerate(OMEGA18)}


def F18(state):
    tau, g = state
    return (PI[tau], comp(g, inv(H[tau])))


def colors4(state):
    tau, g = state
    return applyg(g, REPS4[tau])


def exposed(state):
    c = colors4(state)
    return tuple(c[p] for p in FREE)


# 1. Exact 18 -> 12 exposed quotient and fiber profile.
B = sorted({exposed(s) for s in OMEGA18})
assert len(B) == 12
assert all(x[0] != x[2] and x[1] != x[2] for x in B)
assert len([x for x in B if x[0] == x[1]]) == 6
assert len([x for x in B if x[0] != x[1]]) == 6

fibers = defaultdict(list)
for s in OMEGA18:
    fibers[exposed(s)].append(s)
assert Counter(len(v) for v in fibers.values()) == Counter({2: 6, 1: 6})
assert all(len(fibers[x]) == (2 if x[0] == x[1] else 1) for x in B)

# 2. F18 descends to a well-defined 12-state T.
def T_formula(x):
    a, b, c = x
    if a == b:
        return x
    assert len({a, b, c}) == 3
    return (b, c, a)

T_from_fiber = {}
for x, lifts in fibers.items():
    images = {exposed(F18(s)) for s in lifts}
    assert len(images) == 1
    y = next(iter(images))
    assert y == T_formula(x)
    T_from_fiber[x] = y
assert set(T_from_fiber.values()) == set(B)

# 3. Unique {E,A} x S3 parameterization and wire action.
B_SG = {}
for sector in (0, 1):
    for g in S3:
        x = applyg(g, RHO[sector])
        assert x in B
        assert x not in B_SG
        B_SG[x] = (sector, g)
assert len(B_SG) == 12

for x in B:
    sector, g = B_SG[x]
    y = T_formula(x)
    sy, gy = B_SG[y]
    assert sy == sector
    expected = g if sector == 0 else comp(g, R)
    assert gy == expected

# T has six fixed E states and two A-sector 3-cycles.
assert sum(T_formula(x) == x for x in B) == 6
for x in B:
    y = x
    for _ in range(3):
        y = T_formula(y)
    assert y == x

BIDX = {x: i for i, x in enumerate(B)}


def rel12(edges):
    """Outer relation x_left -> T(y_right_input) after physical inequalities T(x)[p] != y[q]."""
    out = set()
    pos = {p: i for i, p in enumerate(FREE)}
    for x in B:
        tx = T_formula(x)
        for y in B:
            if all(tx[pos[p]] != y[pos[q]] for p, q in edges):
                out.add((BIDX[x], BIDX[T_formula(y)]))
    return frozenset(out)


def rel18(edges):
    out = set()
    for a0 in OMEGA18:
        a1 = F18(a0)
        ca = colors4(a1)
        for b0 in OMEGA18:
            cb = colors4(b0)
            if all(ca[p] != cb[q] for p, q in edges):
                b1 = F18(b0)
                out.add((IDX18[a0], IDX18[b1]))
    return frozenset(out)


def quotient_sector_gain(rel):
    triples = set()
    for ia, ib in rel:
        x, y = B[ia], B[ib]
        sx, gx = B_SG[x]
        sy, gy = B_SG[y]
        hrel = comp(inv(gy), gx)
        triples.add((sx, sy, hrel))
    return frozenset(triples)


def edge_configs(k):
    for left in combinations(FREE, k):
        for right in combinations(FREE, k):
            for perm_right in permutations(right):
                yield tuple(zip(left, perm_right))


# 4. Every single edge forbids exactly a size-two S3 evaluation coset for each sector pair.
for edges in edge_configs(1):
    q = quotient_sector_gain(rel12(edges))
    assert len(q) == 16
    for sl in (0, 1):
        for sr in (0, 1):
            gains = {h for a, b, h in q if a == sl and b == sr}
            assert len(gains) == 4

# 5. Exhaustive exact catalog of k=1,2,3 physical partial splices.
expected = {
    1: {
        "configs": 9,
        "distinct": 9,
        "pair_counts": Counter({96: 9}),
        "q_counts": Counter({16: 9}),
    },
    2: {
        "configs": 18,
        "distinct": 18,
        "pair_counts": Counter({60: 8, 66: 2, 72: 8}),
        "q_counts": Counter({10: 8, 11: 2, 12: 8}),
    },
    3: {
        "configs": 6,
        "distinct": 6,
        "pair_counts": Counter({42: 4, 54: 2}),
        "q_counts": Counter({7: 4, 9: 2}),
    },
}

catalog = {}
for k in (1, 2, 3):
    by_rel = defaultdict(list)
    configs = list(edge_configs(k))
    for edges in configs:
        r = rel12(edges)
        by_rel[r].append(edges)
        # Global colour action is free on both endpoints, so relation size is 6 times quotient size.
        q = quotient_sector_gain(r)
        assert len(r) == 6 * len(q)
    pair_counts = Counter(len(r) for r in by_rel)
    q_counts = Counter(len(quotient_sector_gain(r)) for r in by_rel)
    assert len(configs) == expected[k]["configs"]
    assert len(by_rel) == expected[k]["distinct"]
    assert pair_counts == expected[k]["pair_counts"]
    assert q_counts == expected[k]["q_counts"]
    catalog[k] = by_rel

# 6. Cross-check the six full-splice matchings against the v8.0 18-state counts.
full_expected_18 = {
    ((0, 0), (2, 2), (3, 3)): 132,
    ((0, 0), (2, 3), (3, 2)): 84,
    ((0, 2), (2, 0), (3, 3)): 132,
    ((0, 2), (2, 3), (3, 0)): 84,
    ((0, 3), (2, 0), (3, 2)): 84,
    ((0, 3), (2, 2), (3, 0)): 84,
}
full_expected_12 = {
    ((0, 0), (2, 2), (3, 3)): 54,
    ((0, 0), (2, 3), (3, 2)): 42,
    ((0, 2), (2, 0), (3, 3)): 54,
    ((0, 2), (2, 3), (3, 0)): 42,
    ((0, 3), (2, 0), (3, 2)): 42,
    ((0, 3), (2, 2), (3, 0)): 42,
}
for edges in edge_configs(3):
    assert len(rel18(edges)) == full_expected_18[edges]
    assert len(rel12(edges)) == full_expected_12[edges]

print("PASS: 18 full C4 states -> 12 exposed states with fiber profile 6x2 + 6x1")
print("PASS: v7.9 wire descends exactly to T(E,g)=(E,g), T(A,g)=(A,g*r), r=(1,2,0)")
print("PASS: one-edge splice catalog: 9 distinct relations, each 96 pairs / 16 sector-gain triples")
print("PASS: two-edge splice catalog: 18 distinct; pair counts 60x8, 66x2, 72x8")
print("PASS: three-edge splice catalog: 6 distinct; pair counts 42x4, 54x2; v8.0 full-state counts replayed")
print("VERDICT: EXACT_12STATE_SECTOR_S3_QUOTIENT_ESTABLISHED; PARTIAL_SPLICE_FRONTIER_REDUCED")
print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")
