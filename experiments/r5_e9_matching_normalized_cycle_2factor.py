#!/usr/bin/env python3
"""Exact regression for the matching-normalized cycle-2-factor Exact-One theorem."""

from itertools import product


def rows_from_pq(p, q):
    n = len(p)
    assert sorted(p) == list(range(n))
    assert sorted(q) == list(range(n))
    rows = [tuple(sorted((i, p[i], q[i]))) for i in range(n)]
    assert all(len(set(r)) == 3 for r in rows)
    return rows


def assert_linear(rows):
    S = [set(r) for r in rows]
    for i in range(len(S)):
        for j in range(i):
            assert len(S[i] & S[j]) <= 1, (i, j, S[i] & S[j])


def cycle_edges(p, q):
    edges = [tuple(sorted((p[i], q[i]))) for i in range(len(p))]
    assert all(u != v for u, v in edges)
    assert len(edges) == len(set(edges))
    deg = [0] * len(p)
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
    assert set(deg) == {2}, deg
    return edges


def cycle_lengths(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    assert all(len(a) == 2 for a in adj)
    seen = set()
    lengths = []
    for s in range(n):
        if s in seen:
            continue
        cur = s
        prev = None
        length = 0
        while cur not in seen:
            seen.add(cur)
            length += 1
            a, b = adj[cur]
            nxt = a if a != prev else b
            prev, cur = cur, nxt
        lengths.append(length)
    assert sum(lengths) == n
    return sorted(lengths)


def exact_one(rows, x):
    return all(sum(x[j] for j in row) == 1 for row in rows)


def odd_parity(rows, x):
    return all(sum(x[j] for j in row) % 2 == 1 for row in rows)


def cycle_independent(edges, x):
    return all(not (x[u] and x[v]) for u, v in edges)


def check(name, p, q, expected_witnesses=None):
    rows = rows_from_pq(p, q)
    n = len(rows)
    assert_linear(rows)
    edges = cycle_edges(p, q)
    lengths = cycle_lengths(n, edges)

    c_exact = 0
    c_normal = 0
    for x in product((0, 1), repeat=n):
        a = exact_one(rows, x)
        b = odd_parity(rows, x) and cycle_independent(edges, x)
        assert a == b, (name, x, a, b)
        c_exact += int(a)
        c_normal += int(b)

    assert c_exact == c_normal
    if expected_witnesses is not None:
        assert c_exact == expected_witnesses, (name, c_exact, expected_witnesses)

    print(f"{name}: n={n} cycles={lengths} witnesses={c_exact}")


def main():
    # Fano cyclic 7_3: row i = {i, i+1, i+3} mod 7.
    check(
        "FANO7",
        [(i + 1) % 7 for i in range(7)],
        [(i + 3) % 7 for i in range(7)],
        expected_witnesses=0,
    )

    # Frozen 9_3 SAT control from the Boben semantic audit.
    check(
        "SAT9",
        [4, 6, 8, 1, 7, 2, 3, 0, 5],
        [2, 0, 6, 4, 5, 3, 7, 8, 1],
        expected_witnesses=1,
    )

    # Frozen 10_3 UNSAT control from the Boben semantic audit.
    check(
        "UNSAT10",
        [5, 0, 4, 2, 9, 1, 7, 3, 6, 8],
        [3, 2, 7, 6, 0, 4, 9, 8, 1, 5],
        expected_witnesses=0,
    )

    print("PASS R5_E9_MATCHING_NORMALIZED_CYCLE_2FACTOR")
    print("EXACT_ONE_IFF_AFFINE_PARITY_AND_CYCLE_INDEPENDENCE = VERIFIED")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
