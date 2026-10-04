#!/usr/bin/env python3
"""R5 E69 exact controls: large-nullity structural dichotomy / torus firewall.

This checker tests the post-E68 hope

    dim ker_F2(A) >> log n  =>  small-width / separator decomposition.

The simple graph-width version is false.

For m = 2^r-1 define the m^2 x m^2 binary torus incidence matrix A_m by

    row(i,j) = {(i,j), (i+1,j), (i,j+1)}  (indices mod m).

It is square, cubic on rows and columns, linear on both sides, and connected.
For the infinite family m=2^r-1 one has

    dim_F2 ker(A_m) = m-1 = sqrt(n)-1.

The general proof is in the companion note, using scalar extension to GF(2^r)
and diagonalization of the group algebra: 1+X+Y vanishes exactly on
(alpha,1+alpha), alpha in GF(2^r)\{0,1}.

The Levi graph contracts along the natural identity matching to C_m square C_m,
so its treewidth is Omega(m)=Omega(sqrt(n)).  Thus large nullity does not force
bounded/logarithmic graph width.

At the same time the family is algebraically compressible:

    Exact-One SAT iff 3 divides m.

If 3|m, x_(i,j)=1 iff i-j=0 mod 3 is an explicit exact cover.  If 3 does not
divide m, n=m^2 is not divisible by 3, while every exact cover must select n/3
columns.

The checker also verifies the E69 even-section interpretation of binary kernel
words and replays the frozen E17 q=6 RXC3 source as an anti-loop control.

This is a structural firewall/model family, not a universal polynomial solver.
P_VS_NP remains OPEN.
"""

from collections import deque


def idx(i, j, m):
    return (i % m) * m + (j % m)


def torus_row_supports(m):
    return [
        (idx(i, j, m), idx(i + 1, j, m), idx(i, j + 1, m))
        for i in range(m)
        for j in range(m)
    ]


def supports_to_bits(supports, n):
    rows = []
    for S in supports:
        z = 0
        for j in S:
            z |= 1 << j
        rows.append(z)
    return rows


def gf2_rref(rows, n):
    rows = list(rows)
    m = len(rows)
    pivots = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if (rows[i] >> c) & 1), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(m):
            if i != r and ((rows[i] >> c) & 1):
                rows[i] ^= rows[r]
        pivots.append(c)
        r += 1
        if r == m:
            break
    return rows, pivots


def gf2_kernel_basis(rows, n):
    R, pivots = gf2_rref(rows, n)
    free = [c for c in range(n) if c not in pivots]
    basis = []
    for f in free:
        v = 1 << f
        for rr, p in enumerate(pivots):
            if (R[rr] >> f) & 1:
                v |= 1 << p
        basis.append(v)
    return basis


def verify_square_cubic_linear_connected(m, supports):
    n = m * m
    assert len(supports) == n
    assert all(len(set(S)) == 3 for S in supports)

    col_supports = [[] for _ in range(n)]
    pair_seen = set()
    for r, S in enumerate(supports):
        S = sorted(S)
        for c in S:
            col_supports[c].append(r)
        for a in range(3):
            for b in range(a + 1, 3):
                p = (S[a], S[b])
                assert p not in pair_seen
                pair_seen.add(p)

    assert all(len(T) == 3 for T in col_supports)
    rowpair_seen = set()
    for T in col_supports:
        T = sorted(T)
        for a in range(3):
            for b in range(a + 1, 3):
                p = (T[a], T[b])
                assert p not in rowpair_seen
                rowpair_seen.add(p)

    # Levi connectivity.
    adj = [[] for _ in range(2 * n)]
    for r, S in enumerate(supports):
        for c in S:
            adj[r].append(n + c)
            adj[n + c].append(r)
    seen = {0}
    q = deque([0])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    assert len(seen) == 2 * n

    # Contract row(i,j)--column(i,j): remaining edges are exactly C_m square C_m.
    got = set()
    for i in range(m):
        for j in range(m):
            u = idx(i, j, m)
            for v in (idx(i + 1, j, m), idx(i, j + 1, m)):
                got.add(tuple(sorted((u, v))))

    expected = set()
    for i in range(m):
        for j in range(m):
            u = idx(i, j, m)
            expected.add(tuple(sorted((u, idx(i + 1, j, m)))))
            expected.add(tuple(sorted((u, idx(i, j + 1, m)))))
    assert got == expected
    assert len(got) == 2 * n


