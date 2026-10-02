#!/usr/bin/env python3
"""Exact finite controls for R5 E18.

Dependency-free checks for:
  * projective-kernel compression over Q;
  * frozen PG15 SAT / UNSAT controls;
  * the R5 E17 q=6 hardness target (36 kernel-fixed coordinates);
  * the R5 E16 ring family (projective compression does not fake-close it);
  * existence of balanced 2-edge cuts in E16 finite controls.

The companion note contains the symbolic proofs.
"""

from fractions import Fraction
from itertools import combinations


SAT_ROWS = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
    (3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
    (6,9,15),(7,8,15),(7,11,12),
]
PERM_P = [5,7,9,10,3,1,14,2,4,6,12,13,8,0,11]
PERM_Q = [12,9,14,11,13,10,7,3,1,0,2,5,6,8,4]


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
        A[r] = [v / z for v in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[r][j] for j in range(n)]
        pivots.append(c)
        r += 1
        if r == m:
            break
    return A, pivots


def rank_q(M):
    return len(rref_q(M)[1])


def nullspace_q(M):
    R, pivots = rref_q(M)
    n = len(R[0]) if R else 0
    free = [c for c in range(n) if c not in pivots]
    out = []
    for f in free:
        v = [Fraction(0)] * n
        v[f] = Fraction(1)
        for rr, p in enumerate(pivots):
            v[p] = -R[rr][f]
        out.append(v)
    return out


def projective_kernel_profile(A):
    """Return the exact E18 projective-kernel profile.

    A nullspace basis K_1,...,K_d is stored as columns of N.
    Coordinate i is the row functional b_i=(K_1[i],...,K_d[i]).
    """
    basis = nullspace_q(A)
    d = len(basis)
    n = len(A[0])
    if d == 0:
        return {
            "d": 0,
            "verdict": "UNSAT_FULL_Q_RANK",
            "fixed_coordinates": list(range(n)),
        }

    rows = [[basis[k][i] for k in range(d)] for i in range(n)]
    fixed = [i for i, row in enumerate(rows) if not any(row)]
    if fixed:
        return {
            "d": d,
            "verdict": "UNSAT_KERNEL_FIXED_COORDINATE",
            "fixed_coordinates": fixed,
        }

    classes = {}
    for i, row in enumerate(rows):
        p = next(j for j, v in enumerate(row) if v)
        lead = row[p]
        key = tuple(v / lead for v in row)
        classes.setdefault(key, []).append((i, row))

    forced = []
    flexible = []
    incompatible = []

    for items in classes.values():
        rep = items[0][1]
        p = next(j for j, v in enumerate(rep) if v)
        allowed_t = {Fraction(-1), Fraction(2)}
        scalars = []

        for i, row in items:
            c = row[p] / rep[p]
            assert row == [c * v for v in rep]
            scalars.append((i, c))
            allowed_t &= {Fraction(-1, 1) / c, Fraction(2, 1) / c}

        if not allowed_t:
            incompatible.append(scalars)
        elif len(allowed_t) == 1:
            forced.append((rep, next(iter(allowed_t)), scalars))
        else:
            assert allowed_t == {Fraction(-1), Fraction(2)}
            flexible.append((rep, allowed_t, scalars))

    if incompatible:
        return {
            "d": d,
            "classes": len(classes),
            "verdict": "UNSAT_PROJECTIVE_RATIO",
            "incompatible": incompatible,
        }

    F = [rep[:] for rep, _, _ in forced]
    rhs = [t for _, t, _ in forced]
    if F:
        rank_F = rank_q(F)
        augmented = [row + [rhs[i]] for i, row in enumerate(F)]
        if rank_q(augmented) > rank_F:
            return {
                "d": d,
                "classes": len(classes),
                "forced_classes": len(forced),
                "verdict": "UNSAT_FORCED_PROJECTIVE_SYSTEM",
            }
        delta = d - rank_F
    else:
        delta = d

    return {
        "d": d,
        "classes": len(classes),
        "forced_classes": len(forced),
        "flexible_classes": len(flexible),
        "delta": delta,
        "verdict": "PROJECTIVE_RESIDUAL",
    }


def matrix_from_rows(rows, n):
    return [[int(j + 1 in row) for j in range(n)] for row in rows]


def pg15_unsat_matrix():
    n = 15
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in (i, PERM_P[i], PERM_Q[i]):
            A[i][j] = 1
    return A


# ----- R5 E17 target -----


def rx_fixture():
    q = 6
    source_sets = [tuple(sorted({i, (i + 1) % q, (i + 3) % q}))
                   for i in range(q)]
    assert all(len(C) == 3 for C in source_sets)
    return q, source_sets


def transform_e12(q, source_sets):
    target = []
    x = [f"x:{i}" for i in range(q)]
    xp = [f"xp:{i}" for i in range(q)]

    for j, C in enumerate(source_sets):
        a, b, c = C
        bx = [x[a], x[b], x[c]]
        bxp = [xp[a], xp[b], xp[c]]
        z = [f"g{j}:z{i}" for i in range(1, 7)]
        zp = [f"g{j}:Z{i}" for i in range(1, 7)]
        t = [f"g{j}:t{i}" for i in range(1, 4)]

        target.extend([
            {bx[0], z[0], z[3]},
            {bx[1], z[1], z[4]},
            {bx[2], z[2], z[5]},
            {z[0], z[1], z[2]},
            {z[3], z[4], z[5]},
            {bxp[0], zp[0], zp[3]},
            {bxp[1], zp[1], zp[4]},
            {bxp[2], zp[2], zp[5]},
            {zp[0], zp[1], zp[2]},
            {zp[3], zp[4], zp[5]},
            {z[1], z[5], t[0]},
            {z[2], z[3], t[1]},
            {z[0], z[4], t[2]},
            {zp[1], zp[5], t[1]},
            {zp[2], zp[3], t[2]},
            {zp[0], zp[4], t[0]},
            {t[0], t[1], t[2]},
        ])
    return target


