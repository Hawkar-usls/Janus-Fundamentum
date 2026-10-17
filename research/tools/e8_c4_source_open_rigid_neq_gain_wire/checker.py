#!/usr/bin/env python3
"""Exact replay for v7.7 four-C4 source-open rigid NEQ gain wire."""

from collections import Counter, defaultdict
from itertools import permutations, product

D = range(3)
S3 = list(permutations(D))
PID = {p: i for i, p in enumerate(S3)}
IDENTITY = (0, 1, 2)
ID_INDEX = PID[IDENTITY]
REPS = {
    0: (0, 1, 0, 1),
    1: (0, 1, 0, 2),
    2: (0, 1, 2, 1),
}

# Component IDs: X=0, Y=1, Z=2, W=3.
X, Y, Z, W = 0, 1, 2, 3

FULL_CYCLE = [
    (X,0),(Y,3),(X,3),(Z,1),(W,1),(Z,2),(W,0),(Y,1),
    (X,1),(Z,3),(X,2),(W,3),(Y,0),(W,2),(Z,0),(Y,2),(X,0),
]
CUT_EDGES = {
    frozenset(((Y,1),(X,1))),
    frozenset(((Y,2),(X,0))),
}
EXPECTED_BUNDLES = {
    (X,Y): {(0,3),(3,3)},
    (X,Z): {(1,3),(2,3),(3,1)},
    (X,W): {(2,3)},
    (Y,Z): {(2,0)},
    (Y,W): {(0,2),(0,3),(1,0)},
    (Z,W): {(0,2),(1,1),(2,0),(2,1)},
}
EXPECTED_GY = [
    [None,0,3],
    [5,None,5],
    [1,0,None],
]
EXPECTED_INTERNAL_COUNTS = [
    [0,2,1],
    [1,0,1],
    [1,2,0],
]
EXPECTED_RELATIVE_H = [
    [None,(0,1,2),(2,0,1)],
    [(2,1,0),None,(2,1,0)],
    [(0,2,1),(0,1,2),None],
]


def full_edges():
    return [(FULL_CYCLE[i], FULL_CYCLE[i+1]) for i in range(16)]


def kept_edges():
    return [e for e in full_edges() if frozenset(e) not in CUT_EDGES]


def check_topology():
    assert FULL_CYCLE[0] == FULL_CYCLE[-1]
    assert len(FULL_CYCLE[:-1]) == 16
    assert len(set(FULL_CYCLE[:-1])) == 16
    assert set(FULL_CYCLE[:-1]) == {(c,p) for c in (X,Y,Z,W) for p in range(4)}

    fedges = full_edges()
    assert len(fedges) == 16
    assert len({frozenset(e) for e in fedges}) == 16
    assert CUT_EDGES <= {frozenset(e) for e in fedges}

    kedges = kept_edges()
    assert len(kedges) == 14
    degree = Counter(v for e in kedges for v in e)
    expected_d1 = {(X,0),(X,1),(Y,1),(Y,2)}
    assert {v for v,d in degree.items() if d == 1} == expected_d1
    assert all(degree[v] == 2 for v in set(degree) - expected_d1)
    assert all(degree[(Z,p)] == 2 for p in range(4))
    assert all(degree[(W,p)] == 2 for p in range(4))

    adj = defaultdict(list)
    for u,v in kedges:
        adj[u].append(v)
        adj[v].append(u)
    unseen = set(degree)
    comps = []
    while unseen:
        s = next(iter(unseen))
        unseen.remove(s)
        comp = {s}
        stack = [s]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v in unseen:
                    unseen.remove(v)
                    comp.add(v)
                    stack.append(v)
        comps.append(comp)
    assert sorted(map(len, comps)) == [8,8]
    for comp in comps:
        assert sum(1 for v in comp if degree[v] == 1) == 2
        # Connected + two degree-one vertices + all others degree two => path.
        assert sum(degree[v] for v in comp) == 2 * (len(comp)-1)

    # Re-group the 14 kept edges as oriented intercomponent bundles.
    bundles = defaultdict(set)
    for (c,p),(d,q) in kedges:
        assert c != d
        if c < d:
            bundles[(c,d)].add((p,q))
        else:
            bundles[(d,c)].add((q,p))
    assert dict(bundles) == EXPECTED_BUNDLES

    # Reinserting the two cut edges recovers one simple 16-cycle by construction.
    full_degree = Counter(v for e in fedges for v in e)
    assert len(full_degree) == 16
    assert set(full_degree.values()) == {2}


def vertex_colour(tau, gauge, port):
    return gauge[REPS[tau][port]]


def satisfies_kept_edges(tx, gy_idx, ty, tz, gz_idx, tw, gw_idx):
    gx = IDENTITY
    gy = S3[gy_idx]
    gz = S3[gz_idx]
    gw = S3[gw_idx]
    data = {
        X: (tx,gx),
        Y: (ty,gy),
        Z: (tz,gz),
        W: (tw,gw),
    }
    for (c,p),(d,q) in kept_edges():
        tc,gc = data[c]
        td,gd = data[d]
        if vertex_colour(tc,gc,p) == vertex_colour(td,gd,q):
            return False
    return True


def inverse_perm(p):
    return tuple(p.index(k) for k in D)


def check_boundary_relation():
    allowed_gy = [[None]*3 for _ in D]
    internal_counts = [[0]*3 for _ in D]

    for tx,ty in product(D,D):
        accepted = []
        per_g = []
        for gy_idx in range(6):
            count = 0
            for tz,tw in product(D,D):
                for gz_idx,gw_idx in product(range(6), repeat=2):
                    if satisfies_kept_edges(tx,gy_idx,ty,tz,gz_idx,tw,gw_idx):
                        count += 1
            if count:
                accepted.append(gy_idx)
                per_g.append((gy_idx,count))
        if tx == ty:
            assert accepted == []
            allowed_gy[tx][ty] = None
            internal_counts[tx][ty] = 0
        else:
            assert len(accepted) == 1
            gy_idx,count = per_g[0]
            allowed_gy[tx][ty] = gy_idx
            internal_counts[tx][ty] = count

    assert allowed_gy == EXPECTED_GY
    assert internal_counts == EXPECTED_INTERNAL_COUNTS

    relative_h = [[None]*3 for _ in D]
    for tx,ty in product(D,D):
        gi = allowed_gy[tx][ty]
        if gi is None:
            continue
        # h_XY = g_Y^{-1} g_X and g_X=id.
        relative_h[tx][ty] = inverse_perm(S3[gi])
    assert relative_h == EXPECTED_RELATIVE_H

    # Orbit projection is exactly NEQ_3.
    for tx,ty in product(D,D):
        assert (allowed_gy[tx][ty] is not None) == (tx != ty)


def main():
    check_topology()
    check_boundary_relation()
    print("PASS: parent H is one simple Hamiltonian 16-cycle")
    print("PASS: deleting Y1-X1 and Y2-X0 leaves exactly two 8-vertex H paths")
    print("PASS: hidden Z,W ports are fully H-saturated")
    print("PASS: dangling terminal ports are exactly X0,X1,Y1,Y2")
    print("PASS: terminal orbit projection is exactly NEQ_3")
    print("PASS: every unequal orbit pair forces exactly one relative S3 gain")
    print("PASS: full source-open boundary is rigid, not gauge-transparent")
    print("VERDICT: SOURCE_OPEN_RIGID_NEQ_GAIN_WIRE_CONSTRUCTED")
    print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
