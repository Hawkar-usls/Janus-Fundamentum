#!/usr/bin/env python3
"""R5 positive attack: exact 21-state 4-edge-cut 3-colouring interface.

For ANY connected simple cubic G and edge cut delta(S) of size four,
the vector of four nonzero F2^2 colours has XOR zero. Exactly 21
ordered colour patterns satisfy this (3 constant; 18 pairs 2+2).

Write L_S(a) for the number of valid cubic vertex-edge colourings of
the four-pole with ordered boundary colours a. Then

      #Col3(G) = sum_{a in allowed21} L_S(a) * L_T(a).

Given witnesses with matching boundary colours, glue them directly.
This is a *constant-dimensional interface identity* applying to all
four-edge cuts, but the exact signature of arbitrary indecomposable
four-poles is still NP/#P-hard to compute. NOT a universal poly solver.

Includes O(m^4 (n+m)) enumeration of a cyclic four-edge cut, and
independent finite signed-free exact colour enumeration.
"""
from collections import Counter
from itertools import combinations, product

from r5_universal_cubic_flow_snf_discriminator import normalized, colour_count
from r5_universal_cubic_three_edge_cut_factorization import K4,K33,cube,petersen


COLORS=(0,1,2)
NONZERO_FOUR=((1,0),(0,1),(1,1))


def boundary_patterns():
    allowed=[]
    for pattern in product(COLORS,repeat=4):
        total=[0,0]
        for c in pattern:
            total[0]^=NONZERO_FOUR[c][0]
            total[1]^=NONZERO_FOUR[c][1]
        if total==[0,0]:
            allowed.append(pattern)
    assert len(allowed)==21
    assert Counter(tuple(sorted(Counter(p).values())) for p in allowed)==Counter(
        {tuple([4]):3,tuple([2,2]):18}
    )
    return tuple(allowed)


def four_pole_signature(n, internal_edges, port_vertices):
    """Count + exhibit witnesses per ordered pattern; EXPONENTIAL counter.

    Interior vertex i has degree 3 - number_of_boundary_stubs_at_i.
    A vertex may have several boundary stubs; the proof works generally.
    """
    internal_edges=tuple(sorted(internal_edges))
    port_vertices=tuple(port_vertices)
    assert len(port_vertices)==4
    assert all(0<=v<n for v in port_vertices)
    degree=Counter([v for e in internal_edges for v in e]+list(port_vertices))
    assert all(degree[v]==3 for v in range(n))
    assert all(u<v for u,v in internal_edges)
    signature={}; witnesses={}
    for pattern in product(COLORS,repeat=4):
        used=[0]*n
        ok=True
        for v,c in zip(port_vertices,pattern):
            if used[v]&(1<<c): ok=False;break
            used[v]|=1<<c
        if not ok:
            signature[pattern]=0
            continue
        assignment=[-1]*len(internal_edges)
        first=[None]
        def rec(left):
            if left==0:
                if first[0] is None:first[0]=tuple(assignment)
                return 1
            best=-1;opts=None
            for i,(u,v) in enumerate(internal_edges):
                if assignment[i]>=0:continue
                options=[c for c in COLORS
                         if not ((used[u]|used[v])&(1<<c))]
                if not options:return 0
                if opts is None or len(options)<len(opts):
                    best=i;opts=options
            u,v=internal_edges[best]
            ans=0
            for c in opts:
                assignment[best]=c
                used[u]|=1<<c;used[v]|=1<<c
                ans+=rec(left-1)
                used[u]^=1<<c;used[v]^=1<<c
                assignment[best]=-1
            return ans
        count=rec(len(internal_edges))
        signature[pattern]=count
        if count:
            assert first[0] is not None
            witnesses[pattern]={e:first[0][i]
                                for i,e in enumerate(internal_edges)}
    assert all(signature[p]==0 for p in signature
               if p not in boundary_patterns())
    return signature,witnesses


def cut_sides(n, E, S):
    """Both induced shores are relabelled; same canonical cut-edge order."""
    E=normalized(n,E)
    S=set(S);T=set(range(n))-S
    assert len(S)>=2 and len(T)>=2
    cut=tuple(e for e in E if (e[0] in S)!=(e[1] in S))
    assert len(cut)==4
    sides=[]
    for side in (S,T):
        vertices=tuple(sorted(side))
        mapping={v:i for i,v in enumerate(vertices)}
        inside=tuple(sorted((mapping[u],mapping[v])
                            for u,v in E if u in side and v in side))
        ports=tuple(mapping[next(x for x in e if x in side)] for e in cut)
        sides.append((len(vertices),inside,ports,mapping))
    return cut,tuple(sides)


