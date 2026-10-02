#!/usr/bin/env python3
"""Exact checker for the EQ3-linearized post-SNF/RKPR pair-projection control.

The checker reconstructs the 24-variable cubic source, applies the frozen EQ3
regularizer, verifies the 240-variable linear-cubic output, proves exact
rational rank/nullity by a rational kernel plus a finite-field lower bound,
checks RKPR projective classes, lifts an integer source solution, and replays
the two source pair-lattice relations whose contradiction transfers exactly
to occurrence terminals.
"""

from collections import Counter, defaultdict, deque
from itertools import product
from math import prod

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ


P = [5,18,17,19,16,3,21,10,9,6,23,15,8,14,20,2,1,7,0,13,11,22,12,4]
Q = [16,6,19,10,23,4,2,13,7,17,1,21,22,11,3,12,15,20,5,0,9,8,14,18]
SOURCE_INTEGER_SOLUTION = [
    0,0,0,-1,1,1,1,0,1,0,1,0,0,0,1,1,0,0,0,1,1,0,0,0
]
GADGET = [
    (2,5,6),
    (1,4,7),
    (5,7,9),
    (0,3,7),
    (4,6,9),
    (2,4,8),
    (3,8,9),
    (0,5,8),
    (1,3,6),
]
EXPECTED_SOURCE_PROJECTIVE = {
    frozenset((9,16,18)),
    frozenset((1,17)),
    frozenset((2,11)),
    frozenset((6,15)),
    frozenset((8,14)),
    frozenset((12,21)),
}


def source_matrix():
    n = 24
    A = sp.zeros(n, n)
    for i in range(n):
        for j in (i, P[i], Q[i]):
            A[i, j] = 1
    return A


