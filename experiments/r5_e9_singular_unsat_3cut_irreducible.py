#!/usr/bin/env python3
from itertools import combinations
from collections import deque

ROWS = [
    (0,5,12),(1,7,9),(2,9,14),(3,10,11),(3,4,13),
    (1,5,10),(6,7,14),(2,3,7),(1,4,8),(0,6,9),
    (2,10,12),(5,11,13),(6,8,12),(0,8,13),(4,11,14),
]

# Vertices 0..14 are rows; 15..29 are columns.
N = 30
EDGES = [(r, 15+c) for r,triple in enumerate(ROWS) for c in triple]
assert len(EDGES) == 45


def components_after_removed(removed_indices):
    removed = set(removed_indices)
    adj = [[] for _ in range(N)]
    for idx,(u,v) in enumerate(EDGES):
        if idx in removed:
            continue
        adj[u].append(v)
        adj[v].append(u)
    seen = [False]*N
    comps = []
    for s in range(N):
        if seen[s]:
            continue
        q = deque([s]); seen[s] = True; comp=[]
        while q:
            u=q.popleft(); comp.append(u)
            for v in adj[u]:
                if not seen[v]:
                    seen[v]=True; q.append(v)
        comps.append(tuple(sorted(comp)))
    return sorted(comps, key=lambda x:(len(x),x))


def vertex_star_indices(v):
    return frozenset(i for i,e in enumerate(EDGES) if v in e)


def main():
    stars = {vertex_star_indices(v) for v in range(N)}
    assert all(len(s)==3 for s in stars)
    assert len(stars)==30

    disconnecting=[]
    nontrivial=[]
    for comb in combinations(range(len(EDGES)),3):
        comps=components_after_removed(comb)
        if len(comps)>1:
            cset=frozenset(comb)
            sizes=tuple(sorted(len(c) for c in comps))
            disconnecting.append((cset,sizes))
            if sizes != (1,29):
                nontrivial.append((cset,sizes))

    assert len(disconnecting)==30, len(disconnecting)
    assert not nontrivial, nontrivial
    assert {c for c,_ in disconnecting} == stars
    assert {sizes for _,sizes in disconnecting} == {(1,29)}

    print('vertices =', N)
    print('edges =', len(EDGES))
    print('triples_checked =', 45*44*43//6)
    print('disconnecting_3cuts =', len(disconnecting))
    print('all_3cuts_are_vertex_stars = true')
    print('nontrivial_3cuts = 0')
    print('PASS')

if __name__ == '__main__':
    main()
