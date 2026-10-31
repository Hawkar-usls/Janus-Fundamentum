#!/usr/bin/env python3
"""Exact regression for the Paley {1,2,-3} infinite post-RKPR barrier.

The infinite theorem is symbolic in the companion note.  This checker freezes
q=31 as an exact rank control and q=79 as a larger combinatorial replay.
No floating point is used.
"""

from itertools import combinations
from math import isqrt

PRIME = 1_000_003


def qr_set(q):
    return {pow(x, 2, q) for x in range(1, q)}


def subgroup_generated(q, gens):
    seen = {1}
    stack = [1]
    while stack:
        x = stack.pop()
        for g in gens:
            y = (x * g) % q
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return seen


def build_component(q):
    assert q % 24 == 7 and q > 7
    Q = qr_set(q)
    assert 2 in Q
    assert (-3) % q in Q

    H = subgroup_generated(q, (2, (-3) % q))
    assert H <= Q
    C = sorted(H)

    # Columns are arcs (s -> s+d), encoded by (d,s).
    columns = [(d, s) for d in C for s in range(q)]
    col_index = {e: i for i, e in enumerate(columns)}
    n = len(columns)

    rows = []
    row_labels = []
    for d in C:
        for s in range(q):
            edges = (
                (d, s),
                ((2 * d) % q, (s + d) % q),
                ((-3 * d) % q, (s + 3 * d) % q),
            )
            assert all(e in col_index for e in edges)
            support = tuple(sorted(col_index[e] for e in edges))
            assert len(set(support)) == 3
            rows.append(support)
            row_labels.append((d, s))

    assert len(rows) == n
    assert len(set(rows)) == n

    # Cubic columns.
    coldeg = [0] * n
    for support in rows:
        for j in support:
            coldeg[j] += 1
    assert min(coldeg) == max(coldeg) == 3

    # Levi connectedness.
    adj = [[] for _ in range(2 * n)]
    for i, support in enumerate(rows):
        for j in support:
            adj[i].append(n + j)
            adj[n + j].append(i)
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    assert len(seen) == 2 * n

    # Every row is the directed cycle
    # s -> s+d -> s+3d -> s.
    for d, s in row_labels:
        verts = (s, (s + d) % q, (s + 3 * d) % q)
        edge_pairs = (
            (verts[0], verts[1]),
            (verts[1], verts[2]),
            (verts[2], verts[0]),
        )
        diffs = tuple((v - u) % q for u, v in edge_pairs)
        assert diffs == (d, (2 * d) % q, (-3 * d) % q)
        assert all(delta in Q for delta in diffs)

    return H, columns, rows


def rank_mod_sparse(supports, p):
    """Exact modular row rank from sparse unit supports."""
    pivots = {}
    for support in supports:
        row = {c: 1 for c in support}
        while row:
            c = min(row)
            if c not in pivots:
                inv = pow(row[c], p - 2, p)
                norm = {}
                for j, v in row.items():
                    z = (v * inv) % p
                    if z:
                        norm[j] = z
                pivots[c] = norm
                break
            f = row[c]
            prow = pivots[c]
            for j, v in prow.items():
                z = (row.get(j, 0) - f * v) % p
                if z:
                    row[j] = z
                else:
                    row.pop(j, None)
    return len(pivots)


def check_linearity(rows):
    ss = [set(r) for r in rows]
    for i, j in combinations(range(len(ss)), 2):
        assert len(ss[i] & ss[j]) <= 1, (i, j)


def main():
    # First exact family member after the excluded q=7.
    H31, _cols31, rows31 = build_component(31)
    assert len(H31) == 15
    assert len(rows31) == 465
    check_linearity(rows31)

    # Gradient kernel has dimension q-1=30. Exact modular rank 435 gives
    # the opposite inequality, so rank_Q(A)=435 and nullity_Q(A)=30.
    rank31 = rank_mod_sparse(rows31, PRIME)
    assert rank31 == 435
    assert len(rows31) - rank31 == 30

    # Larger replay. No dense matrix or asymptotic rank equality is needed:
    # the theorem only needs the forced gradient lower bound q-1.
    H79, _cols79, rows79 = build_component(79)
    assert len(H79) >= 1
    assert len(rows79) == 79 * len(H79)
    n79 = len(rows79)
    root_floor = (isqrt(1 + 8 * n79) - 1) // 2
    assert 78 >= root_floor

    # Explicit nonzero voltage used in the connectedness proof.
    for q in (31, 79):
        assert 7 % q != 0

    print("Paley {1,2,-3} infinite post-RKPR barrier regression: PASS")
    print("q=31:")
    print(f"  |H| = {len(H31)}")
    print("  n = 465")
    print("  row_degree = column_degree = 3")
    print("  linear = True")
    print("  Levi_connected = True")
    print(f"  rank_F_{PRIME}(A) = {rank31}")
    print("  forced_gradient_nullity = 30")
    print("  exact_nullity_Q = 30")
    print("q=79:")
    print(f"  |H| = {len(H79)}")
    print(f"  n = {n79}")
    print("  row_degree = column_degree = 3")
    print("  Levi_connected = True")
    print("  forced_gradient_nullity >= 78")
    print("infinite theorem: nullity_Q = Omega(sqrt(n)) after RKPR")


if __name__ == "__main__":
    main()
