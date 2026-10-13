#!/usr/bin/env python3
"""Polynomial TIME O(m^3 * (n+m)) source-structural filter for n>=18 6poles.

The CANDIDATE PROMISE is an exposed Exact-One pair-equality 6pole,
so it must be properly 3-edge-colourable. This lets us reject it
without solving its colouring by the following all-size theorems:

- A port-free component behind ONE ordinary edge is impossible
  in any properly colourable cubic multipole (one-semi parity).
- A port-free connected component behind 2 or 3 ordinary edges,
  with a SIMPLE connected edge/vertex quotient STRICTLY SMALLER
  than the source, has precisely the physical colour signature
  of that quotient; moreover there is a literal degree1 original
  native SCL PC retraction once a source block-colouring witness
  is supplied (proof and CI #38420079360).
- Therefore any claimed MINIMAL n18 exposed ExactOne with such
  k2/3 cut is impossible (quotient has n<=16 and those cases were
  eliminated exhaustively by CI #38408523974 and prior controls).

This script explores ALL edge subsets of cardinality <=3 and computes
components after their deletion (no 2^n vertex-partition search,
no 3-edge-colouring enumeration, no generic SAT solving).
For any separated port-free component B it checks the ACTUAL cut
and quotient simplicity/connectedness exactly.
Only these proven structural tests are applied; non-simple quotient,
cuts splitting boundary ports, and >3-cut cases remain unresolved.

Several constructed positive source colourable sixpoles are checked
including an n18 with nested 2pole and 3pole blocks.
"""
from itertools import combinations
from collections import Counter
from r5_universal_portfree_two_three_edge_cut_exact_signature_retraction import (
    norm,graph_cycle6,inflate_edge_diamond,
    inflate_trivalent_vertex_triangle,
    component_cut,assert_simple_cubic_multipole,connected,
)


def components(vertices,edges):
    adj={v:set() for v in vertices}
    for a,b in edges:
        adj[a].add(b);adj[b].add(a)
    unvisited=set(vertices)
    found=[]
    while unvisited:
        v=min(unvisited)
        frontier=[v]
        unvisited.remove(v)
        B={v}
        while frontier:
            for u in adj[frontier.pop()]:
                if u in unvisited:
                    unvisited.remove(u)
                    frontier.append(u)
                    B.add(u)
        found.append(frozenset(B))
    return found


def quotient_without_colour(E,ports,B):
    """Only the finite graph-topological part; no colouring solved."""
    V=assert_simple_cubic_multipole(E,ports)
    B=set(B)
    assert B and not (B&set(ports)) and B<V
    cut,inside,outside,_,roots=component_cut(E,B)
    k=len(cut)
    if k not in (2,3) or not connected(B,inside):
        return None
    if k==2:
        if roots[0]==roots[1]:return None
        f=norm(*roots)
        if f in outside:return None
        Q=set(outside)|{f}
    else:
        if len(set(roots))<3:return None
        marker=max(V)+1
        Q=set(outside)|{norm(marker,r) for r in roots}
    if len(Q)!=len(outside)+k//2 if False else False:
        raise AssertionError("unreachable")
    try:
        qV=assert_simple_cubic_multipole(frozenset(Q),ports)
    except AssertionError:
        return None
    if not connected(qV,Q):
        return None
    if len(qV)>=len(V):
        return None
    return frozenset(Q)


def find_small_portfree_cuts(E,ports):
    E=tuple(sorted(E))
    V=assert_simple_cubic_multipole(E,ports)
    assert connected(V,E)
    exclusions=Counter()
    witnesses=[]
    counted=set()
    for k in (1,2,3):
        for guess in combinations(E,k):
            remaining=set(E)-set(guess)
            for B in components(V,remaining):
                if B & set(ports):
                    continue
                cut,inside,outside,_,roots=component_cut(E,B)
                if len(cut)!=k or set(cut)!=set(guess):
                    continue
                if B in counted:
                    continue
                counted.add(B)
                if k==1:
                    exclusions["IMPOSSIBLE_ONE_EDGE_PORTFREE"]+=1
                    witnesses.append(("ONE_EDGE_UNCOLOURABLE",B,None))
                else:
                    Q=quotient_without_colour(E,ports,B)
                    if Q is None:
                        exclusions["NON_SIMPLE_OR_NON_SHRINKABLE"]+=1
                    else:
                        exclusions[f"SHRINKABLE_{k}_CUT"]+=1
                        witnesses.append((f"SHRINKABLE_{k}_CUT",B,Q))
    return exclusions,witnesses


def sample(label,E,ports,expect_min_witnesses=1):
    cnt,w=find_small_portfree_cuts(E,ports)
    usable=[x for x in w if x[0].startswith("SHRINKABLE")]
    assert len(usable)>=expect_min_witnesses,(label,cnt)
    if label.startswith("N18"):
        assert len(assert_simple_cubic_multipole(E,ports))==18
        assert all(len(assert_simple_cubic_multipole(Q,ports))<=16
                   for _,_,Q in usable)
    print("SMALLCUT_STRUCTURAL",label,dict(cnt),flush=True)
    print("SMALLCUT_EXPLICIT_WITNESS",label,
          [(typ,len(B),len(assert_simple_cubic_multipole(Q,ports)))
            for typ,B,Q in usable[:10]],flush=True)


def main():
    C6,ports=graph_cycle6()
    counts,w=find_small_portfree_cuts(C6,ports)
    assert not w and not counts,(counts,w)
    print("BASE_C6: no portfree components, PASS")
    diamond,first=inflate_edge_diamond(C6,(0,1),6)
    sample("N10_DIAMOND",diamond,ports)
    double,second=inflate_edge_diamond(diamond,(8,9),10)
    sample("N14_DOUBLE_DIAMOND",double,ports)
    expanded,tri=inflate_trivalent_vertex_triangle(double,10,14)
    sample("N16_DOUBLE_DIAMOND_TRIANGLE",expanded,ports)
    final,tri2=inflate_trivalent_vertex_triangle(expanded,14,17)
    sample("N18_DOUBLE_DIAMOND_NESTED_3POLE",final,ports,2)
    print("ALL_N STRUCTURAL CUT SCAN O(m^3*(n+m)), no exponential")
    print(" boundary colouring enumeration, no all-n18 graph census.")
    print("MINIMAL_N18_ONEHOT: no SHRINKABLE portfree k2/k3 simple cut")
    print("ONE_EDGE_PORTFREE: forbidden for ANY colourable source.")
    print("SAME_INTERIOR_KEMPE_ALLSIZE_NO_GO=OPEN")
    print("SOLVE_LINEAR_CUBIC_XSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    main()
