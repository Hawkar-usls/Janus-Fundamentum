#!/usr/bin/env python3
"""Replay old C11 fixed-palette separator composition on the graph4 firewall.

The old Fundamentum C11 line already proved exact fixed-palette factorization
across vertex separators of size 2 and 3, and sealed one explicit size-4
separator composition witness.  This checker ports the same semantic idea to
the current 4-color quotient firewall instead of rediscovering it.

For the twice-Mycielski C5 graph H:
  * H is not 4-colorable;
  * no separator of size 1,2,3 exists;
  * a size-4 separator exists.

For a fixed separator S of size four, color symmetry means a boundary state is
determined (up to global permutation of the four colors) by the equality
partition of S.  There are Bell(4)=15 such states.

For each boundary partition:
  * reject it immediately if an original edge lies inside one equality block;
  * contract vertices required equal;
  * add edges between distinct blocks to force different colors;
  * each connected component of H-S becomes an ordinary 4-coloring subproblem.

The CURRENT polynomial graph4 critical-core closure is used as the downstream
solver.  Independent exact DSATUR is used only as a regression oracle to audit
whether OPEN states are genuinely unresolved; it is not part of the terminal.

The purpose is anti-loop:
  separator-4 factorization is exact and polynomial, but it only closes the
  firewall if the downstream component terminals close every boundary state.

GENERAL_SAT_IN_P is NOT proved.  P_VS_NP remains OPEN.
"""

from itertools import combinations

from graph4color_2xnf_firewall import (
    cycle_graph,
    mycielski,
    exact_k_colorable,
)
from graph4color_critical_core_closure import graph4_critical_core_closure


def adjacency(graph):
    n,E=graph
    A=[set() for _ in range(n)]
    for u,v in E:
        A[u].add(v); A[v].add(u)
    return A


def components_after(graph,removed):
    n,E=graph
    A=adjacency(graph)
    unseen=set(range(n))-set(removed)
    out=[]
    while unseen:
        s=min(unseen)
        unseen.remove(s)
        C={s}
        stack=[s]
        while stack:
            u=stack.pop()
            for v in A[u]:
                if v in unseen:
                    unseen.remove(v)
                    C.add(v)
                    stack.append(v)
        out.append(frozenset(C))
    return tuple(out)


def separators_of_size(graph,k,stop_after_first=False):
    n,_=graph
    out=[]
    for S in combinations(range(n),k):
        C=components_after(graph,S)
        if len(C)>1:
            out.append(tuple(S))
            if stop_after_first:
                break
    return tuple(out)


def set_partitions(items):
    """Canonical set partitions via restricted-growth labels."""
    items=tuple(items)
    if not items:
        return (tuple(),)

    out=[]
    labels=[0]

    def rec(i,maxlabel):
        if i==len(items):
            blocks={}
            for x,l in zip(items,labels):
                blocks.setdefault(l,[]).append(x)
            out.append(tuple(tuple(v) for _,v in sorted(blocks.items())))
            return
        for lab in range(maxlabel+2):
            labels.append(lab)
            rec(i+1,max(maxlabel,lab))
            labels.pop()

    rec(1,0)
    return tuple(out)


def contracted_component_graph(graph,component,S,partition):
    """Ordinary graph encoding one separator equality pattern on one side."""
    n,E=graph
    V=set(component)|set(S)

    rep={}
    for block in partition:
        r=min(block)
        for s in block:
            rep[s]=r

    # Equality inside an existing conflict edge is impossible.
    for u,v in E:
        if u in S and v in S and rep[u]==rep[v]:
            return None

    mapped=set(component)|{min(B) for B in partition}
    edges=set()

    for u,v in E:
        if u not in V or v not in V:
            continue
        a=rep.get(u,u)
        b=rep.get(v,v)
        if a==b:
            return None
        edges.add(tuple(sorted((a,b))))

    # Distinct equality blocks must use distinct colors.
    reps=[min(B) for B in partition]
    for a,b in combinations(reps,2):
        edges.add(tuple(sorted((a,b))))

    order=tuple(sorted(mapped))
    idx={v:i for i,v in enumerate(order)}
    relabeled=frozenset((idx[a],idx[b]) for a,b in edges)
    return len(order),relabeled


