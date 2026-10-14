#!/usr/bin/env python3
"""R5 EXACT seven-fourpole / eleven-join simple 3-edge-connected no-go.

All-size-within-grammar theorem:
Take SEVEN arbitrary connected colourable cubic fourpoles with complete
four-port physical relations from the eleven proved S3-invariant
two-to-four-orbit classes. Join them by eleven ordinary edges whose
seven-block skeleton is SIMPLE and 3-EDGE-CONNECTED. Six physical
semiedges remain, one at each degree-three block, and the seventh
degree-four fourpole acts as an internal "synchronous phase hub".
Choose any perfect logical matching of the six physical semiedges.

NONE of these assemblies realizes all three one-hot equality bits
{100,010,001} without a forbidden bit (000 or 111). Since a GOOD-only
assembly is Kempe-saturated to all 36 physical tuples per occurring
one-hot bit, this excludes a full 108-state physical Exact-One
sixpole WITHIN THIS EXACT BLOCK GRAMMAR, at any internal block sizes.

Proof and reproducibility:
1. The prior independent seven-block generator enumerates all 5670
   labelled simple degree (4,3,3,3,3,3,3) skeletons and certifies four
   full isomorphism orbits of size 2520,1260,1260,630, each with
   3-edge-connectivity.
2. For each representative enumerate all 3^11 proper colours of the
   eleven physical interblock edges. The prior phase_hub_records()
   yields, for EVERY possible seven-vector of fourport colour orbit
   IDs (four types AAAA/AABB/ABAB/ABBA), the EXACT 729-bit physical
   support of its six external ports, not a linear relaxation.
3. For every logical matching, a local orbit vector is BAD if any of
   its proper physical boundary assignments has an excluded Boolean
   bit. An assembly with no bad boundary states cannot select a BAD
   local vector.
4. If a full three-bit assembly existed, choose one full proper
   colouring each for 100/010/001, and their three GOOD-safe local
   orbit vectors p,q,r. Their componentwise OR masks U_v are subsets
   of the true selected fourpole classes S_v. Because all actual
   colour support is MONOTONE under enlarging any block class, U
   cannot permit a BAD vector.
5. Every actual colourable cubic fourpole class has at least TWO
   of the four orbit types. If any U_v has only one orbit, append
   exactly ONE additional orbit from S_v (<=3 choices). The resulting
   masks T_v are valid 11-class masks contained in S_v, so T still
   has all three witnesses and no BAD vector. Conversely any found
   GOOD-safe T would be a REAL physically realizable composition,
   because all eleven fourpole signatures have physical witnesses.
6. Exhaust ALL triples (p,q,r), reject those with a BAD compatible
   local vector, and explicitly test ALL minimal singleton-masked
   extensions. None works in any of the 29 nonisomorphic
   (skeleton, logical-pairing) cases.

Automorphisms: the six exposed port indices lie on six DIFFERENT
degree-three blocks. Any skeleton automorphism induces a permutation
of these six ports. Relabelling constituent 4pole blocks together
with their ordered physical fourport signatures is legitimate because
all eleven classes are allowed for EVERY block. Thus one pairing per
true automorphism orbit suffices. All 15 labelled pairings are shown
covered exactly, yielding 9/7/8/5 representatives on the four
skeletons (29 total).

Observed exact counts over those 29 representatives:
  surviving first-two-good-witness pairs       170704
  completed distinct GOOD witness triples     41781391
  GOOD triples free of immediately BAD vector  1181873
  checked singleton-orbit minimal extensions   14817393
  valid complete three-bit 11-class assemblies 0.

Positive regression: a synthetic orbit-support relation with three
independent safe orbits MUST be accepted by the exact search, so the
negative detector is not hardcoded to reject every input.

CRITICAL LIMIT: This does not exclude the 7-block NON-3CONNECTED
architectures, parallel interblock joins, arbitrary large block
networks, irreducible cubic cores, or general native SCL instances.
P vs NP stays OPEN, SolveLinearCubicXSAT NOT CONSTRUCTED.
"""
from collections import Counter,defaultdict
from itertools import permutations,product,combinations
from r5_exactone_seven_fourpole_synchronous_hub_frontier import (
    SKELETONS, phase_hub_records, verify_all_four_nonisomorphic_skeletons,
    logical_pairings
)

