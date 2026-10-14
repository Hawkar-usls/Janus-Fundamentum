#!/usr/bin/env python3
"""R5 synchronous-physics heuristic FORMALIZED as exact Klein-four phase gates.

This is a MATHEMATICAL colour-flow project, not evidence for new
physical effects or a polynomial-time method for NP-complete tasks.

Theorem 1. For ANY proper 3-edge-colouring of a cubic 6pole, the three
pair difference vectors dA,dB,dC in F2^2 satisfy dA^dB^dC=0.
One-hot Exact-One is equivalent to rank_F2(dA,dB,dC)==1, or to
det_F2(dA,dB)==0 AND (dA,dB)!=(0,0).

Theorem 2. The full 108-state good boundary relation T has EXACTLY the
SAME projections as the full 183-state parity-legal relation P onto
EVERY subset of size 1, 2, or 3. Therefore no conjunction of
constraints involving <=3 PHYSICAL port colours (even with parity P)
can separate T from its 75 forbidden parity-compatible states.
At least one 4-ary boundary constraint, or an equivalent globally
coupled/auxiliary construction, is necessary.
A *single* 4-ary relation on TWO COMPLETE logical port pairs plus
global parity uniquely recovers T.

Theorem 3. The REAL bridge-free n28 two-bit seed's entire 72-state
physical relation R equals parity P plus these local constraints:
  c2!=c3,
  (c0,c2,c5) NOT all 3 distinct,
  (c0,c3,c5) NOT all 3 distinct.
This is an exact PHASE-COMPATIBILITY characterization of its physical
sixport SUPPORT (NOT a construction of the internal graph).

Quantitative fixed K4-minus-edge fourpole grammar obstruction:
Use the previously verified A,B,C,D wiring:
  A[2]=C[1], A[3]=D[1],
  B[2]=C[2], B[3]=D[2], C[3]=D[3],
  outer6=A[:2]+B[:2]+C[0]+D[0],
  logical pairs ((0,5),(1,4),(2,3)).
All 11^4=14641 choices of all-size allowed fourpole signatures
are examined EXACTLY using local orbit pattern masks (not heuristic).

Among choices realizing ALL 108 good external tuples, the MINIMUM
number of forbidden physical tuples is EXACTLY **42**. This minimum
is attained at signature tuples (4,10,6,7) and (4,10,7,6),
with complete 150-state relation (100:36,010:36,001:36,000:24,111:18).

For original fixed A,C,D=(4,3,3), changing ONLY B to add a
homogeneous orbit:
    B=5 ({ABAB,ABBA}):   100:36,010:36 (72, no BAD)
    B=8 (+AAAA):         100:36,010:36,001:18,111:9
    B=9 (+AABB):         100:36,010:36,001:18,111:18
    B=10 (+both):        100:36,010:36,001:18,111:27.
Thus simply relaxing the old B-block's PHASE LOCK is NOT a viable
third-bit construction and the entire four-4pole wiring is excluded,
even when multiple block classes are synchronized.

All-size result only for specified bounded fourpole grammar; DOES NOT
exclude more complex shared interfaces, any indecomposable gadget,
or a universal polynomial SolveLinearCubicXSAT. P vs NP OPEN.
"""
from collections import Counter, defaultdict
from itertools import combinations, permutations, product

from r5_exactone_bridgeless_n28_twobit_constructive import (
    EXPECTED_N28_EDGES, EXPECTED_N28_ROOTS,
    all_physical_colours, find_bridges,
)

COLOURS=(0,1,2)
GF4=(1,2,3)
PAIRINGS=((0,5),(1,4),(2,3))
GOOD=frozenset(("100","010","001"))
ORBIT_REPS=(
    (0,0,0,0),(0,0,1,1),(0,1,0,1),(0,1,1,0)
)
CLASS_ORBITS=tuple(C for k in (2,3,4)
                   for C in combinations(range(4),k))
assert len(CLASS_ORBITS)==11


