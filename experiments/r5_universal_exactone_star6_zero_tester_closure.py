#!/usr/bin/env python3
"""Universal physical 000 tester (4 internal vertex cubic STAR sixpole).

A 6pole M with three given couples has t_i=[same terminal colour].
The STAR test multipole S consists of a centre degree3 vertex, its
three degree3 leaves, each with two exposed terminals designated as
couple i. In a proper colouring, each pair has two DISTINCT colours
and the three internal centre-to-leaf edge colours are all distinct.

Claim 1 (all input, symbolic): The set Col(S) of its full SIX labelled
physical port colours is EXACTLY the set of 48 admissible cubic colour-
parity states with all three couple bits zero. This is important:
S recognizes *every physically possible* 000 boundary state, not
merely an arbitrary proper subset.

Claim 2 (all M): Gluing all six terminals of M to corresponding S
terminals by six fresh full edges produces a 3-edge-colourable cubic
(closed) graph if and only if M has SOME original colouring with
t0=t1=t2=0. Proof: physical boundary colours must agree on each
of six joined edges. Every allowed 000 physical state has an exact
S extension, and no other S state is permitted.

Claim 3: With the three single-pair heterochromatic closures,
M is an EXPOSED ExactOne 6pole iff the STAR closure is NON-3-
EDGE-COLOURABLE (and each closure is heterochromatic and colourable).
If the M internal graph is simple connected and each couple
occurs at two distinct M vertices, the STAR closure is a SIMPLE
cubic graph, giving a completely legal Holyer native SCL.

All general claims are literal combinatorial theorems; this script
checks exact 48-state equality and finite n<=12 instances independently.
"""
from collections import Counter
from itertools import permutations,product
import shutil,subprocess
from r5_universal_exposed_exactone_nauty_n8_all_graphs import (
    graph6_edges,enumerate_port_signatures,PAIRS,
)
from r5_universal_exactone_heterochromatic_triple_closure import (
    evaluate_boundary,
)

COLOURS=tuple(range(3))
ONEHOT={(1,0,0),(0,1,0),(0,0,1)}


def all_even_states():
    return frozenset(a for a in product(COLOURS,repeat=6)
                     if all(a.count(c)%2==0 for c in COLOURS))


def bit(s,pairs):
    return tuple(int(s[i]==s[j]) for i,j in pairs)


def star_physical_states():
    S=set()
    # Three centre-edge colours are exactly a permutation of 012.
    # Each leaf's two ports use the other two colours.
    for internal in permutations(COLOURS):
        choices=[]
        for c in internal:
            other=tuple(x for x in COLOURS if x!=c)
            choices.append((other,other[::-1]))
        for ordered_pairs in product(*choices):
            # Use standard port labels i and i+3.
            signature=[None]*6
            for i,(a,b) in enumerate(ordered_pairs):
                signature[i]=a
                signature[i+3]=b
            S.add(tuple(signature))
    assert len(S)==48
    return frozenset(S)


def check_star_tester():
    even=all_even_states()
    assert len(even)==183 # not all 729 tuples parity admissible
    pairs=((0,3),(1,4),(2,5))
    zero=frozenset(s for s in even if bit(s,pairs)==(0,0,0))
    star=star_physical_states()
    assert len(zero)==48 and zero==star
    assert all(bit(s,pairs)==(0,0,0) for s in star)
    assert all(s in even for s in star)
    print("STAR6_EXACT_000: all 48 physically admissible bit000")
    print("  six-colour boundary states realized EXACTLY PASS")


def check_sample_sources():
    # Independent M-S coloured-state conjunction condition is
    # tested on all n=4,6,8,10,12 graph6 interiors and all 15 port pairings.
    # Translate arbitrary connector ordering to the star standard:
    # star boundary signature indexed by (pair0-left, pair1-left,
    # pair2-left, pair0-right, pair1-right, pair2-right).
    STAR=star_physical_states()
    geng=shutil.which("nauty-geng") or shutil.which("geng")
    if geng is None:
        raise RuntimeError("nauty missing: finite controls UNKNOWN")
    counts=Counter()
    for n in (4,6,8,10,12):
        m=(3*n-6)//2
        cmd=[geng,"-c","-q","-d1","-D3",str(n),str(m)]
        P=subprocess.run(cmd,capture_output=True,text=True,check=True)
        for line in P.stdout.splitlines():
            if not line or line.startswith(">>"):
                continue
            nn,edges=graph6_edges(line)
            assert nn==n
            _,color_states,_=enumerate_port_signatures(n,edges)
            counts["interiors"]+=1
            if not color_states:
                continue
            for pairs in PAIRS:
                counts["interfaces"]+=1
                R,triples,nozero=evaluate_boundary(color_states,pairs)
                permuted_states=frozenset(
                    tuple(x[pairs[i][side]]
                          for side in (0,1) for i in range(3))
                    for x in color_states)
                # Physical gluing means exact tuple membership in STAR.
                gluable=bool(permuted_states & STAR)
                assert gluable==((0,0,0) in R),(
                    "failed tester universal semantic",n,edges,pairs)
                # MATCH3 tester comprises 3 free edges, one per pair:
                # its full boundary has each couple colours equal.
                matching_closure_colourable=((1,1,1) in R)
                singleton_closure_colourable=tuple(
                    any(b[i] for b in R) for i in range(3))
                # Five graph operations: STAR6 closure UNSAT,
                # MATCH3 direct-pair closure UNSAT, 3 single-pair
                # closures SAT. Cubic parity disallows exactly 2 ones.
                all_five=((not gluable) and
                          (not matching_closure_colourable) and
                          all(singleton_closure_colourable))
                assert all_five == (R==ONEHOT),(
                    "five-closure theorem contradicted",n,pairs,R)
                if triples:
                    counts["triple_heterochromatic"]+=1
                    assert gluable
            counts["colorable_interiors"]+=1
        print("STAR6_TESTED",n,dict(counts),flush=True)
    assert counts["interfaces"]==94065
    assert counts["triple_heterochromatic"]==44
    print("ALL_STAR6_FINITE_CONTROLS_PASS",dict(counts))
    print("FIVE_CLOSURES: STAR6 and MATCH3 UNSAT + EACH SINGLE PAIR SAT")
    print("THEOREM: EXPOSED_ONEHOT iff 3 HETEROCHROMATIC")
    print("  SINGLE-PAIR CLOSURES AND STAR6_CLOSED_GRAPH_UNCOLOURABLE")
    print("UNBOUNDED_NATIVE_GF3_PC_DEGREE=OPEN; P_VS_NP=OPEN")


if __name__=="__main__":
    check_star_tester()
    check_sample_sources()
