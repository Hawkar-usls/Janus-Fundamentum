#!/usr/bin/env python3
"""Constructive Brooks terminal for finite-domain inequality quotients.

Suppose an exact affine/subspace quotient has recovered:
  * one object label in a domain of size q=2^ell, q>=4;
  * a conflict graph G;
  * every conflict edge requires unequal labels.

Then the residual is ordinary q-coloring.

Brooks' theorem gives an exact polynomial terminal whenever Delta(G)<=q:
  * a connected component is q-colorable unless it is K_{q+1};
  * K_{q+1} is an explicit UNSAT capacity certificate.

This file implements a constructive version rather than merely citing the
existence theorem.

Algorithm for one connected component:
  1. If some vertex has degree < q, remove it recursively and greedily extend.
  2. Otherwise the component is q-regular.
  3. If it is K_{q+1}, return UNSAT.
  4. If it has a cut vertex, color the cut pieces independently and permute
     colors so the cut vertex agrees.
  5. In the remaining 2-connected, q-regular, non-complete case, search for
     a path u-v-w with u,w nonadjacent and G-{u,w} connected (the standard
     constructive Brooks configuration).  Color u,w alike, then greedily color
     G-{u,w} in reverse BFS distance from v.

All searches are polynomial graph scans.  Returned SAT results carry an
explicit coloring and are independently verified.

This is scoped: if Delta(G)>q the terminal returns OPEN.

GENERAL_SAT_IN_P is NOT proved.  P_VS_NP remains OPEN.
"""

from itertools import combinations

from graph4color_2xnf_firewall import (
    cycle_graph,
    mycielski,
    exact_k_colorable,
)


def make_adj(n,edges):
    adj={v:set() for v in range(n)}
    for u,v in edges:
        if u==v:
            raise ValueError("loop")
        adj[u].add(v); adj[v].add(u)
    return adj


def components(vertices,adj):
    unseen=set(vertices)
    out=[]
    while unseen:
        s=min(unseen)
        unseen.remove(s)
        C={s}
        stack=[s]
        while stack:
            u=stack.pop()
            for v in adj[u]:
                if v in unseen:
                    unseen.remove(v)
                    C.add(v)
                    stack.append(v)
        out.append(frozenset(C))
    return tuple(out)


def connected(vertices,adj):
    vertices=set(vertices)
    if not vertices:
        return True
    return len(components(vertices,adj))==1


def is_complete(vertices,adj):
    V=set(vertices)
    return all((V-{u}) <= adj[u] for u in V)


def verify_coloring(vertices,adj,color,q):
    V=set(vertices)
    if set(color)!=V:
        return False
    if any(not (0<=color[v]<q) for v in V):
        return False
    return all(color[u]!=color[v] for u in V for v in adj[u] if u<v and v in V)


def permute_to_vertex_color(color,v,target=0):
    old=color[v]
    if old==target:
        return dict(color)
    out={}
    for x,c in color.items():
        if c==old:
            out[x]=target
        elif c==target:
            out[x]=old
        else:
            out[x]=c
    return out


def constructive_brooks_component(vertices,adj,q):
    """Return (status,color,reason) for one connected component."""
    V=frozenset(vertices)
    if not V:
        return "SAT",{},"empty"
    assert connected(V,adj)

    deg={v:len(adj[v]&V) for v in V}
    if max(deg.values(),default=0)>q:
        return "OPEN",None,"max_degree_gt_domain"

    # Greedy extension through any sub-q vertex.
    low=next((v for v in sorted(V) if deg[v]<q),None)
    if low is not None:
        st,col,why=constructive_brooks_component(V-{low},adj,q)
        if st!="SAT":
            return st,col,why
        used={col[u] for u in adj[low] if u in col}
        avail=next((c for c in range(q) if c not in used),None)
        assert avail is not None
        col=dict(col); col[low]=avail
        assert verify_coloring(V,adj,col,q)
        return "SAT",col,"greedy_low_degree"

    # With Delta<=q and no low vertex, this component is q-regular.
    assert all(deg[v]==q for v in V)

    if len(V)==q+1 and is_complete(V,adj):
        return "UNSAT",None,"K_q_plus_1"

    # Cut-vertex decomposition.  Each piece plus the cut vertex is smaller;
    # color permutations synchronize the shared cut color.
    for cut in sorted(V):
        parts=components(V-{cut},adj)
        if len(parts)<=1:
            continue
        merged={cut:0}
        for C in parts:
            sub=frozenset(set(C)|{cut})
            st,col,why=constructive_brooks_component(sub,adj,q)
            if st!="SAT":
                return st,col,why
            col=permute_to_vertex_color(col,cut,0)
            for v,c in col.items():
                if v==cut:
                    continue
                assert v not in merged
                merged[v]=c
        assert verify_coloring(V,adj,merged,q)
        return "SAT",merged,"cut_vertex_decomposition"

    # Standard 2-connected Brooks configuration.
    # Search u-v-w with u,w nonadjacent and G-{u,w} connected.
    triple=None
    for v in sorted(V):
        N=sorted(adj[v]&V)
        for u,w in combinations(N,2):
            if w in adj[u]:
                continue
            if connected(V-{u,w},adj):
                triple=(u,v,w)
                break
        if triple:
            break

    # The constructive Brooks lemma guarantees such a triple in the current
    # 2-connected q-regular non-complete case.  Return OPEN rather than
    # overclaim if an implementation/recognition edge case ever violates it.
    if triple is None:
        return "OPEN",None,"brooks_configuration_not_found"

    u,root,w=triple
    H=frozenset(V-{u,w})

    # BFS distances in H rooted at the common neighbour root.
    dist={root:0}
    queue=[root]
    for x in queue:
        for y in sorted(adj[x]&H):
            if y not in dist:
                dist[y]=dist[x]+1
                queue.append(y)
    assert set(dist)==set(H)

    color={u:0,w:0}

    # Decreasing distance: every non-root vertex keeps one parent at smaller
    # distance uncolored.  Root is last and sees u,w in the same color.
    order=sorted(H,key=lambda x:(-dist[x],x))
    for x in order:
        used={color[y] for y in adj[x] if y in color}
        avail=next((c for c in range(q) if c not in used),None)
        assert avail is not None
        color[x]=avail

    assert verify_coloring(V,adj,color,q)
    return "SAT",color,"constructive_brooks"