def truth(s):
    return ''.join(str(int(s[a]==s[b])) for a,b in PAIRINGS)


def parity_legal(s):
    return all(s.count(c)%2==0 for c in COLOURS)


def phase(s):
    return tuple(GF4[s[a]]^GF4[s[b]] for a,b in PAIRINGS)


def determinant(a,b):
    return ((a&1)*((b>>1)&1))^(((a>>1)&1)*(b&1))


def orbit4(port_values):
    dictionary={}
    rep=tuple(dictionary.setdefault(c,len(dictionary))
              for c in port_values)
    try:
        return ORBIT_REPS.index(rep)
    except ValueError:
        return -1


def bitset_support():
    """All 4-block local orbits -> exact 729-bit sixport supports."""
    records=defaultdict(int)
    for outer in product(COLOURS,repeat=6):
        a0,a1,b0,b1,c0,d0=outer
        physical_code=sum(c*3**(5-i) for i,c in enumerate(outer))
        for x,y,z,w,t in product(COLOURS,repeat=5):
            orb=(orbit4((a0,a1,x,y)),
                 orbit4((b0,b1,z,w)),
                 orbit4((c0,x,z,t)),
                 orbit4((d0,y,w,t)))
            if -1 not in orb:
                records[orb] |= 1<<physical_code
    assert len(records)==92
    return records


