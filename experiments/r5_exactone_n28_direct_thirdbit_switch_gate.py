#!/usr/bin/env python3
"""R5: all 1224 simple one-step 2-edge switches of REAL BRIDGELESS n28.

Starting from the fully certified n28 72-state GOOD-only 100/010
sixpole, exchange endpoints of two vertex-disjoint ordinary edges,
retaining simplicity and degree promises.

Exactly 1224 DISTINCT labelled graphs arise; 1221 are connected.
Connected outcomes:
 - 1144 BRIDGELESS, forbidden physical colouring present;
 -   48 BRIDGED, forbidden physical colouring present;
 -   20 BRIDGELESS, GOOD-only with exact 100/010 (72 physical tuples);
 -    4 BRIDGED, GOOD-only with exact 100/010;
 -    5 BRIDGELESS, uncolourable (EMPTY relation).
There is ZERO direct one-switch legal full three-bit 108-state gadget.

The existence-of-forbidden search pins the FIRST selected internal
edge to colour 0, a sound global S3 symmetry reduction: any physical
forbidden equality-bit witness can be recoloured to satisfy that pin.
For each surviving GOOD-only case the complete non-pinned full physical
relation is independently replayed, with exactly 72 physical states.

FINITE local search only; multiple switches or graph enlargement could
produce a legal three-bit gadget. No all-n exclusion or P=NP result.
"""
from collections import Counter
from itertools import combinations, permutations
from r5_exactone_bridgeless_n28_twobit_constructive import (
    build_k4minus_two_bit, find_bridges,
    all_physical_colours, bits
)
from r5_exactone_n10_independent_degree_orbit_bridge_healing import (
    colouring_bits, connected
)

GOOD=frozenset(("100","010","001"))


def all_one_switches(edges):
    original=set(edges)
    result=set()
    for (a,b),(c,d) in combinations(edges,2):
        if len({a,b,c,d})!=4:
            continue
        for raw in (((a,c),(b,d)),((a,d),(b,c))):
            repl={tuple(sorted(x)) for x in raw}
            if len(repl)!=2 or repl&original:
                continue
            result.add(tuple(sorted(
                original-{(a,b),(c,d)}|repl)))
    return result


SIMPLE_FIVE_BLOCK_SKELETONS=(
    ((0,1),(0,2),(0,3),(0,4),(1,2),(1,3),(1,4)),
    ((0,1),(0,2),(0,3),(0,4),(1,2),(1,3),(2,3)),
    ((0,1),(0,2),(0,3),(0,4),(1,2),(1,3),(2,4)),
    ((0,1),(0,2),(0,3),(1,2),(1,3),(2,4),(3,4)),
)


def canonical_five_block_skeleton(edges):
    representatives=[]
    for ren in permutations(range(5)):
        representatives.append(tuple(sorted(
            tuple(sorted((ren[u],ren[v]))) for u,v in edges
        )))
    return min(representatives)


def independently_certify_four_simple_skeletons():
    all_edge_pairs=tuple(combinations(range(5),2))
    canonical=frozenset(
        canonical_five_block_skeleton(candidate)
        for candidate in combinations(all_edge_pairs,7)
        if connected(candidate,5)
    )
    asserted=frozenset(map(
        canonical_five_block_skeleton,
        SIMPLE_FIVE_BLOCK_SKELETONS
    ))
    assert len(canonical)==4 and canonical==asserted
    print("EXACT_FOUR_UNLABELLED_CONNECTED_SIMPLE_5BLOCK_7EDGE_SKELETONS PASS")


def test():
    independently_certify_four_simple_skeletons()
    edges,roots=build_k4minus_two_bit(True)
    assert len(edges)==39 and len(roots)==6
    assert not find_bridges(edges,28)
    neighbors=all_one_switches(edges)
    assert len(neighbors)==1224
    counts=Counter()
    for candidate in neighbors:
        if not connected(candidate,28):
            counts[("DISCONNECTED","n/a")]+=1
            continue
        has_bridge=bool(find_bridges(candidate,28))
        bstate=("BRIDGED" if has_bridge else "BRIDGELESS")
        hist, forbidden=colouring_bits(
            candidate,roots=roots,
            pairs=((0,5),(1,4),(2,3)),
            stop_at_forbidden=True
        )
        if forbidden:
            counts[(bstate,"HAS_FORBIDDEN")]+=1
        elif not hist:
            counts[(bstate,"UNCOLOURABLE")]+=1
        else:
            # One colour was pinned above; use SECOND full (unpinned)
            # enumerator for every surviving GOOD-only case.
            actual=all_physical_colours(candidate,roots)
            observed=Counter(bits(p) for p in actual)
            assert observed==Counter({"100":36,"010":36}),observed
            assert len(actual)==72
            assert not set(observed)-GOOD
            counts[(bstate,"EXACT_TWO_BITS_72")]+=1
    required=Counter({
        ("DISCONNECTED","n/a"):3,
        ("BRIDGELESS","HAS_FORBIDDEN"):1144,
        ("BRIDGED","HAS_FORBIDDEN"):48,
        ("BRIDGELESS","EXACT_TWO_BITS_72"):20,
        ("BRIDGED","EXACT_TWO_BITS_72"):4,
        ("BRIDGELESS","UNCOLOURABLE"):5,
    })
    assert counts==required,(counts,required)
    assert sum(counts.values())==1224
    print("ALL_1224_PHYSICAL_N28_ONE_EDGE_PAIR_SWITCHES",{
        "classification":dict(counts),
        "bridgeless_two_bit_survivors":20,
        "three_bit_108_goodonly":0,
        "proof_scope":"one double-edge endpoint switch of fixed n28",
    },flush=True)
    print("FULL_THREE_BIT_108_GADGET_STILL_OPEN; P_VS_NP_OPEN")


if __name__=="__main__":
    test()
