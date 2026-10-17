#!/usr/bin/env python3
"""Exact finite replay for v7.2 rigid C4 relative-gain holonomy compilation."""

from collections import Counter
from itertools import combinations, permutations

S3 = list(permutations(range(3)))
S3_INDEX = {p: i for i, p in enumerate(S3)}
ID = (0, 1, 2)
REPS = {
    0: (0, 1, 0, 1),
    1: (0, 1, 0, 2),
    2: (0, 1, 2, 1),
}
PORT_PAIRS = [(p, q) for p in range(4) for q in range(4)]
V71_BUNDLES = {
    (0, 1): [(0, 0), (1, 1), (3, 2), (0, 3)],
    (1, 2): [(0, 0), (1, 0), (2, 3), (3, 3)],
    (0, 2): [(1, 1), (2, 1), (2, 2), (3, 2)],
}
EXPECTED_BUNDLE_COUNTS = {1: 16, 2: 120, 3: 528, 4: 1428, 5: 2304, 6: 2040, 7: 816, 8: 90}
EXPECTED_RIGID_COUNTS = {1: 0, 2: 0, 3: 64, 4: 576, 5: 1728, 6: 1856, 7: 800, 8: 88}
EXPECTED_GAIN_SIZES = {
    1: {4},
    2: {2, 3, 4},
    3: {1, 2, 3, 4},
    4: {1, 2, 3, 4},
    5: {1, 2, 3},
    6: {1, 2, 3},
    7: {1, 2, 3},
    8: {1, 2, 3},
}


def compose(p, q):
    """Function composition p o q."""
    return tuple(p[q[x]] for x in range(3))


def inverse(p):
    inv = [None] * 3
    for x, y in enumerate(p):
        inv[y] = x
    return tuple(inv)


def allowed_gain_indices(ta, tb, bundle):
    out = []
    for hi, h in enumerate(S3):
        if all(h[REPS[ta][p]] != REPS[tb][q] for p, q in bundle):
            out.append(hi)
    return tuple(out)


def valid_hamiltonian_bundle(bundle):
    left = Counter(p for p, _ in bundle)
    right = Counter(q for _, q in bundle)
    return max(left.values(), default=0) <= 2 and max(right.values(), default=0) <= 2


def is_orbit_rigid(bundle):
    nonempty = []
    for ta in range(3):
        for tb in range(3):
            gains = allowed_gain_indices(ta, tb, bundle)
            if gains:
                nonempty.append(gains)
    return bool(nonempty) and all(len(gains) == 1 for gains in nonempty)


def replay_local_catalog():
    bundle_counts = {}
    rigid_counts = {}
    gain_sizes = {}
    for r in range(1, 9):
        total = 0
        rigid = 0
        sizes = set()
        for bundle in combinations(PORT_PAIRS, r):
            if not valid_hamiltonian_bundle(bundle):
                continue
            total += 1
            every_nonempty_singleton = True
            saw_nonempty = False
            for ta in range(3):
                for tb in range(3):
                    gains = allowed_gain_indices(ta, tb, bundle)
                    if gains:
                        saw_nonempty = True
                        sizes.add(len(gains))
                        if len(gains) != 1:
                            every_nonempty_singleton = False
            if saw_nonempty and every_nonempty_singleton:
                rigid += 1
        bundle_counts[r] = total
        rigid_counts[r] = rigid
        gain_sizes[r] = sizes
    assert bundle_counts == EXPECTED_BUNDLE_COUNTS
    assert rigid_counts == EXPECTED_RIGID_COUNTS
    assert gain_sizes == EXPECTED_GAIN_SIZES
    return bundle_counts, rigid_counts, gain_sizes


def replay_v71_holonomy():
    # All accepted orbit pairs of each v7.1 pair bundle must carry one unique relative gain.
    for bundle in V71_BUNDLES.values():
        assert is_orbit_rigid(bundle)

    tau = (1, 1, 0)
    h01 = allowed_gain_indices(tau[0], tau[1], V71_BUNDLES[(0, 1)])
    h12 = allowed_gain_indices(tau[1], tau[2], V71_BUNDLES[(1, 2)])
    h02 = allowed_gain_indices(tau[0], tau[2], V71_BUNDLES[(0, 2)])
    assert h01 == (2,)
    assert h12 == (5,)
    assert h02 == (4,)

    # With h_ij = g_j^{-1} o g_i, path 0->1->2 induces h_02 = h_12 o h_01.
    path_gain = compose(S3[h12[0]], S3[h01[0]])
    assert S3_INDEX[path_gain] == 3
    assert path_gain != S3[h02[0]]

    # Replay spanning-tree gauge propagation explicitly.
    g0 = ID
    g1 = compose(g0, inverse(S3[h01[0]]))
    g2 = compose(g1, inverse(S3[h12[0]]))
    induced_h02 = compose(inverse(g2), g0)
    assert induced_h02 == path_gain
    assert induced_h02 != S3[h02[0]]

    return {
        "h01": h01[0],
        "h12": h12[0],
        "h02_direct": h02[0],
        "h02_tree_path": S3_INDEX[path_gain],
    }


def main():
    counts, rigid, sizes = replay_local_catalog()
    holonomy = replay_v71_holonomy()

    print("PASS: exhaustive Hamiltonian-port bundle catalog reproduced")
    print("PASS: bundle counts", counts)
    print("PASS: orbit-rigid counts", rigid)
    print("PASS: nonempty relative-gain sizes", {r: sorted(v) for r, v in sizes.items()})
    print("PASS: v7.1 three pair bundles are orbit-rigid")
    print("PASS: v7.1 tau=(1,1,0) holonomy mismatch", holonomy)
    print("VERDICT: RIGID_RELATIVE_GAINS_ELIMINATE_TO_FUNDAMENTAL_HOLONOMY")
    print("FIREWALL: orbit-label search and non-rigid bundles remain open")
    print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
