#!/usr/bin/env python3
"""R5: FULL 6-fourpole / 9-join LOOPLESS MULTIGRAPH no-108 theorem.

Theorem scope:
Six arbitrary connected properly 3-edge-colourable cubic FOURPOLES,
all 11 all-size ordered four-port signature classes, joined by NINE
ordinary edges BETWEEN DIFFERENT BLOCKS. The connected block skeleton
may have parallel edges, but no loops. Six exposed semiedges remain,
paired into 3 logical pairs in ANY of the 15 possible ways.

There are 217 nonisomorphic connected six-block / nine-edge loopless
multigraph skeletons with maximum degree at most 4:
  14 simple and 203 with parallel edges.
  122 have a bridge, 93 are 2-edge-connected but not 3-edge-connected,
  and 2 are 3-edge-connected.

Of the 122 bridges, 114 have a bridge partitioning the six exposed
semiedges 3+3, thereby excluding 2-or-3 good truth bits by the earlier
ALL-SIZE 11x11x15 bridge theorem. (3 of these are simple, 111 multi.)
The other 103 skeletons include 8 with a 1+5 bridge, 93 2-connected,
and 2 3-connected. Test their entire exact nonlinear colour grammar.
Within each block, the external semiedge permutations act by
permuting the 11 S3-symmetric 4port signature classes, so pairing
options need only be tested up to these local port permutations:
there are exactly 716 representative (skeleton, logical pairing)
cases among those 103 block skeletons (full coverage of all 15
logical matchings per skeleton, without losing any possibilities).

For each case an EXACT monotone three-witness check enumerates all
possible 3^9 connector colourings and the complete physical boundary
supports of their six local colour-orbit vectors. If no 2-orbit or
larger class mask avoids all forbidden tuples while retaining one
witness of EACH good bit 100,010,001, full Exact-One is impossible.
Every one of the 716 complete checks is negative.

Thus NONE of
    217 * 15 * 11**6 = 5,766,431,055
possible class/skeleton/pairing cases has an exact full 108-state
three-bit physical boundary signature. They are logically covered
by compression and symmetry; not enumerated one-by-one.

CRITICAL LIMIT: Only this SIX FOURPOLE / NINE JOIN loopless grammar.
A full 108-state 6pole might still exist as a nondecomposable core or
via >=7 blocks, loops absorbed into blocks, or other architectures.
This theorem is NOT an all-size global no-gadget result and gives
NO general polynomial SolveLinearCubicXSAT; P vs NP remains OPEN.

Requires (and CI also tests) earlier all-size fourpole 11-class atlas
and 3+3 bridge signature theorem.
"""
from collections import Counter
from itertools import combinations, combinations_with_replacement, permutations, product

from r5_exactone_six_fourpole_nineedge_simple_skeleton_gate import (
    canonical_skeleton, connected, all_logical_pairings,
    local_orbit_physical_records, physical_masks_by_pairing,
    prove_no_good_threebit_signature, skeleton_connectivity
)


def all_loopless_nine_join_skeletons():
    edge_types=tuple(combinations(range(6),2))
    candidates=set()
    labelled=0
    for indices in combinations_with_replacement(range(len(edge_types)),9):
        degree=[0]*6
        for k in indices:
            u,v=edge_types[k]
            degree[u]+=1
            degree[v]+=1
            if degree[u]>4 or degree[v]>4:
                break
        else:
            E=tuple(edge_types[k] for k in indices)
            if not connected(E):
                continue
            labelled+=1
            candidates.add(canonical_skeleton(E))
    skeletons=tuple(sorted(candidates))
    assert labelled==110170,labelled
    assert len(skeletons)==217,len(skeletons)
    assert sum(len(set(E))==9 for E in skeletons)==14
    assert Counter(skeleton_connectivity(E) for E in skeletons)==Counter({
        1:122,2:93,3:2
    })
    return skeletons


def bridge_external_splits(E):
    """All distinct physical-port splits induced by single-edge cuts."""
    ext=tuple(4-sum(v in e for e in E) for v in range(6))
    assert sum(ext)==6
    splits=[]
    for k in range(9):
        remaining=E[:k]+E[k+1:]
        # Discovery of one component of a possibly multigraph edge cut.
        seen={E[k][0]}
        stack=[E[k][0]]
        while stack:
            u=stack.pop()
            for a,b in remaining:
                if a==u and b not in seen:
                    seen.add(b);stack.append(b)
                if b==u and a not in seen:
                    seen.add(a);stack.append(a)
        if len(seen)<6:
            count=sum(ext[v] for v in seen)
            splits.append(tuple(sorted((count,6-count))))
    return tuple(sorted(set(splits)))


