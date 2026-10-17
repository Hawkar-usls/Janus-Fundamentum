#!/usr/bin/env python3
"""Exact regression for AF3 parallel-class fixed-point quotient.

The arbitrary-size theorem is proved in the companion research note.  This
checker uses exact F3 arithmetic on the frozen PG15 SAT and singular rank-14
UNSAT controls.
"""

from itertools import combinations

P = 3

SAT_ROWS = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
    (3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
    (6,9,15),(7,8,15),(7,11,12),
]

PERM_P = [5,7,9,10,3,1,14,2,4,6,12,13,8,0,11]
PERM_Q = [12,9,14,11,13,10,7,3,1,0,2,5,6,8,4]


def matrix_from_rows(rows, n):
    return [[int(j + 1 in row) for j in range(n)] for row in rows]


def singular_unsat_matrix():
    n = 15
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in (i, PERM_P[i], PERM_Q[i]):
            A[i][j] = 1
    return A


def affine_parameterization(A, b, p=P):
    m, n = len(A), len(A[0])
    M = [[A[i][j] % p for j in range(n)] + [b[i] % p] for i in range(m)]
    pivots = []
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if M[i][c] % p), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        inv = pow(M[r][c] % p, -1, p)
        M[r] = [(x * inv) % p for x in M[r]]
        for i in range(m):
            if i != r and M[i][c] % p:
                f = M[i][c] % p
                M[i] = [(M[i][j] - f * M[r][j]) % p for j in range(n + 1)]
        pivots.append(c)
        r += 1

    for i in range(r, m):
        if all(M[i][c] % p == 0 for c in range(n)) and M[i][n] % p:
            return None, None, None

    free = [c for c in range(n) if c not in pivots]
    x0 = [0] * n
    for i, c in enumerate(pivots):
        x0[c] = M[i][n] % p

    basis = []
    for f in free:
        v = [0] * n
        v[f] = 1
        for i, c in enumerate(pivots):
            v[c] = (-M[i][f]) % p
        basis.append(v)

    rows = [[basis[j][i] for j in range(len(basis))] for i in range(n)]
    return x0, rows, len(pivots)


def canonical_projective(v):
    for a in v:
        a %= P
        if a:
            inv = pow(a, -1, P)
            return tuple((x * inv) % P for x in v), a
    return None, None


def restrict_affine(r0, rows, v, t):
    """Restrict alpha to v alpha=t and return new coordinate forms."""
    d = len(v)
    pivot = next(i for i, x in enumerate(v) if x % P)
    inv = pow(v[pivot] % P, -1, P)

    alpha0 = [0] * d
    alpha0[pivot] = (t * inv) % P

    free = [j for j in range(d) if j != pivot]
    K = []
    for f in free:
        q = [0] * d
        q[f] = 1
        q[pivot] = (-v[f] * inv) % P
        K.append(q)

    nr0 = []
    nrows = []
    for a, b in zip(r0, rows):
        nr0.append((a + sum(b[j] * alpha0[j] for j in range(d))) % P)
        nrows.append([
            sum(b[j] * K[k][j] for j in range(d)) % P
            for k in range(len(K))
        ])
    return nr0, nrows


def fixed_point_quotient(A):
    r0, rows, rank = affine_parameterization(A, [1] * len(A))
    if r0 is None:
        return {"status": "UNSAT_INCONSISTENT"}

    initial_d = len(rows[0]) if rows else 0
    pin_steps = []

    while True:
        d = len(rows[0]) if rows else 0
        if d == 0:
            return {
                "status": "SAT_POINT" if all(a != 0 for a in r0) else "UNSAT_ZERO",
                "rank_F3": rank,
                "initial_d": initial_d,
                "final_d": 0,
                "pin_steps": pin_steps,
            }

        groups = {}
        for a, b in zip(r0, rows):
            if all(x % P == 0 for x in b):
                if a % P == 0:
                    return {
                        "status": "UNSAT_ZERO",
                        "rank_F3": rank,
                        "initial_d": initial_d,
                        "final_d": d,
                        "pin_steps": pin_steps,
                    }
                continue

            v, lam = canonical_projective(b)
            c = (-a * pow(lam, -1, P)) % P
            groups.setdefault(v, set()).add(c)

        triple = next(((v, C) for v, C in groups.items() if len(C) == 3), None)
        if triple is not None:
            v, C = triple
            return {
                "status": "UNSAT_THREE_OFFSET_COVER",
                "rank_F3": rank,
                "initial_d": initial_d,
                "final_d": d,
                "pin_steps": pin_steps,
                "cover_normal": v,
                "cover_offsets": tuple(sorted(C)),
                "projective_classes": len(groups),
            }

        pin = next(((v, C) for v, C in groups.items() if len(C) == 2), None)
        if pin is None:
            assert all(len(C) == 1 for C in groups.values())
            return {
                "status": "RESIDUAL",
                "rank_F3": rank,
                "initial_d": initial_d,
                "final_d": d,
                "pin_steps": pin_steps,
                "projective_classes": len(groups),
                "offset_profile": tuple(sorted(len(C) for C in groups.values())),
            }

        v, C = pin
        t = next(x for x in range(P) if x not in C)
        pin_steps.append((d, v, tuple(sorted(C)), t))
        r0, rows = restrict_affine(r0, rows, v, t)


def witness_sets(A):
    n = len(A)
    if n % 3:
        return []
    out = []
    for C in combinations(range(n), n // 3):
        S = set(C)
        if all(sum(row[j] for j in S) == 1 for row in A):
            out.append(C)
    return out


def main():
    A_sat = matrix_from_rows(SAT_ROWS, 15)
    A_unsat = singular_unsat_matrix()

    sat = fixed_point_quotient(A_sat)
    unsat = fixed_point_quotient(A_unsat)

    assert sat["status"] == "RESIDUAL"
    assert sat["rank_F3"] == 11
    assert sat["initial_d"] == 4
    assert sat["final_d"] == 4
    assert sat["pin_steps"] == []
    assert sat["projective_classes"] == 11
    assert set(sat["offset_profile"]) == {1}
    assert len(witness_sets(A_sat)) == 4

    assert unsat["status"] == "UNSAT_THREE_OFFSET_COVER"
    assert unsat["rank_F3"] == 14
    assert unsat["initial_d"] == 1
    assert unsat["final_d"] == 1
    assert unsat["pin_steps"] == []
    assert unsat["cover_offsets"] == (0, 1, 2)
    assert witness_sets(A_unsat) == []

    print({"PG15": sat})
    print({"SINGULAR_UNSAT_RANK14": unsat})
    print("AF3 parallel-class fixed-point quotient: PASS")
    print("E8_D1 = EMPTY")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
