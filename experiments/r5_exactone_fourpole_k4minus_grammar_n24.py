#!/usr/bin/env python3
"""R5: exact K4-minus-edge four-4pole assembly grammar + physical n24 control.

ALL-SIZE SEMANTIC COMPOSITION THEOREM.
Take four arbitrary connected properly colourable cubic FOURPOLES
A,B,C,D, each of the 11 globally allowed 4-pole signature classes
(2-4 S3 orbits among AAAA,AABB,ABAB,ABBA), and join their 4 physical
semiports according to the "diamond" or K4-minus-an-edge block graph:
  A[2]=C[1], A[3]=D[1], B[2]=C[2],
  B[3]=D[2], C[3]=D[3].
Physical outer six ports are A[:2],B[:2],C[0],D[0].
Every index represents one distinct physical semiedge.

The relation is the existential JOIN over 5 shared edge-colour
variables. Analyse all 11^4 fourpole-class assignments and all 15
unordered perfect logical pairings of remaining six external ports:
  14641 class assignments, of which 70 are uncolourable;
  219615 class+logical-pairing combinations;
  GOOD-only singlebit:
       100: 340, 010: 274, 001: 213
  GOOD-only TWO bits:
       {100,010}: 2, {001,010}: 2
  GOOD-only full THREE bits: ZERO.
All four TWO-bit composed relations have exactly 72 distinct physical
port colour tuples. This is exact for the entire K4-e grammar at ALL
internal block sizes because 11-class 4pole signature atlas is all-n.

A real n24 example built from FOUR separate 6-vertex connected
hetero-two 4pole components proves physical attainability:
  24 vertices, 33 ordinary edges, six distinct external roots,
  exact 72 proper full internal edge 3-colourings / external tuples,
  physical equality Bits exactly {100,010} (36 each).
  HOWEVER, its actual original graph has ONE internal bridge (6,9):
  its block skeleton K4-e is bridgeless, but the physical full graph
  is NOT. Do NOT call this a bridgeless two-bit gadget!

The 10-vertex bridge 2+4 two-bit gadget already exists. This n24
graph demonstrates a more cyclic 4-block syntax but remains within
the previous 2+4 physical bridge class. It does NOT construct a full
108-state Exact-One gadget or polynomial SolveLinearCubicXSAT.
"""
from collections import Counter,defaultdict
from itertools import combinations,product

from r5_exactone_bridge_grammar_two_bit_n10 import (
    expand_fourpole_class,FOUR_ORBITS,GOOD,PHYSICAL_COLOURS,
    perfect_matchings,port_bits,direct_full_colourings
)

BASE_EDGES=((0,1),(0,2),(0,3),(1,2),(3,4),(3,5),(4,5))
BASE_ROOTS=(1,2,4,5)
CLASSES=(4,5,3,3)
PORT_PERMUTATIONS=(
    (0,2,1,3), # A class 4
    (0,1,2,3), # B class 5
    (0,2,3,1), # C class 3
    (0,2,3,1), # D class 3
)
PHYSICAL_PAIRING=((0,5),(1,4),(2,3))


def assembled_relation_and_catalogue():
    signatures=tuple(expand_fourpole_class(s)
                     for k in (2,3,4)
                     for s in combinations(FOUR_ORBITS,k))
    assert len(signatures)==11 and len(set(signatures))==11
    twoport=[]
    oneport=[]
    for relation in signatures:
        m2=defaultdict(set);m1=defaultdict(set)
        for state in relation:
            m2[(state[2],state[3])].add(state[:2])
            m1[(state[1],state[2],state[3])].add(state[0])
        twoport.append(m2)
        oneport.append(m1)

    def build_relation(i,j,k,l):
        outside=set()
        A,B=twoport[i],twoport[j]
        C,D=oneport[k],oneport[l]
        for x,y,z,w,t in product(PHYSICAL_COLOURS,repeat=5):
            aa=A.get((x,y),())
            if not aa:continue
            bb=B.get((z,w),())
            if not bb:continue
            cc=C.get((x,z,t),())
            if not cc:continue
            dd=D.get((y,w,t),())
            if not dd:continue
            for a,b,c,d in product(aa,bb,cc,dd):
                outside.add(a+b+(c,d))
        return frozenset(outside)
    return signatures,build_relation


