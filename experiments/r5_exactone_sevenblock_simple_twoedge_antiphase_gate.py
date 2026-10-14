#!/usr/bin/env python3
"""R5: exact seven-fourpole SIMPLE low-cut frontier and 2-cut transfer gate.

Inputs: 7 independently connected, properly 3-edge-colourable cubic
FOURPOLES; 11 SIMPLE connected interblock joins; 6 external semiedges,
paired in three equal-colour logical wires.

SCIENTIFIC RESULT (universal IN THE DESCRIBED ALL-SIZE GRAMMAR):
* Exactly 59 unlabelled connected seven-block eleven-join SIMPLE
  skeletons with max degree 4. Their edge connectivity is:
  15 one-edge, 40 two-edge, 4 three-edge.
* ALL 15 one-edge-connected skeletons have a 3+3 physical port
  bridge: impossible to realize full GOOD-only three bits, by the
  earlier all-size 4pole-bridge theorem.
* ALL 40 two-edge-connected skeletons have a 2-cut partitioning
  exactly 2 versus 4 of the physical outer semiedges. ALL have at
  least one degree-two block that forms a FOURPOLE with exactly two
  external ports and two cut ports.
* A full GOOD-only 108-state gadget cannot assign BOTH external ports
  of such a degree-two block to the SAME logical equality pair.
  Indeed, the right remaining six FOURPOLE blocks (9 joining edges)
  would then themselves realize a full three-bit GOOD-only sixpole
  by parity + full S3 extendability of both equal/unequal cut colours.
  This contradicts prior all-size SIX-fourpole multigraph no-go.
* If its two external ports belong to DIFFERENT logical pairs,
  the 11-class 4pole catalogue and exact 3^4 right-port transfer
  condition restrict its 4port orbit signature to exactly:
    {AAAA,ABAB}, {AAAA,ABBA}, {AABB,ABAB}, {AABB,ABBA}.
  In first TWO classes, port colours pass directly (or swapped)
  across the cut, so the right sixblock sixpole would again support
  FULL GOOD-only three-bit, impossible by the prior 6block theorem.
  Thus the ONLY STILL-POSSIBLE two-outer-port 4pole signatures are
    {AABB,ABAB} or {AABB,ABBA}.
  These are genuine ANTI-PHASE fourpoles: equal cut colours transmit
  a DIFFERENT equal outer colour, whereas different cut colours
  transmit the same ordered pair (or its reversal).
* Among the 40 two-edge-connected skeletons:
    18 have 1 degree-two block, 12/15 pairings can survive;
    19 have 2 degree-two blocks, 10/15 pairings survive;
     3 have 3 degree-two blocks,  8/15 pairings survive.
  Thus 430 of 600 possible labelled skeleton+pairing cases survive
  this exact NECESSARY port-pair filtering; the number of remaining
  choices for the forced anti-phase signatures on all degree-two
  blocks is 1384 before selecting classes for other blocks.

WE DO NOT CLAIM UNSAT for the remaining 430 skeleton/pairing cases.
The two anti-phase signatures require exact simultaneous sixblock
compatibility checks or a new topology-independent theorem.
The full 108-state gadget remains OPEN; P vs NP remains OPEN.

STANDALONE REPRODUCIBILITY:
Requires networkx only for 59 proposed n7 atlas representatives.
An INDEPENDENT 352716-combination degree/connectivity enumeration
produces the entire set of 145110 labelled eligible graphs. Their
full 7! relabelling orbits are DISJOINT and their union is EXACTLY the
145110 independently generated graphs. Thus atlas completeness is
not trusted as an unverified axiom in this proof.

All numerical tests are exact finite integer/set operations.
"""
from collections import Counter
from itertools import combinations, permutations, product
import networkx as nx

ORBIT_REPS=(
    (0,0,0,0),(0,0,1,1),(0,1,0,1),(0,1,1,0)
)
COL=range(3)
GOOD={"100","010","001"}
PAIRING=((0,1),(2,3),(4,5))
ALL_EDGES=tuple(combinations(range(7),2))
EDGE_INDEX={e:i for i,e in enumerate(ALL_EDGES)}


def all_matchings(items=(0,1,2,3,4,5)):
    if not items:
        yield ()
    else:
        for k in range(1,len(items)):
            for tail in all_matchings(items[1:k]+items[k+1:]):
                yield ((items[0],items[k]),)+tail


def physically_good(s):
    return sum(s[a]==s[b] for a,b in PAIRING)==1


def full_good_relation():
    return frozenset(s for s in product(COL,repeat=6)
        if all(s.count(c)%2==0 for c in COL) and physically_good(s))


