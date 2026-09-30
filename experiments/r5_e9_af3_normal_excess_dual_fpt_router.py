#!/usr/bin/env python3
"""Exact F3 regression for the AF3 normal-rank / normal-excess dual router."""

from itertools import product

P = 3
SAT_ROWS = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
    (3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
    (6,9,15),(7,8,15),(7,11,12),
]


def source():
    return [[int(j + 1 in row) for j in range(15)] for row in SAT_ROWS]


def rref(M):
    A = [[x % P for x in row] for row in M]
    m = len(A); n = len(A[0]) if m else 0
    piv = []; r = 0
    for c in range(n):
        q = next((i for i in range(r, m) if A[i][c]), None)
        if q is None:
            continue
        A[r], A[q] = A[q], A[r]
        inv = pow(A[r][c], -1, P)
        A[r] = [(x * inv) % P for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [(A[i][j] - f * A[r][j]) % P for j in range(n)]
        piv.append(c); r += 1
        if r == m:
            break
    return A, piv


def rank(M):
    return len(rref(M)[1])


def kernel_basis(A):
    R, piv = rref(A)
    n = len(A[0])
    free = [j for j in range(n) if j not in piv]
    out = []
    for f in free:
        x = [0] * n; x[f] = 1
        for i, c in enumerate(piv):
            x[c] = (-R[i][f]) % P
        out.append(x)
    return out


def affine_one(A):
    m = len(A); n = len(A[0])
    M = [[x % P for x in A[i]] + [1] for i in range(m)]
    R, piv = rref(M)
    # rref() is allowed to pivot in the augmented column, so use a dedicated solve.
    M = [[x % P for x in A[i]] + [1] for i in range(m)]
    rr = 0; pp = []
    for c in range(n):
        q = next((i for i in range(rr, m) if M[i][c]), None)
        if q is None: continue
        M[rr], M[q] = M[q], M[rr]
        inv = pow(M[rr][c], -1, P)
        M[rr] = [(x * inv) % P for x in M[rr]]
        for i in range(m):
            if i != rr and M[i][c]:
                f = M[i][c]
                M[i] = [(M[i][j] - f * M[rr][j]) % P for j in range(n + 1)]
        pp.append(c); rr += 1
    assert not any(all(M[i][j] == 0 for j in range(n)) and M[i][n]
                   for i in range(rr, m))
    x = [0] * n
    for i, c in enumerate(pp): x[c] = M[i][n]
    return x


def canon(normal, forbidden):
    q = next(i for i, x in enumerate(normal) if x % P)
    inv = pow(normal[q] % P, -1, P)
    return tuple((inv * x) % P for x in normal), (inv * forbidden) % P


def solve_unique(M, b):
    # M is square and nonsingular.
    n = len(M)
    A = [[M[i][j] % P for j in range(n)] + [b[i] % P] for i in range(n)]
    for c in range(n):
        q = next(i for i in range(c, n) if A[i][c])
        A[c], A[q] = A[q], A[c]
        inv = pow(A[c][c], -1, P)
        A[c] = [(x * inv) % P for x in A[c]]
        for i in range(n):
            if i != c and A[i][c]:
                f = A[i][c]
                A[i] = [(A[i][j] - f * A[c][j]) % P for j in range(n + 1)]
    return [A[i][n] for i in range(n)]


def row_coeff_in_basis(a, basis_rows):
    # c * B = a  <=> B^T c^T = a^T. Select r independent coordinates.
    r = len(basis_rows)
    d = len(a)
    cols = []
    current = []
    for j in range(d):
        trial = current + [[basis_rows[i][j] for i in range(r)]]
        # rank of columns = rank of transpose list
        mat = [[basis_rows[i][q] for q in [*cols, j]] for i in range(r)]
        if rank(mat) > len(cols):
            cols.append(j)
            if len(cols) == r: break
    assert len(cols) == r
    M = [[basis_rows[i][j] for i in range(r)] for j in cols]
    rhs = [a[j] for j in cols]
    return solve_unique(M, rhs)


def build_pg15_residual():
    A = source()
    c = affine_one(A)
    K = kernel_basis(A)
    d = len(K)
    assert d == 4
    B = [[K[t][i] for t in range(d)] for i in range(15)]

    groups = {}
    for i in range(15):
        normal = B[i]
        assert any(normal)
        forbidden = (-c[i]) % P
        a, b = canon(normal, forbidden)
        groups.setdefault(a, set()).add(b)
    assert all(len(v) == 1 for v in groups.values())
    constraints = [(list(a), next(iter(v))) for a, v in groups.items()]
    return A, c, B, constraints


def normalize_constraints(constraints):
    normals = [a for a, _ in constraints]
    r = rank(normals)
    basis_idx = []
    cur = []
    for i, a in enumerate(normals):
        if rank(cur + [a]) > len(cur):
            cur.append(a); basis_idx.append(i)
            if len(cur) == r: break
    basis_rows = [normals[i] for i in basis_idx]
    basis_forbidden = [constraints[i][1] for i in basis_idx]
    extras = [i for i in range(len(constraints)) if i not in set(basis_idx)]

    C = []; e = []
    for i in extras:
        coeff = row_coeff_in_basis(normals[i], basis_rows)
        assert [sum(coeff[t] * basis_rows[t][j] for t in range(r)) % P
                for j in range(len(normals[i]))] == normals[i]
        C.append(coeff)
        e.append((constraints[i][1] - sum(coeff[t] * basis_forbidden[t]
                                          for t in range(r))) % P)
    return r, basis_idx, basis_rows, basis_forbidden, C, e


def syndrome_dp(C, e, r):
    k = len(C)
    cols = [[C[j][i] for j in range(k)] for i in range(r)]
    parent = [{(0,) * k: None}]
    states = {(0,) * k}
    max_states = 1
    for i, v in enumerate(cols):
        nxt = {}
        for s in states:
            for sign in (1, 2):
                t = tuple((s[j] + sign * v[j]) % P for j in range(k))
                if t not in nxt:
                    nxt[t] = (s, sign)
        states = set(nxt)
        parent.append(nxt)
        max_states = max(max_states, len(states))
    target = next((s for s in states if all(s[j] != e[j] for j in range(k))), None)
    if target is None:
        return None, max_states
    y = [0] * r
    s = target
    for i in range(r, 0, -1):
        prev, sign = parent[i][s]
        y[i - 1] = sign
        s = prev
    return y, max_states


def direct_solutions(C, e, r):
    out = []
    for y in product((1, 2), repeat=r):
        syn = [sum(C[j][i] * y[i] for i in range(r)) % P for j in range(len(C))]
        if all(syn[j] != e[j] for j in range(len(C))):
            out.append(y)
    return out


def reconstruct_pg15(A, c, B, constraints, basis_idx, basis_rows, basis_forbidden, y):
    # Solve basis normal equations a_i alpha = y_i + b_i.
    # basis_rows is 4x4 for PG15.
    rhs = [(y[i] + basis_forbidden[i]) % P for i in range(len(y))]
    alpha = solve_unique(basis_rows, rhs)
    rword = [(c[i] + sum(B[i][t] * alpha[t] for t in range(len(alpha)))) % P
             for i in range(15)]
    assert all(v in (1, 2) for v in rword)
    x = [int(v == 2) for v in rword]
    assert all(sum(A[i][j] * x[j] for j in range(15)) == 1 for i in range(15))
    return tuple(x)


def main():
    A, c, B, constraints = build_pg15_residual()
    assert len(constraints) == 11
    r, idx, basis_rows, bB, C, e = normalize_constraints(constraints)
    k = len(C)
    assert (len(constraints), r, k) == (11, 4, 7)

    direct = direct_solutions(C, e, r)
    assert len(direct) == 4
    y, max_states = syndrome_dp(C, e, r)
    assert y in direct
    witness = reconstruct_pg15(A, c, B, constraints, idx, basis_rows, bB, y)
    assert sum(witness) == 5
    decoded = {reconstruct_pg15(A, c, B, constraints, idx, basis_rows, bB, q)
               for q in direct}
    assert len(decoded) == 4
    assert max_states <= 3 ** k

    # Sharp generic excess-two UNSAT control.
    # Basis forbidden hyperplanes y1=0,y2=0; extras y1+y2=0 and y1-y2=0.
    C2 = [[1, 1], [1, 2]]
    e2 = [0, 0]
    assert direct_solutions(C2, e2, 2) == []
    y2, states2 = syndrome_dp(C2, e2, 2)
    assert y2 is None
    assert states2 <= 9

    print({
        'status': 'PASS_AF3_NORMAL_EXCESS_DUAL_FPT_ROUTER',
        'PG15_m': 11,
        'PG15_normal_rank': r,
        'PG15_normal_excess': k,
        'PG15_avoiding_points': len(direct),
        'PG15_exactone_witnesses': len(decoded),
        'PG15_dp_max_states': max_states,
        'sharp_k2_unsat': True,
        'sharp_k2_dp_max_states': states2,
        'E8_D1': 'EMPTY',
        'P_VS_NP': 'OPEN',
    })


if __name__ == '__main__':
    main()
