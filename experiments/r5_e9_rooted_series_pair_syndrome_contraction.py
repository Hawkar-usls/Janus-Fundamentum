#!/usr/bin/env python3
"""Exact finite regressions for rooted series-pair syndrome contraction.

Controls:
- SAT_12_3 contracts to a constant weighted AG(3,2) core;
- the frozen singular UNSAT 15_3 control has two eight-element series classes,
  one containing the root, forcing rooted cost seven > n/3.

The theorem itself is proved in the companion research note. No finite
regression is promoted to a universal P-vs-NP claim.
"""
from itertools import combinations
import json


def gf2_rank(vecs):
    basis = {}
    for x in vecs:
        y = x
        while y:
            p = y.bit_length() - 1
            if p in basis:
                y ^= basis[p]
            else:
                basis[p] = y
                break
    return len(basis)


def cols_from_supports(n, supports):
    out = []
    for supp in supports:
        v = 0
        for r in supp:
            v |= 1 << r
        out.append(v)
    return out


def cols_from_rows(n, rows):
    out = [0] * n
    for r, row in enumerate(rows):
        for c in row:
            out[c] |= 1 << r
    return out


def is_two_cocircuit(cols, labels, a, b):
    """Rank characterization for a 2-element cocircuit."""
    r = gf2_rank(cols)
    without_pair = [v for v, lab in zip(cols, labels) if lab not in {a, b}]
    if gf2_rank(without_pair) != r - 1:
        return False
    for e in (a, b):
        without_one = [v for v, lab in zip(cols, labels) if lab != e]
        if gf2_rank(without_one) != r:
            return False
    return True


def contract_column(cols, labels, label):
    """Represent M/label by GF(2) row operations then delete pivot row/column."""
    idx = labels.index(label)
    c = cols[idx]
    assert c != 0
    p = (c & -c).bit_length() - 1
    other_ones = [q for q in range(c.bit_length()) if q != p and ((c >> q) & 1)]

    new_cols = []
    new_labels = []
    for j, (v0, lab) in enumerate(zip(cols, labels)):
        if j == idx:
            continue
        v = v0
        if (v >> p) & 1:
            for q in other_ones:
                v ^= 1 << q
        low = v & ((1 << p) - 1)
        high = v >> (p + 1)
        v = low | (high << p)
        new_cols.append(v)
        new_labels.append(lab)
    return new_cols, new_labels


def minimum_root_cost(cols, labels, weights, root):
    ridx = labels.index(root)
    target = cols[ridx]
    others = [(lab, v) for lab, v in zip(labels, cols) if lab != root]
    best = None
    best_set = None
    for mask in range(1 << len(others)):
        syn = 0
        cost = 0
        chosen = []
        for i, (lab, v) in enumerate(others):
            if (mask >> i) & 1:
                syn ^= v
                cost += weights[lab]
                chosen.append(lab)
        if syn == target and (best is None or cost < best):
            best = cost
            best_set = chosen
    return best, best_set


def affine_hyperplane_certificate(cols):
    width = max((v.bit_length() for v in cols), default=0)
    for phi in range(1, 1 << width):
        if all(((phi & v).bit_count() & 1) == 1 for v in cols):
            return phi
    return None


def series_classes(cols, labels):
    adj = {lab: set() for lab in labels}
    for a, b in combinations(labels, 2):
        if is_two_cocircuit(cols, labels, a, b):
            adj[a].add(b)
            adj[b].add(a)
    seen = set()
    classes = []
    for lab in labels:
        if lab in seen or not adj[lab]:
            continue
        stack = [lab]
        comp = set()
        while stack:
            u = stack.pop()
            if u in comp:
                continue
            comp.add(u)
            seen.add(u)
            stack.extend(adj[u] - comp)
        classes.append(sorted(comp))
    return sorted(classes)