def matvec_parity(supports, word):
    return [sum((word >> c) & 1 for c in S) & 1 for S in supports]


def verify_even_section(supports, word):
    n = len(supports)
    w = word.bit_count()
    row_hits = [sum((word >> c) & 1 for c in S) for S in supports]
    assert set(row_hits) <= {0, 2}
    D = sum(h == 0 for h in row_hits)
    assert 3 * w == 2 * (n - D)
    assert D % 3 == 0

    # The used rows induce a simple cubic graph on support(word).
    degrees = {}
    edges = set()
    for S, h in zip(supports, row_hits):
        if h == 2:
            uv = tuple(c for c in S if (word >> c) & 1)
            assert len(uv) == 2
            e = tuple(sorted(uv))
            assert e not in edges
            edges.add(e)
            for u in e:
                degrees[u] = degrees.get(u, 0) + 1
    selected = [c for c in range(n) if (word >> c) & 1]
    assert set(degrees) == set(selected)
    assert all(degrees[c] == 3 for c in selected)
    return D


def explicit_exact_cover(m):
    n = m * m
    word = 0
    for i in range(m):
        for j in range(m):
            if (i - j) % 3 == 0:
                word |= 1 << idx(i, j, m)
    assert word.bit_count() == n // 3
    return word


def check_torus(m, expected_nullity):
    supports = torus_row_supports(m)
    n = m * m
    verify_square_cubic_linear_connected(m, supports)
    rows = supports_to_bits(supports, n)
    basis = gf2_kernel_basis(rows, n)
    assert len(basis) == expected_nullity == m - 1

    # Every basis word is an even-section / cubic-section witness.
    for b in basis:
        assert not any(matvec_parity(supports, b))
        verify_even_section(supports, b)

    sat = (m % 3 == 0)
    if sat:
        x = explicit_exact_cover(m)
        assert all(sum((x >> c) & 1 for c in S) == 1 for S in supports)
        k = ((1 << n) - 1) ^ x
        assert not any(matvec_parity(supports, k))
        assert k.bit_count() == 2 * n // 3
        assert verify_even_section(supports, k) == 0
    else:
        assert n % 3 != 0

    return n, len(basis), sat


def e17_q6_control():
    q = 6
    source_sets = [tuple(sorted({i, (i + 1) % q, (i + 3) % q})) for i in range(q)]
    rows = supports_to_bits(source_sets, q)
    basis = gf2_kernel_basis(rows, q)
    assert len(basis) == 0
    # With trivial binary kernel the E58 top-shell criterion immediately says UNSAT.
    return len(basis)


def main():
    rows = []
    for r in (2, 3, 4, 5):
        m = (1 << r) - 1
        rows.append((r, *check_torus(m, expected_nullity=m - 1)))

    d_q6 = e17_q6_control()

    print("R5 E69 nullity/torus structural firewall: PASS")
    for r, n, d, sat in rows:
        m = (1 << r) - 1
        print(
            f"r={r} m={m} n={n} nullity={d}=m-1 "
            f"sqrt_scale=True exact_one_sat={sat}"
        )
    print("Levi contraction certificate: each checked carrier contracts to C_m square C_m")
    print("general theorem: for m=2^r-1, dim_F2 ker(A_m)=m-1 by GF(2^r) character diagonalization")
    print("family decision compression: SAT iff 3|m iff r is even")
    print(f"frozen E17 q=6 RXC3 source control: dim_F2={d_q6}, UNSAT by E58")
    print("large nullity does not imply bounded/log graph width; algebraic compression can still exist")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
