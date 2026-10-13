#!/usr/bin/env python3
"""R5: all-size GOOD-only bridge grammar + physical 10-vertex TWO-BIT witness.

THEOREM I. If a colourable connected cubic 6-pole with six distinct
labelled semiedge roots has an ordinary BRIDGE splitting outer ports
3+3, and if its full Boolean pair-equality relation is contained in
GOOD={100,010,001}, it supports EXACTLY ONE bit (not two/three).
Each bridge-side is a properly colourable connected cubic 4-pole.
An all-size Kempe/parity lemma classifies each of their S3-invariant
four-port state relations among exactly 11 sets (2,3,4 orbits
from {AAAA,AABB,ABAB,ABBA}). The two sides' exact relation is their
colour-equality JOIN on the bridge semiedge.

Exhaust ALL 11*11*15 =1815 legal signature-class/matching choices.
GOOD-only outcomes: 6 with only 100, 3 with only 010, 9 with only
001, none with two or all three bits; all 18 outcomes have exactly 36
physical boundary tuples. These facts hold for arbitrary internal size
as the eleven-class enumeration is a proved ALL-SIZE signature atlas.

THEOREM II. If bridge splits port counts 2+4 and entire bit relation
is GOOD-only, its two-port side is a colourable cubic 3-pole, whose
three exposed colours (2 external + the bridge) must ALL differ by
the parity lemma. Therefore its two outer physical colours NEVER
match. By 36-state saturation in EACH realised GOOD bit, a pair of
ports from DIFFERENT logical pairs would be forced equal somewhere.
Thus the two side ports must comprise ONE of the three logical pairs;
that bit is always zero and at most the OTHER TWO bits can be present.

SHARPNESS: This new explicit connected simple cubic 10-vertex 6-pole
with 6 DISTINCT roots achieves exactly both 100 AND 010, all physical
36 states per bit, no 001/000/111, with exactly ONE full internal
3-colouring extending each of its 72 physical boundary tuples.
Physical port roots (0,1,2,4,7,8). Ordered logical pairs of port
INDICES (0,2),(1,3),(4,5).

Its 7-vertex, 5-semiedge side is a physically proper 5-pole with
exactly 36 distinct states and six S3 orbit types; the 3-vertex other
side is a triangle 3-pole (three distinct port roots) and one connecting
ordinary bridge runs between vertices 3 and 9.

Critical limits: This is a TWO-BIT gadget, NOT the full 108-state
three-bit Exact-One gadget. Theorem I does not apply to 2+4 bridges.
Neither theorem provides a general SCL solver or P=NP.
"""
from collections import Counter, defaultdict
from itertools import combinations, permutations, product

GOOD=frozenset(("100","010","001"))
PHYSICAL_COLOURS=range(3)
FOUR_ORBITS=((0,0,0,0),(0,0,1,1),(0,1,0,1),(0,1,1,0))

FIVE_EDGES=(
    (0,1),(0,6),(1,5),(2,4),(2,5),(3,5),(3,6),(4,6),
)
# Five-outer-port fragment has external semiedges at roots 0,1,2,3,4.
# The physical 3-pole triangle has roots 7,8,9 and all 3 distinct.
TEN_EDGES=tuple(sorted(FIVE_EDGES+(
    (7,8),(7,9),(8,9),(3,9)
)))
TEN_ROOTS=(0,1,2,4,7,8)
TEN_LOGICAL_PAIRING=((0,2),(1,3),(4,5))


def port_bits(physical,pairing):
    return "".join(str(int(physical[a]==physical[b])) for a,b in pairing)


def perfect_matchings(indices):
    indices=tuple(indices)
    if not indices:
        yield ()
    else:
        i=indices[0]
        for j in range(1,len(indices)):
            for rest in perfect_matchings(indices[1:j]+indices[j+1:]):
                yield ((i,indices[j]),)+rest


def expand_fourpole_class(classes):
    """Full REAL four-semiedge state support under global S3 colours."""
    return frozenset(
        tuple(ren[c] for c in representative)
        for representative in classes
        for ren in permutations(PHYSICAL_COLOURS)
    )


