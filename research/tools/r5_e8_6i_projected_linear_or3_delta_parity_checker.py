#!/usr/bin/env python3
from itertools import product
import json


def rank_mod(a, p):
    if not a:
        return 0
    a = [[x % p for x in row] for row in a]
    m, n = len(a), len(a[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if a[i][c] % p), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        inv = pow(a[r][c], -1, p)
        a[r] = [(x * inv) % p for x in a[r]]
        for i in range(m):
            if i != r and a[i][c] % p:
                f = a[i][c] % p
                a[i] = [(x - f*y) % p for x, y in zip(a[i], a[r])]
        r += 1
    return r


def principal_feasible(A, p):
    n = len(A)
    out = set()
    for mask in range(1 << n):
        I = [i for i in range(n) if (mask >> i) & 1]
        sub = [[A[i][j] for j in I] for i in I]
        if not I or rank_mod(sub, p) == len(I):
            out.add(mask)
    return out


def is_delta(F, n):
    for X in F:
        for Y in F:
            diff = X ^ Y
            for u in range(n):
                if not ((diff >> u) & 1):
                    continue
                ok = False
                for v in range(n):
                    if not ((diff >> v) & 1):
                        continue
                    toggle = (1 << u) if u == v else ((1 << u) | (1 << v))
                    if (X ^ toggle) in F:
                        ok = True
                        break
                if not ok:
                    return False
    return True


def verify():
    # Coordinates: x1,x2,x3,h.
    A = [
        [0, 0, 1, 1],
        [0, 0, 1, 2],
        [2, 2, 0, 1],
        [2, 1, 2, 0],
    ]
    p = 3
    twist = 0b0011
    visible_mask = 0b0111

    F = principal_feasible(A, p)
    expected_source = {
        0b0000,
        0b0101,
        0b0110,
        0b1001,
        0b1010,
        0b1100,
        0b1111,
    }
    assert F == expected_source

    projected = {(S ^ twist) & visible_mask for S in F}
    OR3 = set(range(1, 8))
    assert projected == OR3
    assert is_delta(OR3, 3)

    # Every signed clause is the cube minus one falsifying mask q.
    signed = {}
    for q in range(8):
        shifted = {x ^ q for x in OR3}
        expected = set(range(8)) - {q}
        assert shifted == expected
        signed[q] = sorted(shifted)

    # EQ_d fails symmetric exchange for all tested d>=3; the proof in the
    # theorem is symbolic for arbitrary d.
    eq_checks = {}
    for d in range(3, 9):
        EQ = {0, (1 << d) - 1}
        eq_checks[d] = is_delta(EQ, d)
        assert not eq_checks[d]

    # Two-occurrence truth-table sanity: pair-union means equal bits.
    pair_rows = [(a, b) for a, b in product((0, 1), repeat=2) if a == b]
    assert pair_rows == [(0, 0), (1, 1)]

    return {
        "status": "PASS",
        "field": "GF(3)",
        "source_principal_feasible_masks": sorted(F),
        "visible_relation_after_twist_projection": sorted(projected),
        "visible_relation": "OR3",
        "all_8_signed_clause_twists": "PASS",
        "OR3_is_delta_matroid": True,
        "EQ_d_delta_checks_d_3_through_8": eq_checks,
        "two_occurrence_pair_coherence": "PASS",
        "scientific_ceiling":
            "PROJECTED_LINEAR_CLAUSE_BRIDGE_ONLY__FANOUT_GADGET_OPEN__D1_EMPTY",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
