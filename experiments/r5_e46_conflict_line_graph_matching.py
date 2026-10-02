#!/usr/bin/env python3
"""Finite exact controls for R5 E46.

Builds the square+cubic+linear incidence system whose rows are the ten triangles
of K5 and whose variables are the ten edges of K5. Verifies:
  * square / row-weight-3 / column-weight-3 / linear;
  * the conflict graph is exactly L(K5);
  * alpha(conflict)=nu(K5)=2 by exact brute force;
  * no Exact-One witness exists (n=10 is already incompatible with n/3).

The theorem itself is general: whenever a supplied root graph H satisfies
G_A=L(H), Exact-One reduces to testing whether H has a matching of size n/3.
"""

from itertools import combinations


def all_edges(vertices):
    return list(combinations(vertices, 2))


def build_k5_triangle_edge_incidence():
    V = range(5)
    edges = all_edges(V)
    eidx = {e:i for i,e in enumerate(edges)}
    triangles = list(combinations(V, 3))
    A = []
    for T in triangles:
        row = [0]*len(edges)
        for e in combinations(T, 2):
            row[eidx[tuple(sorted(e))]] = 1
        A.append(row)
    return A, edges


def conflict_graph(A):
    n = len(A[0])
    adj = [set() for _ in range(n)]
    for row in A:
        vs = [j for j,x in enumerate(row) if x]
        for a,b in combinations(vs, 2):
            adj[a].add(b); adj[b].add(a)
    return adj


def line_graph_adj(edges):
    n = len(edges)
    adj = [set() for _ in range(n)]
    for i,j in combinations(range(n), 2):
        if set(edges[i]) & set(edges[j]):
            adj[i].add(j); adj[j].add(i)
    return adj


def alpha_bruteforce(adj):
    n = len(adj)
    best = 0
    for mask in range(1<<n):
        k = mask.bit_count()
        if k <= best:
            continue
        ok = True
        for i in range(n):
            if (mask>>i)&1:
                for j in adj[i]:
                    if j>i and ((mask>>j)&1):
                        ok = False; break
                if not ok: break
        if ok: best = k
    return best


def matching_number_bruteforce(edges):
    n = len(edges)
    best = 0
    for mask in range(1<<n):
        k = mask.bit_count()
        if k <= best: continue
        used=set(); ok=True
        for i,e in enumerate(edges):
            if (mask>>i)&1:
                if e[0] in used or e[1] in used:
                    ok=False; break
                used.update(e)
        if ok: best=k
    return best


def main():
    A, edges = build_k5_triangle_edge_incidence()
    n = len(A)
    assert n == len(A[0]) == 10
    assert all(sum(r)==3 for r in A)
    assert all(sum(A[i][j] for i in range(n))==3 for j in range(n))
    for i,j in combinations(range(n),2):
        assert sum(A[i][c] and A[j][c] for c in range(n)) <= 1

    G = conflict_graph(A)
    L = line_graph_adj(edges)
    assert G == L
    a = alpha_bruteforce(G)
    nu = matching_number_bruteforce(edges)
    assert a == nu == 2

    print("R5 E46 conflict line-graph matching control: PASS")
    print("K5 triangle-edge carrier: n=10, square/cubic/linear")
    print("conflict graph = L(K5): PASS")
    print("alpha(L(K5)) = matching_number(K5) = 2")
    print("Exact-One target size n/3 is nonintegral, so control is UNSAT")


if __name__ == "__main__":
    main()