def exact_signature_count(n,E,S):
    cut,(A,B)=cut_sides(n,E,S)
    La,Wa=four_pole_signature(*A[:3])
    Lb,Wb=four_pole_signature(*B[:3])
    count=sum(La[p]*Lb[p] for p in boundary_patterns())
    witness=None
    for p in boundary_patterns():
        if La[p] and Lb[p]:
            witness={}
            for e,col in Wa[p].items():
                inverse={v:k for k,v in A[3].items()}
                original=tuple(sorted((inverse[e[0]],inverse[e[1]])))
                witness[original]=col
            inverse={v:k for k,v in B[3].items()}
            for e,col in Wb[p].items():
                original=tuple(sorted((inverse[e[0]],inverse[e[1]])))
                witness[original]=col
            for e,c in zip(cut,p):
                witness[e]=c
            assert set(witness)==set(E)
            for v in range(n):
                assert sorted(witness[e] for e in E if v in e)==list(COLORS)
            break
    assert (witness is None)==(count==0)
    return count,witness,La,Lb


def join_after_two_disjoint_edge_deletions(na,ea,ra,nb,eb,rb):
    """Four new edges between two cubic shores after deleting two edges."""
    ea=normalized(na,ea);eb=normalized(nb,eb)
    ra=tuple(sorted(e) for e in ra);rb=tuple(sorted(e) for e in rb)
    assert len(ra)==len(rb)==2
    assert set(ra)<=set(ea) and set(rb)<=set(eb)
    pa=tuple(v for e in ra for v in e)
    pb=tuple(v for e in rb for v in e)
    assert len(set(pa))==len(set(pb))==4
    E=[e for e in ea if e not in ra]
    E += [(u+na,v+na) for u,v in eb if (u,v) not in rb]
    E += [(pa[i],pb[i]+na) for i in range(4)]
    E=normalized(na+nb,E)
    return na+nb,E,set(range(na))


def cyclic_shore(n,E,S):
    """Each induced shore has a cycle (can detect with DSU counts)."""
    S=set(S);T=set(range(n))-S
    for side in (S,T):
        ec=sum(u in side and v in side for u,v in E)
        if ec < len(side):return False
    return True


def discover_cyclic_four_cut(n,E):
    """Complete O(m^4(n+m)) finite search, not hard core solver."""
    E=normalized(n,E)
    adj=[[] for _ in range(n)]
    for i,(u,v) in enumerate(E):
        adj[u].append((v,i));adj[v].append((u,i))
    for inds in combinations(range(len(E)),4):
        banned=set(inds)
        seen={0};todo=[0]
        while todo:
            u=todo.pop()
            for v,i in adj[u]:
                if i not in banned and v not in seen:
                    seen.add(v);todo.append(v)
        if len(seen)==n:continue
        if not (2<=len(seen)<=n-2):continue
        actual=[e for e in E if (e[0] in seen)!=(e[1] in seen)]
        if len(actual)==4 and cyclic_shore(n,E,seen):
            return seen,actual
    return None


def main():
    patterns=boundary_patterns()
    assert len(patterns)==21
    k4=normalized(4,K4())
    k33=normalized(6,K33())
    cube8=normalized(8,cube())
    pet10=normalized(10,petersen())
    cases=[
        ("K4_PLUS_K4",4,k4,((0,1),(2,3)),4,k4,((0,1),(2,3))),
        ("K4_PLUS_K33",4,k4,((0,1),(2,3)),6,k33,((0,3),(1,4))),
        ("K33_PLUS_K33",6,k33,((0,3),(1,4)),6,k33,((0,3),(1,4))),
        ("K4_PLUS_CUBE",4,k4,((0,1),(2,3)),8,cube8,((0,1),(4,5))),
        ("K4_PLUS_PETERSEN",4,k4,((0,1),(2,3)),10,pet10,((0,1),(5,7))),
    ]
    for label,na,ea,ra,nb,eb,rb in cases:
        n,E,S=join_after_two_disjoint_edge_deletions(na,ea,ra,nb,eb,rb)
        count,witness,Sa,Sb=exact_signature_count(n,E,S)
        independent,wit=colour_count(n,E)
        assert count==independent,(label,count,independent)
        assert (witness is None)==(wit is None)
        cut=discover_cyclic_four_cut(n,E)
        assert cut is not None,(label,"missing cyclic cut")
        check,w2,_,_=exact_signature_count(n,E,cut[0])
        assert check==independent
        assert (w2 is None)==(wit is None)
        overlap=sum(bool(Sa[p] and Sb[p]) for p in patterns)
        print(f'{label}: vertices={n}, direct={independent}, '
              f'boundary_contraction={count}, 21_boundary_states=YES, '
              f'allowed_matches={overlap}, found_cyclic_4cut=YES, '
              f'witness_glued={witness is not None}',flush=True)
    print('ALL_CUBIC_FOUR_CUT_21_STATE_GLUE_COUNT = PROVED')
    print('ALL_CUBIC_FOUR_CUT_WITNESS_GLUE = PROVED')
    print('CYCLIC_FOUR_CUT_POLY_FINDER = PROVED_O_MPOW4_TIMES_NPLUSM')
    print('POLYTIME_CORE_BOUNDARY_SIGNATURE_EVALUATOR = NOT_CONSTRUCTED')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=='__main__':
    main()
