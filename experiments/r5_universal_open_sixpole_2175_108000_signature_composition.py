#!/usr/bin/env python3
"""Exact open-sixpole signature search; no unproven universal no-go.

1) ALL 145 three-edge matchings of Petersen graph, with ALL 15 ways of
   pairing the six resulting open ports: 2175 complete finite checks.
2) ALL 3-edge gluings of two frozen sixpoles C6/Petersen:
   choose 3 ports from each and biject them (20*20*6=2400),
   then all 15 pairings of the remaining six ports. Three type
   combinations => 108000 exact relation projections.
Compositions are exactly source-semantic: independent internal proper
3-edge-colourings glue iff joined port colours match. This is NOT a
Polynomial Calculus back-simulation or global algorithm.
"""
from collections import Counter,defaultdict
from itertools import combinations, permutations, product


def petersen_edges():
    result=set()
    def add(u,v):result.add(tuple(sorted((u,v))))
    for i in range(5):
        add(i,(i+1)%5)
        add(i,i+5)
        add(5+i,5+(i+2)%5)
    assert len(result)==15
    return tuple(sorted(result))


PETERSEN=petersen_edges()
REFERENCE=((0,1),(2,3),(5,8))
TARGET=frozenset({(1,0,0),(0,1,0),(0,0,1)})
FULL=frozenset({(0,0,0),(1,0,0),(0,1,0),(0,0,1),(1,1,1)})
ATMOST=frozenset({(0,0,0),(1,0,0),(0,1,0),(0,0,1)})


def all_pairings(items):
    if not items:
        yield ()
        return
    first,*tail=items
    for i,second in enumerate(tail):
        for suffix in all_pairings(tail[:i]+tail[i+1:]):
            yield ((first,second),)+suffix


PAIRINGS=tuple(all_pairings(list(range(6))))
assert len(PAIRINGS)==15


def three_edge_matchings(edges):
    return tuple(group for group in combinations(edges,3)
                 if len({v for edge in group for v in edge})==6)


MATCHINGS=three_edge_matchings(PETERSEN)
assert len(MATCHINGS)==145


def petersen_signature_set(cut):
    assert len(cut)==3 and set(cut).issubset(PETERSEN)
    ports=tuple(v for e in cut for v in e)
    assert len(set(ports))==6
    remainder=tuple(e for e in PETERSEN if e not in cut)
    assert len(remainder)==12
    incident={v:[] for v in range(10)}
    for i,(a,b) in enumerate(remainder):
        incident[a].append(i);incident[b].append(i)
    assert all(len(incident[v])==(2 if v in ports else 3)
               for v in range(10))
    colours=[-1]*len(remainder)
    signatures=set()
    solutions=0
    def dfs(k):
        nonlocal solutions
        if k==len(remainder):
            solutions+=1
            # Colours 0+1+2=3, so the missing third colour is 3-a-b.
            signatures.add(tuple(3-colours[incident[v][0]]
                                   -colours[incident[v][1]] for v in ports))
            return
        a,b=remainder[k]
        for c in (0,1,2):
            if all(colours[j]!=c for v in (a,b)
                   for j in incident[v] if j<k):
                colours[k]=c
                dfs(k+1)
                colours[k]=-1
    dfs(0)
    assert solutions>0
    return frozenset(signatures),solutions


def ring6_signatures():
    S=set()
    count=0
    for edges in product((0,1,2),repeat=6):
        if any(edges[i]==edges[(i-1)%6] for i in range(6)):
            continue
        count+=1
        S.add(tuple(3-edges[(i-1)%6]-edges[i] for i in range(6)))
    assert count==66 and len(S)==63
    return frozenset(S)


def truth_relation(signatures,pairs):
    return frozenset(tuple(int(colors[a]==colors[b]) for a,b in pairs)
                     for colors in signatures)


def audit_petersen():
    counts=Counter()
    for cut in MATCHINGS:
        S,_=petersen_signature_set(cut)
        for pairs in PAIRINGS:
            R=truth_relation(S,pairs)
            assert R in (ATMOST,FULL), (cut,pairs,R)
            assert R!=TARGET
            counts["AT_MOST_ONE" if R==ATMOST else "FULL_FIVE"]+=1
    assert counts=={"AT_MOST_ONE":145,"FULL_FIVE":2030},counts
    print("PETERSEN_145x15: all 2175 complete; at-most-one=145,")
    print("  full-five=2030; EXPOSED_EXACT_ONE=0 PASS")
    return petersen_signature_set(REFERENCE)[0]


def compose_exact(SA,SB,linkA,linkB):
    restA=tuple(i for i in range(6) if i not in linkA)
    restB=tuple(i for i in range(6) if i not in linkB)
    reverse=defaultdict(set)
    for colors in SA:
        reverse[tuple(colors[i] for i in linkA)].add(
            tuple(colors[i] for i in restA))
    out=set()
    for colors in SB:
        for a in reverse.get(tuple(colors[i] for i in linkB),()):
            out.add(a+tuple(colors[i] for i in restB))
    return frozenset(out)


def audit_three_port_gluings(label,SA,SB):
    counts=Counter()
    n=0
    for left in combinations(range(6),3):
        for right_subset in combinations(range(6),3):
            for right in permutations(right_subset):
                S=compose_exact(SA,SB,left,right)
                if not S:
                    counts["UNCOLOURABLE"]+=1
                    continue
                n+=1
                for pairs in PAIRINGS:
                    T=truth_relation(S,pairs)
                    assert T!=TARGET, (label,left,right,pairs)
                    counts[tuple(sorted(T))]+=1
    assert n==2400,n
    assert sum(v for k,v in counts.items()
               if k!="UNCOLOURABLE")==36000
    print(f"GLUE3_{label}: {n} exact three-wire joins x 15 pairings;")
    print("  NO_EXACT_ONE PASS")
    return counts


def main():
    P=audit_petersen()
    C=ring6_signatures()
    stats={}
    for name,A,B in (("C6_C6",C,C),("C6_PETERSEN",C,P),
                     ("PETERSEN_PETERSEN",P,P)):
        stats[name]=audit_three_port_gluings(name,A,B)
    assert len(stats["C6_C6"])==3,stats["C6_C6"]
    assert stats["C6_PETERSEN"]=={tuple(sorted(FULL)):36000}
    assert stats["PETERSEN_PETERSEN"]=={tuple(sorted(FULL)):36000}
    assert stats["C6_C6"][tuple(sorted(FULL))]==35712
    print("TOTAL: 7200 joins, 108000 decoded boundary pair relations.")
    print("FINITE_SEARCH_EXACT_ONE = NOT_FOUND; not a general impossibility theorem")
    print("UNBOUNDED_NATIVE_GF3_PC_DEGREE=OPEN; SolveLinearCubicXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
