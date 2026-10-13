#!/usr/bin/env python3
"""The SIX published nontrivial 20-vertex snarks (Forbes) -> 1800 exact 6-pole gates.

Independent published source:
Anthony D. Forbes, "Snark Designs", arXiv:1207.3032 v2,
PDF pp.14-15, section 4, edge sets S1..S6:
https://oro.open.ac.uk/56584/1/1207.3032.pdf

The 1-based published edge data are transcribed directly below.
For EACH S_i verify source simplicity, every degree3, and full native
uncolourability (complete exact DFS), then for each of its 20 induced
claws delete centre + 3 leaves, enumerate ALL proper full internal
3-edge-colourings, and classify all 15 external two-port pairings.
No bit-only gluing approximation: state is a full six-colour tuple.

All such deletions have 16 interior vertices /21 edges and open six
terminals. Each EXPOSED ExactOne gate is explicitly reported with
source graph, claw centre, pairing, ports and actual 100/010/001
six-colour witnesses for independent replay. Also check the physical
STAR6 forbidden-zero condition for each *natural* claw pairing.

This does NOT cover all 20-vertex cubic uncolourable graphs, only the
six NONTRIVIAL snarks in the precise cited paper.
"""
from collections import Counter
import re
from r5_universal_j5_20vertex_snark_star_deletion_sixpole import (
    enumerate_edge_colours,induced_claw_sixpole,ALL_PAIRS,
    bit_relation,BITS3,
)

# Edge sets S1...S6 from Forbes, 1-based endpoints in print.
SOURCE={
"S1": """
1-2 2-3 2-4 5-6 6-7 6-8 9-10 10-11 10-12
13-14 14-15 14-16 17-18 18-20 18-19 1-17 13-17
5-9 9-13 1-5 3-20 16-19 4-7 8-11 12-15 3-8
7-12 11-16 15-20 4-19
""",
"S2": """
1-2 1-3 1-5 2-4 2-11 3-10 3-18 4-6 4-8
5-7 5-8 6-7 6-14 7-9 8-10 9-10 9-12 11-12 11-17
12-13 13-16 13-19 14-15 14-19 15-16 15-17 16-18
17-20 18-20 19-20
""",
"S3": """
1-2 1-4 1-7 2-3 2-8 3-10 3-17 4-9 4-10
5-6 5-9 5-13 6-7 6-11 7-19 8-9 8-12 10-12 11-12
11-14 13-16 13-18 14-15 14-18 15-16 15-17 16-19
17-20 18-20 19-20
""",
"S4": """
1-2 1-3 1-7 2-4 2-8 3-9 3-10 4-5 4-17
5-6 5-9 6-7 6-11 7-19 8-9 8-12 10-12 10-13
11-12 11-14 13-16 13-18 14-15 14-18 15-16 15-17
16-19 17-20 18-20 19-20
""",
"S5": """
1-2 1-4 1-7 2-3 2-8 3-5 3-10 4-9 4-10
5-6 5-9 6-7 6-11 7-19 8-9 8-12 10-17 11-12
11-14 12-13 13-16 13-18 14-15 14-18 15-16 15-17
16-19 17-20 18-20 19-20
""",
"S6": """
1-2 1-4 1-7 2-3 2-8 3-5 3-10 4-9 4-17
5-6 5-9 6-7 6-11 7-19 8-9 8-12 10-12 10-13
11-12 11-14 13-16 13-18 14-15 14-18 15-16 15-17
16-19 17-20 18-20 19-20
""",
}


def paper_graph(s):
    pairs=re.findall(r"(\d+)-(\d+)",SOURCE[s])
    G=tuple(sorted(tuple(sorted((int(a)-1,int(b)-1))) for a,b in pairs))
    assert len(G)==30 and len(set(G))==30,(s,len(G))
    assert all(a!=b and 0<=a<b<20 for a,b in G)
    assert all(sum(v in e for e in G)==3 for v in range(20))
    return G


def girth(G):
    neighbours=[set() for _ in range(20)]
    for u,v in G:
        neighbours[u].add(v)
        neighbours[v].add(u)
    best=100
    for root in range(20):
        frontier=[(root,-1,0)]
        visited={root:0}
        for u,parent,dist in frontier:
            for v in neighbours[u]:
                if v==parent:
                    continue
                if v in visited:
                    best=min(best,dist+visited[v]+1)
                else:
                    visited[v]=dist+1
                    frontier.append((v,u,dist+1))
    return best


def check_source_and_claws(s):
    H=paper_graph(s)
    assert girth(H)>=5,("wrong paper transcription, girth < 5",s,girth(H))
    count,signatures=enumerate_edge_colours(tuple(range(20)),H)
    assert count==0 and not signatures,("source not snark",s,count)
    c=Counter()
    witness=None
    relations=Counter()
    for centre in range(20):
        V,E,ports,natural=induced_claw_sixpole(H,centre)
        assert len(V)==16 and len(E)==21 and len(ports)==6
        n,physical=enumerate_edge_colours(V,E,ports)
        assert n>0 and physical,("deletion uncolourable",s,centre)
        natural_bits=bit_relation(physical,natural)
        assert (0,0,0) not in natural_bits,(
            "unexpected STAR closure SAT contradicts published snark",s,centre)
        c["claw_centres"]+=1
        c["open_claw_inner_colourings"]+=n
        c["open_claw_boundary_tuples"]+=len(physical)
        for pairs in ALL_PAIRS:
            b=bit_relation(physical,pairs)
            c["pairings"]+=1
            relations[tuple(sorted(b))]+=1
            if b==BITS3:
                c["EXACT_ONE"]+=1
                explicit={q:next(p for p in physical if tuple(
                  int(p[a]==p[d]) for a,d in pairs)==q) for q in BITS3}
                witness=(s,centre,ports,pairs,explicit)
                print("FOUND_EXPOSED_ONEHOT_S16_PHYSICAL",witness,flush=True)
        print("S20_CLAW",s,centre,{"full_internal_colours":n,
          "full_boundary_tuples":len(physical),
          "natural_paired_bits":sorted(natural_bits)},flush=True)
    assert c["claw_centres"]==20 and c["pairings"]==300
    print("S20_SOURCE_SUMMARY",s,{"girth":girth(H),**c},flush=True)
    print("S20_RELATION_COUNTS",s,{str(k):v for k,v in relations.items()},flush=True)
    return c,witness


def main():
    assert set(SOURCE)=={"S1","S2","S3","S4","S5","S6"}
    total=Counter()
    witnesses=[]
    for name in SOURCE:
        c,w=check_source_and_claws(name)
        total.update(c)
        if w:
            witnesses.append(w)
    assert total["claw_centres"]==120
    assert total["pairings"]==1800
    print("PAPER_SIX_20_SNARKS_120_CLAWS",dict(total),flush=True)
    print("PAPER_SIX_EXACTONE_WITNESSES",witnesses,flush=True)
    if witnesses:
        print("POSITIVE_GADGET_CANDIDATE!  Requires independent original")
        print(" colour witness, real closure UNCOLOURABILITY certificate,")
        print(" and uniform GF3 PC back-simulation.",flush=True)
    else:
        print("NO_EXACT_ONE_WITH_STAR_DELETION_FROM_THE_SIX")
        print(" PUBLISHED_NONTRIVIAL_20_VERTEX_SNARKS")
        print(" DOES NOT EXCLUDE ALL 20-VERTEX NON-3-EDGE-COLOURABLE GRAPHS")
    print("ALLSIZES_UNRESTRICTED_GADGET=OPEN")
    print("GLOBAL_PC_BACKSIM=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    main()