GOOD=("100","010","001")
EXPECTED={
    0:{"orbits":9,"pairs":48533,"triples":11590395,
       "survivors":342002,"extensions":4269270},
    1:{"orbits":7,"pairs":47213,"triples":12014345,
       "survivors":309555,"extensions":4044777},
    2:{"orbits":8,"pairs":52884,"triples":13257203,
       "survivors":354552,"extensions":4561146},
    3:{"orbits":5,"pairs":22074,"triples":4919448,
       "survivors":175764,"extensions":1942200},
}


def pairing_key(p):
    return tuple(sorted(tuple(sorted(x)) for x in p))


def true_pairing_orbits(edges, port_vertices):
    """Compute genuine graph automorphisms, NOT guessed S6 symmetry."""
    original={tuple(sorted(e)) for e in edges}
    automorphisms=[]
    pos={v:i for i,v in enumerate(port_vertices)}
    for perm in permutations(range(7)):
        transformed={tuple(sorted((perm[u],perm[v]))) for u,v in edges}
        if transformed!=original:continue
        assert {perm[v] for v in port_vertices}==set(port_vertices)
        automorphisms.append(tuple(pos[perm[v]] for v in port_vertices))
    full={pairing_key(p) for p in logical_pairings()}
    remaining=set(full)
    classes=[]
    while remaining:
        p=min(remaining)
        orbit={pairing_key(tuple((perm[a],perm[b]) for a,b in p))
               for perm in automorphisms}
        assert orbit<=full
        assert orbit<=remaining
        remaining-=orbit
        classes.append((p,len(orbit)))
    assert sum(x[1] for x in classes)==len(full)==15
    return automorphisms,tuple(classes)


