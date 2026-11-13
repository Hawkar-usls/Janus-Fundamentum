#!/usr/bin/env python3
"""All-source exact cycle-root spin elimination after E118 Hall matching.

Choose a matched cubic source (n variable vertices, n clause-edges).
Non-owner edges form a loopless 2-regular multigraph H with c cycles.
Use one spanning tree per cycle. Each edge spin q_v is the parity of
endpoint p spins, so choose n-c free forest-edge gradient bits.
For fixed gradients q, each cycle retains one common spin b_C.
Its two assignments can be summed exactly as two polynomial products.

Consequently the COMPLETE E118 target half-weight enumerator is
computed in O(poly(n)*2^(n-c)) integer bit operations, a factor 2^c
fewer explicit states than the earlier E118 n-bit source sum.
This is NOT worst-case polynomial: c<=floor(n/2) for every
loopless 2-factor, so n-c>=ceil(n/2).
Any polynomial universal solver needs FURTHER algebraic contraction.

Exact independent whole-polynomial replay: q9 SAT/UNSAT and connected
q6 opposite-SAT pair with identical unlabelled 2-factor.
"""
from __future__ import annotations

from collections import Counter, defaultdict

from r5_universal_boolean_quadratic_pc2_attack import cyclic_source,source_solutions
from r5_universal_e118_matching_port_phase_normal_form import (
    incidence_perfect_matching,
    exact_phase_histogram_n_source_bits,
    local_weight_poly,
    polynomial_convolution,
)
from r5_universal_e118_hadamard_cycle_edge_dual_attack import (
    other_port_graph,
)


def forest_components_from_owner_edges(source,matching):
    names,edge_endpoints,incident,cycle_sizes=other_port_graph(source,matching)
    visited=set()
    components=[]
    tree_edges=[]
    parent=[]
    for root in names:
        if root in visited:continue
        visited.add(root)
        queue=[root]
        vertices=[root]
        edges=[]
        for u in queue:
            for label in incident[u]:
                a,b=edge_endpoints[label]
                v=b if u==a else a
                if v in visited: continue
                visited.add(v)
                queue.append(v)
                vertices.append(v)
                edges.append(label)
                parent.append((u,v,label))
                tree_edges.append(label)
        components.append(vertices)
        assert len(edges)==len(vertices)-1
    n=len(names)
    c=len(components)
    assert set(visited)==set(names)
    assert sum(map(len,components))==n
    assert sum(len(comp)-1 for comp in components)==n-c
    assert len(tree_edges)==n-c
    assert c<=n//2
    assert sorted(map(len,components))==cycle_sizes
    assert len(set(tree_edges))==n-c
    return names,edge_endpoints,components,tree_edges,parent


def spin_cycle_elimination_histogram(source,matching):
    names,edges,components,tree_edges,parent=forest_components_from_owner_edges(
        source,matching
    )
    n=len(names);c=len(components)
    at={name:i for i,name in enumerate(tree_edges)}
    hist=defaultdict(int)
    # THIS loop can be exponential. Each iteration nevertheless sums
    # all 2^c cycle-root spins WITHOUT enumerating them.
    for mask in range(1<<(n-c)):
        relative={}
        for comp in components:
            relative[comp[0]]=0
        for u,v,owner in parent:
            assert u in relative and v not in relative
            relative[v]=relative[u]^((mask>>at[owner])&1)
        assert len(relative)==n
        q={owner:relative[a]^relative[b]
            for owner,(a,b) in edges.items()}
        assert len(q)==n
        assert all(q[owner]==(mask>>at[owner])&1
                   for owner in tree_edges)
        pol={0:1}
        for comp in components:
            a={0:1};b={0:1}
            for v in comp:
                a=polynomial_convolution(
                    a,local_weight_poly(relative[v],q[v])
                )
                b=polynomial_convolution(
                    b,local_weight_poly(1^relative[v],q[v])
                )
            together=defaultdict(int)
            for deg,coef in a.items():together[deg]+=coef
            for deg,coef in b.items():together[deg]+=coef
            pol=polynomial_convolution(pol,together)
        for degree,coef in pol.items():
            hist[degree]+=coef
    assert sum(hist.values())==1<<(2*n)
    assert all(degree%2==0 for degree,val in hist.items() if val)
    return dict(hist),c,1<<(n-c)


def q6_cases():
    return (
        ("CONNECTED_UNSAT_Q6",(
            ("v3","v0","v1"),("v4","v1","v2"),("v5","v2","v0"),
            ("v0","v3","v4"),("v1","v4","v5"),("v2","v5","v3"),
        ),{0:"v3",1:"v4",2:"v5",3:"v0",4:"v1",5:"v2"},0),
        ("CONNECTED_SAT_Q6",(
            ("v3","v0","v1"),("v4","v1","v2"),("v5","v2","v0"),
            ("v1","v3","v4"),("v2","v4","v5"),("v0","v5","v3"),
        ),{0:"v3",1:"v4",2:"v5",3:"v1",4:"v2",5:"v0"},3),
    )


def main():
    cases=[
        ("E118_UNSAT_Q9",cyclic_source(9,1,6),None,0,1),
        ("E118_SAT_Q9",cyclic_source(9,1,2),None,3,4),
        *( (name,source,matching,expected,2)
            for name,source,matching,expected in q6_cases()),
    ]
    for name,source,provided_match,expected_source,expected_cycles in cases:
        matching=(provided_match if provided_match is not None
                  else incidence_perfect_matching(source))
        hist,c,states=spin_cycle_elimination_histogram(source,matching)
        primal=exact_phase_histogram_n_source_bits(source,matching)
        assert hist==primal,(name,
            {k:(hist.get(k,0),primal.get(k,0))
             for k in set(hist)|set(primal)
             if hist.get(k,0)!=primal.get(k,0)})
        n=len(source)
        assert c==expected_cycles,(name,c)
        assert states==1<<(n-c)
        assert len(source_solutions(source))==expected_source
        # E118 target n_target=10n, top weight=2n_target/3.
        # Weight polynomial uses alpha^(weight) not z^(weight/2).
        exponent=(20*n)//3
        multiplicity=1<<(2*n//3)
        assert hist.get(exponent,0)==expected_source*multiplicity,(name,exponent,hist.get(exponent,0))
        print(f"{name}: source_n={n} cycles={c} "
              f"exact states={states} vs {1<<n}; "
              f"target top alpha^{exponent}={hist.get(exponent,0)}; "
              "all coefficients independent replay PASS")

    print("HALL_MATCHED_SOURCE_PHASE_CYCLE_ROOT_SPIN_ELIMINATION=PROVED_ALL_INPUTS")
    print("EXPLICIT_SPIN_STATE_COUNT=2^(n-c); c<=floor(n/2) ALWAYS")
    print("CYCLE_ONLY_GRADIENT_ENUMERATION_NEVER_GIVES_UNIFORM_POLY_BOUND")
    print("GLOBAL_PHASE_POLYNOMIAL_CONTRACTION=UNPROVED; P_VS_NP=OPEN")


if __name__=="__main__":
    main()
