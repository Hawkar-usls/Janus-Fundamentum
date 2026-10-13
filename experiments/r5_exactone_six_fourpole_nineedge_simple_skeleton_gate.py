#!/usr/bin/env python3
"""R5: COMPLETE six-4pole SIMPLE block-skeleton 108-state Exact-One gate.

UNIVERSAL-WITHIN-GRAMMAR theorem:
Glue SIX arbitrary connected 3-edge-colourable cubic fourpoles (each
with its complete physical 4-port relation in one of the eleven
S3-invariant 2/3/4-orbit classes) along NINE ordinary edges. Require
the interblock skeleton to be a CONNECTED SIMPLE six-vertex graph,
each vertex block-degree <=4. Exactly SIX semiedges remain exposed,
and pair them in ANY of the 15 perfect matchings.

There are exactly 14 unlabeled legal simple block skeletons:
  three with skeleton edge connectivity one,
  nine with connectivity two,
  two with connectivity three.
There are 14 * 15 * 11**6 = 372_027_810 potential assignments
of skeleton, logical matching, and six fourpole signature classes.

For ALL these instances, NO composition has full physical Boolean
support EXACTLY {100,010,001}, or more generally GOOD-only support
simultaneously containing all 3 bits. This is an ALL-SIZE theorem
ONLY for this stated SIX-FOURPOLE SIMPLE-BLOCK-SKELETON grammar.
It does NOT cover parallel interblock edges, >=7 blocks or a genuinely
indecomposable cubic sixpole. It does NOT construct SolveLinearCubicXSAT.

MACHINE CERTIFICATE TRICK (does not naively enumerate 372M cases):
1. Enumerate all 3**9 assignments of colours to the NINE interface
   edges of a skeleton, and all local compatible 4-colour vectors
   (there are only FOUR S3 orbits AAAA, AABB, ABAB, ABBA).
   For each six-vector of local orbit IDs, store the COMPLETE 729-bit
   set of physically possible external six-port colour tuples.
   This is exact existential relational composition, not a heuristic.
2. For each of 15 logical matchings, mark as BAD any local orbit
   six-vector allowing ANY forbidden physical tuple. A legal GOOD-only
   assembly CANNOT include any such vector; allowed good witnesses
   must therefore come from other, individually SAFE vectors.
3. If an assembly had ALL three onehot bits, choose one full physical
   witness each for 100,010,001. These induce three local-orbit
   six-vectors p,q,r that are each individually SAFE.
   At block v, the union mask U_v of the three orbit IDs must be a
   subset of the actual block signature mask (2,3,or4 orbits).
   Monotonicity means U cannot allow a BAD six-vector.
4. If |U_v|>=2 at all six blocks, U itself is an actual 11-class
   assignment with no forbidden tuple and 3 good bits -- a solution.
   If a block has |U_v|=1, choose ONE further orbit from its actual
   >=2-class signature: there are <=3 choices per such block.
   The resulting minimal size>=2 masks must still have no BAD tuple.
5. Exhaust ALL SAFE triples (p,q,r) and all such necessary local
   extensions. None passes. This is COMPLETELY EXHAUSTIVE even though
   the 372M block signatures are never explicitly materialized.

Each local orbit is indeed realized by a true properly colourable
fourpole signature whenever an 11-class mask includes it. The atlas
of 11 classes is a prerequisite (previous all-size R5 4pole theorem);
the construction is NOT an abstract-cover-only approximation.

Regression: connected simple six-node skeleton generation with
independent canonical labels, 3+9+2 edge connectivity distribution,
all 15 logical pairings, every 3**9 edge colour vector, exact
physical states and 6-local-orbit compatibility.

All-n global physical full Exact-One existence remains OPEN.
SolveLinearCubicXSAT NOT CONSTRUCTED; P vs NP OPEN.
"""
from collections import Counter, defaultdict
from itertools import combinations, permutations, product

NUM_BLOCKS = 6
EDGE_COUNT = 9
COLOURS = (0,1,2)
ORBIT_REPS = ((0,0,0,0),(0,0,1,1),(0,1,0,1),(0,1,1,0))
GOOD = ("100","010","001")


def connected(edges):
    adj=[[] for _ in range(6)]
    for u,v in edges:
        adj[u].append(v);adj[v].append(u)
    seen={0}
    stack=[0]
    while stack:
        u=stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v);stack.append(v)
    return len(seen)==6


