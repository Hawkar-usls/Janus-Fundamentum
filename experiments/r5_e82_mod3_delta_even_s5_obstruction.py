#!/usr/bin/env python3
"""R5 E82: universal mod-3 boundary conservation, delta-evenness, and S5 reduction.

For any ExactOne_3/Equality_3 Tanner cluster, boundary coordinates split into
check-side and variable-side cut incidences.  Every feasible boundary state F
obeys

    |F_var| - |F_check| == -|C|  (mod 3),

because if y is the number of selected internal variable vertices and I is the
number of selected internal Tanner edges, then

    3y = I + |F_var|,
    |C| = I + |F_check|.

Hence two feasible boundary states can never differ in exactly one coordinate.
Any odd delta-matroid contains a pair of feasible sets at Hamming distance one
(minimize an odd symmetric difference and apply symmetric exchange).  Therefore
EVERY exact RXC3 Tanner boundary relation which is a delta-matroid is even.

The same signed mod-3 affine invariant is preserved by twists and delta-matroid
minors.  Bouchet-Duchamp characterize binary delta-matroids by excluded minors
(twists of S1,...,S5).  Direct finite verification shows S1-S4 admit no signed
+/-1 mod-3 invariant, whereas S5 does.  Thus among the five minimal nonbinary
obstructions, only S5 can occur inside an RXC3 exact delta boundary relation.

This checker replays the mod-3 identity on frozen q=6/q=8/q=9 catalogues and
verifies the excluded-minor sign test exactly.  It does not prove that S5 cannot
occur.  P_VS_NP remains OPEN.
"""

from itertools import product

from r5_e77_source_aligned_delta_composition_frontier import (
    Q6_SETS,
    Q9_SETS,
    source_matrix,
    tanner_adj,
    connected_mask,
    boundary_relation,
    symmetric_exchange_failure,
)


Q8_SETS = [tuple(sorted({j, (j+1) % 8, (j+3) % 8})) for j in range(8)]


def check_boundary_count(A, mask):
    q = len(A)
    C = [i for i in range(q) if (mask >> i) & 1]
    V = [j for j in range(q) if (mask >> (q+j)) & 1]
    internal_edges = sum(A[i][j] for i in C for j in V)
    return 3*len(C) - internal_edges, len(C)


def assert_mod3_identity_on_all_connected(A):
    q = len(A)
    adj = tanner_adj(A)
    delta_count = 0
    for mask in range(1, 1 << (2*q)):
        if not connected_mask(mask, adj):
            continue
        arity, family, _edges, _a, _b = boundary_relation(A, mask)
        if not family:
            continue
        check_bdry, check_vertices = check_boundary_count(A, mask)
        check_mask = (1 << check_bdry) - 1
        for F in family:
            fc = (F & check_mask).bit_count()
            fv = (F >> check_bdry).bit_count()
            assert (fv - fc + check_vertices) % 3 == 0

        if symmetric_exchange_failure(family, arity) is None:
            delta_count += 1
            # Universal theorem consequence: every delta boundary family is even.
            parities = {F.bit_count() & 1 for F in family}
            assert len(parities) == 1
            # Stronger local consequence used in the proof: no distance-one pair.
            fam = set(family)
            for F in fam:
                for e in range(arity):
                    assert (F ^ (1 << e)) not in fam
    return delta_count


def fam(n, subsets):
    out = set()
    for S in subsets:
        m = 0
        for i in S:
            m |= 1 << i
        out.add(m)
    return n, frozenset(out)


S1 = fam(3, [(), (0,1), (0,2), (1,2), (0,1,2)])
S2 = fam(3, [(), (0,), (1,), (2,), (0,1), (0,2), (1,2)])
S3 = fam(3, [(), (1,), (2,), (0,1), (0,2), (0,1,2)])
S4 = fam(4, [(), (0,1), (0,2), (0,3), (1,2), (1,3), (2,3)])
S5 = fam(4, [(), (0,1), (0,3), (1,2), (2,3), (0,1,2,3)])


def signed_mod3_invariants(item):
    n, F = item
    out = []
    for signs in product((1, -1), repeat=n):
        values = {
            sum(signs[i] for i in range(n) if (X >> i) & 1) % 3
            for X in F
        }
        if len(values) == 1:
            out.append((signs, next(iter(values))))
    return out


def verify_excluded_minor_filter():
    inv = [signed_mod3_invariants(S) for S in (S1,S2,S3,S4,S5)]
    assert inv[0] == []
    assert inv[1] == []
    assert inv[2] == []
    assert inv[3] == []
    assert set(inv[4]) == {
        ((1,-1,1,-1), 0),
        ((-1,1,-1,1), 0),
    }
    return inv


def main():
    d6 = assert_mod3_identity_on_all_connected(source_matrix(6, Q6_SETS))
    d8 = assert_mod3_identity_on_all_connected(source_matrix(8, Q8_SETS))
    d9 = assert_mod3_identity_on_all_connected(source_matrix(9, Q9_SETS))
    assert (d6,d8,d9) == (99,200,412)

    inv = verify_excluded_minor_filter()

    print("R5 E82 mod3 delta-even / S5 obstruction reduction: PASS")
    print("exact catalogues replayed: q6=99 q8=200 q9=412 delta interfaces")
    print("universal identity: |F_var|-|F_check| == -|C| (mod 3)")
    print("theorem: exact RXC3 boundary + symmetric exchange => EVEN delta-matroid")
    print("Bouchet-Duchamp signed-mod3 filter: S1-S4 impossible; only S5 survives")
    print("S5 sign invariants=", inv[4])
    print("next representation killer-test: realize or exclude an S5 twist/minor in an exact RXC3 delta interface")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
