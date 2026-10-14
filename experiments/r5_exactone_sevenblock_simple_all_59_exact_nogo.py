#!/usr/bin/env python3
"""R5 COMPLETE simple seven-fourpole / eleven-join Exact-One NO-GO.

All sizes WITHIN the specified grammar of seven connected colourable
cubic 4poles joined by 11 edges forming a SIMPLE CONNECTED 7-block
skeleton, with any perfect logical matching of six physical semiedges.

The previous high-connectivity exact verifier excludes all 4
3-edge-connected skeletons. The all-size fourpole bridge theorem
excludes all 15 one-edge-connected skeletons: EACH has a 3+3 port
bridge. This executable proves NO-GO for ALL REMAINING 40 simple
2-edge-connected sevenblock skeletons.

Exhaustive cut/transfer theorem (see separate n7 atlas verifier):
Every one of the 40 has at least one degree-2 constituent 4pole H
exposing TWO physical semiedges x,y and TWO cut semiedges a,b.
If x,y form one entire logical pair, cut parity x XOR y=a XOR b
transfers exactly the truth bit to the other six-block physical
sixpole, giving full threebit GOOD on those six blocks -- IMPOSSIBLE
by prior exact all-size six-fourpole loopless multigraph theorem.
If x,y belong to DIFFERENT logical pairs, the 11-class 4pole atlas
and all-81 right-four-port transfer compatibility allow only
{AAAA,ABAB},{AAAA,ABBA},{AABB,ABAB},{AABB,ABBA} on H.
The first two identities just wire/swap x,y to/from a,b and likewise
force FULL GOOD on the remaining 6 blocks, already excluded.
Thus H must be an "ANTIPHASE" {AABB,ABAB} or {AABB,ABBA} physical
4pole. Swapping the two exposed semiedge indices turns these two
signature classes into one another. Since ALL 12 cross-logical-pair
perfect matchings are checked, it SUFFICES to fix {AABB,ABAB}
on one designated degree-two block per skeleton. Other six 4poles
retain ALL 11 possible signature classes.

The remaining SIX constituent fourpoles and their NINE internal
joins form a connected SIMPLE six-block graph. The designated
antiphase block is removed and its TWO connecting edges become TWO
physical semiedges of this right sixblock. Right physical port order
is (the other FOUR original outer ports in vertex order,cut0,cut1).
For each of all 3**9 interface colourings, enumerate every compatible
four-semiedge local orbit. Group into six-orbit vectors, storing the
EXACT 729-bit external physical 6port relation for each local pattern.

For each of 40 original skeletons and each of 12 allowed logical
pairings (480 checks), compose this full sixblock relation with the
fixed ACTUAL {AABB,ABAB} 4pole signature through the TWO cut-edge
colours, to calculate exact possible final Boolean bits.

A candidate GOOD-only 3-bit assembly requires three individually
GOOD-safe sixblock orbit vectors (one witness per 100,010,001).
Their per-block orbit bitwise union must not enable ANY forbidden
physical output, and singleton orbit unions must be extended to
>=2-orbit actual colourable fourpole signatures, again retaining
NO forbidden output. Exhaust EVERY such three-witness triple and
all up-to-three-per-singleton extensions, using exact integer bitsets.

INDEPENDENT EXACT SEARCH RESULTS:
    40 twoedge skeletons;
    480 exact matching checks;
    315782 first-two-good pairs surviving forbidden screening;
    22063552 third-good witness triples examined;
    414690 three-witness unions pass immediate BAD screening;
    3812910 singleton local-orbit extensions checked;
    ZERO valid full threebit physical boundary relations.

In this precise grammar, NO 108-state full Exact-One exists. This
is an ALL-INTERNAL-SIZES proof ONLY WITHIN THE SIMPLE SEVEN-4POLE
ELEVEN-JOIN GRAMMAR, relying on the prior all-size 4pole atlas,
3+3 bridge theorem, sixblock loopless multigraph no-go and existing
sevenblock 3-edge high-connectivity theorem.

DO NOT extrapolate to sevenblock multigraphs with parallel joins,
8+ blocks or arbitrary irreducible cubic cores.
SolveLinearCubicXSAT not constructed; P vs NP OPEN.
"""
from collections import Counter,defaultdict
from itertools import combinations,permutations,product

