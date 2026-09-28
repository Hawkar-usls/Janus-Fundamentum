#!/usr/bin/env python3
"""Exact regression for the two-edge-twist 3-cut-irreducible nullity family."""

from fractions import Fraction
from itertools import combinations


def perfect_matchings(vertices):
    vertices = tuple(vertices)
    if not vertices:
        yield ()
        return
    a = vertices[0]
    for k in range(1, len(vertices)):
        b = vertices[k]
        rest = vertices[1:k] + vertices[k + 1 :]
        for tail in perfect_matchings(rest):
            yield tuple(sorted(((min(a, b), max(a, b)),) + tail))


def rank_q(mat):
    a = [[Fraction(x) for x in row] for row in mat]
    m, n = len(a), len(a[0])
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if a[i][c]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        pivot = a[r][c]
        a[r] = [x / pivot for x in a[r]]
        for i in range(m):
            if i != r and a[i][c]:
                f = a[i][c]
                a[i] = [a[i][j] - f * a[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def verify_carrier(a):
    n = len(a)
    assert all(len(row) == n for row in a)
    assert all(sum(row) == 3 for row in a)
    assert all(sum(a[i][j] for i in range(n)) == 3 for j in range(n))
    supports = [{j for j, x in enumerate(row) if x} for row in a]
    for i, j in combinations(range(n), 2):
        assert len(supports[i] & supports[j]) <= 1


def verify_witness(a, x):
    return all(sum(row[j] * x[j] for j in range(len(x))) == 1 for row in a)


def levi_edges(a):
    n = len(a)
    return [(i, n + j) for i in range(n) for j in range(n) if a[i][j]]


def connected_and_cut_profile(a, exhaustive=True):
    n = len(a)
    nv = 2 * n
    edges = levi_edges(a)
    adj = [[] for _ in range(nv)]
    for ei, (u, v) in enumerate(edges):
        adj[u].append((v, ei))
        adj[v].append((u, ei))

    def comp_sizes(banned):
        banned = set(banned)
        seen = [False] * nv
        sizes = []
        for s in range(nv):
            if seen[s]:
                continue
            stack = [s]
            seen[s] = True
            size = 0
            while stack:
                u = stack.pop()
                size += 1
                for v, ei in adj[u]:
                    if ei in banned or seen[v]:
                        continue
                    seen[v] = True
                    stack.append(v)
            sizes.append(size)
        return sorted(sizes)

    assert comp_sizes(()) == [nv]
    counts = {1: 0, 2: 0, 3: 0}
    nontrivial = []
    if exhaustive:
        for r in (1, 2, 3):
            for cut in combinations(range(len(edges)), r):
                sizes = comp_sizes(cut)
                if len(sizes) > 1:
                    counts[r] += 1
                    if sizes[0] != 1:
                        nontrivial.append((r, cut, sizes))
    return edges, counts, nontrivial


def lift(a, twists):
    n = len(a)
    twists = set(twists)
    out = [[0] * (2 * n) for _ in range(2 * n)]
    for i in range(n):
        for j in range(n):
            if not a[i][j]:
                continue
            if (i, j) in twists:
                out[i][j + n] = 1
                out[i + n][j] = 1
            else:
                out[i][j] = 1
                out[i + n][j + n] = 1
    return out


def choose_two_twists(a, forbidden):
    n = len(a)
    candidates = [(i, j) for i in range(n) for j in range(n) if a[i][j] and (i, j) not in forbidden]
    for e, f in combinations(candidates, 2):
        if e[0] != f[0] and e[1] != f[1]:
            return (e, f)
    raise AssertionError("no nonadjacent twist pair")


def main():
    points = list(combinations(range(6), 2))
    matchings = sorted(set(perfect_matchings(range(6))))
    assert len(points) == len(matchings) == 15
    a0 = [[int(p in m) for p in points] for m in matchings]
    verify_carrier(a0)

    assert rank_q(a0) == 10
    assert len(a0) - rank_q(a0) == 5

    # Star at ground point 0: every perfect matching contains exactly one such edge.
    x0 = [int(0 in p) for p in points]
    assert sum(x0) == 5
    assert verify_witness(a0, x0)

    cycle_rows = [5, 2, 10, 13, 8]
    cycle_cols = [12, 11, 6, 10, 8]
    expected = [
        [1, 0, 0, 0, 1],
        [1, 1, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 1, 1],
    ]
    assert [[a0[i][j] for j in cycle_cols] for i in cycle_rows] == expected

    cycle_inc = set()
    for ii, r in enumerate(cycle_rows):
        for jj, c in enumerate(cycle_cols):
            if expected[ii][jj]:
                cycle_inc.add((r, c))
    assert len(cycle_inc) == 10

    _, counts0, bad0 = connected_and_cut_profile(a0, exhaustive=True)
    assert counts0 == {1: 0, 2: 0, 3: 30}
    assert not bad0

    twists1 = choose_two_twists(a0, cycle_inc)
    a1 = lift(a0, twists1)
    verify_carrier(a1)
    assert rank_q(a1) == 22
    assert len(a1) - rank_q(a1) == 8
    x1 = x0 + x0
    assert verify_witness(a1, x1)

    # Because no cycle incidence is twisted, the sheet-0 cycle survives verbatim.
    for r, c in cycle_inc:
        assert a1[r][c] == 1

    _, counts1, bad1 = connected_and_cut_profile(a1, exhaustive=True)
    assert counts1 == {1: 0, 2: 0, 3: 60}
    assert not bad1

    # Second canonical lift, again avoiding the designated sheet-0 10-cycle.
    twists2 = choose_two_twists(a1, cycle_inc)
    a2 = lift(a1, twists2)
    verify_carrier(a2)
    assert len(a2) == 60
    assert len(a2) - rank_q(a2) == 14
    assert verify_witness(a2, x1 + x1)

    print("PASS")
    print("base_n=15 base_nullity_Q=5 cuts=(0,0,30 trivial)")
    print(f"twists1={twists1} n1=30 nullity_Q=8 cuts=(0,0,60 trivial)")
    print(f"twists2={twists2} n2=60 nullity_Q=14")
    print("arbitrary theorem recurrence: k_{t+1}>=2k_t-2 => k_t>=n_t/5+2")


if __name__ == "__main__":
    main()
