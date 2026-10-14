#!/usr/bin/env python3
"""R5 exact ANTIPHASE fourpole transfer -> mandatory 87-state sixpole.

ALL-SIZE conditional identity, for a proper cubic 4-pole H with
ordered fourport relation {AABB,ABAB}, whose physical ports are
(x,y,a,b), and whose x,y belong to DIFFERENT logical pairs:
  a!=b: x=a,y=b
  a==b: x=y!=a, two possible values of x.

Use global final logical port order (x,u,y,v,w,z) with physical
equality pairs (x,u),(y,v),(w,z). The right 6-pole order is
(u,v,w,z,a,b). Full 108-state GOOD exact-one relation on final six
ports holds IF AND ONLY IF the right 6-pole physical relation equals
a precisely frozen 87-state set R87 of proper Klein-four parity
tuples. All 87 right states are ESSENTIAL (each has unique full
GOOD external witnesses, and every one of 108 has unique right
origin). Cut a,b equal: 21 states; unequal: 66 states; R87 has
15 orbits under global 3-colour permutations.

Second anti-phase class {AABB,ABBA} is equivalent by swapping
x and y with the corresponding reordering of logical pairs.

STRUCTURAL NECESSARY FILTER:
The right six-pole comprises SIX arbitrary connected colourable
cubic FOURPOLES with NINE LOOPLESS interblock joins (parallel links
allowed). Exact isomorphism-complete skeleton catalogue generator:
  r5_sixblock_217_loopless_catalogue_for_antiphase.cpp
returns exactly 110170 connected labelled, 217 canonical isotypes.

For EVERY skeleton and EVERY ordered attachment of TWO cut ports
(15 cut position pairs) and EVERY ordering of remaining FOUR outer
ports (24 permutations), compute complete external proper 3-colour
support for EACH possible six-vector of LOCAL fourpole orbit IDs,
using all 3**9 joining-edge colourings. Call a local orbit vector
SAFE if its complete external support is a subset of the relabelled
R87. For any realizable six-block physical boundary signature with
full target R87, the union of SAFE orbit-vector external supports
must COVER all 87 required right physical states.

This is an OVERAPPROXIMATION: it allows inconsistent selection of
fourpole orbit types between different boundary states. It is a
NECESSARY test, not sufficient. Independently executed exact counts:
   total skeleton * placements:        217 * 15 * 24 = 78120
   impossible even at SAFE envelope:                      57504
   first-stage survivors requiring fixed 11-class CSP:   20616
   skeletons impossible under ALL attachments:              114
   skeletons passing envelope under ALL attachments:         24
No full threebit graph or final UNSAT for all 20616 survivors
is claimed. General 108 physical cubic Exact-One remains OPEN.
Polynomial native SolveLinearCubicXSAT NOT CONSTRUCTED; P vs NP OPEN.

All numerical regressions are exact deterministic integer and
exhaustive proper 3-colour orbit calculations, no heuristic physics.
"""
from collections import Counter, defaultdict
from itertools import combinations, permutations, product
from pathlib import Path
from hashlib import sha256
import sys

from r5_exactone_six_fourpole_nineedge_simple_skeleton_gate import (
    local_orbit_physical_records
)

COLOURS=(0,1,2)
GF4=(1,2,3)
PAIRS=((0,1),(2,3),(4,5))
ALL_SIX=tuple(product(COLOURS,repeat=6))
FOUR_REPS=((0,0,1,1),(0,1,0,1))
ANTIPHASE=frozenset(tuple(rename[c] for c in rep)
    for rename in permutations(COLOURS) for rep in FOUR_REPS)


def good108():
    return frozenset(s for s in ALL_SIX
        if all(s.count(c)%2==0 for c in COLOURS)
        and sum(s[a]==s[b] for a,b in PAIRS)==1)


def canonical_colours(s):
    ren={}
    return tuple(ren.setdefault(c,len(ren)) for c in s)


