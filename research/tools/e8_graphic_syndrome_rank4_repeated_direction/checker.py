#!/usr/bin/env python3
from itertools import product

MOD = 3

K4_EDGES = [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
K4_Q = [
    [1,2,0,1,0,0],
    [1,0,2,0,1,0],
    [0,1,2,0,0,1],
]


def rank_mod3(M):
    A = [[x % MOD for x in row] for row in M]
    if not A:
        return 0
    m, n = len(A), len(A[0])
    r = 0
    for c in range(n):
        piv = next((i for i in range(r, m) if A[i][c]), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        inv = 1 if A[r][c] == 1 else 2
        A[r] = [(inv*x) % MOD for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [(A[i][j] - f*A[r][j]) % MOD for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def mat_vec(A, s):
    return tuple(sum(a*x for a, x in zip(row, s)) % MOD for row in A)


def incidence(vertices, edges):
    idx = {v:i for i,v in enumerate(vertices)}
    B = [[0]*len(edges) for _ in vertices]
    for j,(u,v) in enumerate(edges):
        B[idx[u]][j] = 2  # -1
        B[idx[v]][j] = 1
    return B


def check_flow_rows(B, A):
    for row in A:
        for brow in B:
            assert sum(x*y for x,y in zip(brow,row)) % MOD == 0


def projective_normalize(col):
    if all(x % 3 == 0 for x in col):
        return None
    c = [x % 3 for x in col]
    first = next(x for x in c if x)
    if first == 2:
        c = [(2*x) % 3 for x in c]
    return tuple(c)


def build_k4_plus_cycle(l):
    # K4 vertices are ('k',0..3); cycle vertices are ('c',0..l-1).
    verts = [('k',i) for i in range(4)] + [('c',i) for i in range(l)]
    edges = [(('k',u),('k',v)) for u,v in K4_EDGES]
    cyc_start = len(edges)
    edges += [(('c',i),('c',(i+1)%l)) for i in range(l)]
    bridge_index = len(edges)
    edges += [(('k',0),('c',0))]

    m = len(edges)
    A = []
    for row in K4_Q:
        A.append(row + [0]*l + [0])
    A.append([0]*6 + [1]*l + [0])
    return verts, edges, A, cyc_start, bridge_index


def main():
    # Constant projective geometry count.
    pg33 = (3**4 - 1) // (3 - 1)
    assert pg33 == 40

    # K4 quotient itself is zero-free.
    for signs in product((1,2), repeat=6):
        assert mat_vec(K4_Q, signs) != (0,0,0)

    for l in range(3,9):
        verts, edges, A, cyc_start, bridge_index = build_k4_plus_cycle(l)
        B = incidence(verts, edges)
        assert rank_mod3(A) == 4
        check_flow_rows(B, A)

        # Every cycle edge is the same repeated projective direction e4.
        cols = [tuple(A[r][j] for r in range(4)) for j in range(len(edges))]
        cycle_dirs = {projective_normalize(cols[j]) for j in range(cyc_start, cyc_start+l)}
        assert cycle_dirs == {(0,0,0,1)}
        assert projective_normalize(cols[bridge_index]) is None

        # Quotient by repeated line = first three coordinates; support is exactly K4.
        projected = [c[:3] for c in cols]
        assert projected[:6] == [tuple(K4_Q[r][j] for r in range(3)) for j in range(6)]
        assert all(c == (0,0,0) for c in projected[6:])

        # Exact finite replay: no full sign vector maps to zero.
        # Total edges <=15 in these controls, so exhaustive replay is tiny.
        for signs in product((1,2), repeat=len(edges)):
            assert mat_vec(A, signs) != (0,0,0,0)

    print('PASS: rank4 repeated-direction reduction controls')
    print('PG(3,3) projective points = 40')
    print('K4 + C_l family verified for l=3..8')
    print('rank4 support is unbounded before minimal-rank quotienting')
    print('quotient by the repeated line exposes the rank3 K4 obstruction')


if __name__ == '__main__':
    main()
