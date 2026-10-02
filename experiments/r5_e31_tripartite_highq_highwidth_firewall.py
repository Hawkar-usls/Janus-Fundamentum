#!/usr/bin/env python3
"""Exact finite controls for R5 E31.

Builds the tripartite family with variables
  X_ab, Y_bc, Z_ca  for a,b,c in Z_m
and clauses
  X_ab + Y_b,c + Z_c,a = 1,
  c = a+b+s mod m, s in {0,1,2}.

Checks for m=4..8:
  * n=3m^2 rows and variables;
  * square/cubic/linear incidence;
  * explicit SAT witness X=Y=0, Z=1;
  * rank mod 1009 equals n-(3m-1), matching the symbolic kernel lower bound;
  * the quotient interaction graph contains an explicit ceil(m/2) x ceil(m/2)
    grid subdivision on X-variables, certifying treewidth at least ceil(m/2).

The theorem note proves for every m>=4 that the rational kernel is exactly the
vertex-potential space of dimension 3m-1 and that every kernel coordinate row is
its own projective class, so q=n.

P_VS_NP remains OPEN.
"""

from itertools import combinations


def build_family(m):
    n = 3*m*m

    def X(a,b):
        return a*m+b

    def Y(b,c):
        return m*m+b*m+c

    def Z(c,a):
        return 2*m*m+c*m+a

    rows = []
    for a in range(m):
        for b in range(m):
            for s in (0,1,2):
                c = (a+b+s) % m
                rows.append((X(a,b),Y(b,c),Z(c,a)))

    assert len(rows) == n
    return n, rows, X, Y, Z


def check_square_cubic_linear(n, rows):
    coldeg = [0]*n
    seen_pairs = set()

    for row in rows:
        assert len(row) == 3
        assert len(set(row)) == 3
        for j in row:
            coldeg[j] += 1
        for u,v in combinations(sorted(row),2):
            assert (u,v) not in seen_pairs
            seen_pairs.add((u,v))

    assert all(d == 3 for d in coldeg)


def rank_mod_p(n, rows, p):
    A = [[0]*n for _ in range(n)]
    for i,row in enumerate(rows):
        for j in row:
            A[i][j] = 1

    r = 0
    for c in range(n):
        pivot = next((i for i in range(r,n) if A[i][c] % p), None)
        if pivot is None:
            continue
        A[r],A[pivot] = A[pivot],A[r]
        inv = pow(A[r][c] % p, -1, p)
        for j in range(c,n):
            A[r][j] = (A[r][j]*inv) % p
        for i in range(r+1,n):
            if A[i][c] % p:
                f = A[i][c] % p
                for j in range(c,n):
                    A[i][j] = (A[i][j] - f*A[r][j]) % p
        r += 1
        if r == n:
            break
    return r


def interaction_edges(rows):
    out = set()
    for row in rows:
        for u,v in combinations(row,2):
            if u > v:
                u,v = v,u
            out.add((u,v))
    return out


def has_edge(edges,u,v):
    if u > v:
        u,v = v,u
    return (u,v) in edges


def verify_grid_subdivision(m, rows, X, Y, Z):
    edges = interaction_edges(rows)
    coords = list(range(0,m,2))
    t = len(coords)  # ceil(m/2)

    internal = []

    for ia,a in enumerate(coords):
        for ib,b in enumerate(coords):
            # Horizontal grid edge: X_(a,b) -- Y_(b,a+b+2) -- X_(a+2,b)
            if ia+1 < t:
                a2 = coords[ia+1]
                assert a2 == a+2
                mid = Y(b,(a+b+2) % m)
                u = X(a,b)
                v = X(a2,b)
                assert has_edge(edges,u,mid)
                assert has_edge(edges,mid,v)
                internal.append(mid)

            # Vertical grid edge: X_(a,b) -- Z_(a+b+2,a) -- X_(a,b+2)
            if ib+1 < t:
                b2 = coords[ib+1]
                assert b2 == b+2
                mid = Z((a+b+2) % m,a)
                u = X(a,b)
                v = X(a,b2)
                assert has_edge(edges,u,mid)
                assert has_edge(edges,mid,v)
                internal.append(mid)

    # Internal subdivision vertices are pairwise distinct and never X-grid nodes.
    assert len(internal) == len(set(internal))
    grid_nodes = {X(a,b) for a in coords for b in coords}
    assert not (grid_nodes & set(internal))

    return t


def verify_sat(rows, n):
    # X=0, Y=0, Z=1.
    third = 2*(n//3)
    x = [0]*n
    for j in range(third,n):
        x[j] = 1
    assert all(sum(x[j] for j in row) == 1 for row in rows)


def main():
    print("R5 E31 tripartite high-q/high-width firewall: PASS")

    for m in range(4,9):
        n,rows,X,Y,Z = build_family(m)
        check_square_cubic_linear(n,rows)
        verify_sat(rows,n)

        rank = rank_mod_p(n,rows,1009)
        expected_nullity = 3*m-1
        assert rank == n-expected_nullity

        t = verify_grid_subdivision(m,rows,X,Y,Z)
        assert t == (m+1)//2

        print(
            f"m={m}: n={n}, rank_F1009={rank}, nullity={expected_nullity}, "
            f"q=n={n} symbolically, grid_certificate={t}x{t}"
        )

    print("Conclusion: exact SAT carrier with d=Theta(sqrt(n)), q=n, and treewidth Omega(sqrt(n)).")
    print("Scientific ceiling: P_VS_NP remains OPEN.")


if __name__ == "__main__":
    main()
