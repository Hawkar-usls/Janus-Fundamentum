#!/usr/bin/env python3
"""Exact all-size NO-GO for 3-edge-connected 7-fourpole MULTIGRAPH hubs.

THEOREM (specified grammar only):
For seven arbitrarily large, independently colourable connected
cubic FOURPOLES, joined by 11 ordinary inter-block edges according
to a LOOPLESS 3-edge-connected 7-vertex MULTIGRAPH, the complete
six-port three-edge-colouring relation CANNOT simultaneously contain
all three GOOD equality bits 100/010/001 and exclude forbidden 000/111.

WHY COMPLETE: 3-edge-connectivity requires all 7 block degrees >=3.
Their degree sum=22, so one has degree 4 and six have degree 3. Fix
the unique degree-4 hub at vertex 0. Independently enumerate ALL
simple+multiple-edge labelled multigraphs with degree vector
(4,3,3,3,3,3,3), forbidding self-loops. EXACT census:
   all degree-realizations: 13440
   connected:              12300
   minimum edge-cut 1:      2400
   minimum edge-cut 2:      7830
   minimum edge-cut 3:      2070.
Canonically classify the 2070 3-edge-connected graphs under the
6! permutations of the nonhub vertices. Exactly 7 isomorphism
classes; FOUR simple already proved UNSAT, THREE new with 1 pair of
parallel edges:
   new class 0: 360 labelled hub-fixed graphs
   new class 1: 720 labelled hub-fixed graphs
   new class 2: 180 labelled hub-fixed graphs.
The four simple orbits have 360,90,180,180 labelled members.

For EACH NEW class, enumerate all 3**11 actual connector colourings
and collect the exact 729-bit physical external boundary support per
seven-vector of Klein-four legal local fourpole orbit IDs. Then
compute the ACTUAL automorphism orbits of all 15 external logical
pairings. Exhaust complete monotone three-GOOD-witness SAT
certificates, with all singleton-orbit extensions to one of eleven
legal connected fourpole signatures, and test every resulting class
selection for a forbidden boundary colouring.

New skeleton0: 9 pairing orbits, 9897799 witness triples,
  4308735 extensions, ZERO full GOOD-only triples;
new skeleton1: 15 pairing orbits, 17394573 witness triples,
  7356171 extensions, ZERO;
new skeleton2: 6 pairing orbits, 8703917 witness triples,
  3004170 extensions, ZERO.

The previously independently proven four SIMPLE 3-edge-connected
sevenblock skeletons also have zero viable GOOD-only threebit
composition. This file adds the exactly THREE missed parallel-link
skeletons. Together the 7 iso classes COMPLETE the 3-edge-connected
7-fourpole 11join LOOPLESS MULTIGRAPH grammar.

Proof is all-size ONLY within the seven-fourpole 11join specified
grammar. Low edge-connectivity (1/2), >=8 blocks, internal self-joins
or arbitrary indecomposable sixpoles are NOT excluded. P vs NP OPEN,
universal polynomial native SolveLinearCubicXSAT NOT CONSTRUCTED.

Requires previous exact seven-simple phase_hub_records, true pairing
automorphism orbits, and monotone three-witness verifier.
"""
from collections import Counter
from itertools import combinations, permutations

from r5_exactone_seven_fourpole_synchronous_hub_frontier import (
    SKELETONS, phase_hub_records
)
from r5_exactone_seven_fourpole_synchronous_hub_exact_three_witness import (
    true_pairing_orbits, complete_three_witness_search
)

PARALLEL_SKELETONS=(
    ((0,1),(0,1),(0,2),(0,3),(1,4),(2,3),(2,5),
     (3,6),(4,5),(4,6),(5,6)),
    ((0,1),(0,1),(0,2),(0,3),(1,4),(2,4),(2,5),
     (3,5),(3,6),(4,6),(5,6)),
    ((0,1),(0,1),(0,2),(0,3),(1,4),(2,5),(2,6),
     (3,5),(3,6),(4,5),(4,6)),
)
EXPECTED=(
    (360,9,1266,10857,44695,9897799,359293,4308735),
    (720,15,1288,10791,76140,17394573,606009,7356171),
    (180,6,1351,10731,36223,8703917,252174,3004170),
)


def edge_connectivity(E):
    minimum=11
    for subset in range(1, 1<<6):
        cut=sum(((subset>>u)&1)!=((subset>>v)&1)
                for u,v in E)
        minimum=min(minimum,cut)
    return minimum


def valid_cubic_hub(E):
    deg=Counter(v for a,b in E for v in (a,b))
    return (len(E)==11 and
            all(a<b for a,b in E) and
            tuple(deg[i] for i in range(7))==(4,3,3,3,3,3,3))


def canonical_hub_label(E):
    best=None
    for p in permutations(range(1,7)):
        ren=(0,)+p
        image=tuple(sorted(
            (min(ren[a],ren[b]),max(ren[a],ren[b]))
            for a,b in E
        ))
        if best is None or image<best:best=image
    return best