def tuple_from_code(i):
    return tuple((i//(3**(5-j)))%3 for j in range(6))


def all_physical_relation_from_classes(records,classes):
    masks=tuple(sum(1<<o for o in CLASS_ORBITS[ci]) for ci in classes)
    relation=0
    for local_orbits,outer_support in records.items():
        if all(masks[v] & (1<<local_orbits[v])
               for v in range(4)):
            relation |= outer_support
    return relation


def histogram_for_relation(bitset):
    counter=Counter()
    while bitset:
        bit=bitset&-bitset
        code=bit.bit_length()-1
        counter[truth(tuple_from_code(code))]+=1
        bitset^=bit
    return counter


def verify_flow_phase_theorem():
    all_729=tuple(product(COLOURS,repeat=6))
    parity=tuple(s for s in all_729 if parity_legal(s))
    target=frozenset(s for s in parity if truth(s) in GOOD)
    assert len(parity)==183
    assert len(target)==108
    assert Counter(truth(s) for s in parity)==Counter({
        "000":48,"100":36,"010":36,"001":36,"111":27
    })
    for s in all_729:
        if not parity_legal(s):
            continue
        a,b,c=phase(s)
        assert (a^b^c)==0
        is_onehot=truth(s) in GOOD
        rank_one=(determinant(a,b)==0 and (a|b)!=0)
        assert rank_one==is_onehot,(s,a,b,c)
    print("ALL_183_PARITY_STATES_GF4_SYNCHRONOUS_RANK_ONE_IFF_EXACTONE PASS")

    # All proper <=3 marginal relations equal parity-only marginals.
    for k in (1,2,3):
        for group in combinations(range(6),k):
            proj=lambda states:{tuple(s[j] for j in group)
                                for s in states}
            assert proj(target)==proj(parity),(k,group)
    # A 4-port gate seeing the TWO COMPLETE logical pairs suffices
    # under global cubic Kirchhoff/port parity constraints.
    group=(0,5,1,4)
    allowed={tuple(s[i] for i in group) for s in target}
    recovered={s for s in parity if
               tuple(s[i] for i in group) in allowed}
    assert len(allowed)==48 and recovered==target
    print("TRIPLE_ONLY_SYNCHRONIZATION_CANNOT_EXCLUDE_75_FORBIDDEN PASS")
    print("TWO_COMPLETE_PAIRS_FOUR_BODY_SYNC_GATE_PLUS_PARITY_EXACT_108 PASS")
    return frozenset(parity),target


def verify_n28_two_bit_boundary_physics(parity):
    E=EXPECTED_N28_EDGES
    roots=EXPECTED_N28_ROOTS
    assert len(E)==39 and len(set(roots))==6
    assert not find_bridges(E,28)
    actual=all_physical_colours(E,roots)
    assert len(actual)==72 and sum(actual.values())==144
    expected=frozenset(
        s for s in parity
        if s[2]!=s[3]
        and len({s[0],s[2],s[5]})<=2
        and len({s[0],s[3],s[5]})<=2
    )
    assert set(actual)==expected and len(expected)==72
    assert Counter(truth(s) for s in actual)==Counter({
        "100":36,"010":36
    })
    print("REAL_N28_144_FULL_COLOURS_MATCH_EXACT_2_TRIPLES_PLUS_PAIR_SYNC",{
        "state_count":len(expected),"physical_bridges":0,
        "threebody_nonrainbow_constraints":((0,2,5),(0,3,5)),
        "twoport_phase_not_equal":(2,3),
        "third_bit_001":0,
    })


def quantitative_K4minus_wiring_gate():
    records=bitset_support()
    target_masks={
        b:sum(1<<i for i in range(729)
              if truth(tuple_from_code(i))==b and
              parity_legal(tuple_from_code(i)))
        for b in GOOD
    }
    good_mask=0
    for subset in target_masks.values():
        assert subset.bit_count()==36
        good_mask |= subset
    assert good_mask.bit_count()==108
    for B in (5,8,9,10):
        rel=all_physical_relation_from_classes(records,(4,B,3,3))
        counts=histogram_for_relation(rel)
        expected={
            5:Counter({"100":36,"010":36}),
            8:Counter({"100":36,"010":36,"001":18,"111":9}),
            9:Counter({"100":36,"010":36,"001":18,"111":18}),
            10:Counter({"100":36,"010":36,"001":18,"111":27}),
        }[B]
        assert counts==expected,(B,counts,expected)
        print("SYNCHRONOUS_B_FOURPOLE_PHASE_UNLOCK",{
            "B_class":B,
            "physical_external_tuple_histogram":dict(counts),
            "full_third_bit_reached":False,
            "forbidden_states":sum(v for bit,v in counts.items()
                                   if bit not in GOOD),
        },flush=True)

    minimum=729
    winners=[]
    covered=0
    for selected in product(range(11),repeat=4):
        relation=all_physical_relation_from_classes(records,selected)
        if (relation&good_mask)!=good_mask:
            continue
        covered+=1
        forbidden=(relation^good_mask).bit_count()
        if forbidden<minimum:
            minimum=forbidden
            winners=[selected]
        elif forbidden==minimum:
            winners.append(selected)
    assert minimum==42 and sorted(winners)==[
        (4,10,6,7),(4,10,7,6)
    ],(minimum,winners)
    for selected in winners:
        relation=all_physical_relation_from_classes(records,selected)
        assert histogram_for_relation(relation)==Counter({
            "100":36,"010":36,"001":36,"000":24,"111":18
        })
    print("ALL_11_POWER4_FIXED_K4minus_PHASE_LOCK_TRADEOFF",{
        "fourpole_class_assignments_total":11**4,
        "assignments_saturating_all_108_good":covered,
        "minimum_forbidden_if_all_108_present":minimum,
        "minimizing_class_sequences":winners,
        "minimal_physical_state_count":150,
    },flush=True)


if __name__=="__main__":
    parity,target=verify_flow_phase_theorem()
    verify_n28_two_bit_boundary_physics(parity)
    quantitative_K4minus_wiring_gate()
    print("SYNCHRONOUS_PHYSICS_ROLE=HEURISTIC_DISCOVERY_OF_EXACT_BOUNDARY_INVARIANTS")
    print("NO_NEW_PHYSICAL_LAW; NO_POLY_GENERAL_SCL_SOLVER")
    print("FULL_108_THREEBIT_PHYSICAL_GADGET_OPEN; P_VS_NP_OPEN")