def fourpole_signatures():
    return tuple((ids,frozenset(
        tuple(perm[c] for c in ORBIT_REPS[i])
        for i in ids for perm in permutations(COL)
    )) for k in (2,3,4) for ids in combinations(range(4),k))


def maximum_safe_right_relation(signature,external_indices,target):
    """Exact 2-edge colour-compatible RIGHT maximal relation.

    Left physical FOURPOLE port order: (left ext0,left ext1,cut0,cut1).
    Right physical SIXPOLE order: four other original ext ports
    (ascending user indices) followed by cut0,cut1.
    A RIGHT state is safe iff EVERY legal extension by the left
    4pole yields an Exact-One allowed full sixport state.
    """
    right_indices=tuple(i for i in range(6) if i not in external_indices)
    grouped={}
    for t in signature:
        grouped.setdefault(t[2:],set()).add(t[:2])
    by_right={}
    for s in target:
        k=tuple(s[i] for i in right_indices)
        by_right.setdefault(k,set()).add(
            tuple(s[i] for i in external_indices))
    right=set()
    for out in product(COL,repeat=4):
        xor_right=0
        for c in out:
            xor_right ^= (1,2,3)[c]
        for cut,left_options in grouped.items():
            if (1,2,3)[cut[0]]^(1,2,3)[cut[1]] != xor_right:
                continue
            if left_options <= by_right.get(out,set()):
                right.add(out+cut)
    return frozenset(right)


def exact_port_transfer_taxonomy():
    target=full_good_relation()
    assert len(target)==108
    signatures=fourpole_signatures()
    assert len(signatures)==11
    viable={}
    for ext in ((0,1),(0,2)):  # SAME logical pair / CROSS pair
        yes=[]
        right=tuple(i for i in range(6) if i not in ext)
        for ids,relation in signatures:
            safe_right=maximum_safe_right_relation(
                relation,ext,target)
            projected=set()
            # Relational composition: EVERY right state in safe_right
            # may independently combine with all left extensions.
            for rr in safe_right:
                left4={s[:2] for s in relation if s[2:]==rr[4:]}
                for left in left4:
                    s=[None]*6
                    for j,val in zip(right,rr[:4]):s[j]=val
                    for j,val in zip(ext,left):s[j]=val
                    projected.add(tuple(s))
            yes_case=(projected==target)
            if yes_case:yes.append(ids)
            if ext==(0,1) and yes_case:
                assert len(safe_right)==108
                # Replace left logical pair by the two cut semiedges.
                assert all(sum(r[a]==r[b] for a,b
                  in ((4,5),(0,1),(2,3)))==1 for r in safe_right)
            if ext==(0,2) and ids in ((0,2),(0,3)):
                assert yes_case and len(safe_right)==108
                new_pair=(
                    ((4,0),(5,1),(2,3)) if ids==(0,2)
                    else ((5,0),(4,1),(2,3))
                )
                assert all(sum(r[a]==r[b] for a,b
                         in new_pair)==1 for r in safe_right)
            if ext==(0,2) and ids in ((1,2),(1,3)):
                assert yes_case and len(safe_right)==87
        viable[ext]=yes
    assert len(viable[(0,1)])==9
    assert viable[(0,2)]==[
        (0,2),(0,3),(1,2),(1,3)
    ]
    print("ALL_11_FOURPOLE_CLASS_EXACT_T_TRANSFER",{
        "same_logical_pair_possible_classes":viable[(0,1)],
        "cross_logical_pair_possible_classes":viable[(0,2)],
        "cross_classes_excluded_by_sixblock_full_GOOD_theorem":
            ((0,2),(0,3)),
        "only_unresolved_antiphase_classes":((1,2),(1,3)),
    },flush=True)


def labelled_simple_degree_connected_graphs():
    """Independent labelled census; does NOT call graph atlas."""
    good=set()
    for ids in combinations(range(len(ALL_EDGES)),11):
        degree=[0]*7
        adj=[0]*7
        for index in ids:
            u,v=ALL_EDGES[index]
            degree[u]+=1
            degree[v]+=1
            if degree[u]>4 or degree[v]>4:
                break
            adj[u] |= 1<<v
            adj[v] |= 1<<u
        else:
            visited=1
            while True:
                next_seen=visited
                for v in range(7):
                    if visited&(1<<v):
                        next_seen |= adj[v]
                if next_seen==visited:break
                visited=next_seen
            if visited==127:
                good.add(sum(1<<i for i in ids))
    return good


