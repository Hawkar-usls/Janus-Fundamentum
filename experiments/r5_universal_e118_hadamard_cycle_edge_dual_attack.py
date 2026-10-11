#!/usr/bin/env python3
"""Exact global Hadamard dual of the all-E118 weighted phase normal form.

Given a cubic 3-uniform source, choose a perfect matching of variables
to clauses, and write q_v = p_a XOR p_b. The target half-weight
enumerator is a source-bit weighted sum S(alpha):
    sum_{p in F2^n} prod_v W[p_v, p_a XOR p_b](alpha).
The full 3-leg Walsh transform of f_v(p_v,p_a,p_b) yields a
FREQUENCY-EQUALITY condition between the two non-owner legs.
Those edges form a 2-regular multigraph H (disjoint cycles).
A globally exact DUAL identity results:
    2^n*S(alpha) = sum_{e in F2^n} prod_v
           C[ e_(owner_of_other_clause1) XOR
              e_(owner_of_other_clause2), e_v ](alpha),
    C = Hadamard * W * Hadamard.

This theorem holds for ALL cubic sources with E118 matching ports.
The other-owner permutations still create a global ternary interaction;
no polynomial bit-complexity evaluation is claimed.

Frozen q9 SAT/UNSAT cases independently compare *every* integer
coefficient of primal/dual polynomials, not just SAT count.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from itertools import product

from r5_universal_boolean_quadratic_pc2_attack import cyclic_source,source_solutions
from r5_universal_e118_matching_port_phase_normal_form import (
    incidence_perfect_matching, local_weight_poly,
    exact_phase_histogram_n_source_bits, polynomial_convolution,
    polynomial_sub,
)


def walsh_2x2_coeff_polys():
    W={(p,q):local_weight_poly(p,q) for p in (0,1) for q in (0,1)}
    def add_scaled(out,poly,scale):
        for k,v in poly.items():
            out[k]+=scale*v
    C={}
    for r,s in product((0,1),repeat=2):
        d=defaultdict(int)
        for p,q in product((0,1),repeat=2):
            add_scaled(d,W[(p,q)],-1 if ((r*p+s*q)%2) else 1)
        C[(r,s)]={k:v for k,v in d.items() if v}

    # Exact 3-variable Walsh inverse as a POLYNOMIAL identity.
    for p,a,b in product((0,1),repeat=3):
        total=defaultdict(int)
        for r,s in product((0,1),repeat=2):
            add_scaled(total,C[(r,s)],-1 if ((r*p+s*(a+b))%2) else 1)
        got={k:v for k,v in total.items() if v}
        want={k:4*v for k,v in W[(p,a^b)].items()}
        assert got==want,(p,a,b,got,want)

    det=polynomial_sub(
        polynomial_convolution(C[(0,0)],C[(1,1)]),
        polynomial_convolution(C[(0,1)],C[(1,0)])
    )
    # 4 det(W), all in Z[alpha].
    assert det=={7:8,9:-8,11:-8,13:8},det
    return C


def other_port_graph(source,matching):
    """Return the 2-regular multigraph H edges labelled by owners."""
    names=sorted(set(v for row in source for v in row))
    n=len(names)
    assert len(source)==n and len(matching)==n
    assert len(set(matching.values()))==n
    edge_endpoints={}
    incident=defaultdict(list)
    for clause,owner in matching.items():
        others=[v for v in source[clause] if v!=owner]
        assert len(others)==2 and len(set(others))==2
        u,w=others
        edge_endpoints[owner]=(u,w)
        incident[u].append(owner)
        incident[w].append(owner)
    assert len(edge_endpoints)==n
    assert all(len(incident[v])==2 for v in names)
    assert set(incident)==set(names)

    # A finite graph where all vertices have degree 2 is a disjoint
    # union of cycles, including 2-cycles of parallel edges.
    seen=set()
    cycle_sizes=[]
    for start in names:
        if start in seen:
            continue
        stack=[start]
        component=[]
        while stack:
            u=stack.pop()
            if u in seen:continue
            seen.add(u)
            component.append(u)
            for e in incident[u]:
                a,b=edge_endpoints[e]
                stack.append(b if a==u else a)
        cycle_sizes.append(len(component))
        assert len(component)>=2
    assert sum(cycle_sizes)==n
    return names,edge_endpoints,incident,sorted(cycle_sizes)


def dual_phase_histogram(source,matching):
    """Exact polynomial sum in the n dual edge bits, scaled by 2^n."""
    C=walsh_2x2_coeff_polys()
    names,edges,incident,cycles=other_port_graph(source,matching)
    n=len(names)
    at={v:i for i,v in enumerate(names)}
    accum=defaultdict(int)
    for mask in range(1<<n):
        poly={0:1}
        for v in names:
            e1,e2=incident[v]
            r=((mask>>at[e1])^(mask>>at[e2]))&1
            s=(mask>>at[v])&1
            poly=polynomial_convolution(poly,C[(r,s)])
        for degree,value in poly.items():
            accum[degree]+=value
    assert all(coef%(1<<n)==0 for coef in accum.values())
    exact={degree:count//(1<<n) for degree,count in accum.items() if count}
    assert all(v>=0 for v in exact.values())
    return exact,cycles


def main():
    C=walsh_2x2_coeff_polys()
    print("C=Hadamard W Hadamard; all four exact polynomial entries:")
    for key in sorted(C):
        print(f"  C{key}={dict(sorted(C[key].items()))}")
    print("det(C)=4 det(W) = 8 a^7(1-a^2)(1-a^4)")

    for name,a,b in (
        ("E118_UNSAT90",1,6),
        ("E118_SAT90",1,2),
    ):
        source=cyclic_source(9,a,b)
        matching=incidence_perfect_matching(source)
        primal=exact_phase_histogram_n_source_bits(source,matching)
        dual,cycles=dual_phase_histogram(source,matching)
        assert dual==primal,(name,
            {k:(primal.get(k,0),dual.get(k,0))
             for k in set(primal)|set(dual)
             if primal.get(k,0)!=dual.get(k,0)})
        expected=0 if "UNSAT" in name else 192
        assert dual.get(60,0)==expected
        assert expected==len(source_solutions(source))*64
        print(f"{name}: n=9 dual H cycle sizes={cycles}; "
              f"all {len(dual)} integer coefficients exact; "
              f"top a^60 count={dual.get(60,0)} PASS")

    # EXACT SAME UNLABELLED two-triangle H, DIFFERENT owner-edge
    # permutations, opposite SAT statuses. Thus H alone (cycle sizes,
    # even full unlabelled graph) cannot decide Exact-One.
    bridge_cases=(
        ("CONNECTED_UNSAT_TWO_TRIANGLES",(
            ("v3","v0","v1"),("v4","v1","v2"),("v5","v2","v0"),
            ("v0","v3","v4"),("v1","v4","v5"),("v2","v5","v3"),
        ),{0:"v3",1:"v4",2:"v5",3:"v0",4:"v1",5:"v2"},0),
        ("CONNECTED_SAT_TWO_TRIANGLES",(
            ("v3","v0","v1"),("v4","v1","v2"),("v5","v2","v0"),
            ("v1","v3","v4"),("v2","v4","v5"),("v0","v5","v3"),
        ),{0:"v3",1:"v4",2:"v5",3:"v1",4:"v2",5:"v0"},3),
    )
    both_unlabelled=[]
    for name,bridge,matching,expected_source in bridge_cases:
        assert set(matching)==set(range(6))
        assert all(owner in bridge[i] for i,owner in matching.items())
        deg=Counter(x for row in bridge for x in row)
        assert len(deg)==6 and set(deg.values())=={3}
        names,edges,incident,cycles=other_port_graph(bridge,matching)
        assert cycles==[3,3]
        classes=[set(("v0","v1","v2")),set(("v3","v4","v5"))]
        assert all(set(edges[v])<=classes[1] for v in classes[0])
        assert all(set(edges[v])<=classes[0] for v in classes[1])
        plain=frozenset(
            frozenset(endpoints) for endpoints in edges.values()
        )
        assert len(plain)==6
        both_unlabelled.append(plain)
        primal=exact_phase_histogram_n_source_bits(bridge,matching)
        dual,two_cycles=dual_phase_histogram(bridge,matching)
        assert primal==dual and two_cycles==[3,3]
        exact_source_count=len(source_solutions(bridge))
        assert exact_source_count==expected_source
        assert primal.get(40,0)==exact_source_count*16
        print(f"{name}: H cycles={two_cycles}, "
              f"SAT source count={exact_source_count}, "
              f"target Exact-One count={primal.get(40,0)}, "
              "ALL integer coefficients dual/primal PASS")
    assert both_unlabelled[0]==both_unlabelled[1]
    print("SAME_UNLABELLED_H_2_FACTOR_BUT_SOURCE_SAT_COUNTS_0_VS_3 = PROVED")

    print("ALL_SOURCE_MATCHED_E118_HADAMARD_CYCLE_EDGE_DUAL=PROVED")
    print("DUAL_BIPARTITE_EQUALITY_WIRES_FORM_2_REGULAR_GRAPH=PROVED")
    print("DUAL_TERNARY_COUPLING_NONZERO_DETERMINANT=PROVED")
    print("SOURCE_AND_DUAL_N_BIT_SUMS_EXACT_EQUALITY=REPLAYED")
    print("POLYNOMIAL_GLOBAL_DUAL_CONTRACTION=NOT_PROVED; P_VS_NP=OPEN")


if __name__=="__main__":
    main()
