#!/usr/bin/env python3
"""Exact F3 regression for the AF3 normal-rank / syndrome-image-rank router."""

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
        if q is None: continue
        A[r], A[q] = A[q], A[r]
        inv = pow(A[r][c], -1, P)
        A[r] = [(x * inv) % P for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [(A[i][j] - f * A[r][j]) % P for j in range(n)]
        piv.append(c); r += 1
        if r == m: break
    return A, piv


def rank(M): return len(rref(M)[1])


def kernel_basis(A):
    R, piv = rref(A); n = len(A[0])
    free = [j for j in range(n) if j not in piv]
    out = []
    for f in free:
        x = [0] * n; x[f] = 1
        for i, c in enumerate(piv): x[c] = (-R[i][f]) % P
        out.append(x)
    return out


def affine_one(A):
    m = len(A); n = len(A[0])
    M = [[x % P for x in A[i]] + [1] for i in range(m)]
    rr = 0; piv = []
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
        piv.append(c); rr += 1
    assert not any(all(M[i][j] == 0 for j in range(n)) and M[i][n]
                   for i in range(rr, m))
    x = [0] * n
    for i, c in enumerate(piv): x[c] = M[i][n]
    return x


def solve_unique(M, b):
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


def independent_rows_for_columns(Q):
    # Q is k x rho of full column rank; return rho row indices making a square nonsingular minor.
    rho = len(Q[0]) if Q else 0
    chosen = []
    for i in range(len(Q)):
        trial = [Q[j] for j in chosen + [i]]
        if rank(trial) > len(chosen):
            chosen.append(i)
            if len(chosen) == rho: break
    assert len(chosen) == rho
    return chosen


def solve_in_column_basis(Q, v):
    rows = independent_rows_for_columns(Q)
    M = [[Q[i][j] for j in range(len(Q[0]))] for i in rows]
    b = [v[i] for i in rows]
    w = solve_unique(M, b)
    assert [sum(Q[i][j] * w[j] for j in range(len(w))) % P for i in range(len(Q))] == v
    return w


def canon(normal, forbidden):
    q = next(i for i, x in enumerate(normal) if x)
    inv = pow(normal[q], -1, P)
    return tuple((inv * x) % P for x in normal), (inv * forbidden) % P


def row_coeff(a, basis_rows):
    # Solve c * B = a using an independent square coordinate minor.
    r = len(basis_rows); d = len(a); chosen = []
    for j in range(d):
        mat = [[basis_rows[i][q] for q in chosen + [j]] for i in range(r)]
        if rank(mat) > len(chosen):
            chosen.append(j)
            if len(chosen) == r: break
    assert len(chosen) == r
    M = [[basis_rows[i][j] for i in range(r)] for j in chosen]
    c = solve_unique(M, [a[j] for j in chosen])
    assert [sum(c[t] * basis_rows[t][j] for t in range(r)) % P for j in range(d)] == a
    return c


def pg15_residual():
    A = source(); particular = affine_one(A); K = kernel_basis(A); d = len(K)
    assert d == 4
    eval_rows = [[K[t][i] for t in range(d)] for i in range(15)]
    groups = {}
    for i in range(15):
        a, b = canon(eval_rows[i], (-particular[i]) % P)
        groups.setdefault(a, set()).add(b)
    assert all(len(v) == 1 for v in groups.values())
    constraints = [(list(a), next(iter(v))) for a, v in groups.items()]
    return A, particular, eval_rows, constraints


def normalize(constraints):
    normals = [a for a, _ in constraints]; r = rank(normals)
    basis_idx = []; basis_rows = []
    for i, a in enumerate(normals):
        if rank(basis_rows + [a]) > len(basis_rows):
            basis_rows.append(a); basis_idx.append(i)
            if len(basis_rows) == r: break
    bB = [constraints[i][1] for i in basis_idx]
    extra = [i for i in range(len(constraints)) if i not in set(basis_idx)]
    C = []; e = []
    for i in extra:
        c = row_coeff(normals[i], basis_rows)
        C.append(c)
        e.append((constraints[i][1] - sum(c[t] * bB[t] for t in range(r))) % P)
    return r, basis_idx, basis_rows, bB, C, e


def direct_solutions(C, e, r):
    out = []
    for y in product((1, 2), repeat=r):
        s = [sum(C[j][i] * y[i] for i in range(r)) % P for j in range(len(C))]
        if all(s[j] != e[j] for j in range(len(C))): out.append(y)
    return out


def compressed_dp(C, e, r):
    k = len(C)
    full_cols = [[C[j][i] for j in range(k)] for i in range(r)]
    rho = rank(C)

    # Greedy column-space basis Q.
    basis_cols = []
    for v in full_cols:
        old = rank([[q[i] for q in basis_cols] for i in range(k)]) if basis_cols else 0
        trial_cols = basis_cols + [v]
        trial = [[q[i] for q in trial_cols] for i in range(k)]
        if rank(trial) > old:
            basis_cols.append(v)
            if len(basis_cols) == rho: break
    assert len(basis_cols) == rho
    Q = [[basis_cols[j][i] for j in range(rho)] for i in range(k)]
    W = [solve_in_column_basis(Q, v) for v in full_cols]

    zero = (0,) * rho
    states = {zero}; parents = [{zero: None}]; max_states = 1
    for w in W:
        nxt = {}
        for s in states:
            for sign in (1, 2):
                t = tuple((s[j] + sign * w[j]) % P for j in range(rho))
                if t not in nxt: nxt[t] = (s, sign)
        states = set(nxt); parents.append(nxt); max_states = max(max_states, len(states))

    def expand(t):
        return [sum(Q[i][j] * t[j] for j in range(rho)) % P for i in range(k)]

    target = next((t for t in states if all(expand(t)[j] != e[j] for j in range(k))), None)
    if target is None: return None, rho, max_states
    y = [0] * r; t = target
    for i in range(r, 0, -1):
        prev, sign = parents[i][t]; y[i - 1] = sign; t = prev
    return tuple(y), rho, max_states


def reconstruct(A, particular, eval_rows, basis_rows, bB, y):
    alpha = solve_unique(basis_rows, [(y[i] + bB[i]) % P for i in range(len(y))])
    rw = [(particular[i] + sum(eval_rows[i][t] * alpha[t] for t in range(len(alpha)))) % P
          for i in range(15)]
    assert all(v in (1, 2) for v in rw)
    x = tuple(int(v == 2) for v in rw)
    assert all(sum(A[i][j] * x[j] for j in range(15)) == 1 for i in range(15))
    return x


def main():
    A, particular, eval_rows, constraints = pg15_residual()
    r, idx, basis_rows, bB, C, e = normalize(constraints)
    k = len(C)
    assert (len(constraints), r, k, rank(C)) == (11, 4, 7, 4)

    direct = direct_solutions(C, e, r)
    assert len(direct) == 4
    y, rho, max_states = compressed_dp(C, e, r)
    assert y in direct
    decoded = {reconstruct(A, particular, eval_rows, basis_rows, bB, q) for q in direct}
    assert len(decoded) == 4
    assert rho == 4 and max_states <= 3 ** rho

    C2 = [[1,1],[1,2]]; e2 = [0,0]
    assert direct_solutions(C2, e2, 2) == []
    y2, rho2, states2 = compressed_dp(C2, e2, 2)
    assert y2 is None and rho2 == 2 and states2 <= 9

    print({
        'status': 'PASS_AF3_SYNDROME_RANK_DUAL_FPT_ROUTER',
        'PG15_m': 11, 'PG15_r': r, 'PG15_k': k, 'PG15_rho': rho,
        'PG15_avoiding_points': len(direct), 'PG15_witnesses': len(decoded),
        'PG15_compressed_dp_max_states': max_states,
        'sharp_k2_rho2_unsat': True,
        'E8_D1': 'EMPTY', 'P_VS_NP': 'OPEN',
    })


if __name__ == '__main__': main()
