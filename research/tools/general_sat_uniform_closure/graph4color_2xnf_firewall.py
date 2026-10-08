#!/usr/bin/env python3
"""General graph-coloring quotient firewall for native 2-XNF.

For any graph G=(V,E), give each vertex v two Boolean variables (v,0),(v,1).
For every edge uv add the native 2-XNF clause

    (x_u0 XOR x_v0) OR (x_u1 XOR x_v1).

The clause is false exactly when the two 2-bit vertex labels are equal.
Therefore the formula is satisfiable iff G is properly 4-colorable.

So a perfect finite-domain/subspace quotient recovery theorem does NOT by
itself yield a polynomial general SAT solver: on this exact quotient it must
still solve arbitrary graph 4-colorability.

Frozen nontrivial control:
  M^2(C5), the twice-Mycielski graph of C5:
    vertices=23,
    triangle-free,
    chromatic number 5,
so its native 2-XNF formula is UNSAT for the 4-color domain.

The checker verifies triangle-freeness and non-4-colorability by an independent
DSATUR-style exact coloring search.  It then records how the current closure
stack treats the formula.

This is a firewall, not a lower bound on all possible SAT algorithms.
P_VS_NP remains OPEN.
"""

from itertools import combinations

from two_sided_gaussian_probe_closure import two_sided_gaussian_probe_closure
from binary_alldifferent_capacity_terminal import detect_complete_alldifferent
from subspace_alldifferent_capacity_terminal import detect_subspace_alldifferent
from uniform_gaussian_implication_audit import rank_vectors


def cycle_graph(n):
    return n, frozenset(
        tuple(sorted((i,(i+1)%n)))
        for i in range(n)
    )


def mycielski(graph):
    n,E=graph
    # old vertices 0..n-1; shadows n..2n-1; apex 2n
    out=set(E)
    for u,v in E:
        out.add(tuple(sorted((u,n+v))))
        out.add(tuple(sorted((v,n+u))))
    w=2*n
    for i in range(n):
        out.add((n+i,w))
    return 2*n+1,frozenset(out)


def has_triangle(graph):
    n,E=graph
    adj=[set() for _ in range(n)]
    for u,v in E:
        adj[u].add(v); adj[v].add(u)
    return any(
        (adj[u]&adj[v])
        for u,v in E
    )


def graph4_xnf(graph):
    n,E=graph
    clauses=[]
    for u,v in sorted(E):
        a=(1<<(2*u)) ^ (1<<(2*v))
        b=(1<<(2*u+1)) ^ (1<<(2*v+1))
        clauses.append(((a,0),(b,0)))
    return tuple(clauses),2*n


def exact_k_colorable(graph,k):
    """Independent exact DSATUR-style backtracking, fixture checker only."""
    n,E=graph
    adj=[set() for _ in range(n)]
    for u,v in E:
        adj[u].add(v); adj[v].add(u)

    color=[-1]*n

    def choose_vertex():
        best=None
        key=None
        for v in range(n):
            if color[v]>=0:
                continue
            sat=len({color[u] for u in adj[v] if color[u]>=0})
            deg=len(adj[v])
            z=(sat,deg,-v)
            if key is None or z>key:
                key=z; best=v
        return best

    def rec(done):
        if done==n:
            return True
        v=choose_vertex()
        used={color[u] for u in adj[v] if color[u]>=0}
        for c in range(k):
            if c in used:
                continue
            color[v]=c
            if rec(done+1):
                return True
            color[v]=-1
        return False

    return rec(0)


def normal_rank(source):
    normals=[L[0] for C in source for L in C]
    return rank_vectors(normals)


def verify_formula_semantics_small():
    # Exhaust every assignment on a tiny edge and compare to 4-color labels.
    G=(2,frozenset({(0,1)}))
    F,n=graph4_xnf(G)
    assert n==4
    # Exactly 4*3 ordered unequal color pairs.
    sat=0
    for x in range(1<<n):
        ok=True
        for a,b in F:
            va=(a[0]&x).bit_count()&1
            vb=(b[0]&x).bit_count()&1
            if not (va or vb):
                ok=False
                break
        sat+=ok
    assert sat==12


def verify_triangle_free_5chromatic_fixture():
    G=cycle_graph(5)
    assert not has_triangle(G)
    assert exact_k_colorable(G,3)

    G=mycielski(G)
    assert not has_triangle(G)
    assert exact_k_colorable(G,4)

    G=mycielski(G)
    assert G[0]==23
    assert not has_triangle(G)
    assert not exact_k_colorable(G,4)

    F,n=graph4_xnf(G)
    assert n==46

    # Current complete-AllDifferent recognizers are correctly scoped and must
    # not misclassify an arbitrary sparse conflict graph as K_p.
    old=detect_complete_alldifferent(F)
    sub=detect_subspace_alldifferent(F)
    assert old["status"]=="OPEN"
    assert sub["status"]=="OPEN"

    st,E,A,stats=two_sided_gaussian_probe_closure(F,n)
    assert st!="SAT_LINEAR"

    return {
        "vertices":G[0],
        "edges":len(G[1]),
        "triangle_free":True,
        "4_colorable":False,
        "2xnf_variables":n,
        "2xnf_clauses":len(F),
        "normal_rank":normal_rank(F),
        "two_sided_probe":st,
        "probe_learned_rank":len(E or ()),
        "complete_alldifferent":old["status"],
        "subspace_complete_alldifferent":sub["status"],
        **stats,
    }


def main():
    verify_formula_semantics_small()
    receipt=verify_triangle_free_5chromatic_fixture()

    print("GRAPH 4-COLORING 2-XNF QUOTIENT FIREWALL: PASS")
    print(receipt)
    print("universal identity: F_G SAT iff G is 4-colorable")
    print("finite-domain quotient discovery alone does not solve arbitrary quotient graphs")
    print("next target: quotient + tractable conflict-structure dichotomy, not capacity alone")
    print("GENERAL_SAT_IN_P = NOT_PROVED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