def mandatory_right87():
    target=good108()
    assert len(target)==108 and len(ANTIPHASE)==12
    right={}
    origins=defaultdict(list)
    for state in ALL_SIX: # order u,v,w,z,a,b
        xor=0
        for c in state:xor^=GF4[c]
        if xor:continue
        outcomes={
            (x,state[0],y,state[1],state[2],state[3])
            for x,y,a,b in ANTIPHASE if (a,b)==state[4:]
        }
        if outcomes and outcomes<=target:
            right[state]=outcomes
            for s in outcomes:origins[s].append(state)
    assert len(right)==87
    assert set(origins)==target
    assert all(len(r)==1 for r in origins.values())
    assert sum(len(outcomes) for outcomes in right.values())==108
    assert Counter(state[4]==state[5] for state in right)==Counter({
        False:66,True:21
    })
    assert len({canonical_colours(s) for s in right})==15
    frozen="\\n".join("".join(map(str,state)) for state in sorted(right))+"\\n"
    assert sha256(frozen.encode()).hexdigest()==(
        "e763a3440ee9c03f0da62a3387cebf93214c3d13f01fc5e83eff977c3c37fcb9"
    )
    # Every safe right state is mandatory, since it gives at least
    # one target full state with one and only one generating right.
    assert all(outcomes for outcomes in right.values())
    print("ANTIPHASE_TRANSFER_EXACT_TARGET_RIGHT87",{
        "full_exactone_state_count":108,
        "mandatory_right_states":87,
        "right_S3_colour_orbits":15,
        "cut_colours_equal":21,
        "cut_colours_unequal":66,
        "complete_full_state_unique_right_origin":108,
    },flush=True)
    return frozenset(right)


def right_target_mask(required,cut,order):
    outside=tuple(i for i in range(6) if i not in cut)
    result=0
    for s in required:
        mapped=[None]*6
        for j,c in zip(order,s[:4]):mapped[outside[j]]=c
        mapped[cut[0]]=s[4];mapped[cut[1]]=s[5]
        assert None not in mapped
        code=sum(c*3**(5-j) for j,c in enumerate(mapped))
        result|=1<<code
    assert result.bit_count()==87
    return result


def load_catalogue(path):
    graphs=[]
    for line in Path(path).read_text().strip().splitlines():
        E=tuple(sorted(tuple(map(int,e.split('-')))
            for e in line.split(',')))
        assert len(E)==9 and all(0<=u<v<6 for u,v in E)
        degree=Counter(v for edge in E for v in edge)
        assert max(degree.values())<=4
        graphs.append(E)
    assert len(graphs)==len(set(graphs))==217
    return graphs


def exact_safe_envelope_all_217(catalogue):
    necessary=mandatory_right87()
    placements=tuple((cut,order,right_target_mask(necessary,cut,order))
        for cut in combinations(range(6),2)
        for order in permutations(range(4)))
    assert len(placements)==360
    totals=Counter()
    cases=[]
    for index,E in enumerate(load_catalogue(catalogue)):
        records,_=local_orbit_physical_records(E)
        matched=0
        for cut,order,target in placements:
            envelope=0
            for support in records.values():
                if not (support & ~target):
                    envelope |= support
            if (target&~envelope):
                totals["impossible"]+=1
            else:
                totals["unresolved"]+=1
                matched+=1
                if len(cases)<8:cases.append((index,cut,order))
        if matched==0:totals["all_assignments_impossible_skeletons"]+=1
        if matched==360:totals["all_assignments_survive_skeletons"]+=1
        if index%40==0:
            print("ANTIPHASE_217_ENVELOPE_PROGRESS",{
                "sixblock_index":index,
                "unresolved_so_far":totals["unresolved"],
            },flush=True)
    expected=Counter({
        "impossible":57504,
        "unresolved":20616,
        "all_assignments_impossible_skeletons":114,
        "all_assignments_survive_skeletons":24,
    })
    assert totals==expected,(totals,expected)
    print("SIXBLOCK_ALL_217_ANTIPHASE_87_NECESSARY_FILTER_PASS",{
        "counts":dict(totals),
        "full_placement_checks":217*15*24,
        "first_not_yet_excluded":cases,
        "scientific_gate":"NECESSARY_FILTER_ONLY_NOT_COMPLETE_UNSAT"
    },flush=True)


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit(
            "Usage: python script.py /tmp/sixblock_217_catalogue.txt")
    exact_safe_envelope_all_217(sys.argv[1])
