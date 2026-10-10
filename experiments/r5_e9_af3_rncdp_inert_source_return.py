#!/usr/bin/env python3
"""Exact F3 regression for the AF3/RNCDP inert source-return theorem.

Uses the Paley(11) 55x55 source as a genuine APSQ-inert control:
all coordinate kernel normals are nonzero and projectively distinct over F3.
"""

from itertools import combinations

P = 3
Q = 11
RES = {1, 3, 4, 5, 9}


def is_arc(u, v):
    return u != v and ((v-u) % Q) in RES


def build_source():
    arcs = [(u, v) for u in range(Q) for v in range(Q) if is_arc(u, v)]
    idx = {e: i for i, e in enumerate(arcs)}
    triangles = []
    for a, b, c in combinations(range(Q), 3):
        out = {a: 0, b: 0, c: 0}
        es = []
        for u, v in ((a, b), (a, c), (b, c)):
            e = (u, v) if is_arc(u, v) else (v, u)
            es.append(e)
            out[e[0]] += 1
        if sorted(out.values()) == [1, 1, 1]:
            triangles.append(tuple(es))
    A = [[0]*len(arcs) for _ in triangles]
    for i, tri in enumerate(triangles):
        for e in tri:
            A[i][idx[e]] = 1
    return A


def rref_mod(M, p=P):
    A = [[x % p for x in row] for row in M]
    m = len(A)
    n = len(A[0]) if m else 0
    piv = []
    r = 0
    for c in range(n):
        k = next((i for i in range(r, m) if A[i][c]), None)
        if k is None:
            continue
        A[r], A[k] = A[k], A[r]
        inv = pow(A[r][c], -1, p)
        A[r] = [(x*inv) % p for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [(A[i][j]-f*A[r][j]) % p for j in range(n)]
        piv.append(c)
        r += 1
        if r == m:
            break
    return A, piv


def rank_mod(M):
    return len(rref_mod(M)[1])


def kernel_basis(M):
    R, piv = rref_mod(M)
    n = len(M[0])
    free = [j for j in range(n) if j not in piv]
    out = []
    for f in free:
        x = [0]*n
        x[f] = 1
        for i, c in enumerate(piv):
            x[c] = (-R[i][f]) % P
        out.append(x)
    return out


def affine_one(A):
    n = len(A[0])
    M = [[x % P for x in A[i]] + [1] for i in range(len(A))]
    r = 0
    piv = []
    for c in range(n):
        k = next((i for i in range(r, len(M)) if M[i][c]), None)
        if k is None:
            continue
        M[r], M[k] = M[k], M[r]
        inv = pow(M[r][c], -1, P)
        M[r] = [(x*inv) % P for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c]:
                f = M[i][c]
                M[i] = [(M[i][j]-f*M[r][j]) % P for j in range(n+1)]
        piv.append(c)
        r += 1
    assert not any(all(M[i][j] == 0 for j in range(n)) and M[i][n]
                   for i in range(r, len(M)))
    x = [0]*n
    for i, c in enumerate(piv):
        x[c] = M[i][n]
    return x


def matvec(A, x):
    return [sum(a*b for a, b in zip(row, x)) % P for row in A]


def canonical_projective(v):
    k = next((i for i, x in enumerate(v) if x % P), None)
    assert k is not None
    inv = pow(v[k] % P, -1, P)
    return tuple((inv*x) % P for x in v)


def main():
    A = build_source()
    n = len(A)
    assert n == 55 and all(len(row) == 55 for row in A)
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))

    rankA = rank_mod(A)
    assert rankA == 44
    K = kernel_basis(A)              # basis vectors as rows
    d = len(K)
    assert d == 11

    # Convert kernel basis to B with basis vectors as columns: B is n x d.
    B = [[K[t][i] for t in range(d)] for i in range(n)]
    assert rank_mod(B) == d
    assert all(matvec(A, K[t]) == [0]*n for t in range(d))

    # Genuine APSQ-inert condition: every coordinate normal is nonzero and
    # every projective class occurs exactly once.
    normals = [canonical_projective(row) for row in B]
    assert len(set(normals)) == n

    # Since A B = 0, row(A) lies in left-kernel(B). Dimensions agree:
    # rank(A)=n-rank(B)=44, so equality is exact.
    AB = [[sum(A[i][k]*B[k][j] for k in range(n)) % P
           for j in range(d)] for i in range(n)]
    assert all(x == 0 for row in AB for x in row)
    epsilon = n - rank_mod(B)
    assert epsilon == rankA == 44

    # Exact affine/source-return identity on deterministic parameter samples.
    c = affine_one(A)
    assert matvec(A, c) == [1]*n
    samples = [
        [0]*d,
        [1]*d,
        [2]*d,
        [(i*i + 2*i + 1) % 3 for i in range(d)],
        [(2*i + 1) % 3 for i in range(d)],
    ]
    for alpha in samples:
        y = [sum(B[i][j]*alpha[j] for j in range(d)) % P for i in range(n)]
        s = [(c[i] + y[i]) % P for i in range(n)]
        assert matvec(A, s) == [1]*n
        # RNCDP b=-c; y=b+s is the same relation coordinatewise.
        b = [(-z) % P for z in c]
        assert all((b[i] + s[i]) % P == y[i] for i in range(n))

    print({
        'status': 'PASS_AF3_RNCDP_INERT_SOURCE_RETURN',
        'control': 'Paley11',
        'n': n,
        'rank_F3_A': rankA,
        'kernel_dim_F3': d,
        'APSQ_projective_classes': len(set(normals)),
        'APSQ_coordinate_inert': True,
        'RNCDP_epsilon': epsilon,
        'rowspace_H_equals_rowspace_A': True,
        'E8_D1': 'EMPTY',
        'P_VS_NP': 'OPEN',
    })


if __name__ == '__main__':
    main()
