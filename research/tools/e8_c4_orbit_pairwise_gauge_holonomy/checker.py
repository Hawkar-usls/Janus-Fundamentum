#!/usr/bin/env python3
"""Exact replay for the v7.1 smooth-C4 pairwise gauge-elimination barrier."""

from itertools import permutations, product
from collections import defaultdict

WORD = [0, 1, 2, 1, 0, 2, 0, 2, 0, 1, 2, 1]
REPS = {
    0: (0, 1, 0, 1),
    1: (0, 1, 0, 2),
    2: (0, 1, 2, 1),
}
S3 = list(permutations(range(3)))
EXPECTED = {
    (0, 1): {(0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 1), (2, 2)},
    (1, 2): {(1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)},
    (0, 2): {(1, 0), (1, 1), (1, 2)},
}
FALSE_POSITIVE_TAU = (1, 1, 0)


def occurrence_data():
    occ = defaultdict(list)
    occurrence_index = []
    counts = defaultdict(int)
    for pos, component in enumerate(WORD):
        occurrence_index.append(counts[component])
        counts[component] += 1
        occ[component].append(pos)
    return occ, occurrence_index


def build_graph():
    n = len(WORD)
    occ, _ = occurrence_data()
    h_edges = {tuple(sorted((i, (i + 1) % n))) for i in range(n)}
    f_edges = set()
    for component in range(3):
        vs = occ[component]
        assert len(vs) == 4
        for j in range(4):
            f_edges.add(tuple(sorted((vs[j], vs[(j + 1) % 4]))))
    assert h_edges.isdisjoint(f_edges)
    edges = h_edges | f_edges
    assert len(edges) == 24
    adj = [set() for _ in range(n)]
    for u, v in edges:
        assert u != v
        adj[u].add(v)
        adj[v].add(u)
    assert all(len(a) == 4 for a in adj)
    return edges, h_edges, f_edges, occ


def graph_has_no_three_colouring(edges):
    # Global colour symmetry lets us fix vertex 0 to colour 0.
    for rest in product(range(3), repeat=11):
        colour = (0,) + rest
        if all(colour[u] != colour[v] for u, v in edges):
            return False, colour
    return True, None


def verify_c4_orbit_decomposition():
    proper = {
        c
        for c in product(range(3), repeat=4)
        if all(c[i] != c[(i + 1) % 4] for i in range(4))
    }
    represented = {}
    for tau, rep in REPS.items():
        for gi, g in enumerate(S3):
            c = tuple(g[x] for x in rep)
            assert c not in represented
            represented[c] = (tau, gi)
    assert len(proper) == 18
    assert set(represented) == proper


def port_bundles():
    _, occurrence_index = occurrence_data()
    bundles = defaultdict(list)
    n = len(WORD)
    for i in range(n):
        j = (i + 1) % n
        a, b = WORD[i], WORD[j]
        assert a != b
        p, q = occurrence_index[i], occurrence_index[j]
        if a < b:
            bundles[(a, b)].append((p, q))
        else:
            bundles[(b, a)].append((q, p))
    return dict(bundles)


def pair_relation(edges):
    relation = set()
    for ta in range(3):
        for tb in range(3):
            accepted = False
            for ga in S3:
                for gb in S3:
                    if all(ga[REPS[ta][p]] != gb[REPS[tb][q]] for p, q in edges):
                        accepted = True
                        break
                if accepted:
                    break
            if accepted:
                relation.add((ta, tb))
    return relation


def global_gauge_exists(tau, bundles):
    for gauges in product(S3, repeat=3):
        ok = True
        for (a, b), edges in bundles.items():
            ga, gb = gauges[a], gauges[b]
            if any(ga[REPS[tau[a]][p]] == gb[REPS[tau[b]][q]] for p, q in edges):
                ok = False
                break
        if ok:
            return gauges
    return None


def any_orbit_gauge_colouring(bundles):
    for tau in product(range(3), repeat=3):
        if global_gauge_exists(tau, bundles) is not None:
            return tau
    return None


def symbolic_holonomy_check():
    # For tau=(1,1,0), normalize component 2's alternating colours to c0=0,c1=1,c2=2.
    # The 0--2 bundle forces component-0 colour names (a0,a1,a2)=(c2,c0,c1).
    # The 1--2 bundle forces (b0,b1,b2)=(c2,c1,c0).
    c0, c1, c2 = 0, 1, 2
    a = (c2, c0, c1)
    b = (c2, c1, c0)
    assert a[0] == b[0] == c2
    # Yet R01 contains the port edge (0,0), which requires inequality.
    return a[0] != b[0]


def main():
    edges, h_edges, f_edges, occ = build_graph()
    assert occ == {0: [0, 4, 6, 8], 1: [1, 3, 9, 11], 2: [2, 5, 7, 10]}
    assert len(h_edges) == 12 and len(f_edges) == 12

    verify_c4_orbit_decomposition()

    unsat, witness = graph_has_no_three_colouring(edges)
    assert unsat and witness is None

    bundles = port_bundles()
    assert bundles == {
        (0, 1): [(0, 0), (1, 1), (3, 2), (0, 3)],
        (1, 2): [(0, 0), (1, 0), (2, 3), (3, 3)],
        (0, 2): [(1, 1), (2, 1), (2, 2), (3, 2)],
    }

    relations = {pair: pair_relation(bundle) for pair, bundle in bundles.items()}
    assert relations == EXPECTED

    tau = FALSE_POSITIVE_TAU
    assert (tau[0], tau[1]) in relations[(0, 1)]
    assert (tau[1], tau[2]) in relations[(1, 2)]
    assert (tau[0], tau[2]) in relations[(0, 2)]
    assert global_gauge_exists(tau, bundles) is None
    assert symbolic_holonomy_check() is False

    # Strong cross-check: the orbit/gauge coordinates cover all C4 colourings,
    # and no one of the 27*6^3 exact global states colours the graph.
    assert any_orbit_gauge_colouring(bundles) is None

    print("PASS: smooth C4 control is simple 4-regular Hamiltonian and not 3-colourable")
    print("PASS: 18 proper C4 colourings = 3 orbit labels x 6 S3 gauges")
    print("PASS: exact projected relations sizes R01/R12/R02 = 7/6/3")
    print("PASS: tau=(1,1,0) passes every pair projection but has no global S3 gauges")
    print("VERDICT: PAIRWISE_EXISTENTIAL_S3_GAUGE_ELIMINATION_IS_NOT_EXACT")
    print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