def sat12_control():
    supports = [
        (0,1,2),(3,4,5),(6,7,8),(9,10,11),
        (10,1,8),(11,2,3),(3,1,6),(10,4,0),
        (8,4,11),(9,5,6),(2,9,7),(7,5,0),
    ]
    cols = cols_from_supports(12, supports) + [(1 << 12) - 1]
    labels = list(range(13))
    root = 12
    weights = {lab: (0 if lab == root else 1) for lab in labels}

    initial_rank = gf2_rank(cols)
    initial_cost, initial_witness = minimum_root_cost(cols, labels, weights, root)
    assert initial_cost == 4
    assert initial_witness == [0,1,2,3]

    pairs = [(4,6),(8,9),(5,10),(7,11)]
    trace = []
    for a, b in pairs:
        assert is_two_cocircuit(cols, labels, a, b)
        before, _ = minimum_root_cost(cols, labels, weights, root)
        weights[b] += weights[a]
        cols, labels = contract_column(cols, labels, a)
        after, wit = minimum_root_cost(cols, labels, weights, root)
        assert after == before == 4
        trace.append({
            "two_cocircuit": [a,b],
            "contracted": a,
            "aggregated_into": b,
            "root_cost": after,
            "witness_after": wit,
        })

    assert len(cols) == 9
    assert gf2_rank(cols) == 5
    assert is_two_cocircuit(cols, labels, 0, root)

    offset = weights[0]
    cols, labels = contract_column(cols, labels, 0)
    reduced_cost, reduced_witness = minimum_root_cost(cols, labels, weights, root)
    assert offset == 1
    assert reduced_cost == 3
    assert offset + reduced_cost == initial_cost
    assert reduced_witness == [1,2,3]

    assert len(cols) == 8
    assert len(set(cols)) == 8
    assert all(v != 0 for v in cols)
    assert gf2_rank(cols) == 4

    phi = affine_hyperplane_certificate(cols)
    assert phi is not None

    r = gf2_rank(cols)
    n = len(cols)
    min_lambda = None
    for size in range(2, n - 1):
        for S0 in combinations(range(n), size):
            if n - size < 2:
                continue
            S = set(S0)
            X = [cols[i] for i in S]
            Y = [cols[i] for i in range(n) if i not in S]
            lam = gf2_rank(X) + gf2_rank(Y) - r
            min_lambda = lam if min_lambda is None else min(min_lambda, lam)
            assert lam >= 2

    final = {
        "labels": labels,
        "rank": r,
        "columns": cols,
        "weights": [weights[lab] for lab in labels],
        "root": root,
        "affine_hyperplane_phi": phi,
        "minimum_root_cost": reduced_cost,
        "fixed_offset": offset,
        "total_cost": offset + reduced_cost,
        "minimum_root_support": reduced_witness,
        "min_connectivity_lambda_nontrivial": min_lambda,
        "identified_matroid": "AG(3,2)",
    }

    return {
        "initial_rank": initial_rank,
        "initial_root_cost": initial_cost,
        "initial_witness": initial_witness,
        "series_trace": trace,
        "root_series_pair": [0,root],
        "final": final,
    }


def singular15_control():
    rows = [
        (0,5,12),(1,7,9),(2,9,14),(3,10,11),(3,4,13),
        (1,5,10),(6,7,14),(2,3,7),(1,4,8),(0,6,9),
        (2,10,12),(5,11,13),(6,8,12),(0,8,13),(4,11,14),
    ]
    n = 15
    root = 15
    cols = cols_from_rows(n, rows) + [(1 << n) - 1]
    labels = list(range(16))
    weights = {lab: (0 if lab == root else 1) for lab in labels}

    assert gf2_rank(cols) == 14
    classes = series_classes(cols, labels)
    expected = [
        [0,2,3,6,11,12,13,14],
        [1,4,5,7,8,9,10,15],
    ]
    assert classes == expected

    # The root is in the second eight-element series class. By binary
    # circuit-cocircuit parity, every rooted circuit must contain all seven
    # nonroot members. Their XOR is indeed the root syndrome, so cost 7 is
    # attained and is the exact optimum.
    root_class = next(C for C in classes if root in C)
    forced = [e for e in root_class if e != root]
    syn = 0
    for e in forced:
        syn ^= cols[labels.index(e)]
    assert syn == cols[labels.index(root)]
    min_cost, witness = minimum_root_cost(cols, labels, weights, root)
    assert min_cost == 7
    assert witness == forced
    assert n // 3 == 5
    assert min_cost > n // 3

    return {
        "n": n,
        "augmented_rank": 14,
        "series_classes": classes,
        "root_series_class": root_class,
        "forced_root_support": forced,
        "minimum_root_cost": min_cost,
        "exactone_target": n // 3,
        "decision": "UNSAT",
    }


def main():
    out = {
        "status": "PASS_ROOTED_SERIES_PAIR_SYNDROME_CONTRACTION",
        "scientific_ceiling": "FINITE_EXACT_REGRESSIONS__THEOREM_IN_COMPANION_NOTE__NO_D1_PROMOTION__P_VS_NP_OPEN",
        "SAT_12_3": sat12_control(),
        "SINGULAR_UNSAT_15_3": singular15_control(),
        "conclusion": "SAT12 collapses to weighted AG(3,2); singular15 is decided by a root series class",
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
