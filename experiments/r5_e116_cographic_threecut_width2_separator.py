#!/usr/bin/env python3
"""R5 E116: cographic 3-edge-cut width-2 separator firewall.

Let H be a connected graph and let W=C(H)^* be the faithful cographic normal
space obtained from edge-coordinate functionals restricted to the binary cycle
space.

For a vertex set S, let W_S be the span of edge normals incident to at least
one vertex of S, and W_T the analogous span for T=V-S.

In the faithful cographic representation:

    W_S intersect W_T = span{g_e : e in delta(S)}.

Reason: if one vector has an S-supported edge representative and a T-supported
representative, their difference is a cut-space vector.  Subtracting the cut
of the S-side part removes all S-internal edges and leaves only delta(S).

Hence the subspace-arrangement cut width equals the rank of the crossing-edge
normals.

For a nontrivial 3-edge cut in a 3-edge-connected graph:
  * the three cut normals sum to zero (sum the vertex-star relations over S);
  * none is zero and no two are parallel;
  * therefore the cut-normal span has rank exactly two.

Thus every nontrivial cographic 3-edge cut is an exact width-2 separator for
the distinguished-check normal arrangement.  It is discoverable in polynomial
time by enumerating edge triples and testing connectivity.

This does not yet prove that arbitrary mixed-normal external Tanner checks
respect the same decomposition.  It removes "nontrivial 3-edge cut" as a new
intrinsic high-width phenomenon in the faithful distinguished cographic core.

P_VS_NP remains OPEN.
"""

from itertools import combinations


def gf2_rank(rows):
    rows=[int(r) for r in rows if r]
    rank=0
    col=0
    maxbit=max((r.bit_length() for r in rows),default=0)
    while col<maxbit and rank<len(rows):
        p=next((i for i in range(rank,len(rows)) if (rows[i]>>col)&1),None)
        if p is None:
            col+=1
            continue
        rows[rank],rows[p]=rows[p],rows[rank]
        for i in range(len(rows)):
            if i!=rank and ((rows[i]>>col)&1):
                rows[i]^=rows[rank]
        rank+=1
        col+=1
    return rank


def gf2_nullspace(rows,n):
    rows=[int(r) for r in rows if r]
    rank=0
    piv=[]
    for col in range(n):
        p=next((i for i in range(rank,len(rows)) if (rows[i]>>col)&1),None)
        if p is None:
            continue
        rows[rank],rows[p]=rows[p],rows[rank]
        for i in range(len(rows)):
            if i!=rank and ((rows[i]>>col)&1):
                rows[i]^=rows[rank]
        piv.append(col)
        rank+=1

    free=[c for c in range(n) if c not in set(piv)]
    basis=[]
    for f in free:
        x=1<<f
        for i,p in enumerate(piv):
            if (rows[i]>>f)&1:
                x |= 1<<p
        basis.append(x)
    return tuple(basis)


def connected_components(n,edges,removed=frozenset()):
    removed=set(removed)
    adj=[set() for _ in range(n)]
    for i,(u,v) in enumerate(edges):
        if i in removed:
            continue
        adj[u].add(v)
        adj[v].add(u)
    unseen=set(range(n))
    comps=[]
    while unseen:
        s=next(iter(unseen))
        C=set()
        stack=[s]
        while stack:
            u=stack.pop()
            if u in C:
                continue
            C.add(u)
            unseen.discard(u)
            stack.extend(v for v in adj[u] if v not in C)
        comps.append(frozenset(C))
    return tuple(comps)


def incidence_rows(n,edges):
    rows=[]
    for v in range(n):
        r=0
        for e,(a,b) in enumerate(edges):
            if v in (a,b):
                r |= 1<<e
        rows.append(r)
    return tuple(rows)


def cographic_normals(n,edges):
    inc=incidence_rows(n,edges)
    cycle_basis=gf2_nullspace(inc,len(edges))
    normals=[]
    for e in range(len(edges)):
        g=0
        for i,z in enumerate(cycle_basis):
            if (z>>e)&1:
                g |= 1<<i
        normals.append(g)
    return tuple(cycle_basis),tuple(normals)


def intersection_dim(A,B):
    return gf2_rank(A)+gf2_rank(B)-gf2_rank(tuple(A)+tuple(B))


def triangular_prism():
    E=set()
    for off in (0,3):
        for i in range(3):
            E.add(tuple(sorted((off+i,off+(i+1)%3))))
    for i in range(3):
        E.add((i,3+i))
    return tuple(sorted(E))


def mobius_ladder(n):
    E=set()
    for i in range(n):
        E.add(tuple(sorted((i,(i+1)%n))))
    for i in range(n//2):
        E.add((i,i+n//2))
    return tuple(sorted(E))


def cut_edges(edges,S):
    S=set(S)
    return tuple(i for i,(u,v) in enumerate(edges) if (u in S)^(v in S))


def incident_edges(edges,S):
    S=set(S)
    return tuple(i for i,(u,v) in enumerate(edges) if u in S or v in S)


def verify_three_cut_width2(n,edges,S):
    T=set(range(n))-set(S)
    cyc,normals=cographic_normals(n,edges)
    cut=cut_edges(edges,S)
    assert len(cut)==3

    # Both sides nontrivial and connected after deleting the crossing cut.
    comps=connected_components(n,edges,cut)
    assert len(comps)==2
    assert set(comps)=={frozenset(S),frozenset(T)}
    assert min(map(len,comps))>1

    # Sum of cut normals is zero: cographic image of the cut relation.
    x=0
    for e in cut:
        x ^= normals[e]
    assert x==0

    # In the 3-edge-connected example, rank is exactly two.
    rcut=gf2_rank([normals[e] for e in cut])
    assert rcut==2

    ES=incident_edges(edges,S)
    ET=incident_edges(edges,T)
    WS=[normals[e] for e in ES]
    WT=[normals[e] for e in ET]
    wint=intersection_dim(WS,WT)
    assert wint==rcut==2

    return {
        "vertices":n,
        "edges":len(edges),
        "cycle_rank":len(cyc),
        "cut":cut,
        "cut_normal_rank":rcut,
        "arrangement_width":wint,
    }


def count_nontrivial_three_cuts(n,edges):
    count=0
    for rem in combinations(range(len(edges)),3):
        comps=connected_components(n,edges,rem)
        if len(comps)==2 and min(map(len,comps))>1:
            count+=1
    return count


def main():
    P=triangular_prism()
    info=verify_three_cut_width2(6,P,{0,1,2})
    assert count_nontrivial_three_cuts(6,P)>=1

    M=mobius_ladder(12)
    # E115's concrete 3-circuit-rigid example: only trivial vertex-star cuts.
    assert count_nontrivial_three_cuts(12,M)==0

    print("R5 E116 cographic 3-edge-cut width-2 separator: PASS")
    print("triangular prism:",info)
    print("nontrivial 3-edge cut => exact distinguished-arrangement width 2")
    print("3-edge cuts are polynomially discoverable by brute edge-triple enumeration")
    print("Möbius ladder 12 nontrivial 3-edge cuts=0 -> E115 rigid no-lift lane")
    print("remaining joint-lift escape: mixed-normal external-check leakage / non-faithful quotient")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
