#!/usr/bin/env python3
"""R5: exact cube-of-Pfaffian coefficient cancellation audit.

For simple cubic G, Q_G(x)=Pf(K_G(x)) for the skew adjacency
matrix with ordered vertices and signs +x_(u,v) for u<v.
Each perfect matching contributes its crossing-parity sign.

The coefficient [product_(e in E) x_e] Q_G(x)^3 is an algebraic sum
of 3-edge-colourings. On SAT K3,3 it is EXACTLY ZERO, independently
of vertex order or of flipping each common edge sign.
The *unsigned* perfect-matching polynomial cube has a positive
coefficient (12). Three independently-labelled Pfaffians instead have
a nonzero coefficient POLYNOMIAL on every SAT graph.

This does NOT produce an n^O(1) coefficient extraction algorithm.
All exact finite counters below are worst-case exponential.
"""
from itertools import combinations

from r5_universal_cubic_flow_snf_discriminator import normalized, colour_count
from r5_universal_cubic_flow_lowmoment_collision_20v import flower, SAT20


def enumerate_matchings(n, E):
    edge_set = set(E)
    def walk(rem):
        if not rem:
            yield ()
            return
        u = min(rem)
        for v in sorted(rem - {u}):
            if (u,v) not in edge_set: continue
            for tail in walk(rem-{u,v}):
                yield ((u,v),)+tail
    yield from walk(set(range(n)))


def crossing_sign(M):
    pairs=tuple(sorted(M))
    crossings=sum(1 for i,(a,b) in enumerate(pairs)
                  for c,d in pairs[i+1:]
                  if (a<c<b<d) or (c<a<d<b))
    return -1 if crossings%2 else 1


def exact_pfaffian_cube(n, raw, orientation_masks=(0,0,0)):
    E=normalized(n,raw)
    m=len(E)
    allmask=(1<<m)-1
    edge_index={e:i for i,e in enumerate(E)}
    records=[]
    for M in enumerate_matchings(n,E):
        mask=sum(1<<edge_index[e] for e in M)
        records.append((mask,crossing_sign(M)))
    index={mask:sign for mask,sign in records}
    assert len(index)==len(records)
    positive=negative=0
    for mask0,sign0 in records:
        for mask1,sign1 in records:
            if mask0 & mask1: continue
            mask2=allmask^(mask0|mask1)
            if mask2 not in index: continue
            sign=sign0*sign1*index[mask2]
            for i,mask in enumerate((mask0,mask1,mask2)):
                if (mask & orientation_masks[i]).bit_count()%2:
                    sign=-sign
            if sign==1: positive+=1
            else: negative+=1
    return positive,negative,len(records)


def make_cube():
    return [(v,v^(1<<bit)) for v in range(8) for bit in range(3)
            if v<(v^(1<<bit))]


def pentagonal_prism():
    return ([(i,(i+1)%5) for i in range(5)]
            + [(i,5+i) for i in range(5)]
            + [(5+i,5+(i+1)%5) for i in range(5)])


def petersen():
    return ([(i,(i+1)%5) for i in range(5)]
            + [(i,5+i) for i in range(5)]
            + [(5+i,5+(i+2)%5) for i in range(5)])


def main():
    cases=(
        ('K4',4,list(combinations(range(4),2)),6),
        ('K33',6,[(u,v) for u in range(3) for v in range(3,6)],12),
        ('CUBE',8,make_cube(),24),
        ('PRISM5',10,pentagonal_prism(),30),
        ('PETERSEN',10,petersen(),0),
        ('FLOWER_J5',20,flower(5),0),
        ('SAT20',20,SAT20,72),
    )
    for name,n,raw,expected in cases:
        E=normalized(n,raw)
        direct,witness=colour_count(n,E)  # independent graph backtracker
        pos,neg,pm=exact_pfaffian_cube(n,E)
        assert direct==expected
        assert pos+neg==direct, (name,pos,neg,direct)
        assert (witness is not None)==(expected>0)
        if name=='K33':
            assert (pos,neg,pm)==(6,6,6)
            assert pos-neg==0 and direct==12
            # The same edge signs used in all three Pfaffian factors
            # multiply every full-squarefree term by one fixed global
            # sign, hence cannot repair K33 cancellation.
            for common_signs in (0,1,0x155,0x1ff):
                a,b,_=exact_pfaffian_cube(n,E,(common_signs,)*3)
                assert (a,b)==(6,6)
            # Distinct factor orientation signs can break cancellation.
            p,q,_=exact_pfaffian_cube(n,E,(114,25,281))
            assert (p,q,p-q)==(4,8,-4)
        print(f'{name}: vertices={n}, edge_colours={direct}, '
              f'perfect_matchings={pm}, PfCube_plus={pos}, '
              f'PfCube_minus={neg}, PfCube_signed={pos-neg}',flush=True)

    print('K33_SAT12_BUT_SINGLE_PFAFFIAN_CUBE_COEFFICIENT_ZERO = PROVED_FINITE')
    print('COMMON_EDGE_REORIENTATION_CANNOT_REPAIR_CANCELLATION = PROVED_ALL_GRAPH')
    print('INDEPENDENT_LABELLED_THREE_PFAFFIAN_COEFFICIENT =')
    print('    NONZERO_POLYNOMIAL_IFF_EDGE_3COLOURABLE, IDENTITY_ONLY')
    print('POLY_TIME_SQUAREFREE_COEFFICIENT_EXTRACTOR = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=='__main__':
    main()
