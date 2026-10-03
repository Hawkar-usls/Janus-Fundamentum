#!/usr/bin/env python3
"""R5 E64 exact controls: connected post-quotient nullity firewall.

This checker moves beyond the raw E12 gadget representation and tests the
quotient-level hypothesis directly on genuine connected v_3 configurations.

It constructs two independent square-cubic-linear incidence matrices R:

1. Tutte-Coxeter / generalized quadrangle GQ(2,2):
   * q = 15,
   * Levi graph connected, cubic, bipartite, girth 8,
   * rank_Q(R) = 10, nullity = 5,
   * exactly 6 {-1,2}-valued kernel vectors, hence SAT.

2. Tutte 12-cage / generalized hexagon GH(2,2), reconstructed from the
   standard LCF notation:
   * q = 63,
   * Levi graph connected, cubic, bipartite, girth 12,
   * rank_Q(R) = 49, nullity = 14,
   * no {-1,2}-valued kernel vector among all 2^14 free-coordinate
     assignments, hence UNSAT.

For any square cubic R,
    R x = 1 with x in {0,1}^q
iff
    y = 3x - 1 belongs to ker_Q(R) and y_i in {-1,2}.

Scientific ceiling:
These fixtures refute tiny/automatic connected-quotient nullity hopes and show
that singularity, connectivity, high girth, and strong symmetry do not force a
two-level kernel vector.  They do NOT prove an asymptotic lower bound on
quotient nullity and do NOT give a universal polynomial algorithm.

P_VS_NP remains OPEN.
"""

from collections import deque
from fractions import Fraction
import itertools


TUTTE12_LCF = [
    17, 27, -13, -59, -35, 35, -11, 13, -53,
    53, -27, 21, 57, 11, -21, -57, 59, -17,
]


def rank_q(M):
    A = [[Fraction(v) for v in row] for row in M]
    m = len(A)
    n = len(A[0]) if m else 0
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if A[i][c]), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        z = A[r][c]
        A[r] = [v / z for v in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[r])]
        r += 1
        if r == m:
            break
    return r


def rref_q(M):
    A = [[Fraction(v) for v in row] for row in M]
    m = len(A)
    n = len(A[0]) if m else 0
    pivots = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if A[i][c]), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        z = A[r][c]
        A[r] = [v / z for v in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[r])]
        pivots.append(c)
        r += 1
        if r == m:
            break
    return A, pivots


def two_level_kernel_count(M):
    """Exact 2^d search using the free coordinates of an RREF basis."""
    R, pivots = rref_q(M)
    n = len(M[0])
    free = [c for c in range(n) if c not in pivots]
    count = 0

    for vals in itertools.product((-1, 2), repeat=len(free)):
        ok = True
        for rr, _pc in enumerate(pivots):
            value = -sum(R[rr][f] * v for f, v in zip(free, vals))
            if value not in (Fraction(-1), Fraction(2)):
                ok = False
                break
        if ok:
            count += 1

    return len(free), count


def graph_from_incidence(M):
    q = len(M)
    assert q and all(len(row) == q for row in M)
    adj = [set() for _ in range(2 * q)]
    for i, row in enumerate(M):
        for j, v in enumerate(row):
            if v:
                a, b = i, q + j
                adj[a].add(b)
                adj[b].add(a)
    return adj


def connected(adj):
    seen = {0}
    todo = [0]
    while todo:
        u = todo.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                todo.append(v)
    return len(seen) == len(adj)


