#!/usr/bin/env python3
"""Exact controls for R5 E17.

Dependency-free checks for the R5 E12 hardness gadget:
  * one-gadget internal rank = 13 and local nullity = 4;
  * port projection has dimension 2;
  * projected port relations force L1=L2=L3 and Lp1=Lp2=Lp3;
  * zero-port local kernel has dimension 2;
  * the q=6 RXC3 fixture has det=-9 and source nullity 0;
  * its 102x102 target has rank 90 and nullity 12 = 2q+2d_source.

The symbolic R5 E17 note supplies the general-q proof.
"""

from fractions import Fraction
from itertools import combinations


def rank_q(M):
    A = [[Fraction(x) for x in row] for row in M]
    m = len(A)
    n = len(A[0]) if m else 0
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if A[i][c]), None)
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        z = A[r][c]
        A[r] = [x / z for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def det_q(M):
    A = [[Fraction(x) for x in row] for row in M]
    n = len(A)
    det = Fraction(1)
    for c in range(n):
        pivot = next((i for i in range(c, n) if A[i][c]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != c:
            A[c], A[pivot] = A[pivot], A[c]
            det = -det
        z = A[c][c]
        det *= z
        for i in range(c + 1, n):
            if A[i][c]:
                f = A[i][c] / z
                for j in range(c, n):
                    A[i][j] -= f * A[c][j]
    return det


def rref_q(M):
    A = [[Fraction(x) for x in row] for row in M]
    m = len(A)
    n = len(A[0]) if m else 0
    pivots = []
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if A[i][c]), None)
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        z = A[r][c]
        A[r] = [x / z for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[r][j] for j in range(n)]
        pivots.append(c)
        r += 1
        if r == m:
            break
    return A, pivots


def nullspace_q(M):
    R, pivots = rref_q(M)
    n = len(R[0]) if R else 0
    free = [c for c in range(n) if c not in pivots]
    basis = []
    for f in free:
        v = [Fraction(0)] * n
        v[f] = Fraction(1)
        for rr, p in enumerate(pivots):
            v[p] = -R[rr][f]
        basis.append(v)
    return basis


def gadget():
    boundary = ["x1","x2","x3","p1","p2","p3"]
    z = [f"z{i}" for i in range(1, 7)]
    zp = [f"Z{i}" for i in range(1, 7)]
    t = [f"t{i}" for i in range(1, 4)]
    elements = boundary + z + zp + t

    triples = [
        ("L1", {"x1","z1","z4"}),
        ("L2", {"x2","z2","z5"}),
        ("L3", {"x3","z3","z6"}),
        ("L4", {"z1","z2","z3"}),
        ("L5", {"z4","z5","z6"}),
        ("P1", {"p1","Z1","Z4"}),
        ("P2", {"p2","Z2","Z5"}),
        ("P3", {"p3","Z3","Z6"}),
        ("P4", {"Z1","Z2","Z3"}),
        ("P5", {"Z4","Z5","Z6"}),
        ("D1", {"z2","z6","t1"}),
        ("D2", {"z3","z4","t2"}),
        ("D3", {"z1","z5","t3"}),
        ("D4", {"Z2","Z6","t2"}),
        ("D5", {"Z3","Z4","t3"}),
        ("D6", {"Z1","Z5","t1"}),
        ("D7", {"t1","t2","t3"}),
    ]
    return elements, triples


def incidence(elements, triples):
    ei = {e:i for i,e in enumerate(elements)}
    M = [[0] * len(triples) for _ in elements]
    for j, (_, T) in enumerate(triples):
        for e in T:
            M[ei[e]][j] = 1
    return M


def check_local_quotient():
    elements, triples = gadget()
    J = incidence(elements, triples)
    Jint = J[6:]  # 15 internal element rows
    assert len(Jint) == 15 and len(Jint[0]) == 17
    assert rank_q(Jint) == 13

    K = nullspace_q(Jint)
    assert len(K) == 4

    ports = [0,1,2,5,6,7]  # L1,L2,L3,P1,P2,P3
    projection = [[K[c][p] for c in range(len(K))] for p in ports]
    assert rank_q(projection) == 2

    # Every local kernel vector has equal unprimed and equal primed port triples.
    for v in K:
        assert v[0] == v[1] == v[2]
        assert v[5] == v[6] == v[7]

    # Add zero-port equations: dimension must drop from 4 to exactly 2.
    augmented = [row[:] for row in Jint]
    for p in ports:
        row = [0] * 17
        row[p] = 1
        augmented.append(row)
    assert 17 - rank_q(augmented) == 2

    return 13, 4, 2, 2


def rx_fixture():
    q = 6
    source_sets = [tuple(sorted({i, (i+1)%q, (i+3)%q})) for i in range(q)]
    assert all(len(C) == 3 for C in source_sets)
    return q, source_sets


def source_matrix(q, source_sets):
    R = [[0] * q for _ in range(q)]
    for j, C in enumerate(source_sets):
        for e in C:
            R[e][j] = 1
    return R


def transform_rx(q, source_sets):
    target = []
    x = [f"x:{i}" for i in range(q)]
    xp = [f"xp:{i}" for i in range(q)]

    for j, C in enumerate(source_sets):
        a,b,c = C
        bx = [x[a],x[b],x[c]]
        bxp = [xp[a],xp[b],xp[c]]
        z = [f"g{j}:z{i}" for i in range(1,7)]
        zp = [f"g{j}:Z{i}" for i in range(1,7)]
        t = [f"g{j}:t{i}" for i in range(1,4)]
        target.extend([
            {bx[0],z[0],z[3]}, {bx[1],z[1],z[4]}, {bx[2],z[2],z[5]},
            {z[0],z[1],z[2]}, {z[3],z[4],z[5]},
            {bxp[0],zp[0],zp[3]}, {bxp[1],zp[1],zp[4]}, {bxp[2],zp[2],zp[5]},
            {zp[0],zp[1],zp[2]}, {zp[3],zp[4],zp[5]},
            {z[1],z[5],t[0]}, {z[2],z[3],t[1]}, {z[0],z[4],t[2]},
            {zp[1],zp[5],t[1]}, {zp[2],zp[3],t[2]}, {zp[0],zp[4],t[0]},
            {t[0],t[1],t[2]},
        ])
    return target


def natural_target_matrix(target):
    elements = sorted(set().union(*target))
    ei = {e:i for i,e in enumerate(elements)}
    B = [[0] * len(target) for _ in elements]
    for j,T in enumerate(target):
        for e in T:
            B[ei[e]][j] = 1
    return B


def source_exact_covers(q, source_sets):
    out = []
    for chosen in combinations(range(q), q // 3):
        seen = set()
        ok = True
        for j in chosen:
            C = set(source_sets[j])
            if seen & C:
                ok = False
                break
            seen |= C
        if ok and len(seen) == q:
            out.append(chosen)
    return out


def check_fixture():
    q, source_sets = rx_fixture()
    R = source_matrix(q, source_sets)
    assert rank_q(R) == 6
    assert det_q(R) == -9
    assert source_exact_covers(q, source_sets) == []

    target = transform_rx(q, source_sets)
    B = natural_target_matrix(target)
    assert len(B) == 17*q
    assert len(B[0]) == 17*q
    rank = rank_q(B)
    nullity = len(B[0]) - rank
    assert rank == 90
    assert nullity == 12
    assert nullity == 2*q + 2*(q-rank_q(R))
    return rank, nullity


def main():
    internal_rank, local_nullity, port_rank, gauge_dim = check_local_quotient()
    target_rank, target_nullity = check_fixture()
    print("R5 E17 exact controls: PASS")
    print(
        "one gadget: "
        f"internal_rank={internal_rank}, local_nullity={local_nullity}, "
        f"port_projection_rank={port_rank}, zero_port_gauge_dim={gauge_dim}"
    )
    print("q=6 source: det=-9, rank=6, nullity=0, exact covers=0")
    print(
        f"q=6 target: rank={target_rank}, nullity={target_nullity} "
        "= 2q + 2*d_source"
    )


if __name__ == "__main__":
    main()