def audit_separator4():
    H=mycielski(mycielski(cycle_graph(5)))
    assert H[0]==23
    assert not exact_k_colorable(H,4)

    small={}
    for k in (1,2,3):
        small[k]=separators_of_size(H,k,stop_after_first=True)
        assert small[k]==tuple()

    sep4=separators_of_size(H,4,stop_after_first=True)
    assert sep4
    S=sep4[0]

    comps=components_after(H,S)
    assert len(comps)>=2

    states=set_partitions(S)
    assert len(states)==15

    receipts=[]
    exact_global_feasible=0
    poly_sat=0
    poly_unsat=0
    poly_open=0

    for P in states:
        per=[]
        exact_all=True
        saw_poly_unsat=False
        saw_poly_open=False

        for C in comps:
            G=contracted_component_graph(H,C,S,P)
            if G is None:
                exact=False
                status="UNSAT"
                detail={"status":"UNSAT","reason":"BOUNDARY_EDGE_EQUALITY_CONFLICT"}
            else:
                exact=exact_k_colorable(G,4)
                detail=graph4_critical_core_closure(G)
                status=detail["status"]

                # Regression oracle checks soundness of downstream claims.
                if status=="SAT":
                    assert exact
                if status=="UNSAT":
                    assert not exact

            exact_all &= exact
            saw_poly_unsat |= (status=="UNSAT")
            saw_poly_open |= (status=="OPEN")
            per.append({
                "component_size":len(C),
                "transformed_vertices":None if G is None else G[0],
                "exact_4colorable":exact,
                "poly_status":status,
                "poly_reason":detail.get("reason"),
            })

        if exact_all:
            exact_global_feasible+=1

        if saw_poly_unsat:
            poly_unsat+=1
            pstatus="UNSAT"
        elif saw_poly_open:
            poly_open+=1
            pstatus="OPEN"
        else:
            poly_sat+=1
            pstatus="SAT"

        # H is exactly UNSAT, so no separator state may extend globally.
        assert not exact_all
        # Current polynomial stack must never certify SAT for an impossible
        # boundary state.
        assert pstatus!="SAT"

        receipts.append({
            "partition":P,
            "poly_status":pstatus,
            "components":tuple(per),
        })

    assert exact_global_feasible==0
    assert poly_sat==0
    # The key firewall: separator-4 is exact but current downstream closures
    # do not reject every boundary state.
    assert poly_open>0

    return {
        "vertices":H[0],
        "edges":len(H[1]),
        "separator_lt4":False,
        "separator4":S,
        "component_sizes":tuple(sorted(len(C) for C in comps)),
        "boundary_states":len(states),
        "exact_feasible_states":exact_global_feasible,
        "poly_rejected_states":poly_unsat,
        "poly_open_states":poly_open,
        "receipts":tuple(receipts),
    }


def main():
    r=audit_separator4()
    print("GRAPH4 C11 SEPARATOR-4 REPLAY: PASS")
    print("graph:",{"vertices":r["vertices"],"edges":r["edges"]})
    print("no separator of size 1/2/3")
    print("separator4:",r["separator4"],"component sizes:",r["component_sizes"])
    print("Bell(4) boundary states:",r["boundary_states"])
    print("exact globally feasible states:",r["exact_feasible_states"])
    print("current polynomially rejected states:",r["poly_rejected_states"])
    print("current downstream OPEN states:",r["poly_open_states"])
    print("C11 separator factorization is exact but does NOT yet close every state")
    print("next target: polynomial boundary-relation extraction / precolor extension on the OPEN side")
    print("GENERAL_SAT_IN_P = NOT_PROVED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