def generate_all_degree_hub_graphs():
    """Each undirected loopless multigraph EXACTLY once."""
    remaining=[4,3,3,3,3,3,3]
    totals=Counter()
    canonical=Counter()
    def visit(u,sofar):
        if u==7:
            if not any(remaining):
                totals["degree"]+=1
                E=tuple(sorted(sofar))
                # For loopless seven-block degree>=3 all cut tests
                # can be done over unordered nontrivial vertex sets.
                minimum=edge_connectivity(E)
                if minimum>=1:totals["connected"]+=1
                totals[f"cut_{minimum}"]+=1
                if minimum>=3:
                    canonical[canonical_hub_label(E)]+=1
            return
        if not remaining[u]:
            visit(u+1,sofar)
            return
        choices=tuple(v for v in range(u+1,7) if remaining[v])
        needed=remaining[u]
        def allocate(i,left,added):
            if i==len(choices):
                if left==0:
                    old=remaining[u]
                    remaining[u]=0
                    visit(u+1,sofar+added)
                    remaining[u]=old
                return
            v=choices[i]
            allocate(i+1,left,added)
            for count in range(1,min(left,remaining[v])+1):
                remaining[v]-=count
                allocate(i+1,left-count,added+((u,v),)*count)
                remaining[v]+=count
        allocate(0,needed,())
    visit(0,())
    assert totals==Counter({
        "degree":13440,"connected":12300,
        "cut_0":1140,"cut_1":2400,"cut_2":7830,"cut_3":2070
    }),totals
    assert len(canonical)==7
    assert sum(canonical.values())==2070
    parallel=tuple(sorted(
        (E,k) for E,k in canonical.items() if len(set(E))<11
    ))
    assert len(parallel)==3
    assert tuple(E for E,k in parallel)==PARALLEL_SKELETONS
    assert tuple(k for E,k in parallel)==(360,720,180)
    assert Counter(k for E,k in canonical.items() if len(set(E))==11)==Counter({
        360:1,90:1,180:2
    })
    assert all(valid_cubic_hub(E) and edge_connectivity(E)==3
               for E in PARALLEL_SKELETONS)
    print("ALL_SEVENBLOCK_3EDGE_CONNECTED_LOOPLESS_MULTIGRAPH_ISO_CLASSES",{
        "hub_fixed_degree_realizations":13440,
        "connected":12300,
        "hub_fixed_edgeconn3_labelled":2070,
        "isomorphism_classes":7,
        "simple_classes_previous":4,
        "parallel_classes_new":3,
        "parallel_orbit_sizes":(360,720,180),
    },flush=True)


def run():
    generate_all_degree_hub_graphs()
    expected_total=Counter()
    for index,E in enumerate(PARALLEL_SKELETONS):
        (
            labelled,pairing_orbits,expected_records,expected_wires,
            pairs,triples,survivors,extensions
        )=EXPECTED[index]
        records,valid_wires,port_vertices=phase_hub_records(E)
        assert len(records)==expected_records
        assert valid_wires==expected_wires
        automorphisms,orbits=true_pairing_orbits(E,port_vertices)
        assert len(orbits)==pairing_orbits
        stats=Counter()
        for logical_pairs,multiplicity in orbits:
            counts,solution=complete_three_witness_search(
                records,logical_pairs)
            if solution is not None:
                raise AssertionError(
                    "LEGAL_FULL_GOOD_108_BOUNDARY_RELATION_FOUND",
                    index,logical_pairs,solution
                )
            stats.update(counts)
            stats["pairing_orbits"]+=1
            stats["physical_logical_pairings"]+=multiplicity
            print("SEVENBLOCK_MULTI_3EDGE_PAIRING_UNSAT",{
                "new_parallel_skeleton":index,
                "logical_pairing":logical_pairs,
                "automorphism_multiplicity":multiplicity,
                "witness_counts":counts,
            },flush=True)
        assert stats==Counter({
            "pairs":pairs,"triples":triples,
            "survivors":survivors,"extensions":extensions,
            "pairing_orbits":pairing_orbits,
            "physical_logical_pairings":15,
        }),(index,stats)
        expected_total.update(stats)
        print("SEVENBLOCK_MULTI_3EDGE_SKELETON_UNSAT",{
            "skeleton":index,
            "ordinary_join_edges":E,
            "true_automorphisms":len(automorphisms),
            "orbit_patterns":len(records),
            "proper_wire_colourings":valid_wires,
            "complete_pairing_orbits":pairing_orbits,
            "full_threebit_GOOD_only":0,
            "exact_counts":dict(stats),
        },flush=True)
    assert expected_total==Counter({
        "pairs":157058,
        "triples":35996289,
        "survivors":1217476,
        "extensions":14669076,
        "pairing_orbits":30,
        "physical_logical_pairings":45,
    }),expected_total
    print("ALL_SIZE_SEVEN_FOURPOLE_3EDGE_LOOPLESS_MULTIGRAPH_UNSAT",{
        "all_iso_skeletons":7,
        "prior_simple_iso_skeletons":4,
        "new_parallel_iso_skeletons":3,
        "all_15_logical_pairings_per_new_skeleton":True,
        "new_exact_three_witness_tests":35996289,
        "new_minimal_extensions":14669076,
        "full_108_GOOD_only_class_assignments":0,
    },flush=True)
    print("SEVENBLOCK_1_AND_2_EDGE_CONNECTED_MULTIGRAPH_GRAMMAR_OPEN")
    print("GENERAL_CUBIC_SIXPOLE_EXACTONE_OPEN; P_VS_NP_OPEN")


if __name__=="__main__":
    run()