def masks_for(pairing):
    masks={b:0 for b in GOOD}
    masks["BAD"]=0
    for code in range(729):
        s=tuple((code//3**(5-i))%3 for i in range(6))
        truth="".join(str(int(s[u]==s[v])) for u,v in pairing)
        masks[truth if truth in GOOD else "BAD"] |= 1<<code
    assert sum(v.bit_count() for v in masks.values())==729
    return masks


def support_bad(masks,conflict):
    """A forbidden local-orbit pattern contained in all chosen masks?"""
    result=conflict[0][masks[0]] & conflict[1][masks[1]]
    result &= conflict[2][masks[2]] & conflict[3][masks[3]]
    if not result:return False
    return bool(result & conflict[4][masks[4]]
                & conflict[5][masks[5]] & conflict[6][masks[6]])


def complete_three_witness_search(records,pairing):
    """Return SAT certificate or finite complete UNSAT audit counters."""
    masks=masks_for(pairing)
    excluded=masks["BAD"]
    bad=tuple(z for z,statebits in records.items() if statebits&excluded)
    goods=tuple(
        tuple(z for z,statebits in records.items()
              if not (statebits&excluded) and statebits&masks[b])
        for b in GOOD
    )
    assert all(goods),("missing candidate witness",pairing)
    conflicts=[[0]*16 for _ in range(7)]
    for j,p in enumerate(bad):
        flag=1<<j
        for v,orb in enumerate(p):
            for mask in range(1,16):
                if mask&(1<<orb):
                    conflicts[v][mask]|=flag
    cnt=Counter()
    for p in goods[0]:
        for q in goods[1]:
            first=tuple((1<<a)|(1<<b) for a,b in zip(p,q))
            if support_bad(first,conflicts):
                continue
            cnt["pairs"]+=1
            for r in goods[2]:
                cnt["triples"]+=1
                union=tuple(mask|(1<<a) for mask,a in zip(first,r))
                if support_bad(union,conflicts):
                    continue
                cnt["survivors"]+=1
                singleton=tuple(v for v,m in enumerate(union)
                                if m.bit_count()==1)
                if not singleton:
                    return dict(cnt), (union,(p,q,r))
                additions=tuple(
                    tuple(union[v] | (1<<orb) for orb in range(4)
                          if not union[v]&(1<<orb))
                    for v in singleton
                )
                for choice in product(*additions):
                    cnt["extensions"]+=1
                    tested=list(union)
                    for v,mask in zip(singleton,choice):
                        tested[v]=mask
                    if not support_bad(tested,conflicts):
                        return dict(cnt),(tuple(tested),(p,q,r))
    return dict(cnt),None


def positive_control():
    p=((0,1),(2,3),(4,5))
    masks=masks_for(p)
    records={
       (0,)*7 : 1 << next(i for i in range(729)
            if masks["100"]&(1<<i)),
       (1,)*7 : 1 << next(i for i in range(729)
            if masks["010"]&(1<<i)),
       (2,)*7 : 1 << next(i for i in range(729)
            if masks["001"]&(1<<i))
    }
    _,sat=complete_three_witness_search(records,p)
    assert sat is not None
    selected,_=sat
    assert all(m.bit_count()>=2 for m in selected)
    print("POSITIVE_CONTROL_THREE_GOOD_SAFE_PATTERNS_IS_SAT PASS")


def run():
    verify_all_four_nonisomorphic_skeletons()
    positive_control()
    totals=Counter()
    for index,E in enumerate(SKELETONS):
        records,assignments,exposed=phase_hub_records(E)
        automorphisms,orbits=true_pairing_orbits(E,exposed)
        assert len(orbits)==EXPECTED[index]["orbits"]
        stats=Counter()
        for p,orbit_size in orbits:
            counter,solution=complete_three_witness_search(records,p)
            if solution is not None:
                raise AssertionError(
                    "LEGAL FULL THREE-BIT EXACTONE FOURPOLE GRAMMAR SAT",
                    index,p,solution
                )
            stats.update(counter)
            stats["orbits"]+=1
            stats["pairings_covered"]+=orbit_size
            print("EXACT_SEVEN_HUB_PAIRING_UNSAT",{
                "skeleton":index,
                "pairing":p,
                "automorphism_orbit_size":orbit_size,
                "witness_counts":counter
            },flush=True)
        assert stats["pairings_covered"]==15
        for key,value in EXPECTED[index].items():
            assert stats[key]==value,(index,key,stats[key],value)
        print("EXACT_SEVEN_HUB_SKELETON_UNSAT",{
            "skeleton":index,
            "true_skeleton_automorphisms":len(automorphisms),
            "exact_physical_local_orbit_records":len(records),
            "proper_interblock_colourings":assignments,
            "pairing_orbits":len(orbits),
            "full_pairings_covered":15,
            "counts":dict(stats),
        },flush=True)
        totals.update(stats)
    assert totals["orbits"]==29
    assert totals["pairings_covered"]==60
    assert totals["pairs"]==170704
    assert totals["triples"]==41781391
    assert totals["survivors"]==1181873
    assert totals["extensions"]==14817393
    assert 4*15*11**7==1169230260
    print("EXACT_ALLSIZE_SEVEN_FOURPOLE_3EDGE_SIMPLE_11JOIN_GRAMMAR_UNSAT",{
        "skeletons":4,
        "automorphism_orbit_pairing_checks":29,
        "full_labelled_pairings":60,
        "logically_covered_signature_pairing_choices":4*15*11**7,
        "exact_search_counts":dict(totals),
        "full_threebit_goodonly_signatures":0,
        "scope":"only 7 fourpoles with simple 3-edge-connected 11-edge skeleton"
    },flush=True)
    print("GENERAL_CUBIC_6POLE_108_STATES=OPEN")
    print("SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    run()
