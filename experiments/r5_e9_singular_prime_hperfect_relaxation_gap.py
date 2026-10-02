#!/usr/bin/env python3
from fractions import Fraction
from itertools import combinations

ROWS = [
    (0,6,9),
    (1,2,12),
    (2,4,11),
    (1,3,13),
    (3,4,10),
    (0,5,12),
    (6,8,13),
    (5,7,10),
    (4,8,9),
    (1,7,9),
    (8,10,14),
    (3,7,11),
    (6,11,12),
    (5,13,14),
    (0,2,14),
]
N = 15


def rank_q(mat):
    a = [[Fraction(v) for v in row] for row in mat]
    m, n = len(a), len(a[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        q = a[r][c]
        a[r] = [v / q for v in a[r]]
        for i in range(m):
            if i != r and a[i][c]:
                q = a[i][c]
                a[i] = [x - q*y for x, y in zip(a[i], a[r])]
        r += 1
        if r == m:
            break
    return r


def build_matrix():
    A = [[0]*N for _ in range(N)]
    for i, row in enumerate(ROWS):
        for j in row:
            A[i][j] = 1
    return A


def conflict_edges():
    E = set()
    for row in ROWS:
        for u, v in combinations(row, 2):
            E.add(tuple(sorted((u, v))))
    return E


def independent(S, E):
    return all(tuple(sorted((u, v))) not in E for u, v in combinations(S, 2))


def connected(vertices, edges):
    if not vertices:
        return True
    adj = {v:set() for v in vertices}
    for a,b in edges:
        adj[a].add(b); adj[b].add(a)
    seen = {next(iter(vertices))}
    stack = list(seen)
    while stack:
        v = stack.pop()
        for w in adj[v]:
            if w not in seen:
                seen.add(w); stack.append(w)
    return len(seen) == len(vertices)


def levi_edges():
    return [(('r',i),('c',j)) for i,row in enumerate(ROWS) for j in row]


def component_sizes_after_cut(edges, cut):
    verts = {x for e in edges for x in e}
    remain = [e for e in edges if e not in cut]
    adj = {v:set() for v in verts}
    for a,b in remain:
        adj[a].add(b); adj[b].add(a)
    unseen=set(verts); sizes=[]
    while unseen:
        s=next(iter(unseen)); unseen.remove(s); stack=[s]; k=0
        while stack:
            v=stack.pop(); k+=1
            for w in adj[v]:
                if w in unseen:
                    unseen.remove(w); stack.append(w)
        sizes.append(k)
    return sorted(sizes)


def main():
    A = build_matrix()
    assert all(sum(row)==3 for row in A)
    assert all(sum(A[i][j] for i in range(N))==3 for j in range(N))
    assert all(len(set(ROWS[i]) & set(ROWS[j])) <= 1
               for i in range(N) for j in range(i))
    assert rank_q(A) == 14

    E = conflict_edges()
    assert len(E) == 45
    assert connected(set(range(N)), E)

    # Exact clique number = 3.
    assert any(all(tuple(sorted((u,v))) in E for u,v in combinations(S,2))
               for S in combinations(range(N),3))
    assert not any(all(tuple(sorted((u,v))) in E for u,v in combinations(S,2))
                   for S in combinations(range(N),4))

    # Exact alpha = 4.
    assert independent((2,3,5,6), E)
    assert not any(independent(S,E) for S in combinations(range(N),5))

    # Exact Levi <=3 cut census: only 30 trivial cubic vertex stars at size 3.
    LE = levi_edges()
    V = {x for e in LE for x in e}
    assert connected(V, LE)
    for k in (1,2):
        assert not any(len(component_sizes_after_cut(LE,set(F))) > 1
                       for F in combinations(LE,k))
    cuts3=[]
    for F in combinations(LE,3):
        sizes=component_sizes_after_cut(LE,set(F))
        if len(sizes)>1:
            cuts3.append((F,sizes))
    assert len(cuts3)==30
    assert all(sizes == [1,29] for _,sizes in cuts3)

    # h-perfect relaxation target certificate.
    # omega=3 makes x*=1/3 satisfy every clique inequality.
    # For every odd hole length l>=5, l/3 <= (l-1)/2.
    for l in range(5,N+1,2):
        assert Fraction(l,3) <= Fraction(l-1,2)
    # Row triangles upper-bound sum x by 5 because every vertex occurs in 3 rows.
    assert sum(len(r) for r in ROWS) == 3*N
    h_relax_opt = Fraction(N,3)
    assert h_relax_opt == 5

    print('PASS')
    print('rank_Q=14 nullity_Q=1')
    print('alpha=4 omega=3 target=5')
    print('Levi cuts: 1->0, 2->0, 3->30 all trivial')
    print('h-perfect relaxation optimum=5 via x*=1/3 + row-triangle upper bound')


if __name__ == '__main__':
    main()
