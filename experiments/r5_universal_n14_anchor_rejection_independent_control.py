#!/usr/bin/env python3
"""Independent control for anchored n14 exact-one rejection logic.

Two distinct manually constructed 14-vertex / 18-edge sixpoles
(14-cycle + four disjoint chords; no isomorphism claim) are exhaustively coloured by an
independent non-anchored DFS. All 15 full boundary bit relations are
obtained without early pruning and compared with their versions
restricted to first edge colour 0. We also call the optimized
anchored exact-one candidate detector on each exact same graph.
Never treat this as an all-n14 classification; the large nauty
census is independent CI and must finish separately.
"""
from itertools import product
from collections import Counter
from r5_universal_exposed_exactone_n14_anchored_rejection import (
    PAIRINGS,ONEHOT_MASK,graph_test
)


CHORDS={
    "antipodal": ((0,7),(1,8),(2,9),(3,10)),
    "mixed": ((0,5),(1,7),(2,9),(3,11)),
}


def make_graph(label):
    n=14
    edges={tuple(sorted((i,(i+1)%n))) for i in range(n)}
    chords=CHORDS[label]
    assert len({v for e in chords for v in e})==8
    for a,b in chords:
        assert a!=b
        edges.add(tuple(sorted((a,b))))
    E=tuple(sorted(edges))
    assert len(E)==18
    D=Counter(x for e in E for x in e)
    assert all(D[x] in (2,3) for x in range(n))
    assert sum(3-D[x] for x in range(n))==6
    return E


def full_relations(E,first_colour=None):
    n=14
    inc=[[] for _ in range(n)]
    for i,(a,b) in enumerate(E):
        inc[a].append(i)
        inc[b].append(i)
    count=0
    seen=set()
    c=[-1]*len(E)
    signatures=[]
    def dfs(i):
        nonlocal count
        if i==len(E):
            count+=1
            opts=[]
            for inds in inc:
                miss=[x for x in range(3) if x not in [c[t] for t in inds]]
                if len(miss)==1:
                    opts.append([miss])
                elif len(miss)==2:
                    opts.append([miss,miss[::-1]])
            for v in product(*opts):
                state=tuple(x for block in v for x in block)
                assert len(state)==6
                seen.add(state)
            return
        a,b=E[i]
        for x in range(3):
            if i==0 and first_colour is not None and x!=first_colour:
                continue
            if any(c[t]==x for u in (a,b) for t in inc[u] if t<i):
                continue
            c[i]=x
            dfs(i+1)
            c[i]=-1
    dfs(0)
    rel=[frozenset(tuple(int(s[a]==s[b]) for a,b in pair)
                   for s in seen) for pair in PAIRINGS]
    return rel,count,len(seen)


def main():
    previous=set()
    for offset in CHORDS:
        E=make_graph(offset)
        # Independent physical-colour reference enumerates every label,
        # not only the globally normalized colour of the first edge.
        full,nfull,ns=full_relations(E,None)
        anch,nanch,nas=full_relations(E,0)
        assert nanch>0 and nfull==3*nanch
        assert full==anch,("anchoring changes equality bits",offset)
        expected=any(rel==frozenset(((1,0,0),(0,1,0),(0,0,1)))
                     for rel in full)
        result,ports,exact,_,_=graph_test(E)
        assert (result=="candidate")==expected
        assert len(ports)==6
        print("N14_CONTROL",{"topology":offset,"full_colourings":nfull,
             "anchored":nanch,"full_boundary_signatures":ns,
             "anchored_boundary_signatures":nas,
             "full_pairing_equals_anchored":True,
             "optimized_result":result})
        previous.add(tuple(sorted(E)))
    print("N14_ANCHORED_SOURCE_ALGORITHM_CONTROL_PASS")
    print("ALL_N14_ISOM_GRAPH_CENSUS: independently validated by its own CI only")


if __name__=="__main__":
    main()