def all_n_k4minus_grammar_gate():
    signatures,relation=assembled_relation_and_catalogue()
    pairings=tuple(perfect_matchings(range(6)))
    assert len(pairings)==15
    all_cases=0; empty=0; good=Counter()
    two_examples={}
    for indices in product(range(11),repeat=4):
        r=relation(*indices)
        if not r:
            empty+=1
            all_cases+=15
            continue
        for pairing in pairings:
            all_cases+=1
            bits=frozenset(port_bits(state,pairing) for state in r)
            if bits<=GOOD:
                assert bits
                assert len(r)==36*len(bits),(indices,pairing,bits,len(r))
                assert len(bits) in (1,2)
                good[tuple(sorted(bits))]+=1
                if len(bits)==2:
                    two_examples.setdefault(tuple(sorted(bits)),
                                            (indices,pairing))
    assert all_cases==11**4*15==219615
    assert empty==70
    assert good==Counter({
        ("100",):340, ("010",):274, ("001",):213,
        ("010","100"):2, ("001","010"):2,
    }),good
    assert sum(v for bits,v in good.items() if len(bits)==2)==4
    # Independently re-evaluate one fixed physical graph's signature.
    explicit=relation(*CLASSES)
    assert len(explicit)==72
    assert Counter(port_bits(s,PHYSICAL_PAIRING) for s in explicit)==Counter({
        "100":36,"010":36
    })
    print("ALL_N_K4_MINUS_EDGE_FOUR_4POLE_GRAMMAR",{
        "fourpole_signature_classes":11,
        "class_assignments":14641,"uncolourable_assignments":empty,
        "paired_compositions":219615,
        "GOODonly_single_bit":{''.join(k):v for k,v in good.items() if len(k)==1},
        "GOODonly_two_bits":{'/'.join(k):v for k,v in good.items() if len(k)==2},
        "GOODonly_full_three_bits":0,
    },flush=True)
    return signatures,explicit


def actual_n24_graph():
    E=[]
    ps=[]
    for k,perm in enumerate(PORT_PERMUTATIONS):
        offset=6*k
        E.extend((u+offset,v+offset) for u,v in BASE_EDGES)
        ps.append(tuple(BASE_ROOTS[j]+offset for j in perm))
    A,B,C,D=ps
    E.extend(((A[2],C[1]),(A[3],D[1]),(B[2],C[2]),
              (B[3],D[2]),(C[3],D[3])))
    E=tuple(sorted(tuple(sorted(edge)) for edge in E))
    roots=A[:2]+B[:2]+C[:1]+D[:1]
    assert len(E)==33 and len(set(E))==33
    assert roots==(1,4,7,8,13,19)
    assert len(set(roots))==6
    return E,roots


def graph_is_connected(E,n=24):
    adj=[[] for _ in range(n)]
    for u,v in E:adj[u].append(v);adj[v].append(u)
    seen={0};stack=[0]
    while stack:
        for v in adj[stack.pop()]:
            if v not in seen:
                seen.add(v);stack.append(v)
    return len(seen)==n


def physical_replay(signatures,predicted):
    # Check all FOUR real 4pole port permutations have the exact
    # catalogue signatures used in the all-size symbolic composition.
    def canon(s):
        dictionary={}
        return tuple(dictionary.setdefault(c,len(dictionary)) for c in s)
    orderedclasses=tuple(
        frozenset(canon(s) for s in signatures[k])
        for k in CLASSES
    )
    for k,perm in enumerate(PORT_PERMUTATIONS):
        root_positions=tuple(BASE_ROOTS[i] for i in perm)
        p=direct_full_colourings(BASE_EDGES,root_positions)
        assert frozenset(canon(s) for s in p)==orderedclasses[k]
    E,roots=actual_n24_graph()
    assert graph_is_connected(E)
    bridges=[e for e in E if not graph_is_connected(
        tuple(x for x in E if x!=e))]
    assert bridges==[(6,9)],bridges
    full=direct_full_colourings(E,roots)
    assert frozenset(full)==predicted,(len(full),len(predicted))
    bits=Counter(port_bits(p,PHYSICAL_PAIRING) for p in full)
    assert bits==Counter({"100":36,"010":36}),bits
    assert len(full)==72
    assert sum(map(len,full.values()))==72
    assert set(map(len,full.values()))=={1}
    print("REAL_PHYSICAL_N24_FOUR_BLOCK_K4_MINUS_EDGE_TWO_BIT",{
        "n":24,"ordinary_edges":len(E),
        "physical_port_roots":roots,"logical_pairing":PHYSICAL_PAIRING,
        "full_colourings":72,"physical_states":72,
        "bit_histogram":dict(bits),
        "actual_graph_bridges":bridges,
        "block_level_skeleton_is_bridgeless":True,
        "real_graph_is_bridgeless":False,
    },flush=True)


if __name__=="__main__":
    signatures,predicted=all_n_k4minus_grammar_gate()
    physical_replay(signatures,predicted)
    print("ALL_N_K4_e_CYCLIC_GRAMMAR_HAS_NO_THREE_BIT_GOODONLY")
    print("FULL_108_EXACTONE_SIXPOLE_OPEN; SolveLinearCubicXSAT_NOT_CONSTRUCTED; P_VS_NP_OPEN")