def all_size_three_plus_three_gate():
    catalogue=tuple(expand_fourpole_class(s)
                    for k in (2,3,4)
                    for s in combinations(FOUR_ORBITS,k))
    assert len(catalogue)==11 and len(set(catalogue))==11
    pairing_list=tuple(perfect_matchings(range(6)))
    assert len(pairing_list)==15
    good_counts=Counter()
    other_counts=Counter()
    cases=0
    for A in catalogue:
        for B in catalogue:
            # A[3], B[3] identify the SINGLE bridge port, with the
            # remaining 3 outer ports per side ordered A[:3], B[:3].
            relation=frozenset(a[:3]+b[:3]
                for a in A for b in B if a[3]==b[3])
            assert relation
            for pairing in pairing_list:
                cases+=1
                histogram=Counter(port_bits(s,pairing) for s in relation)
                observed=frozenset(histogram)
                if observed<=GOOD:
                    assert len(observed)==1,(observed,pairing)
                    assert len(relation)==36
                    assert set(histogram.values())=={36}
                    good_counts[tuple(sorted(observed))]+=1
                else:
                    other_counts[tuple(sorted(observed))]+=1
    assert cases==11*11*15==1815
    assert good_counts==Counter({
        ("100",):6,("010",):3,("001",):9
    }),good_counts
    assert sum(good_counts.values())==18
    assert sum(other_counts.values())==1797
    print("ALL_N_3PLUS3_BRIDGE_11x11x15",{
        "catalogue":11,"pairings":15,"cases":1815,
        "good_single_bit":dict(good_counts),
        "good_two_bits":0,"good_three_bits":0,
        "all_good_relations_have_36_port_tuples":True
    },flush=True)


def direct_full_colourings(edges,roots):
    """Independent proper 3-edge-colouring DFS, NO boundary fixed."""
    vertices={v for e in edges for v in e}
    n=max(vertices)+1
    assert vertices==set(range(n))
    assert len(set(edges))==len(edges)
    deg=Counter(v for e in edges for v in e)
    assert len(roots)==len(set(roots))
    assert all(deg[v]+(v in roots)==3 for v in range(n))
    # Underlying ordinary-edge graph connected.
    adj=[[] for _ in range(n)]
    for u,v in edges:adj[u].append(v);adj[v].append(u)
    seen={0}; stack=[0]
    while stack:
        for v in adj[stack.pop()]:
            if v not in seen:
                seen.add(v);stack.append(v)
    assert len(seen)==n

    # A separate full-edge-colouring DFS with bitmask incidence.
    used=[0]*n
    current=[-1]*len(edges)
    out=defaultdict(list)
    def visit(k=0):
        if k==len(edges):
            p=tuple({1:0,2:1,4:2}[7^used[v]] for v in roots)
            out[p].append(tuple(current))
            return
        u,v=edges[k]
        available=7&~(used[u]|used[v])
        while available:
            c=available&-available
            available^=c
            current[k]={1:0,2:1,4:2}[c]
            used[u]^=c;used[v]^=c
            visit(k+1)
            used[u]^=c;used[v]^=c
        current[k]=-1
    visit()
    return out


def canonical_fivepole_orbit(state):
    ren={}
    return tuple(ren.setdefault(c,len(ren)) for c in state)


def real_two_bit_ten_vertex_gate():
    five=direct_full_colourings(FIVE_EDGES,tuple(range(5)))
    assert len(five)==36
    assert sum(map(len,five.values()))==36
    five_orbits=Counter(canonical_fivepole_orbit(s) for s in five)
    assert len(five_orbits)==6
    assert set(five_orbits.values())=={6}
    rel=direct_full_colourings(TEN_EDGES,TEN_ROOTS)
    actual=Counter(port_bits(s,TEN_LOGICAL_PAIRING) for s in rel)
    assert len(rel)==72,(len(rel),actual)
    assert actual==Counter({"100":36,"010":36}),actual
    assert all(len(completions)==1 for completions in rel.values())
    assert sum(map(len,rel.values()))==72
    # Verify independently by exact gluing of a real 5-pole to
    # the fully colourable triangle: its three semiedge colours
    # are all different, with the joint one at old port 3.
    composed=frozenset(
        tuple(z[k] for k in (0,1,2,4))+(a,b)
        for z in five for a,b in permutations(PHYSICAL_COLOURS,2)
        if {a,b,z[3]}=={0,1,2}
    )
    assert frozenset(rel)==composed
    assert all(len(set(z))==3 for z in five)
    print("ACTUAL_CONNECTED_CUBIC_N10_TWO_BIT_GADGET",{
        "edges":TEN_EDGES,
        "ordered_port_roots":TEN_ROOTS,
        "logical_port_index_pairs":TEN_LOGICAL_PAIRING,
        "n":10,"m":12,
        "fivepole_states":len(five),
        "fivepole_orbit_classes":dict(five_orbits),
        "physical_sixpole_states":len(rel),
        "full_internal_colourings":sum(map(len,rel.values())),
        "bit_histogram":dict(actual),
        "all_fibre_multiplicities_equal_one":True,
        "triangle_three_pole_grafting_verified":True,
    },flush=True)


