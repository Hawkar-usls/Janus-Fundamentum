#!/usr/bin/env python3
"""R5 E72: exact E12 multi-field rank firewall controls.

Checks the local E12 gadget quotient over F2 and F3 and the resulting
global nullity formulas for square cubic source matrices R:

    d2(T) = 2q + 2 d2(R)
    d3(T) = 3q + d3(R) + c(R)

where T is the 17q x 17q E12 target and c(R) is the number of connected
components of the bipartite incidence graph of R.

Together with E17's rational identity dQ(T)=2q+2dQ(R), these formulas
show that the E12 hardness bridge remains linearly deep in the
dQ/r2/r3 middle band.
"""

from fractions import Fraction


def rank_mod(M, p):
    A = [[int(x) % p for x in row] for row in M]
    m = len(A)
    n = len(A[0]) if m else 0
    r = 0
    for col in range(n):
        pivot = next((i for i in range(r, m) if A[i][col] % p), None)
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        inv = pow(A[r][col], -1, p)
        A[r] = [(x * inv) % p for x in A[r]]
        for i in range(m):
            if i != r and A[i][col]:
                f = A[i][col]
                A[i] = [(A[i][j] - f * A[r][j]) % p for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def rref_mod(M, p):
    A = [[int(x) % p for x in row] for row in M]
    m = len(A)
    n = len(A[0]) if m else 0
    pivots = []
    r = 0
    for col in range(n):
        pivot = next((i for i in range(r, m) if A[i][col] % p), None)
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        inv = pow(A[r][col], -1, p)
        A[r] = [(x * inv) % p for x in A[r]]
        for i in range(m):
            if i != r and A[i][col]:
                f = A[i][col]
                A[i] = [(A[i][j] - f * A[r][j]) % p for j in range(n)]
        pivots.append(col)
        r += 1
        if r == m:
            break
    return A, pivots


def nullspace_mod(M, p):
    R, pivots = rref_mod(M, p)
    n = len(R[0]) if R else 0
    free = [j for j in range(n) if j not in pivots]
    basis = []
    for f in free:
        v = [0] * n
        v[f] = 1
        for i, pc in enumerate(pivots):
            v[pc] = (-R[i][f]) % p
        basis.append(v)
    return basis


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


NAMES = [
    "L1","L2","L3","L4","L5",
    "P1","P2","P3","P4","P5",
    "D1","D2","D3","D4","D5","D6","D7",
]
IDX = {name: i for i, name in enumerate(NAMES)}


def eq(*names):
    row = [0] * 17
    for name in names:
        row[IDX[name]] += 1
    return row


def local_internal_matrix():
    return [
        eq("L1","L4","D3"),
        eq("L2","L4","D1"),
        eq("L3","L4","D2"),
        eq("L1","L5","D2"),
        eq("L2","L5","D3"),
        eq("L3","L5","D1"),
        eq("P1","P4","D6"),
        eq("P2","P4","D4"),
        eq("P3","P4","D5"),
        eq("P1","P5","D5"),
        eq("P2","P5","D6"),
        eq("P3","P5","D4"),
        eq("D1","D6","D7"),
        eq("D2","D4","D7"),
        eq("D3","D5","D7"),
    ]


PORTS = [IDX[x] for x in ("L1","L2","L3","P1","P2","P3")]


def projection_rank(basis, p):
    if not basis:
        return 0
    M = [[v[i] for v in basis] for i in PORTS]
    return rank_mod(M, p)


def check_local():
    M = local_internal_matrix()

    K2 = nullspace_mod(M, 2)
    assert rank_mod(M, 2) == 13
    assert len(K2) == 4
    assert projection_rank(K2, 2) == 2
    assert len(K2) - projection_rank(K2, 2) == 2
    for v in K2:
        l1,l2,l3,p1,p2,p3 = [v[i] for i in PORTS]
        assert l1 == l2 == l3
        assert p1 == p2 == p3

    K3 = nullspace_mod(M, 3)
    assert rank_mod(M, 3) == 12
    assert len(K3) == 5
    assert projection_rank(K3, 3) == 3
    assert len(K3) - projection_rank(K3, 3) == 2
    for v in K3:
        l1,l2,l3,p1,p2,p3 = [v[i] for i in PORTS]
        assert (l1 + l2 + l3) % 3 == 0
        t = (p1 + l1) % 3
        assert (p2 + l2) % 3 == t
        assert (p3 + l3) % 3 == t

    return {
        "F2": (13, 4, 2, 2),
        "F3": (12, 5, 3, 2),
    }


def source_matrix(q, source_sets):
    R = [[0] * q for _ in range(q)]
    for j, C in enumerate(source_sets):
        assert len(C) == 3
        for e in C:
            R[e][j] = 1
    return R


def frozen_q6():
    q = 6
    sets = [tuple(sorted({i, (i + 1) % q, (i + 3) % q})) for i in range(q)]
    return q, sets


def fano_q7(rotated=False):
    q = 7
    base = []
    for j in range(q):
        C = [(j + d) % q for d in (0,1,3)]
        if rotated:
            C = [C[1], C[2], C[0]]
        base.append(tuple(C))
    return q, base


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

    elements = sorted(set().union(*target))
    assert len(elements) == 17 * q
    ei = {e:i for i,e in enumerate(elements)}
    B = [[0] * len(target) for _ in elements]
    for j,T in enumerate(target):
        for e in T:
            B[ei[e]][j] = 1
    assert len(B) == 17 * q and len(B[0]) == 17 * q
    return B


def incidence_components(R):
    q = len(R)
    seen = set()
    comps = 0
    for node in [("e",i) for i in range(q)] + [("c",j) for j in range(q)]:
        if node in seen:
            continue
        comps += 1
        seen.add(node)
        stack = [node]
        while stack:
            side,u = stack.pop()
            if side == "e":
                neigh = [("c",j) for j in range(q) if R[u][j]]
            else:
                neigh = [("e",i) for i in range(q) if R[i][u]]
            for v in neigh:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
    return comps


def direct_sum(parts):
    q = sum(len(C) for C in parts)
    out = []
    off = 0
    for C in parts:
        for triple in C:
            out.append(tuple(x + off for x in triple))
        off += len(C)
    assert len(out) == q
    return q, out


def field_profile(q, source_sets):
    R = source_matrix(q, source_sets)
    T = transform_rx(q, source_sets)
    c = incidence_components(R)

    r2R = rank_mod(R, 2)
    r3R = rank_mod(R, 3)
    d2R = q - r2R
    d3R = q - r3R

    r2T = rank_mod(T, 2)
    r3T = rank_mod(T, 3)
    d2T = 17*q - r2T
    d3T = 17*q - r3T

    assert d2T == 2*q + 2*d2R
    assert d3T == 3*q + d3R + c
    assert r2T == 13*q + 2*r2R
    assert r3T == 13*q + r3R - c
    assert r2T >= 13*q
    assert r3T >= 12*q

    return {
        "q": q, "c": c,
        "r2R": r2R, "d2R": d2R, "r3R": r3R, "d3R": d3R,
        "r2T": r2T, "d2T": d2T, "r3T": r3T, "d3T": d3T,
    }


def main():
    check_local()

    q6, C6 = frozen_q6()
    f6 = field_profile(q6, C6)
    T6 = transform_rx(q6, C6)
    R6 = source_matrix(q6, C6)
    dQR = q6 - rank_q(R6)
    dQT = 17*q6 - rank_q(T6)
    assert dQT == 2*q6 + 2*dQR == 12
    assert f6["d2T"] == 12
    assert f6["d3T"] == 20

    q7, C7 = fano_q7(False)
    f7 = field_profile(q7, C7)
    q7r, C7r = fano_q7(True)
    f7r = field_profile(q7r, C7r)
    assert f7["d3T"] == f7r["d3T"] == 23

    q12, C12 = direct_sum([C6, C6])
    f12 = field_profile(q12, C12)
    assert f12["c"] == 2
    assert f12["d2T"] == 24
    assert f12["d3T"] == 40

    print("R5 E72 E12 multi-field rank firewall: PASS")
    print("local F2: internal_rank=13 nullity=4 port_dim=2 gauge_dim=2")
    print("local F3: internal_rank=12 nullity=5 port_dim=3 gauge_dim=2")
    print(
        "F3 port quotient: l1+l2+l3=0 and "
        "p_i=-l_i+t for a common t"
    )
    print("global identities:")
    print("  d2(T)=2q+2*d2(R), r2(T)=13q+2*r2(R)>=13q")
    print("  d3(T)=3q+d3(R)+c, r3(T)=13q+r3(R)-c>=12q")
    print("  E17: dQ(T)=2q+2*dQ(R)>=2q")
    print("frozen q=6:", f6)
    print("Fano q=7:", f7)
    print("disconnected q=12:", f12)
    print("scientific ceiling: P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