def canonical_skeleton(edges):
    """Canonical graph code under all vertex permutations preserving degree."""
    deg=Counter(v for edge in edges for v in edge)
    groups=defaultdict(list)
    for v in range(6):
        groups[deg[v]].append(v)
    block_keys=sorted(groups)
    best=None
    for choices in product(*(permutations(groups[d]) for d in block_keys)):
        order=tuple(v for group in choices for v in group)
        ren={v:k for k,v in enumerate(order)}
        candidate=tuple(sorted(
            (min(ren[u],ren[v]),max(ren[u],ren[v]))
            for u,v in edges
        ))
        if best is None or candidate<best:
            best=candidate
    return best


def skeleton_connectivity(edges):
    """Minimum edge boundary of a proper vertex subset, <=3 by degree."""
    answer=9
    for mask in range(1,(1<<6)-1):
        cut=sum(bool(mask&(1<<u))!=bool(mask&(1<<v))
                for u,v in edges)
        answer=min(answer,cut)
    return answer


def all_six_block_skeletons():
    universe=tuple(combinations(range(6),2))
    representatives=set()
    labelled=0
    for edges in combinations(universe,9):
        degree=Counter(v for e in edges for v in e)
        if max(degree.values())>4 or not connected(edges):
            continue
        labelled+=1
        representatives.add(canonical_skeleton(edges))
    assert labelled==3700, labelled
    graphs=tuple(sorted(representatives))
    assert len(graphs)==14
    assert Counter(skeleton_connectivity(g) for g in graphs)==Counter({
        1:3,2:9,3:2
    })
    return graphs


def all_logical_pairings(ports):
    ports=tuple(ports)
    if not ports:
        yield ()
        return
    a=ports[0]
    for j in range(1,len(ports)):
        b=ports[j]
        for tail in all_logical_pairings(ports[1:j]+ports[j+1:]):
            yield ((a,b),)+tail


def canonical_colour_tuple(t):
    mapping={}
    return tuple(mapping.setdefault(c,len(mapping)) for c in t)


def local_orbit_physical_records(edges):
    """Map local 6-block 4port orbit IDs -> 729-bit physical state support.

    Internal edge endpoints ordered by sorted global interface edge
    indices; external physical semiedges ordered first within each
    block in vertex index order. This is a VALID ordered 4-port choice.
    """
    edges=tuple(sorted(edges))
    incidence={v:tuple(i for i,(u,w) in enumerate(edges)
                       if v==u or v==w) for v in range(6)}
    degrees=tuple(len(incidence[v]) for v in range(6))
    ext=tuple(4-d for d in degrees)
    assert all(0<=k<=3 for k in ext) and sum(ext)==6
    orbit_id={rep:i for i,rep in enumerate(ORBIT_REPS)}
    local=[]
    for v,d in enumerate(degrees):
        lookup=defaultdict(list)
        for outer in product(COLOURS,repeat=4-d):
            for interior in product(COLOURS,repeat=d):
                rep=canonical_colour_tuple(outer+interior)
                if rep in orbit_id:
                    lookup[interior].append((outer,orbit_id[rep]))
        local.append(lookup)
    records=defaultdict(int)
    complete_assignments=0
    for inner_colours in product(COLOURS,repeat=9):
        possibilities=[]
        for v in range(6):
            input_tuple=tuple(inner_colours[j] for j in incidence[v])
            valid=local[v].get(input_tuple,())
            if not valid:
                break
            possibilities.append(valid)
        else:
            for local_choices in product(*possibilities):
                outside=tuple(c for outer,_ in local_choices for c in outer)
                assert len(outside)==6
                physical_number=sum(c*3**(5-j)
                                    for j,c in enumerate(outside))
                assert all(outside.count(c)%2==0 for c in COLOURS)
                orbit_vector=tuple(orb for _,orb in local_choices)
                records[orbit_vector]|=1<<physical_number
                complete_assignments+=1
    assert 100 <= len(records) <= 1000
    return dict(records),complete_assignments