def incidence_from_sets(sets):
    universe = sorted(set().union(*sets))
    pos = {v: i for i, v in enumerate(universe)}
    M = [[0] * len(sets) for _ in universe]
    for j, S in enumerate(sets):
        for v in S:
            M[pos[v]][j] = 1
    return M


# ----- R5 E16 ring -----


def e16_matrix(k):
    n = 9 * k

    def idx(block, i, j):
        return block * 9 + (i % 3) * 3 + (j % 3)

    A = [[0] * n for _ in range(n)]
    for b in range(k):
        for i in range(3):
            for j in range(3):
                r = idx(b, i, j)
                cols = [
                    r,
                    idx(b, i + 1, j),
                    idx((b + 1) % k, 0, 1)
                    if (i, j) == (0, 0)
                    else idx(b, i, j + 1),
                ]
                for c in cols:
                    A[r][c] = 1
    return A


def levi_graph(A):
    """Return adjacency sets and edge list for the row/column Levi graph."""
    nrows = len(A)
    ncols = len(A[0])
    N = nrows + ncols
    adj = [set() for _ in range(N)]
    edges = []
    for r in range(nrows):
        for c, v in enumerate(A[r]):
            if v:
                u = r
                w = nrows + c
                adj[u].add(w)
                adj[w].add(u)
                edges.append((u, w))
    return adj, edges


def components_after_removing_edges(adj, removed):
    rem = {tuple(sorted(e)) for e in removed}
    unseen = set(range(len(adj)))
    comps = []
    while unseen:
        root = next(iter(unseen))
        unseen.remove(root)
        stack = [root]
        comp = [root]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if tuple(sorted((u, v))) in rem:
                    continue
                if v in unseen:
                    unseen.remove(v)
                    stack.append(v)
                    comp.append(v)
        comps.append(comp)
    return comps


def has_balanced_two_edge_cut(A):
    """Finite-control recognizer: both sides at most 2N/3."""
    adj, edges = levi_graph(A)
    N = len(adj)
    for e1, e2 in combinations(edges, 2):
        comps = components_after_removing_edges(adj, (e1, e2))
        if len(comps) < 2:
            continue
        sizes = [len(C) for C in comps]
        m = len(comps)
        for mask in range(1, (1 << m) - 1):
            left = sum(sizes[i] for i in range(m) if (mask >> i) & 1)
            right = N - left
            if max(left, right) * 3 <= 2 * N:
                return True, (e1, e2), (left, right)
    return False, None, None


def check_pg15():
    sat = matrix_from_rows(SAT_ROWS, 15)
    unsat = pg15_unsat_matrix()

    ps = projective_kernel_profile(sat)
    pu = projective_kernel_profile(unsat)

    assert ps["d"] == 4
    assert ps["verdict"] == "PROJECTIVE_RESIDUAL"
    assert ps["delta"] == 4

    assert pu["d"] == 1
    assert pu["verdict"] == "UNSAT_PROJECTIVE_RATIO"

    return ps, pu


def check_e17():
    q, source = rx_fixture()
    B = incidence_from_sets(transform_e12(q, source))
    assert len(B) == 102 and len(B[0]) == 102
    profile = projective_kernel_profile(B)

    assert profile["d"] == 12
    assert profile["verdict"] == "UNSAT_KERNEL_FIXED_COORDINATE"
    assert len(profile["fixed_coordinates"]) == 36

    expected = []
    ports = {0, 1, 2, 5, 6, 7}
    for g in range(6):
        expected.extend(17 * g + p for p in sorted(ports))
    assert profile["fixed_coordinates"] == expected

    return profile


def check_e16():
    rows = []
    for k in range(2, 7):
        A = e16_matrix(k)
        profile = projective_kernel_profile(A)
        assert profile["d"] == k + 1
        assert profile["verdict"] == "PROJECTIVE_RESIDUAL"
        assert profile["delta"] == k + 1

        ok, cut, split = has_balanced_two_edge_cut(A)
        assert ok
        rows.append((k, len(A), profile["d"], split))
    return rows


def main():
    ps, pu = check_pg15()
    e17 = check_e17()
    e16 = check_e16()

    print("R5 E18 exact controls: PASS")
    print(
        "PG15 SAT: "
        f"d={ps['d']}, projective residual delta={ps['delta']}"
    )
    print(
        "PG15 UNSAT: "
        f"d={pu['d']}, caught by incompatible projective ratio"
    )
    print(
        "E17 q=6 UNSAT: "
        f"d={e17['d']}, kernel-fixed coordinates="
        f"{len(e17['fixed_coordinates'])}"
    )
    print("E16 finite ring controls:")
    for k, n, d, split in e16:
        print(
            f"  k={k}: n={n}, d={d}, "
            f"balanced 2-edge split={split[0]}+{split[1]}"
        )


if __name__ == "__main__":
    main()
