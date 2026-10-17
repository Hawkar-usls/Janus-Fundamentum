#!/usr/bin/env python3
import itertools


def edge(u,v):
    return (u,v) if u<v else (v,u)


def hamiltonian(n):
    return {edge(i,(i+1)%n) for i in range(n)}


def build(n, groups):
    E=set(hamiltonian(n))
    for g in groups:
        g=tuple(sorted(g))
        for i in range(4):
            e=edge(g[i],g[(i+1)%4])
            assert e not in E
            E.add(e)
    deg=[0]*n
    for u,v in E:
        deg[u]+=1; deg[v]+=1
    assert all(d==4 for d in deg)
    return E


def colorable(n,E):
    adj=[set() for _ in range(n)]
    for u,v in E:
        adj[u].add(v); adj[v].add(u)
    order=sorted(range(n), key=lambda x:-len(adj[x]))
    col={}
    def rec(i):
        if i==n:
            return dict(col)
        v=order[i]
        used={col[u] for u in adj[v] if u in col}
        for c in range(3):
            if c not in used:
                col[v]=c
                ans=rec(i+1)
                if ans is not None: return ans
                del col[v]
        return None
    return rec(0)


def quotient(n,E,groups,choices):
    p=list(range(n))
    def find(x):
        while p[x]!=x:
            p[x]=p[p[x]]; x=p[x]
        return x
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b: p[b]=a
    for g,ch in zip(groups,choices):
        g=tuple(sorted(g))
        union(g[0],g[2]) if ch==0 else union(g[1],g[3])
    roots=sorted({find(i) for i in range(n)})
    idx={r:i for i,r in enumerate(roots)}
    Q=set()
    for u,v in E:
        a,b=find(u),find(v)
        if a==b:
            return len(roots),None
        Q.add(edge(idx[a],idx[b]))
    return len(roots),Q


def c4_truth_table():
    for colors in itertools.product(range(3), repeat=4):
        a,b,c,d=colors
        proper=(a!=b and b!=c and c!=d and d!=a)
        if proper:
            assert a==c or b==d
            if len(set(colors))==3:
                assert (a==c) ^ (b==d)
            if len(set(colors))==2:
                assert a==c and b==d


def eight_vertex_failure():
    groups=[(0,2,4,6),(1,3,5,7)]
    E=build(8,groups)
    assert colorable(8,E) is None
    for choices in itertools.product((0,1), repeat=2):
        qn,Q=quotient(8,E,groups,choices)
        assert Q is not None
        assert colorable(qn,Q) is None


def contraction_equivalence_controls():
    # Exhaustively verify the local witness reduction on several small smooth C4 graphs.
    controls=[
        (8,[(0,2,4,6),(1,3,5,7)]),
        (12,[(0,3,6,9),(1,4,7,10),(2,5,8,11)]),
    ]
    for n,groups in controls:
        E=build(n,groups)
        original=colorable(n,E) is not None
        some=False
        for choices in itertools.product((0,1), repeat=len(groups)):
            qn,Q=quotient(n,E,groups,choices)
            if Q is not None and colorable(qn,Q) is not None:
                some=True; break
        assert original==some


def main():
    c4_truth_table()
    eight_vertex_failure()
    contraction_equivalence_controls()
    print("PASS C4 proper 3-coloring implies an equal-color diagonal on all 3^4 assignments")
    print("PASS two-color/three-color diagonal overlap classification")
    print("PASS exact diagonal-contraction equivalence on finite smooth controls")
    print("PASS explicit 8-vertex cycle+C4+C4 control is not 3-colorable")

if __name__=='__main__':
    main()
