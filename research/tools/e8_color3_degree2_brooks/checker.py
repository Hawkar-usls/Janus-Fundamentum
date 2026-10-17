#!/usr/bin/env python3
import itertools
from collections import deque


def normalize_graph(n, edges):
    E={tuple(sorted(e)) for e in edges if e[0]!=e[1]}
    assert all(0<=u<n and 0<=v<n for u,v in E)
    return E


def adjacency(n, edges, active=None):
    if active is None:
        active=set(range(n))
    adj={v:set() for v in active}
    for u,v in edges:
        if u in active and v in active:
            adj[u].add(v); adj[v].add(u)
    return adj


def peel_degree2(n, edges):
    active=set(range(n))
    adj=adjacency(n,edges,active)
    q=deque(v for v in active if len(adj[v])<=2)
    inq=set(q)
    stack=[]
    while q:
        v=q.popleft(); inq.discard(v)
        if v not in active or len(adj[v])>2:
            continue
        nbrs=tuple(sorted(adj[v]))
        stack.append((v,nbrs))
        active.remove(v)
        for u in nbrs:
            adj[u].remove(v)
            if len(adj[u])<=2 and u not in inq:
                q.append(u); inq.add(u)
        del adj[v]
    return active, stack


def components(active, edges):
    adj=adjacency(max(active)+1 if active else 0,edges,active) if active else {}
    comps=[]; seen=set()
    for s in active:
        if s in seen: continue
        comp=set([s]); seen.add(s); q=[s]
        while q:
            v=q.pop()
            for u in adj[v]:
                if u not in seen:
                    seen.add(u); comp.add(u); q.append(u)
        comps.append(comp)
    return comps


def is_k4_component(comp, edges):
    if len(comp)!=4: return False
    cnt=sum(1 for u,v in edges if u in comp and v in comp)
    return cnt==6


def brute_3color(n, edges, active=None):
    if active is None: active=set(range(n))
    verts=sorted(active)
    col={}
    adj=adjacency(n,edges,active)
    # order by degree for speed
    verts.sort(key=lambda v:-len(adj[v]))
    def rec(i):
        if i==len(verts): return dict(col)
        v=verts[i]
        forbidden={col[u] for u in adj[v] if u in col}
        for c in range(3):
            if c not in forbidden:
                col[v]=c
                ans=rec(i+1)
                if ans is not None: return ans
                del col[v]
        return None
    return rec(0)


def reconstruct(stack, coloring, edges):
    col=dict(coloring)
    for v,nbrs in reversed(stack):
        used={col[u] for u in nbrs if u in col}
        c=next(c for c in range(3) if c not in used)
        col[v]=c
    return col


def valid_coloring(n, edges, col):
    return len(col)==n and all(col[u]!=col[v] for u,v in edges)


def brooks_terminal_prediction(n, edges):
    active, stack=peel_degree2(n,edges)
    if not active:
        return True, active, stack
    adj=adjacency(n,edges,active)
    if max(len(adj[v]) for v in active)>3:
        return None, active, stack
    bad=any(is_k4_component(comp,edges) for comp in components(active,edges))
    return (not bad), active, stack


def exhaustive_subcubic_replay():
    checked=0
    for n in range(1,6):
        universe=list(itertools.combinations(range(n),2))
        for mask in range(1<<len(universe)):
            edges={e for i,e in enumerate(universe) if (mask>>i)&1}
            if any(sum(v in e for e in edges)>3 for v in range(n)):
                continue
            pred,active,stack=brooks_terminal_prediction(n,edges)
            assert pred is not None
            brute=brute_3color(n,edges)
            assert pred==(brute is not None), (n,edges,pred,brute)
            if pred:
                core_col=brute_3color(n,edges,active)
                full=reconstruct(stack,core_col or {},edges)
                assert valid_coloring(n,edges,full)
            checked+=1
    return checked


def nad3_truth_table():
    for nbr_cols in itertools.product(range(3),repeat=3):
        extendable=any(all(c!=x for x in nbr_cols) for c in range(3))
        assert extendable == (len(set(nbr_cols))<=2)


def degree4_silence_controls():
    # K5 is 4-regular: peeling must be silent.
    n=5; K5=set(itertools.combinations(range(n),2))
    active,stack=peel_degree2(n,K5)
    assert active==set(range(n)) and not stack
    assert brute_3color(n,K5) is None

    # Octahedral graph K_{2,2,2} is planar, 4-regular, and 3-colourable; peeling is also silent.
    parts=[{0,1},{2,3},{4,5}]
    E=set()
    for i in range(3):
        for j in range(i+1,3):
            for u in parts[i]:
                for v in parts[j]: E.add(tuple(sorted((u,v))))
    active,stack=peel_degree2(6,E)
    assert active==set(range(6)) and not stack
    col=brute_3color(6,E)
    assert col is not None and valid_coloring(6,E,col)


def main():
    checked=exhaustive_subcubic_replay()
    nad3_truth_table()
    degree4_silence_controls()
    print(f"PASS exhaustive subcubic Brooks/peel replay on {checked} graphs")
    print("PASS degree<=2 reverse reconstruction controls")
    print("PASS degree-3 existential elimination equals NAD3 on all 27 neighbour colourings")
    print("PASS 4-regular SAT/UNSAT controls are untouched by degree<=2 peeling")


if __name__=='__main__':
    main()
