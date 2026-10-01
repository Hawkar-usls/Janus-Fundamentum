#!/usr/bin/env python3
"""Exact q=5419 diamond-macro BFS and order-10 balanced 4-critical replay."""

from collections import deque
from itertools import product

Q = 5419
R = (-2) % Q


def orbit_minus2(q):
    out=[]; seen=set(); x=1; r=(-2)%q
    while x not in seen:
        seen.add(x); out.append(x); x=(x*r)%q
    assert x==1
    return tuple(out)


O=orbit_minus2(Q)
assert len(O)==21 and len(O)%3==0
IDX={s:k for k,s in enumerate(O)}
S=tuple(sorted(set(O)|{(-s)%Q for s in O}))
assert len(S)==42


def phi(c,d):
    d%=Q
    if d in IDX:
        return (-IDX[d]-c)%3
    nd=(-d)%Q
    if nd in IDX:
        return (IDX[nd]+c)%3
    return None


def diamond_macros(c):
    """Map each exact macro move to one balanced-diamond realization (a,b)."""
    out={}
    for a in S:
        pa=phi(c,a)
        for b in S:
            if a==b:
                continue
            pb=phi(c,b)
            pba=phi(c,(b-a)%Q)
            if pba is None or (pb-pa)%3 != pba:
                continue
            t=(a+b)%Q
            if len({0,a,b,t})<4:
                continue
            out.setdefault((t,(pa+pb)%3),(a,b))
    return out


def diamond_implication_exhaustive(c,a,b):
    """Brute-force all F3 potentials on K4-e and verify its forced endpoint equation."""
    pa=phi(c,a); pb=phi(c,b); pba=phi(c,(b-a)%Q)
    assert pa is not None and pb is not None and pba is not None
    assert (pb-pa)%3==pba
    t=(a+b)%Q
    # local vertices 0,a,b,t; edge required differences/gains in that order
    req=[(0,1,pa),(0,2,pb),(1,2,pba),(1,3,pb),(2,3,pa)]
    delta=(pa+pb)%3
    avoiding=0
    for p in product(range(3),repeat=4):
        ok=True
        for u,v,g in req:
            if (p[v]-p[u])%3==g:
                ok=False; break
        if not ok:
            continue
        avoiding+=1
        assert (p[3]-p[0])%3==delta
    assert avoiding>0
    return avoiding


def shortest_macro_path(c,macros):
    moves=sorted(macros)
    targets={(d,phi(c,d)) for d in S}
    start=(0,0)
    dist={start:0}; prev={}; dq=deque([start])
    hit=None
    while dq:
        x=dq.popleft()
        if x in targets and x!=start:
            hit=x; break
        for m in moves:
            y=((x[0]+m[0])%Q,(x[1]+m[1])%3)
            if y in dist:
                continue
            dist[y]=dist[x]+1
            prev[y]=(x,m)
            dq.append(y)
    assert hit is not None
    path=[]; cur=hit
    while cur!=start:
        old,m=prev[cur]
        path.append(m); cur=old
    path.reverse()
    return hit,path,len(dist)


def build_chain(c,path,macros):
    root=0; groot=0
    gauge={0:0}
    edges=set(); diamonds=[]
    for m in path:
        a,b=macros[m]
        pa=phi(c,a); pb=phi(c,b)
        A=(root+a)%Q; B=(root+b)%Q; tip=(root+m[0])%Q
        vals={root:groot,A:(groot+pa)%3,B:(groot+pb)%3,tip:(groot+m[1])%3}
        assert len({root,A,B,tip})==4
        for v,g in vals.items():
            if v in gauge:
                assert gauge[v]==g
            gauge[v]=g
        local=[(root,A),(root,B),(A,B),(A,tip),(B,tip)]
        for e in local:
            edges.add(tuple(sorted(e)))
        diamonds.append((root,A,B,tip,a,b,m))
        root=tip; groot=(groot+m[1])%3
    # final forbidden coordinate edge returns the contradiction
    assert phi(c,root)==groot
    edges.add(tuple(sorted((0,root))))
    return gauge,edges,diamonds,root


def is_3colorable(vertices,edges):
    vs=list(vertices); pos={v:i for i,v in enumerate(vs)}
    adj=[set() for _ in vs]
    for a,b in edges:
        i,j=pos[a],pos[b]; adj[i].add(j); adj[j].add(i)
    order=sorted(range(len(vs)),key=lambda x:-len(adj[x]))
    col=[-1]*len(vs)
    def rec(k):
        if k==len(order):
            return True
        v=order[k]
        used={col[u] for u in adj[v] if col[u]>=0}
        for z in range(3):
            if z in used:
                continue
            col[v]=z
            if rec(k+1):
                return True
            col[v]=-1
        return False
    return rec(0)


def edge4critical(vertices,edges):
    es=sorted(edges)
    assert not is_3colorable(vertices,es)
    for i in range(len(es)):
        assert is_3colorable(vertices,es[:i]+es[i+1:])
    return True


def verify_gain_edges(c,gauge,edges):
    for a,b in edges:
        g=phi(c,(b-a)%Q)
        if g is None:
            # reverse orientation is the supported traversal
            g2=phi(c,(a-b)%Q)
            assert g2 is not None
            assert (gauge[a]-gauge[b])%3==g2
        else:
            assert (gauge[b]-gauge[a])%3==g


EXPECTED_DISTANCE={0:3,1:3,2:3}
EXPECTED_ENDPOINTS={0:(2032,0),1:(2709,0),2:(508,0)}
EXPECTED_PATHS={
    0:[(129,1),(516,1),(1387,1)],
    1:[(129,1),(516,1),(2064,1)],
    2:[(129,1),(4411,1),(1387,1)],
}

results={}
for c in range(3):
    macros=diamond_macros(c)
    assert len(macros)==42
    implication_assignments=sum(diamond_implication_exhaustive(c,a,b) for a,b in macros.values())
    hit,path,visited=shortest_macro_path(c,macros)
    assert len(path)==EXPECTED_DISTANCE[c]
    assert hit==EXPECTED_ENDPOINTS[c]
    assert path==EXPECTED_PATHS[c]
    gauge,edges,diamonds,end=build_chain(c,path,macros)
    assert end==hit[0]
    assert len(gauge)==10
    assert len(edges)==16
    verify_gain_edges(c,gauge,edges)
    assert edge4critical(gauge.keys(),edges)
    results[c]=(hit,path,visited,implication_assignments,tuple(sorted(gauge)),tuple(sorted(edges)))

print('PASS_PALEY5419_DIAMOND_MACRO_BFS_EXACT_ORDER10_4CRITICAL_COVER')
print('q=5419 L=21 support_degree=42')
for c in range(3):
    hit,path,visited,assignments,verts,edges=results[c]
    print(f'c={c}: macro_count=42 shortest_macro_distance=3 hit={hit} visited_states={visited}')
    print(f'c={c}: path={path}')
    print(f'c={c}: vertices={verts}')
    print(f'c={c}: graph_vertices=10 graph_edges=16 edge4critical=True local_avoiding_assignments_checked={assignments}')
print('PARENT_THEOREM: balanced_order<=9 absent for all slices')
print('CONCLUSION: minimum_balanced_ordinary_4critical_order=10')
print('MACRO_BFS_STATE_SPACE=3q; CONSTRUCTOR=POLYNOMIAL_FOR_THIS_CARRIER')
print('FAMILY_WIDE_DIAMOND_MACRO_REACHABILITY=OPEN')
print('E8_D1=EMPTY P_VS_NP=OPEN')
