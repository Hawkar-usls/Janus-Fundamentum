#!/usr/bin/env python3
"""R5 exact no-GOOD-threebit for ALL 7-block 2edge-connected
LOOPLESS multigraphs with NO degree-two constituent fourpole.

This is the previously open special 54,810-labelled-graph class:
7 colourable cubic fourpoles joined by 11 distinct physical connector
edges, with parallel edges allowed. No self-loops on block skeleton.
Every block has degree 3 or 4, so necessarily the degree multiset
(4,3,3,3,3,3,3), one degree4 hub and six single-port degree3 blocks.
The block skeleton has exactly edge-connectivity TWO.

Independently enumerate all labelled (hub fixed at vertex0) degree
realizations: total=13440, disconnected=1140, edgecut1=2400,
edgecut2=7830, edgecut3=2070. Exactly 19 isomorphism types in edgecut2,
ALL using parallel edges, with 6! terminal relabel permutations.
Orbit sizes sum=7830; multiplying by 7 possible positions of the
unique hub covers exactly 54,810 labelled edgecut2 skeletons with no
two-outer-port block.

For each of 19 cases compute EXACT full local 729-bit external-colour
support for every seven-fourpole S3 local orbit vector by enumerating
all 3**11 connector colourings. Check all 15 logical pairings, up to
ACTUAL skeleton automorphisms (199 checks representing all 285).
Apply mathematically COMPLETE monotone 3-GOOD-witness + singleton
class extension test. Every case is UNSAT.

19 cases, 199 pairing-orbit checks, 82606770 three-good-witness
triples, 49606866 minimally completed physical class masks,
ZERO full GOOD-only threebit signatures.

Thus ALL 2edgeconnected 7-fourpole 11-join loopless skeletons having
zero degree-two blocks are excluded for arbitrary internal constituent
sizes. Still OPEN: 2edgeconnected skeletons WITH degree-two blocks,
and 1edgeconnected 1+5 transfer inflations; global physical ExactOne
and polynomial SolveLinearCubicXSAT remain OPEN, P vs NP OPEN.
"""
from collections import Counter
from itertools import permutations

from r5_exactone_seven_fourpole_synchronous_hub_frontier import (
    phase_hub_records
)
from r5_exactone_seven_fourpole_synchronous_hub_exact_three_witness import (
    true_pairing_orbits, complete_three_witness_search, positive_control
)

EXPECTED=(
 (360,11, 993,12069,27982,4361170,460722,4410090),
 (360,11, 841,12459, 5840, 610116, 64720,1259856),
 (180, 7,1078,11685,24331,4263080,270955,2591739),
 (720,15,1023,11529,37239,5985574,521252,4362516),
 (720,15, 903,11889,10728,1345984,122624,2034432),
 (360, 9,1122,11151,33402,6178724,308276,2664624),
 (720,15,1114,11277,43072,7808041,381645,4229709),
 (360, 9,1062,11337,20189,3452028,153721,1677129),
 (360, 9,1130,11217,27619,5220620,281166,2840274),
 (720,15,1124,11217,39411,7397089,363460,4278324),
 (720,15, 983,11649,21248,3147406,244456,2706072),
 (360, 9,1029,11589,15552,2514262,217648,2342784),
 (180, 7, 950,11637,14726,2237373,268242,1762350),
 (180, 7, 870,11937, 4000, 460410, 48640, 727056),
 ( 90, 5,1052,11199,14342,2463664,145372,1077228),
 (360,11,1147,10941,38749,7393665,252424,2754822),
 (360, 9,1199,10851,36708,7519421,266262,3034896),
 (360, 9,1162,10887,31779,6203178,235013,2511033),
 (360,11,1053,11289,24075,4044965,217624,2341932),
)

TERMINAL_PERMS=tuple(permutations(range(1,7)))


def minimum_edge_cut(edges):
    best=11
    for mask in range(1,1<<6):
        cut=sum(((mask>>u)&1)!=((mask>>v)&1) for u,v in edges)
        best=min(best,cut)
        if best==0:return 0
    return best


def canonical_hub(edges):
    best=None
    for tail in TERMINAL_PERMS:
        ren=(0,)+tail
        transformed=tuple(sorted(
            (min(ren[u],ren[v]),max(ren[u],ren[v]))
            for u,v in edges))
        if best is None or transformed<best:best=transformed
    return best