def complete_sevenblock_simple_skeletons():
    from_atlas=tuple(
        tuple(sorted(tuple(sorted(e)) for e in G.edges()))
        for G in nx.graph_atlas_g()
        if G.number_of_nodes()==7 and G.number_of_edges()==11
        and nx.is_connected(G)
        and max(dict(G.degree()).values())<=4
    )
    assert len(from_atlas)==59
    orbits=set()
    orbit_sizes=[]
    for E in from_atlas:
        current=set()
        for permutation in permutations(range(7)):
            mask=0
            for u,v in E:
                a,b=permutation[u],permutation[v]
                if a>b:a,b=b,a
                mask |= 1<<EDGE_INDEX[a,b]
            current.add(mask)
        assert not current&orbits
        orbits |= current
        orbit_sizes.append(len(current))
    independent=labelled_simple_degree_connected_graphs()
    assert len(orbits)==sum(orbit_sizes)==len(independent)==145110
    assert orbits==independent
    print("SEVEN_SIMPLE_ELEVEN_JOIN_ATLAS_INDEPENDENT_ORBIT_CENSUS",{
        "unlabelled":59,"labelled":145110,
        "disjoint_7factorial_label_orbits":True,
        "independent_full_labelled_generator":True
    },flush=True)
    return from_atlas


def cut_sides(E,cut):
    remaining=tuple(e for e in E if e not in cut)
    neighbors=[[] for _ in range(7)]
    for u,v in remaining:
        neighbors[u].append(v)
        neighbors[v].append(u)
    start=cut[0][0]
    seen={start}
    queue=[start]
    for u in queue:
        for v in neighbors[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    return seen


def edge_connectivity_and_cuts(E):
    mincut=11
    splits={}
    degree=Counter(v for e in E for v in e)
    exposed={v:4-degree[v] for v in range(7)}
    for subset in range(1,(1<<7)-1):
        if not subset&1:continue
        S={v for v in range(7) if subset>>v&1}
        border=sum((u in S)!=(v in S) for u,v in E)
        if border<mincut:mincut=border
        if border<=2:
            physical=sum(exposed[v] for v in S)
            splits.setdefault(border,set()).add(
                min(physical,6-physical))
    return mincut,splits,exposed


def cut_pairing_census(skeletons):
    matching_list=tuple(all_matchings())
    assert len(matching_list)==15
    cats=Counter()
    surv=Counter()
    for E in skeletons:
        conn,splits,exposed=edge_connectivity_and_cuts(E)
        cats[conn]+=1
        if conn==1:
            # Universal 3+3 bridge no-go applies.
            assert 3 in splits.get(1,set()),(E,splits)
        elif conn==2:
            # Every 2-cut (including nontrivial ones) splits 2+4.
            assert splits.get(2)=={2},(E,splits)
            degree2=[v for v in range(7) if 4-exposed[v]==2]
            assert degree2
            labelled={}
            k=0
            for v in range(7):
                labelled[v]=tuple(range(k,k+exposed[v]))
                k+=exposed[v]
            assert k==6
            valid=sum(all(not any(set(p)==set(labelled[v])
                          for p in matching)
                       for v in degree2)
                for matching in matching_list)
            assert valid in (8,10,12)
            surv[(len(degree2),valid)]+=1
        else:
            assert conn==3
    assert cats==Counter({1:15,2:40,3:4}),cats
    assert surv==Counter({(1,12):18,(2,10):19,(3,8):3}),surv
    matched=sum(v*n for (_,v),n in surv.items())
    assert matched==430
    choices=sum(n*valid*(2**degree2) for (degree2,valid),n
                in surv.items())
    assert choices==1384,choices
    print("SEVEN_SIMPLE_LOW_CUT_THIRD_BIT_FRONTIER",{
        "skeleton_edge_connectivity":dict(cats),
        "all_15_bridged_have_3PLUS3_split":True,
        "all_40_twoedge_skeletons_have_2PLUS4_split":True,
        "degree2_block_survivor_counts":{
          str(k):v for k,v in surv.items()},
        "surviving_pairings_from_40_times15":matched,
        "remaining_antiphase_local_class_choices":choices,
        "universally_excluded_by_earlier_proved_theorems":
            "all bridge skeletons; all 3-edge-connected skeletons;"
            " all same-pair 2-cuts; all direct-transfer 2-cut classes",
        "scope":"remaining 40 two-edge skeletons require full phase-coupling check"
    },flush=True)


if __name__=="__main__":
    exact_port_transfer_taxonomy()
    g=complete_sevenblock_simple_skeletons()
    cut_pairing_census(g)
    print("NOT_ALL_7BLOCK_SIMPLE_GRAMMAR_UNSAT")
    print("PHYSICAL_108_FULL_THREEBIT_GADGET_OPEN")
    print("SolveLinearCubicXSAT_NOT_CONSTRUCTED; P_VS_NP_OPEN")