def rank_mod_p(M, p):
    a = [[int(M[i, j]) % p for j in range(M.cols)] for i in range(M.rows)]
    r = 0
    for c in range(M.cols):
        pivot = next((i for i in range(r, M.rows) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        inv = pow(a[r][c], -1, p)
        for j in range(c, M.cols):
            a[r][j] = (a[r][j] * inv) % p
        for i in range(r + 1, M.rows):
            f = a[i][c]
            if f:
                for j in range(c, M.cols):
                    a[i][j] = (a[i][j] - f * a[r][j]) % p
        r += 1
        if r == M.rows:
            break
    return r


def smith_invariants(M):
    D = smith_normal_form(M, domain=ZZ)
    return [abs(int(D[i, i])) for i in range(min(D.rows, D.cols)) if D[i, i] != 0]


def integer_system_solvable(M, b):
    r = M.rank()
    if M.row_join(b).rank() != r:
        return False
    d = smith_invariants(M)
    da = smith_invariants(M.row_join(b))
    assert len(d) == len(da) == r
    return prod(d) == prod(da)


def pair_relation(A, i, j):
    n = A.cols
    allowed = []
    for a, b in product((0,1), repeat=2):
        ei = [0] * n
        ej = [0] * n
        ei[i] = 1
        ej[j] = 1
        M = A.col_join(sp.Matrix([ei, ej]))
        rhs = sp.Matrix([1] * A.rows + [a, b])
        if integer_system_solvable(M, rhs):
            allowed.append((a, b))
    return allowed


def build_regularized(A):
    n = A.rows
    incident_rows = [[] for _ in range(n)]
    for r in range(n):
        for v in range(n):
            if A[r, v]:
                incident_rows[v].append(r)
    assert all(len(rs) == 3 for rs in incident_rows)

    terminal = {}
    for v, rs in enumerate(incident_rows):
        for t, r in enumerate(sorted(rs)):
            terminal[(r, v)] = 10 * v + t

    rows = []
    # Nine local gadget clauses per source variable.
    for v in range(n):
        for clause in GADGET:
            rows.append(tuple(10 * v + j for j in clause))

    # One retained old clause per source row, on distinct occurrence terminals.
    for r in range(n):
        vs = [v for v in range(n) if A[r, v]]
        assert len(vs) == 3
        rows.append(tuple(terminal[(r, v)] for v in vs))

    N = 10 * n
    assert len(rows) == N
    L = sp.zeros(N, N)
    for r, row in enumerate(rows):
        for c in row:
            L[r, c] = 1
    return L, rows, terminal


def verify_linear_cubic_connected(L, rows):
    N = L.rows
    assert all(sum(int(L[r, c]) for c in range(N)) == 3 for r in range(N))
    assert all(sum(int(L[r, c]) for r in range(N)) == 3 for c in range(N))

    supports = [set(row) for row in rows]
    assert all(len(supports[i] & supports[j]) <= 1
               for i in range(N) for j in range(i))

    adj = [[] for _ in range(2 * N)]
    for r, supp in enumerate(supports):
        for c in supp:
            adj[r].append(N + c)
            adj[N + c].append(r)
    seen = {0}
    q = deque([0])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    assert len(seen) == 2 * N


def normalized_projective_classes(K):
    rows = [tuple(K[i, j] for j in range(K.cols)) for i in range(K.rows)]
    assert all(any(v != 0 for v in row) for row in rows)
    buckets = defaultdict(list)
    for i, row in enumerate(rows):
        first = next(v for v in row if v != 0)
        key = tuple(sp.cancel(v / first) for v in row)
        buckets[key].append(i)
    # This control must have equality only, not merely proportionality.
    for members in buckets.values():
        ref = rows[members[0]]
        assert all(rows[i] == ref for i in members[1:])
    return list(buckets.values())


def output_kernel_from_source(A):
    ns = A.nullspace()
    assert len(ns) == 3
    Ksrc = sp.Matrix.hstack(*ns)
    K = sp.zeros(240, 27)

    # Three source-kernel directions u.
    for v in range(24):
        for j in range(3):
            u = Ksrc[v, j]
            for loc in (0,1,2,9):
                K[10*v + loc, j] = u
            for loc in (3,4,5):
                K[10*v + loc, j] = -u

    # Twenty-four independent private gadget directions w_v.
    for v in range(24):
        col = 3 + v
        for loc in (6,7,8):
            K[10*v + loc, col] = 1
        for loc in (3,4,5):
            K[10*v + loc, col] = -1

    return Ksrc, K


def lifted_integer_solution(q):
    z = [0] * 240
    for v, qv in enumerate(q):
        # r_v = 0: T=q, R=0, S=1-q.
        for loc in (0,1,2,9):
            z[10*v + loc] = qv
        for loc in (3,4,5):
            z[10*v + loc] = 1 - qv
        for loc in (6,7,8):
            z[10*v + loc] = 0
    return sp.Matrix(z)


def verify_gadget_parameterization():
    G = sp.zeros(9, 10)
    for r, clause in enumerate(GADGET):
        for c in clause:
            G[r, c] = 1
    assert G.rank() == 8
    one = sp.ones(9, 1)
    # Two explicit affine directions q and r plus one base point.
    base = sp.Matrix([0,0,0,1,1,1,0,0,0,0])
    dq = sp.Matrix([1,1,1,-1,-1,-1,0,0,0,1])
    dr = sp.Matrix([0,0,0,-1,-1,-1,1,1,1,0])
    assert G * base == one
    assert G * dq == sp.zeros(9,1)
    assert G * dr == sp.zeros(9,1)
    assert sp.Matrix.hstack(dq, dr).rank() == 2
    # rank 8 means nullity 2, so these are the complete affine parameters.


def main():
    A = source_matrix()
    one24 = sp.ones(24, 1)
    assert A.rank() == 21
    assert len(A.nullspace()) == 3
    assert A * sp.Matrix(SOURCE_INTEGER_SOLUTION) == one24

    # Source global lattice membership and strict pair contradiction.
    assert integer_system_solvable(A, one24)
    assert pair_relation(A, 5, 12) == [(1,0)]
    assert pair_relation(A, 3, 5) == [(1,0)]

    Ksrc = sp.Matrix.hstack(*A.nullspace())
    src_classes = normalized_projective_classes(Ksrc)
    src_nontrivial = {frozenset(c) for c in src_classes if len(c) > 1}
    assert src_nontrivial == EXPECTED_SOURCE_PROJECTIVE

    verify_gadget_parameterization()
    L, rows, terminal = build_regularized(A)
    assert L.shape == (240, 240)
    verify_linear_cubic_connected(L, rows)

    # Construct a 27-dimensional rational kernel exactly.
    Ksrc2, K = output_kernel_from_source(A)
    assert Ksrc2 == Ksrc
    assert K.rank() == 27
    assert L * K == sp.zeros(240, 27)

    # A nonzero 213x213 minor modulo 5 gives rank_Q(L) >= 213, while the
    # 27-dimensional rational kernel gives rank_Q(L) <= 213. Hence exact.
    assert rank_mod_p(L, 5) == 213
    exact_rank_q = 213
    exact_nullity_q = 27

    # Exhaustive projective classification on the exact kernel basis.
    classes = normalized_projective_classes(K)
    sizes = Counter(len(c) for c in classes)
    assert sizes == Counter({3: 48, 4: 11, 8: 5, 12: 1})

    # Explicit integer-lattice witness for the 240-variable output.
    z0 = lifted_integer_solution(SOURCE_INTEGER_SOLUTION)
    assert L * z0 == sp.ones(240, 1)

    # Terminal assignment convention is occurrence-dependent for old clauses,
    # but all three local terminals are equal in every rational/integer gadget
    # solution. Local terminal 0 therefore represents source value q_v.
    t5 = 10 * 5
    t12 = 10 * 12
    t3 = 10 * 3
    assert (t5, t12, t3) == (50, 120, 30)

    # Exact transfer theorem: gadget equations force local terminals equal to q_v;
    # retained old clauses impose Aq=1; every integer source q extends using r=0.
    # Therefore the source relations replay verbatim on terminal representatives.
    R_50_120 = pair_relation(A, 5, 12)
    R_30_50 = pair_relation(A, 3, 5)
    assert R_50_120 == [(1,0)]  # forces terminal/source 5 = 1
    assert R_30_50 == [(1,0)]   # second coordinate forces terminal/source 5 = 0

    print("PASS R5_E9_EQ3_LINEARIZED_POST_SNF_RKPR_PAIR_PROJECTION_STRICT_CONTROL")
    print("source: n=24 rank_Q=21 nullity_Q=3 integer-lattice=PASS RKPR=equality-only")
    print("output: n=240 connected=true linear=true cubic=true")
    print(f"output exact rank_Q={exact_rank_q} nullity_Q={exact_nullity_q}")
    print("output RKPR class sizes: 1x12, 5x8, 11x4, 48x3; equality-only")
    print("output integer-lattice=PASS via explicit lifted integer solution")
    print("R_(50,120)={(1,0)} => x50=1")
    print("R_(30,50)={(1,0)}  => x50=0")
    print("pair-projection 2-CSP => UNSAT")
    print("POST_SNF_RKPR_LINEAR_CUBIC_SUFFICIENCY = FALSIFIED")
    print("PAIR2_COMPLETENESS = OPEN")
    print("P_VS_NP=OPEN E8_D1=EMPTY")


if __name__ == "__main__":
    main()