def independent_hub_twoedge_census():
    remaining=[4]+[3]*6
    counts=Counter()
    classes=Counter()
    def extend(u,edges):
        if u==7:
            if any(remaining):return
            kind=minimum_edge_cut(edges)
            counts[kind]+=1
            if kind==2:
                classes[canonical_hub(edges)]+=1
            return
        if remaining[u]==0:
            extend(u+1,edges)
            return
        later=tuple(v for v in range(u+1,7) if remaining[v])
        required=remaining[u]
        def allocate(k,left,added):
            if k==len(later):
                if left==0:
                    old=remaining[u];remaining[u]=0
                    extend(u+1,edges+added)
                    remaining[u]=old
                return
            v=later[k]
            allocate(k+1,left,added)
            for m in range(1,min(left,remaining[v])+1):
                remaining[v]-=m
                allocate(k+1,left-m,added+((u,v),)*m)
                remaining[v]+=m
        allocate(0,required,())
    extend(0,())
    assert counts==Counter({0:1140,1:2400,2:7830,3:2070}),counts
    assert len(classes)==19
    assert sum(classes.values())==7830
    assert all(len(set(E))<11 for E in classes) # all 19 have parallel joins
    assert tuple(sorted(classes.values()))==tuple(sorted(
        r[0] for r in EXPECTED))
    print("SEVENBLOCK_MULTIGRAPH_EDGE2_NO_DEG2_COMPLETE_CENSUS",{
        "hub_fixed_degree_realizations":sum(counts.values()),
        "hub_fixed_twoedge_labelled":counts[2],
        "all_hub_positions_labelled":7*counts[2],
        "exact_nonisomorphic_twoedge_types":len(classes),
        "every_type_has_parallel_edges":True,
        "all_cut_classes":dict(counts)
    },flush=True)
    return tuple(sorted(classes.items()))


def run():
    positive_control()
    classes=independent_hub_twoedge_census()
    overall=Counter()
    for index,(E,orbit_size) in enumerate(classes):
        (
          nlabel, nmatch, nrecords, nwire, npairs,
          ntriples, nsurvivors, nextensions
        )=EXPECTED[index]
        assert orbit_size==nlabel,(index,orbit_size,nlabel)
        records,good_wires,ports=phase_hub_records(E)
        assert len(records)==nrecords and good_wires==nwire
        automorphisms,representatives=true_pairing_orbits(E,ports)
        assert len(representatives)==nmatch
        totals=Counter()
        for pairing,multiplicity in representatives:
            stats,solution=complete_three_witness_search(
                records,pairing)
            if solution is not None:
                raise AssertionError(
                    "FULL_108_GOODONLY_SOLUTION_FOUND",
                    index,E,pairing,solution
                )
            totals.update(stats)
            totals["checks"]+=1
            totals["logical_pairings_covered"]+=multiplicity
        assert totals==Counter({
            "pairs":npairs, "triples":ntriples,
            "survivors":nsurvivors, "extensions":nextensions,
            "checks":nmatch, "logical_pairings_covered":15
        }),(index,totals)
        overall.update(totals)
        print("SEVENBLOCK_MULTI_EDGE2_NO_DEG2_UNSAT",{
            "class":index,"labelled_hub_fixed_orbit":orbit_size,
            "records":len(records),"wire_colourings":good_wires,
            "automorphisms":len(automorphisms),
            "pairing_orbits":nmatch,
            "all_15_labelled_pairings_covered":True,
            "exact_complete_checks":dict(totals),
            "GOODONLY_ALL_THREE_BITS":0
        },flush=True)
    assert overall==Counter({
        "pairs":470992,"triples":82606770,
        "survivors":4824222,"extensions":49606866,
        "checks":199,"logical_pairings_covered":285
    }),overall
    print("ALL_SIZE_SEVENBLOCK_MULTIGRAPH_EDGE2_WITHOUT_DEG2_NO_GO",{
        "nonisomorphic_skeletons":19,
        "labelled_skeletons_hub_anywhere":54810,
        "distinct_pairing_orbits_checked":199,
        "fully_covered_pairings":285,
        "exact_GOOD_witness_triples_checked":82606770,
        "exact_minimal_legal_extensions_checked":49606866,
        "FULL_108_GOODONLY_CLASS_ASSIGNMENTS":0,
        "scope":"7 arbitrary size 4poles, 11 loopless joins, mincut2, min-degree3"
    },flush=True)
    print("TWO_EDGE_MULTIGRAPHS_WITH_DEGREE_TWO_BLOCKS_STILL_OPEN")
    print("P_VS_NP_OPEN; SolveLinearCubicXSAT_NOT_CONSTRUCTED")


if __name__=="__main__":
    run()
