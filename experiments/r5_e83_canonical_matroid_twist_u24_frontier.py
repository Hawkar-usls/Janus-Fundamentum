#!/usr/bin/env python3
"""R5 E83: canonical matroid twist theorem + explicit U2,4 frontier.

Universal theorem proved in the companion note:
For ANY exact ExactOne_3/Equality_3 Tanner boundary relation D which is a
Delta-matroid, the signed integer quantity

    phi(F) = |F_var| - |F_check|

is exactly constant over all feasible boundary states F (not merely mod 3).
Consequently, twisting D by the complete set P of variable-side boundary
coordinates makes every feasible set equicardinal:

    |F xor P| = |P| - phi(F).

Since twists preserve the Delta axiom, D*P is a matroid.  Thus every exact RXC3
Delta interface is canonically a twist of a matroid.

The checker replays the theorem on every connected delta interface in frozen
q=6, q=8 and q=9 controls.  It also gives an explicit connected 6x6 NONLINEAR
Tanner cluster whose four-coordinate boundary relation is S5 (up to twist), and
whose canonical variable-boundary twist is U_{2,4}.  This shows the remaining
U2,4 obstruction is real for general Tanner clusters and that source linearity
is essential if one wants to exclude it.

P_VS_NP remains OPEN.
"""

from itertools import combinations

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


def boundary_side_counts(A, mask):
    q = len(A)
    C = [i for i in range(q) if (mask >> i) & 1]
    V = [j for j in range(q) if (mask >> (q+j)) & 1]
    internal = sum(A[i][j] for i in C for j in V)
    check_boundary = 3*len(C) - internal
    var_boundary = 3*len(V) - internal
    return check_boundary, var_boundary


def basis_exchange_failure(family, n):
    F = set(family)
    if not F:
        return ("empty",)
    sizes = {x.bit_count() for x in F}
    if len(sizes) != 1:
        return ("not_equicardinal", tuple(sorted(sizes)))
    for X in F:
        for Y in F:
            xonly = X & ~Y
            yonly = Y & ~X
            for e in range(n):
                if not ((xonly >> e) & 1):
                    continue
                if not any(
                    (yonly >> f) & 1 and (X ^ (1 << e) ^ (1 << f)) in F
                    for f in range(n)
                ):
                    return X,Y,e
    return None


def verify_all_delta_interfaces(A, expected_count):
    q = len(A)
    adj = tanner_adj(A)
    count = 0
    for mask in range(1, 1 << (2*q)):
        if not connected_mask(mask, adj):
            continue
        arity, family, _edges, _a, _b = boundary_relation(A, mask)
        if not family or symmetric_exchange_failure(family, arity) is not None:
            continue
        count += 1
        c_boundary, v_boundary = boundary_side_counts(A, mask)
        assert c_boundary + v_boundary == arity
        var_mask = ((1 << v_boundary) - 1) << c_boundary

        phi = {
            (F & var_mask).bit_count() - (F & ((1 << c_boundary)-1)).bit_count()
            for F in family
        }
        assert len(phi) == 1

        twisted = {F ^ var_mask for F in family}
        assert len({X.bit_count() for X in twisted}) == 1
        assert basis_exchange_failure(twisted, arity) is None

    assert count == expected_count
    return count


def generic_boundary_relation(a,b,edges):
    c_nei = [[] for _ in range(a)]
    v_nei = [[] for _ in range(b)]
    for i,j in edges:
        c_nei[i].append(j)
        v_nei[j].append(i)

    pos = 0
    cb=[]
    vb=[]
    for i in range(a):
        cb.append(tuple(range(pos, pos+3-len(c_nei[i]))))
        pos += 3-len(c_nei[i])
    check_boundary = pos
    for j in range(b):
        vb.append(tuple(range(pos, pos+3-len(v_nei[j]))))
        pos += 3-len(v_nei[j])

    family=set()
    for ymask in range(1 << b):
        base=0
        for j in range(b):
            if (ymask >> j) & 1:
                for p in vb[j]:
                    base |= 1 << p
        partial=[base]
        feasible=True
        for i in range(a):
            s=sum((ymask >> j) & 1 for j in c_nei[i])
            if s > 1:
                feasible=False
                break
            if s == 1:
                continue
            if not cb[i]:
                feasible=False
                break
            partial=[z | (1 << p) for z in partial for p in cb[i]]
        if feasible:
            family.update(partial)
    return pos, check_boundary, family


def verify_explicit_s5_witness():
    # Connected 6+6 Tanner cluster with 16 internal edges and four boundary
    # stubs.  It deliberately contains Tanner C4s, so it is OUTSIDE the
    # square-cubic-linear source class.
    edges = {
        (0,1),(0,3),(0,4),
        (1,0),(1,2),(1,5),
        (2,0),(2,4),
        (3,1),(3,3),(3,4),
        (4,1),(4,5),
        (5,0),(5,2),(5,5),
    }
    arity, check_boundary, family = generic_boundary_relation(6,6,edges)
    assert arity == 4 and check_boundary == 2
    assert family == {0,5,6,9,10,15}
    assert symmetric_exchange_failure(family,4) is None

    # Variable-side boundary coordinates are bits 2 and 3.
    var_mask = 12
    twisted = {F ^ var_mask for F in family}
    all_two_subsets = {
        (1 << i) | (1 << j)
        for i,j in combinations(range(4),2)
    }
    assert twisted == all_two_subsets
    assert basis_exchange_failure(twisted,4) is None

    # U_{2,4} is the unique excluded minor for binary matroids.
    assert len(twisted) == 6
    assert {x.bit_count() for x in twisted} == {2}

    # Explicit source-linearity violation: several variable pairs share two
    # included checks, hence Tanner C4s occur.
    shared=[]
    for u,v in combinations(range(6),2):
        common=[i for i in range(6) if (i,u) in edges and (i,v) in edges]
        if len(common) >= 2:
            shared.append((u,v,tuple(common)))
    assert shared
    return shared


def main():
    q6 = verify_all_delta_interfaces(source_matrix(6,Q6_SETS), 99)
    q8 = verify_all_delta_interfaces(source_matrix(8,Q8_SETS), 200)
    q9 = verify_all_delta_interfaces(source_matrix(9,Q9_SETS), 412)
    shared = verify_explicit_s5_witness()

    print("R5 E83 canonical matroid twist / U2,4 frontier: PASS")
    print("exact delta interfaces replayed: q6=99 q8=200 q9=412")
    print("universal theorem replay: phi(F)=|F_var|-|F_check| is exactly constant")
    print("canonical twist by all variable-boundary coordinates is equicardinal and satisfies matroid basis exchange")
    print("explicit general-Tanner witness: S5 boundary -> canonical U2,4 matroid")
    print("witness violates source linearity via Tanner C4s:", shared)
    print("remaining linear-source representation question: can canonical boundary matroid have a U2,4 minor under C4-free RXC3 geometry?")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