def girth(adj):
    best = None
    n = len(adj)
    for s in range(n):
        dist = [-1] * n
        parent = [-1] * n
        dist[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    parent[v] = u
                    q.append(v)
                elif parent[u] != v:
                    g = dist[u] + dist[v] + 1
                    if best is None or g < best:
                        best = g
    return best


def verify_square_cubic_linear(M, expected_girth):
    q = len(M)
    assert q > 0 and all(len(row) == q for row in M)
    assert all(v in (0, 1) for row in M for v in row)
    assert all(sum(row) == 3 for row in M)
    assert all(sum(M[i][j] for i in range(q)) == 3 for j in range(q))

    for i in range(q):
        for j in range(i + 1, q):
            assert sum(a * b for a, b in zip(M[i], M[j])) <= 1
            assert sum(M[k][i] * M[k][j] for k in range(q)) <= 1

    adj = graph_from_incidence(M)
    assert all(len(N) == 3 for N in adj)
    assert connected(adj)
    assert girth(adj) == expected_girth
    return adj


def perfect_matchings_k6():
    def rec(rem):
        if not rem:
            yield ()
            return
        a = min(rem)
        for b in sorted(rem - {a}):
            pair = tuple(sorted((a, b)))
            for rest in rec(rem - {a, b}):
                yield tuple(sorted((pair,) + rest))

    out = []
    seen = set()
    for M in rec(set(range(6))):
        f = frozenset(M)
        if f not in seen:
            seen.add(f)
            out.append(M)
    assert len(out) == 15
    return out


def tutte_coxeter_incidence():
    """15 edges of K6 versus its 15 perfect matchings."""
    edges = list(itertools.combinations(range(6), 2))
    pms = perfect_matchings_k6()
    pos = {e: i for i, e in enumerate(edges)}
    M = [[0] * 15 for _ in range(15)]
    for j, F in enumerate(pms):
        for e in F:
            M[pos[e]][j] = 1
    return M


def graph_from_lcf(base, repeat):
    seq = list(base) * repeat
    n = len(seq)
    adj = [set() for _ in range(n)]

    for i in range(n):
        j = (i + 1) % n
        adj[i].add(j)
        adj[j].add(i)

    for i, step in enumerate(seq):
        j = (i + step) % n
        adj[i].add(j)
        adj[j].add(i)

    assert all(len(N) == 3 for N in adj)
    return adj


def bipartite_incidence(adj):
    n = len(adj)
    color = [None] * n
    color[0] = 0
    q = deque([0])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if color[v] is None:
                color[v] = 1 - color[u]
                q.append(v)
            else:
                assert color[v] != color[u]

    assert all(c is not None for c in color)
    left = [i for i, c in enumerate(color) if c == 0]
    right = [i for i, c in enumerate(color) if c == 1]
    assert len(left) == len(right)
    rpos = {v: j for j, v in enumerate(right)}

    M = [[0] * len(right) for _ in left]
    for i, u in enumerate(left):
        for v in adj[u]:
            M[i][rpos[v]] = 1
    return M


def tutte12_incidence():
    adj = graph_from_lcf(TUTTE12_LCF, 7)
    assert len(adj) == 126
    assert connected(adj)
    assert girth(adj) == 12
    M = bipartite_incidence(adj)
    assert len(M) == 63
    return M


def check_fixture(name, M, expected_girth, expected_rank, expected_nullity, expected_two_level):
    verify_square_cubic_linear(M, expected_girth)
    r = rank_q(M)
    d, count = two_level_kernel_count(M)

    assert r == expected_rank
    assert d == expected_nullity == len(M) - r
    assert count == expected_two_level

    print(
        f"{name}: q={len(M)} girth={expected_girth} "
        f"rank={r} nullity={d} two_level={count} sat={bool(count)}"
    )


def main():
    tc = tutte_coxeter_incidence()
    check_fixture(
        "TUTTE_COXETER_GQ22",
        tc,
        expected_girth=8,
        expected_rank=10,
        expected_nullity=5,
        expected_two_level=6,
    )

    t12 = tutte12_incidence()
    check_fixture(
        "TUTTE_12_CAGE_GH22",
        t12,
        expected_girth=12,
        expected_rank=49,
        expected_nullity=14,
        expected_two_level=0,
    )

    print("R5 E64 connected post-quotient nullity firewall: PASS")
    print("connected quotient nullity can reach 5 on SAT q=15 and 14 on UNSAT q=63")
    print("singularity/high girth/symmetry do not force the required {-1,2} kernel vector")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
