#!/usr/bin/env python3
"""R5 all-cubic 2-adic Hamiltonian-cycle filtration (exact, not poly).

For a cubic graph with labelled 3-edge-colouring count F(G), fix an edge
e0 incident to a reference vertex. Every proper colouring with the
prescribed three reference-edge colours corresponds to a perfect
matching M containing e0, such that G-M consists only of even cycles.
If it has c cycles it contributes 2**(c-1) colourings.

EXACT all-graph theorem: F(G)/6 = sum_{M includes e0,
                                   G-M all even cycles} 2**(c(M)-1).
Therefore modulo 2**s, only 2-factors with c<=s can contribute.
In particular F(G)/6 mod2 = number of Hamiltonian cycles OMITTING e0 mod2.
By Smith/Thomason parity theorem every edge belongs to an EVEN
number of Hamiltonian cycles, so this equals the parity of the
TOTAL number of Hamiltonian cycles.

No polynomial enumeration for arbitrary Hamiltonian cycles or
perfect matchings is claimed. Exact finite tests are exponential.
"""
from collections import Counter

from r5_universal_cubic_flow_snf_discriminator import (
    normalized, colour_count,
)
from r5_universal_cubic_flow_lowmoment_collision_20v import (
    flower,SAT20,three_edge_colour_count,
)
from r5_universal_cubic_three_edge_cut_factorization import (
    K4,K33,cube,petersen,
)
from r5_universal_modular_flow_count_all_q_no_go import prism


def matchings(n,E):
    adj=[set() for _ in range(n)]
    for u,v in E:
        adj[u].add(v);adj[v].add(u)
    def rec(unused,chosen):
        if not unused:
            yield tuple(chosen)
            return
        u=min(unused)
        for v in sorted(adj[u]&unused):
            yield from rec(unused-{u,v},chosen+[(min(u,v),max(u,v))])
    yield from rec(set(range(n)),[])


def residual_cycles(n,E,M):
    """Return residual cycle lengths (including odd cycles)."""
    MM=set(M)
    nbrs=[[] for _ in range(n)]
    for u,v in E:
        if (u,v) not in MM:
            nbrs[u].append(v);nbrs[v].append(u)
    assert all(len(ns)==2 for ns in nbrs)
    seen=set(); lengths=[]
    for start in range(n):
        if start in seen:continue
        v,prev=start,-1
        L=0
        while v not in seen:
            seen.add(v)
            L+=1
            a,b=nbrs[v]
            next_v=b if a==prev else a
            prev,v=v,next_v
        assert v==start
        lengths.append(L)
    return tuple(sorted(lengths))


def direct_hamiltonian_cycles(n,E):
    """An independent n<=10 DFS count with one fixed start, reversed divided by two."""
    nbr=[[] for _ in range(n)]
    for u,v in E:
        nbr[u].append(v);nbr[v].append(u)
    def visit(u,mask,first):
        if mask.bit_count()==n:
            return int(0 in nbr[u])
        return sum(visit(v,mask|(1<<v),first)
                   for v in nbr[u] if not(mask&(1<<v)))
    total=sum(visit(v,(1<<0)|(1<<v),v) for v in nbr[0])
    assert total%2==0
    return total//2


def audit(name,n,raw,want):
    E=normalized(n,raw)
    F,_,_=three_edge_colour_count(n,E)
    assert F==want
    assert F%6==0
    C=F//6
    hamiltonians=0
    edge_omit_counts=Counter()
    all_layers={e:Counter() for e in E if 0 in e}
    root_edges=sorted(all_layers)
    assert len(root_edges)==3
    complete=0
    for M in matchings(n,E):
        complete+=1
        comps=residual_cycles(n,E,M)
        if len(comps)==1:
            assert comps==(n,)
            hamiltonians+=1
            for e in root_edges:
                if e not in M: edge_omit_counts[e]+=1
        if any(L%2 for L in comps): continue
        for e in root_edges:
            if e in M:
                all_layers[e][len(comps)]+=1
    for e in root_edges:
        exact=sum(count*2**(cycles-1)
                  for cycles,count in all_layers[e].items())
        assert exact==C,(name,e,exact,C)
        assert all_layers[e][1]==hamiltonians-edge_omit_counts[e]
        # Every edge participates in an even number of Hamiltonian cycles:
        assert edge_omit_counts[e]%2==0,(name,e,edge_omit_counts[e])
        assert (C&1)==(all_layers[e][1]&1)==(hamiltonians&1)
        for s in range(1,min(6,n//2+1)):
            full=C%(1<<s)
            truncated=sum(count*2**(k-1)
                          for k,count in all_layers[e].items()
                          if k<=s) % (1<<s)
            assert full==truncated,(name,e,s,full,truncated)
    if n<=10:
        independently=direct_hamiltonian_cycles(n,E)
        assert hamiltonians==independently
    print(f'{name}: vertices={n}, 3edgecolours={F}, normalized={C}, '
          f'Hamilton_cycles={hamiltonians}, '
          f'root_edge={root_edges[0]}, cycle_layers={dict(sorted(all_layers[root_edges[0]].items()))}, '
          f'parity={C&1}, exact_PM={complete}',flush=True)


def main():
    n5,e5=prism(5)
    tests=(
        ('K4',4,K4(),6),
        ('K33',6,K33(),12),
        ('CUBE',8,cube(),24),
        ('PRISM5',n5,e5,30),
        ('PETERSEN',10,petersen(),0),
        ('FLOWER_J5',20,flower(5),0),
        ('SAT20',20,SAT20,72),
    )
    for case in tests: audit(*case)
    print('ALL_CUBIC_ROOT_EDGE_MATCHING_LAYER_IDENTITY = PROVED')
    print('ROOT_EDGE_2ADIC_TRUNCATION_BY_EVEN_2FACTOR_CYCLES = PROVED')
    print('COLORING_ORBIT_PARITY_EQUALS_HAMILTON_CYCLE_PARITY = PROVED_USING_SMITH')
    print('HAM_CYCLE_PARITY_POLYTIME_ORACLE = NOT_CONSTRUCTED')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=="__main__":
    main()