def finite_domain_brooks_terminal(graph,q):
    n,edges=graph
    if q<4:
        return {"status":"OPEN","reason":"domain_lt_4"}
    adj=make_adj(n,edges)
    V=frozenset(range(n))

    maxdeg=max((len(adj[v]) for v in V),default=0)
    if maxdeg>q:
        return {
            "status":"OPEN",
            "reason":"MAX_DEGREE_GT_DOMAIN",
            "max_degree":maxdeg,
            "domain":q,
        }

    coloring={}
    reasons=[]
    for C in components(V,adj):
        st,col,why=constructive_brooks_component(C,adj,q)
        reasons.append(why)
        if st=="UNSAT":
            return {
                "status":"UNSAT",
                "reason":"BROOKS_COMPLETE_EXCEPTION",
                "domain":q,
                "component_size":len(C),
                "component":tuple(sorted(C)),
            }
        if st!="SAT":
            return {
                "status":"OPEN",
                "reason":why,
                "domain":q,
            }
        coloring.update(col)

    assert verify_coloring(V,adj,coloring,q)
    return {
        "status":"SAT",
        "reason":"BROOKS_BOUNDED_DEGREE",
        "domain":q,
        "max_degree":maxdeg,
        "coloring":tuple(coloring[v] for v in range(n)),
        "component_reasons":tuple(reasons),
    }


def complete_graph(n):
    return n,frozenset(combinations(range(n),2))


def complete_bipartite(a,b):
    return a+b,frozenset((i,a+j) for i in range(a) for j in range(b))


def verify_terminal():
    # K5 is the q=4 Brooks exception.
    r=finite_domain_brooks_terminal(complete_graph(5),4)
    assert r["status"]=="UNSAT"

    # K4,4 is 4-regular, 2-connected, non-complete: constructive Brooks lane.
    G=complete_bipartite(4,4)
    r=finite_domain_brooks_terminal(G,4)
    assert r["status"]=="SAT"
    adj=make_adj(*G)
    col={v:r["coloring"][v] for v in range(G[0])}
    assert verify_coloring(range(G[0]),adj,col,4)

    # Low-degree graphs close by greedy extension.
    G=cycle_graph(5)
    r=finite_domain_brooks_terminal(G,4)
    assert r["status"]=="SAT"

    # The E23 graph-coloring firewall remains outside this scoped terminal:
    # it is not 4-colorable and necessarily has max degree >4 by Brooks.
    G=mycielski(mycielski(cycle_graph(5)))
    assert G[0]==23
    assert not exact_k_colorable(G,4)
    r=finite_domain_brooks_terminal(G,4)
    assert r["status"]=="OPEN"
    assert r["reason"]=="MAX_DEGREE_GT_DOMAIN"
    assert r["max_degree"]>4

    # General q control.
    r=finite_domain_brooks_terminal(complete_graph(9),8)
    assert r["status"]=="UNSAT"
    r=finite_domain_brooks_terminal(complete_bipartite(8,8),8)
    assert r["status"]=="SAT"

    return {
        "K5_q4":"UNSAT",
        "K44_q4":"SAT",
        "C5_q4":"SAT",
        "mycielski23_q4":"OPEN_HIGH_DEGREE",
        "K9_q8":"UNSAT",
        "K88_q8":"SAT",
    }


def main():
    receipt=verify_terminal()
    print("FINITE-DOMAIN BROOKS TERMINAL: PASS")
    print(receipt)
    print("theorem lane: recovered inequality quotient + Delta(G)<=q")
    print("SAT unless a connected component is K_{q+1}; coloring is constructed and replayed")
    print("E23 Mycielski 4-color firewall survives only in the high-degree lane")
    print("next frontier: high-degree q-color quotient core, not capacity or bounded degree")
    print("GENERAL_SAT_IN_P = NOT_PROVED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
