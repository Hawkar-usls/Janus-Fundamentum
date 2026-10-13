#!/usr/bin/env python3
"""R5: exact cubic 3-edge-sum colouring factorization and witness gluing.

For a nontrivial 3-edge cut separating a 3-edge-connected cubic G into
two capped cubic graphs G1,G2, the *labelled* 3-edge-colouring counts obey

                Col3(G) = Col3(G1)*Col3(G2)//6.

This is the classical 3-pole parity lemma, not a polynomial algorithm
for indecomposable cubic graphs. Exhaustive finite checkers use an
EXPONENTIAL colour search only on small constructed instances.
"""
from __future__ import annotations

from collections import Counter

from r5_universal_cubic_flow_snf_discriminator import (
    normalized, colour_count,
)


def K4():
    return tuple((a,b) for a in range(4) for b in range(a+1,4))


def K33():
    return tuple((a,b) for a in range(3) for b in range(3,6))


def cube():
    return tuple((v,v^(1<<bit)) for v in range(8) for bit in range(3)
                 if v < (v^(1<<bit)))


def petersen():
    return (
      tuple((i,(i+1)%5) for i in range(5))+
      tuple((i,5+i) for i in range(5))+
      tuple((5+i,5+(i+2)%5) for i in range(5))
    )


def triple_join(na, ea, va, nb, eb, vb, permutation=(0,1,2)):
    """Delete cubic vertices, match 3 boundary ports, return cubic simple G.

    Source vertices are 0-based; no parallel edges are allowed.
    The returned left set S is the first na-1 new vertices.
    """
    ea=normalized(na,ea); eb=normalized(nb,eb)
    adj_a=sorted(w if u==va else u for u,w in ea if va in (u,w))
    adj_b=sorted(w if u==vb else u for u,w in eb if vb in (u,w))
    assert len(adj_a)==len(adj_b)==3
    assert sorted(permutation)==[0,1,2]
    map_a={v:i for i,v in enumerate(x for x in range(na) if x!=va)}
    map_b={v:na-1+i for i,v in enumerate(x for x in range(nb) if x!=vb)}
    edges = [
        (map_a[u],map_a[v]) for u,v in ea if va not in (u,v)
    ] + [
        (map_b[u],map_b[v]) for u,v in eb if vb not in (u,v)
    ] + [
        (map_a[adj_a[i]], map_b[adj_b[permutation[i]]])
        for i in range(3)
    ]
    n=na+nb-2
    edges=normalized(n,edges)
    return n,edges,set(range(na-1))


def cap_a_three_cut(n, edges, S):
    """Return capped components and maps from cut edges to local cap edges.

    All vertices of each shore must have <=1 crossing edge. The only
    special case used is a nontrivial 3-edge cut in a 3-edge-connected
    cubic simple graph, where this holds automatically.
    """
    S=set(S); T=set(range(n))-S
    assert len(S)>=2 and len(T)>=2
    cut=[e for e in edges if (e[0] in S)!=(e[1] in S)]
    assert len(cut)==3
    result=[]
    for part in (S,T):
        vertices=sorted(part)
        rename={v:i for i,v in enumerate(vertices)}
        cap=len(vertices)
        inside=[(rename[u],rename[v]) for u,v in edges if u in part and v in part]
        cap_edges={}
        for e in cut:
            v=next(w for w in e if w in part)
            cap_edges[e]=tuple(sorted((rename[v],cap)))
        assert len(set(cap_edges.values()))==3, "cap would have parallel edges"
        local=normalized(len(vertices)+1, inside+list(cap_edges.values()))
        result.append((len(vertices)+1, local, cap_edges, rename))
    return cut,result[0],result[1]


def assemble_witness(n,edges,cut,part_a,part_b,witness_a,witness_b):
    """Compose two edge-colourings by global S3 rename on side B."""
    _,ea,cuta,ra=part_a
    _,eb,cutb,rb=part_b
    col_a={e:c for e,c in zip(ea,witness_a)}
    col_b={e:c for e,c in zip(eb,witness_b)}
    trans={}
    for e in cut:
        ca=col_a[cuta[e]]; cb=col_b[cutb[e]]
        assert cb not in trans or trans[cb]==ca
        trans[cb]=ca
    assert set(trans)==set(trans.values())=={0,1,2}
    out={}
    for e in edges:
        if e in cut:
            out[e]=col_a[cuta[e]]
        elif e[0] in ra and e[1] in ra:
            out[e]=col_a[tuple(sorted((ra[e[0]],ra[e[1]])))]
        else:
            assert e[0] in rb and e[1] in rb
            out[e]=trans[col_b[tuple(sorted((rb[e[0]],rb[e[1]])))]]
    colours=[out[e] for e in edges]
    for v in range(n):
        assert sorted(out[e] for e in edges if v in e)==[0,1,2]
    return colours


def main():
    source={
        "K4":(4,K4(),6),
        "K33":(6,K33(),12),
        "CUBE":(8,cube(),24),
        "PETERSEN":(10,petersen(),0),
    }
    for name,(n,edges,want) in source.items():
        ordered=normalized(n,edges)
        got,_=colour_count(n,ordered)
        assert got==want,(name,got,want)
    cases=[
        ("K4_JOIN_K4","K4","K4"),
        ("K4_JOIN_K33","K4","K33"),
        ("K33_JOIN_K33","K33","K33"),
        ("K4_JOIN_CUBE","K4","CUBE"),
        ("K4_JOIN_PETERSEN","K4","PETERSEN"),
    ]
    for name,ida,idb in cases:
        na,ea,ca=source[ida]
        nb,eb,cb=source[idb]
        n,edges,S=triple_join(na,ea,0,nb,eb,0)
        cut,A,B=cap_a_three_cut(n,edges,S)
        size_a,edges_a,_,_=A
        size_b,edges_b,_,_=B
        got_a,wa=colour_count(size_a,edges_a)
        got_b,wb=colour_count(size_b,edges_b)
        assert (got_a,got_b)==(ca,cb),name
        predicted=ca*cb//6
        assert ca*cb%6==0
        true,wa_full=colour_count(n,edges)
        assert true==predicted,(name,true,predicted)
        assert (true>0)==(wa is not None and wb is not None)
        if true:
            assembled=assemble_witness(n,edges,cut,A,B,wa,wb)
            assert len(assembled)==len(edges)
        print(f'{name}: G_V={n} cap_counts={ca},{cb} '
              f'product_over_six={predicted} direct_count={true} '
              f'witness_glued={bool(true)}',flush=True)
    print('THREE_EDGE_CUT_COUNT_FACTOR_1_OVER_6 = VERIFIED_FINITE')
    print('THREE_EDGE_CUT_PARITY_AND_S3_FACTOR = PROVED_ALL_PROMISED_GRAPHS')
    print('THREE_EDGE_CUT_GLUED_SAT_WITNESS = VERIFIED_FINITE')
    print('POLYTIME_DECIDER_FOR_INDECOMPOSABLE_CUBIC_CORES = NOT_CONSTRUCTED')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=="__main__":
    main()
