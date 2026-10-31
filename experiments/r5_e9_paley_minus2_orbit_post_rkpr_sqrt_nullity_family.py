#!/usr/bin/env python3
"""Finite exact regressions for the infinite Paley minus-two orbit family.

The arbitrary-size theorem is proved symbolically in the companion note.  This
checker validates the construction on q=11,19,43,59 and performs a modular-rank
sandwich for q<=43:

    A H = 0, rank(H)=q-1  => rank_Q(A) <= n-(q-1)
    rank_mod_p(A)=n-(q-1) => rank_Q(A) >= n-(q-1).

Hence the checked controls have exact rational nullity q-1.
"""

from collections import Counter
from itertools import combinations

PRIMES = (11, 19, 43, 59)
RANK_PRIME = 1_000_003


def residues(q):
    return {x * x % q for x in range(1, q)}


def minus_two_orbit(q):
    out = []
    seen = set()
    d = 1
    while d not in seen:
        seen.add(d)
        out.append(d)
        d = (-2 * d) % q
    assert d == 1
    return out


def rank_mod(mat, p):
    a = [[x % p for x in row] for row in mat]
    m = len(a)
    n = len(a[0]) if m else 0
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        inv = pow(a[r][c], -1, p)
        for j in range(c, n):
            a[r][j] = (a[r][j] * inv) % p
        for i in range(r + 1, m):
            z = a[i][c]
            if not z:
                continue
            for j in range(c, n):
                a[i][j] = (a[i][j] - z * a[r][j]) % p
        r += 1
        if r == m:
            break
    return r


class DSU:
    def __init__(self, n):
        self.p = list(range(n))
        self.sz = [1] * n

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return
        if self.sz[a] < self.sz[b]:
            a, b = b, a
        self.p[b] = a
        self.sz[a] += self.sz[b]


def build(q):
    R = residues(q)
    C = minus_two_orbit(q)
    assert q % 8 == 3
    assert (-1) % q not in R
    assert (-2) % q in R
    assert set(C) <= R

    variables = [(x, d) for d in C for x in range(q)]
    idx = {e: i for i, e in enumerate(variables)}
    n = len(variables)
    rows = []
    for d in C:
        nd = (-2 * d) % q
        for x in range(q):
            rows.append((
                idx[(x, d)],
                idx[((x + d) % q, d)],
                idx[((x + 2 * d) % q, nd)],
            ))
    assert len(rows) == n
    return R, C, variables, rows


def check(q, do_rank):
    R, C, variables, rows = build(q)
    n = len(variables)
    m = len(C)

    # Row size / no duplicate variable inside a row.
    assert all(len(set(row)) == 3 for row in rows)

    # Every variable has degree exactly 3.
    deg = Counter(j for row in rows for j in row)
    assert set(deg.values()) == {3}
    assert len(deg) == n

    # Linearity: no unordered variable pair is repeated in two source rows.
    owner = {}
    for ri, row in enumerate(rows):
        for a, b in combinations(sorted(row), 2):
            pair = (a, b)
            assert pair not in owner, (q, pair, owner[pair], ri)
            owner[pair] = ri

    # Variable graph induced by source rows is connected; hence the Levi graph is.
    dsu = DSU(n)
    for a, b, c in rows:
        dsu.union(a, b)
        dsu.union(a, c)
    assert len({dsu.find(i) for i in range(n)}) == 1

    # Selected directed graph has no reversed duplicate edge.  This also certifies
    # pairwise nonproportional root directions e_v-e_u.
    endpoint_pairs = []
    for x, d in variables:
        endpoint_pairs.append(frozenset((x, (x + d) % q)))
    assert len(set(endpoint_pairs)) == n

    # A*H=0 can be checked row by row without materializing H: sum the three
    # root incidence vectors e_head-e_tail and demand coefficient-wise zero.
    for row in rows:
        coeff = Counter()
        for j in row:
            x, d = variables[j]
            coeff[x] -= 1
            coeff[(x + d) % q] += 1
        assert all(v == 0 for v in coeff.values())

    # One fixed difference d gives a directed q-cycle, so root-incidence rank is q-1.
    d0 = C[0]
    orbit = []
    x = 0
    for _ in range(q):
        orbit.append(x)
        x = (x + d0) % q
    assert len(set(orbit)) == q and x == 0
    root_rank = q - 1

    # Exact UNSAT cycle obstruction once ker(A)=root space: q is not divisible by 3.
    assert q % 3 != 0

    if do_rank:
        dense = [[0] * n for _ in range(n)]
        for i, row in enumerate(rows):
            for j in row:
                dense[i][j] = 1
        rm = rank_mod(dense, RANK_PRIME)
        assert rm == n - root_rank, (q, n, rm, root_rank)
    else:
        rm = None

    # Asymptotic inequality used by the theorem.
    assert m <= (q - 1) // 2
    assert 2 * n < q * q

    return {
        "q": q,
        "orbit": m,
        "n": n,
        "root_rank": root_rank,
        "rank_mod": rm,
        "nullity_exact_when_rank_checked": root_rank if do_rank else None,
    }


def main():
    results = []
    for q in PRIMES:
        results.append(check(q, do_rank=(q <= 43)))

    expected = {
        11: (5, 55, 10),
        19: (9, 171, 18),
        43: (7, 301, 42),
        59: (29, 1711, 58),
    }
    for r in results:
        assert (r["orbit"], r["n"], r["root_rank"]) == expected[r["q"]]

    print("Paley minus-two orbit family regression: PASS")
    for r in results:
        suffix = (
            f", rank_mod={r['rank_mod']}, exact_nullity={r['root_rank']}"
            if r["rank_mod"] is not None else
            ", structural/Fourier theorem control"
        )
        print(
            f"q={r['q']}: |C|={r['orbit']}, n={r['n']}, "
            f"root_rank={r['root_rank']}" + suffix
        )
    print("linear cubic = PASS")
    print("connected = PASS")
    print("root directions projectively distinct = PASS")
    print("cycle-sum UNSAT obstruction q%3!=0 = PASS")


if __name__ == "__main__":
    main()