from r5_exactone_sevenblock_simple_twoedge_antiphase_gate import (
    ORBIT_REPS, all_matchings, fourpole_signatures,
    complete_sevenblock_simple_skeletons, edge_connectivity_and_cuts,
)

COLORS=(0,1,2)
ORBIT_IDS={rep:i for i,rep in enumerate(ORBIT_REPS)}
GOOD=("100","010","001")
RIGHT_STATE=tuple(
    tuple((code//3**(5-i))%3 for i in range(6))
    for code in range(729)
)
ANTIPHASE=next(signature for ids,signature in fourpole_signatures()
               if ids==(1,2))


def canon(seq):
    dictionary={}
    return tuple(dictionary.setdefault(c,len(dictionary)) for c in seq)


def exact_right_sixblock_records(original_edges,isolated):
    """Independent 3^9 connector enumeration; legal six-port support."""
    cross=tuple(sorted(tuple(sorted((u,v))) for u,v in original_edges
                       if isolated in (u,v)))
    assert len(cross)==2
    neighbor=tuple(v if u==isolated else u for u,v in cross)
    ordinary=tuple(sorted(tuple(sorted((u,v))) for u,v in original_edges
        if isolated not in (u,v)))
    assert len(ordinary)==9
    vertices=tuple(v for v in range(7) if v!=isolated)
    deg=Counter(v for e in original_edges for v in e)
    external={}
    next_port=0
    for v in vertices:
        n=4-deg[v]
        external[v]=list(range(next_port,next_port+n))
        next_port+=n
    assert next_port==4
    external[neighbor[0]].append(4)
    external[neighbor[1]].append(5)
    assert sorted(p for ports in external.values() for p in ports)==list(range(6))
    incidences={v:tuple(j for j,e in enumerate(ordinary) if v in e)
                for v in vertices}
    local={}
    for v in vertices:
        lookup=defaultdict(list)
        for outer in product(COLORS,repeat=len(external[v])):
            for inner in product(COLORS,repeat=len(incidences[v])):
                typ=ORBIT_IDS.get(canon(outer+inner),-1)
                if typ>=0:
                    lookup[inner].append((outer,typ))
        local[v]=lookup

    records=defaultdict(int)
    full=0
    for wire in product(COLORS,repeat=9):
        allowed=[]
        for v in vertices:
            choices=local[v].get(tuple(wire[j] for j in incidences[v]))
            if not choices:break
            allowed.append(choices)
        else:
            for selection in product(*allowed):
                physical=[-1]*6
                for v,(outer,kind) in zip(vertices,selection):
                    for port,col in zip(external[v],outer):
                        physical[port]=col
                assert all(c>=0 for c in physical)
                code=sum(c*3**(5-i) for i,c in enumerate(physical))
                ids=tuple(kind for outer,kind in selection)
                records[ids]|=1<<code
                full+=1
    return dict(records),full


def output_bit_labels(right_state,logical_pairing):
    """All real left antiphase extensions of a fixed right 6port state."""
    out=right_state[:4]
    cut=right_state[4:]
    result=set()
    for x,y,a,b in ANTIPHASE:
        if (a,b)!=cut:continue
        full=(x,y)+out
        bit="".join(str(int(full[u]==full[v]))
                    for u,v in logical_pairing)
        result.add(bit)
    return result


def physical_good_bad_bitsets(logical_pairing):
    labels=tuple(output_bit_labels(p,logical_pairing)
                 for p in RIGHT_STATE)
    allowed=tuple(sum(1<<i for i,t in enumerate(labels) if b in t)
                  for b in GOOD)
    bad=sum(1<<i for i,t in enumerate(labels)
            if any(b not in GOOD for b in t))
    return allowed,bad


def exact_three_witness_match(records,goods,badbit):
    """Complete integer-bitset SAT test with positive controls."""
    bad=tuple(p for p,bits in records.items() if bits&badbit)
    valid=tuple(tuple(p for p,bits in records.items()
        if bits&target and not(bits&badbit)) for target in goods)
    if not all(valid):
        return Counter(),None
    conflicts=[[0]*16 for _ in range(6)]
    for j,p in enumerate(bad):
        flag=1<<j
        for v,orbit in enumerate(p):
            for mask in range(1,16):
                if mask&(1<<orbit):
                    conflicts[v][mask]|=flag

    def has_bad(m):
        if not bad:return False
        bits=conflicts[0][m[0]]
        for i in range(1,6):
            bits &= conflicts[i][m[i]]
            if not bits:break
        return bool(bits)

    count=Counter()
    for p in valid[0]:
        for q in valid[1]:
            first=tuple((1<<a)|(1<<b) for a,b in zip(p,q))
            if has_bad(first):continue
            count["pairs"]+=1
            for r in valid[2]:
                count["triples"]+=1
                final=tuple(x|(1<<a) for x,a in zip(first,r))
                if has_bad(final):continue
                count["survivors"]+=1
                singles=tuple(i for i,x in enumerate(final)
                              if x.bit_count()==1)
                if not singles:
                    return count,(final,(p,q,r))
                choices=tuple(tuple(final[i]|(1<<orb)
                             for orb in range(4)
                             if not(final[i]&(1<<orb)))
                             for i in singles)
                for added in product(*choices):
                    count["extensions"]+=1
                    revised=list(final)
                    for v,m in zip(singles,added):revised[v]=m
                    if not has_bad(revised):
                        return count,(tuple(revised),(p,q,r))
    return count,None


def positive_control():
    rec={
        (0,)*6:1<<0,
        (1,)*6:1<<1,
        (2,)*6:1<<2,
    }
    cnt,sat=exact_three_witness_match(
        rec,(1<<0,1<<1,1<<2),0)
    assert sat is not None
    assert all(mask.bit_count()>=2 for mask in sat[0])
    print("POSITIVE_CONTROL_COMPLETE_3WITNESS_SAT PASS",flush=True)


def run():
    positive_control()
    graphs=complete_sevenblock_simple_skeletons()
    all_pairings=tuple(all_matchings())
    assert len(all_pairings)==15
    choices=tuple(p for p in all_pairings
        if all(set(ends)!={0,1} for ends in p))
    assert len(choices)==12
    total=Counter()
    types=Counter()
    index=0
    for E in graphs:
        conn,split,exposed=edge_connectivity_and_cuts(E)
        types[conn]+=1
        if conn!=2:continue  # bridge and 3edge cases proved separately
        isolated=next(v for v in range(7) if exposed[v]==2)
        records,full=exact_right_sixblock_records(E,isolated)
        record_count=Counter()
        for pairing in choices:
            goodbits,badbits=physical_good_bad_bitsets(pairing)
            count,solution=exact_three_witness_match(
                records,goodbits,badbits)
            if solution:
                raise AssertionError(
                    "FULL_GOOD_THREEBIT_7BLOCK_SIMPLE_SAT",
                    index,E,pairing,solution
                )
            record_count.update(count)
            record_count["pairings"]+=1
        assert record_count["pairings"]==12
        total.update(record_count)
        print("SEVENBLOCK_2EDGE_EXACT_UNSAT",{
            "index":index,
            "designated_twoport_block":isolated,
            "right_sixblock_full_local_extensions":full,
            "right_sixblock_orbit_patterns":len(records),
            "twelve_cross_logical_pairings_UNSAT":True,
            "exact_witness_counts":dict(record_count)
        },flush=True)
        index+=1
    assert types==Counter({1:15,2:40,3:4}),types
    expected=Counter({
        "pairings":480,
        "pairs":315782,
        "triples":22063552,
        "survivors":414690,
        "extensions":3812910
    })
    assert total==expected,(total,expected)
    print("ALL_SIZE_SEVEN_FOURPOLE_SIMPLE_ELEVEN_JOIN_NO_EXACTONE",{
        "all_simple_connected_unlabelled_skeletons":59,
        "bridge_3PLUS3_excluded":15,
        "threeedge_prior_exact_UNSAT":4,
        "twoedge_new_exact_UNSAT":40,
        "crosspair_anti_phase_witness_checks":480,
        "full_threebit_GOOD_only_solutions":0,
        "complete_counter_provenance":dict(total),
        "limits":"ONLY 7 fourpoles joined by 11 SIMPLE graph edges"
    },flush=True)
    print("GENERAL_CUBIC_108_STATE_EXACTONE=OPEN")
    print("SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    run()