def physical_masks_by_pairing(pairing):
    answer={"100":0,"010":0,"001":0,"BAD":0}
    for index in range(729):
        colours=tuple((index//(3**(5-j)))%3 for j in range(6))
        bit="".join(str(int(colours[a]==colours[b]))
                    for a,b in pairing)
        key=bit if bit in GOOD else "BAD"
        answer[key]|=1<<index
    assert sum(mask.bit_count() for mask in answer.values())==729
    return answer


def prove_no_good_threebit_signature(records,pairing_masks):
    """Necessary full-threebit witnesses searched EXACTLY.

    A successful triple+extensions would be an explicit PHYSICAL
    11-class signature choice with no forbidden and all 3 onehot bits.
    Conversely, any valid full-threebit 11-class choice must contain
    such a triple+extensions, so finding NONE is a COMPLETE NO-GO.
    """
    badmask=pairing_masks["BAD"]
    bad=tuple(p for p,statebits in records.items() if statebits&badmask)
    good=tuple(tuple(p for p,statebits in records.items()
                     if statebits&pairing_masks[b]
                     and not (statebits&badmask))
               for b in GOOD)
    if not all(good):
        return 0
    # For each position, each subset mask of 4 orbit types, record
    # which forbidden 6-orbit witnesses it contains.
    conflicts=[[0]*16 for _ in range(6)]
    for j,p in enumerate(bad):
        flag=1<<j
        for v,orbit in enumerate(p):
            for mask in range(1,16):
                if (mask>>orbit)&1:
                    conflicts[v][mask]|=flag

    tested=0
    for p in good[0]:
        for q in good[1]:
            masks=tuple((1<<a)|(1<<b) for a,b in zip(p,q))
            if (conflicts[0][masks[0]]&conflicts[1][masks[1]]
                &conflicts[2][masks[2]]&conflicts[3][masks[3]]
                &conflicts[4][masks[4]]&conflicts[5][masks[5]]):
                continue
            for r in good[2]:
                tested+=1
                masks3=tuple(m|(1<<orb) for m,orb in zip(masks,r))
                if (conflicts[0][masks3[0]]&conflicts[1][masks3[1]]
                    &conflicts[2][masks3[2]]&conflicts[3][masks3[3]]
                    &conflicts[4][masks3[4]]&conflicts[5][masks3[5]]):
                    continue
                singletons=tuple(v for v,m in enumerate(masks3)
                                 if m.bit_count()==1)
                if not singletons:
                    raise AssertionError(
                        "DISCOVERED LEGAL THREEBIT CLASS ASSIGNMENT",
                        masks3,pairing_masks,(p,q,r)
                    )
                extensions=tuple(tuple(mask|(1<<o) for o in range(4)
                                       if not ((mask>>o)&1))
                                 for v,mask in enumerate(masks3)
                                 if v in singletons)
                for choice in product(*extensions):
                    amended=list(masks3)
                    for v,mask in zip(singletons,choice):
                        amended[v]=mask
                    if not (
                        conflicts[0][amended[0]]
                        &conflicts[1][amended[1]]
                        &conflicts[2][amended[2]]
                        &conflicts[3][amended[3]]
                        &conflicts[4][amended[4]]
                        &conflicts[5][amended[5]]
                    ):
                        raise AssertionError(
                            "DISCOVERED LEGAL THREEBIT CLASS ASSIGNMENT",
                            tuple(amended),pairing_masks,(p,q,r)
                        )
    return tested


def run():
    skeletons=all_six_block_skeletons()
    pairings=tuple(all_logical_pairings(range(6)))
    assert len(pairings)==15
    physical_tests={p:physical_masks_by_pairing(p) for p in pairings}
    exhaustive=0
    interface_cases=0
    total_triple_tests=0
    by_edgeconn=Counter()
    per_skeleton=[]
    for index,edges in enumerate(skeletons):
        records,full_4orbit_assignments=local_orbit_physical_records(edges)
        local_checks=0
        for pairing in pairings:
            local_checks+=prove_no_good_threebit_signature(
                records,physical_tests[pairing])
            interface_cases+=11**6
        total_triple_tests+=local_checks
        conn=skeleton_connectivity(edges)
        by_edgeconn[conn]+=1
        per_skeleton.append({
            "id":index,"skeleton":''.join(str(v) for e in edges for v in e),
            "edge_connectivity":conn,
            "complete_4orbit_assignments":full_4orbit_assignments,
            "distinct_local_orbit_patterns":len(records),
            "safe_good_triples_audited":local_checks
        })
        print("SIX_FOURPOLE_SKELETON",per_skeleton[-1],flush=True)
    assert interface_cases==14*15*(11**6)==372027810
    assert total_triple_tests>1_000_000
    assert by_edgeconn==Counter({1:3,2:9,3:2})
    print("ALL_SIZE_SIX_FOURPOLE_SIMPLE_GRAMMAR_EXCLUDED",{
        "skeletons":14,"logical_pairings":15,
        "signature_choices_per_block":11,
        "mathematically_covered_compositions":interface_cases,
        "actual_short_certificate_witness_triples_checked":
            total_triple_tests,
        "skeleton_edge_connectivity":dict(sorted(by_edgeconn.items())),
        "GOODONLY_ALL_THREE_BITS":0,
        "coverage":"ONLY 6 connected colourable 4poles + 9 SIMPLE block joins"
    },flush=True)
    print("FULL_THREE_BIT_108_GENERAL_SIXPOLE=OPEN")
    print("SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    run()