def exact_local_port_pairing_orbits(E, pairings):
    """Exhaustive quotient of all 15 pairings by SAME-block port swaps.

    Any permutation of exposed semiedges within a single block is
    equivalent to a permutation of that block's FULL ordered 4-port
    relation; its allowed 11 classes are closed under all such
    permutations. Therefore the property 'some 11-class assignment
    produces exact GOOD three-bit support' is invariant under these
    transformations, even though the individual class names change.
    """
    ext=tuple(4-sum(v in e for e in E) for v in range(6))
    groups=[]
    first=0
    for num in ext:
        groups.append(tuple(range(first,first+num)))
        first+=num
    assert first==6
    actions=[]
    for orders in product(*(permutations(g) for g in groups)):
        mapping={}
        for original,perm in zip(groups,orders):
            mapping.update(zip(original,perm))
        actions.append(mapping)
    assert actions
    seen=set()
    reps=[]
    for p in pairings:
        canonical=tuple(sorted(tuple(sorted(pair)) for pair in p))
        if canonical in seen:
            continue
        orbit=set()
        for mapping in actions:
            translated=tuple(sorted(tuple(sorted(
                (mapping[a],mapping[b]))) for a,b in p))
            orbit.add(translated)
        assert not seen & orbit
        seen |= orbit
        reps.append(p)
    assert len(seen)==15,(len(seen),E)
    return tuple(reps)


def test():
    skeletons=all_loopless_nine_join_skeletons()
    pairings=tuple(all_logical_pairings(range(6)))
    assert len(pairings)==15
    physical_masks={p:physical_masks_by_pairing(p) for p in pairings}
    bridge33=0
    exact_cases=0
    witness_triples=0
    categories=Counter()
    representants=Counter()
    for i,E in enumerate(skeletons):
        splits=bridge_external_splits(E)
        if (3,3) in splits:
            # All-n proven result: no colourable 3+3-bridged
            # cubic sixpole can have >=2 GOOD bits. Applies
            # even if a side consists of several original 4poles.
            bridge33+=1
            categories["bridge_3plus3_pruned"]+=1
            continue
        records,assignments=local_orbit_physical_records(E)
        pairing_reps=exact_local_port_pairing_orbits(E,pairings)
        representants[skeleton_connectivity(E)]+=len(pairing_reps)
        for pairing in pairing_reps:
            # Every physical sixport support obtained by arbitrary
            # allowed 11-class block signatures is included exactly.
            witness_triples+=prove_no_good_threebit_signature(
                records,physical_masks[pairing])
            exact_cases+=1
        conn=skeleton_connectivity(E)
        categories[f"exact_edgeconn_{conn}"]+=1
        if i%25==0:
            print("MULTI6_PROGRESS",{
                "skeleton_id":i,
                "edge_connectivity":conn,
                "pairing_orbit_representatives":len(pairing_reps),
                "cumulative_cases":exact_cases
            },flush=True)
    assert bridge33==114,bridge33
    assert exact_cases==716,exact_cases
    assert categories==Counter({
        "bridge_3plus3_pruned":114,
        "exact_edgeconn_1":8,
        "exact_edgeconn_2":93,
        "exact_edgeconn_3":2
    }),categories
    assert representants[1]+representants[2]+representants[3]==716
    assert witness_triples>1_000_000
    possible=217*15*(11**6)
    assert possible==5766431055
    print("ALL_SIZE_6_FOURPOLE_MULTIGRAPH_GRAMMAR_EXACTONE_NO_GO",{
        "simple_and_parallel_edge_skeletons":217,
        "simple_skeletons":14,
        "multiple_edge_skeletons":203,
        "naive_signature_pairing_combinations":possible,
        "bridge_3plus3_universally_pruned":bridge33,
        "remaining_skeletons_exactly_verified":103,
        "complete_logical_pair_orbits_tested":exact_cases,
        "tested_safe_good_orbit_witness_triples":witness_triples,
        "GOODONLY_FULL_100_010_001_RELATION":0
    },flush=True)
    print("GENERAL_ALL_CUBIC_SIXPOLE_108_GOOD_ONLY_EXISTS_OR_NOT=OPEN")
    print("SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    test()