def all_size_three_fourpole_cycle_gate():
    """Exhaust cyclic A-B-C assembly, 2 exposed + 2 interface ports per 4pole.

    Interface pattern:
      A[2]=B[3], B[2]=C[3], C[2]=A[3].
    The six external ports are A[:2]+B[:2]+C[:2], paired by ANY
    of the 15 perfect matchings. This describes the FULL semantic
    colour relation of arbitrarily large real four-pole components.

    The construction is a bridgeless TRIANGLE at the component level,
    unlike a single-edge block bridge; it is NOT all bridgeless graphs.
    """
    catalogue=tuple(expand_fourpole_class(s)
                    for k in (2,3,4)
                    for s in combinations(FOUR_ORBITS,k))
    assert len(catalogue)==11
    lookup=[]
    for signature in catalogue:
        d=defaultdict(set)
        for s in signature:
            d[(s[2],s[3])].add(s[:2])
        lookup.append(d)
    pairings=tuple(perfect_matchings(range(6)))
    assert len(pairings)==15
    all_cases=0
    empty_cases=0
    good_counts=Counter()
    for i,j,k in product(range(11),repeat=3):
        external=set()
        for ab,bc,ca in product(PHYSICAL_COLOURS,repeat=3):
            A=lookup[i].get((ab,ca),())
            B=lookup[j].get((bc,ab),())
            C=lookup[k].get((ca,bc),())
            for a,b,c in product(A,B,C):
                external.add(a+b+c)
        if not external:
            empty_cases+=15
            all_cases+=15
            continue
        for pairing in pairings:
            all_cases+=1
            observed=frozenset(
                port_bits(state,pairing) for state in external
            )
            if observed<=GOOD:
                assert len(observed)==1,(i,j,k,pairing,observed)
                assert len(external)==36
                good_counts[tuple(sorted(observed))]+=1
    assert all_cases==11**3*15==19965
    assert empty_cases==45
    assert good_counts==Counter({
        ("100",):39,("010",):33,("001",):45
    }),good_counts
    assert sum(good_counts.values())==117
    print("ALL_N_THREE_FOURPOLE_CYCLIC_TRIANGLE_GATE",{
        "compositions":19965,"empty_compositions":45,
        "goodonly_one_bit":dict(good_counts),
        "goodonly_two_bits":0,"goodonly_three_bits":0,
        "all_goodonly_physical_tuple_count":36,
        "claim_scope":"triangle of THREE genuine 4pole blocks",
    },flush=True)


def bridge_cut_parity_taxonomy():
    # Saturated full GOOD bits have 36 parity-legal physical tuples
    # each, and a proper 2-outside+1-bridge cubic 3-pole must have
    # its 3 port colours mutually distinct.
    states=tuple(s for s in product(PHYSICAL_COLOURS,repeat=6)
      if all(s.count(c)%2==0 for c in PHYSICAL_COLOURS)
      and port_bits(s,((0,1),(2,3),(4,5))) in GOOD)
    assert len(states)==108
    by_bit=defaultdict(list)
    for s in states:
        by_bit[port_bits(s,((0,1),(2,3),(4,5)))].append(s)
    assert all(len(by_bit[b])==36 for b in GOOD)
    for i,j in combinations(range(6),2):
        viable={b for b,group in by_bit.items()
                if all(s[i]!=s[j] for s in group)}
        is_logical=any({i,j}=={a,b}
                       for a,b in ((0,1),(2,3),(4,5)))
        assert (len(viable)==2) if is_logical else (len(viable)==0)
        if is_logical:
            equality_bit=next(k for k,pp in enumerate(((0,1),(2,3),(4,5)))
                              if {i,j}==set(pp))
            assert viable==GOOD-{("100","010","001")[equality_bit]}
    print("ALL_N_2PLUS4_BRIDGE_PAIR_MUST_BE_LOGICAL_PAIR; AT_MOST_TWO_BITS PASS")


if __name__=="__main__":
    all_size_three_plus_three_gate()
    all_size_three_fourpole_cycle_gate()
    bridge_cut_parity_taxonomy()
    real_two_bit_ten_vertex_gate()
    print("BRIDGE_SPLIT_2PLUS4_TWO_BITS_SHARP; 3PLUS3_AT_MOST_ONE_BIT")
    print("FULL_THREE_BIT_108_GADGET_NOT_CONSTRUCTED; P_VS_NP=OPEN")
