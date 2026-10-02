#!/usr/bin/env python3
from fractions import Fraction
from itertools import combinations

ROWS = [
    (0,5,12),(1,7,9),(2,9,14),(3,10,11),(3,4,13),
    (1,5,10),(6,7,14),(2,3,7),(1,4,8),(0,6,9),
    (2,10,12),(5,11,13),(6,8,12),(0,8,13),(4,11,14),
]
N = 15
A = [[0]*N for _ in range(N)]
for i,row in enumerate(ROWS):
    for j in row:
        A[i][j] = 1


def rank_q(M):
    M = [[Fraction(x) for x in row] for row in M]
    m, n = len(M), len(M[0])
    r = 0
    for c in range(n):
        p = next((i for i in range(r,m) if M[i][c] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        pivot = M[r][c]
        M[r] = [x/pivot for x in M[r]]
        for i in range(m):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [M[i][j] - f*M[r][j] for j in range(n)]
        r += 1
    return r


# Source-carrier checks.
assert all(sum(row) == 3 for row in A)
assert all(sum(A[i][j] for i in range(N)) == 3 for j in range(N))
assert all(len(set(ROWS[i]) & set(ROWS[j])) <= 1
           for i in range(N) for j in range(i))
assert rank_q(A) == 14

g = [1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1]
assert all(sum(A[i][j]*g[j] for j in range(N)) == 0 for i in range(N))
# rank 14 + nonzero g => ker_Q(A)=span(g).  A {-1,2}-kernel word is
# impossible because any scalar forced by a coordinate g_j=1 makes the
# coordinate with g_j=4 leave {-1,2}.
assert 1 in g and 4 in g
for lam in (-1, 2):
    assert 4*lam not in (-1,2)

# Levi graph, integer-labelled: rows 0..14, columns 15..29.
EDGES = [(i, 15+j) for i,row in enumerate(ROWS) for j in row]
assert len(EDGES) == 45


def component_sizes_after(rem):
    rem = set(rem)
    adj = [[] for _ in range(30)]
    for idx,(u,v) in enumerate(EDGES):
        if idx in rem:
            continue
        adj[u].append(v)
        adj[v].append(u)
    seen = [False]*30
    sizes = []
    for s in range(30):
        if seen[s]:
            continue
        stack = [s]
        seen[s] = True
        size = 0
        while stack:
            u = stack.pop()
            size += 1
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        sizes.append(size)
    return sorted(sizes)


cut_counts = {1:0, 2:0, 3:0}
three_cuts = []
for k in (1,2,3):
    for D in combinations(range(len(EDGES)), k):
        sizes = component_sizes_after(D)
        if len(sizes) > 1:
            cut_counts[k] += 1
            if k == 3:
                three_cuts.append((D, sizes))

assert cut_counts == {1:0, 2:0, 3:30}
assert len(three_cuts) == 30
isolated = set()
for D, sizes in three_cuts:
    assert sizes == [1,29]
    removed = {EDGES[i] for i in D}
    # The unique isolated vertex is the unique common endpoint pattern whose
    # full degree-3 star equals the removed set.
    hits = []
    for v in range(30):
        star = {e for e in EDGES if v in e}
        if star == removed:
            hits.append(v)
    assert len(hits) == 1
    isolated.add(hits[0])
assert isolated == set(range(30))

# Explicit forbidden odd 3x3 balancedness submatrix.
R = [0,12,13]
C = [0,8,12]
sub = [[A[i][j] for j in C] for i in R]
assert sub == [[1,0,1],[0,1,1],[1,1,0]]
assert all(sum(row) == 2 for row in sub)
assert all(sum(sub[i][j] for i in range(3)) == 2 for j in range(3))

print("PASS")
print("rank_Q=14 nullity_Q=1 Exact-One=UNSAT(kernel proof)")
print("cut_counts", cut_counts, "all_3cuts_are_vertex_stars=True")
print("strong_odd_cycle_rows", R, "cols", C)
