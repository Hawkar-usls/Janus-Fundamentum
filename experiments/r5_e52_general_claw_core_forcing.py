#!/usr/bin/env python3
"""Exact controls for R5 E52 general claw-family forcing.

This 18-variable square+cubic+linear carrier has at least three induced claws at
every conflict vertex, so E48/E49/E50 do not apply and the pure E51 all-two-claw
terminal is irrelevant.  Nevertheless the all-claw intersection/union rule forces
x_17=0 and x_16=1-x_0 at vertex 0.

The carrier is independently brute-force UNSAT; E52 is used here only to demonstrate
strictly new forcing inside the >=3-claw sector.

P_VS_NP remains OPEN.
"""
from itertools import combinations

ROWS = [
    {0,12,14}, {1,8,15}, {0,2,11}, {1,3,13}, {4,6,8}, {4,5,13},
    {3,6,10}, {2,5,7}, {8,14,17}, {6,7,9}, {2,10,17}, {3,5,11},
    {11,12,15}, {10,12,13}, {4,9,14}, {7,15,16}, {1,9,16}, {0,16,17},
]
N=18


def verify_carrier():
    assert len(ROWS)==N and all(len(r)==3 for r in ROWS)
    deg=[0]*N
    for r in ROWS:
        for v in r: deg[v]+=1
    assert deg==[3]*N
    for i,j in combinations(range(N),2):
        assert len(ROWS[i]&ROWS[j])<=1


def conflict_graph():
    adj=[set() for _ in range(N)]
    for r in ROWS:
        for a,b in combinations(r,2):
            adj[a].add(b); adj[b].add(a)
    assert all(len(a)==6 for a in adj)
    return adj


def claws(v,adj):
    return [set(t) for t in combinations(sorted(adj[v]),3)
            if all(b not in adj[a] for a,b in combinations(t,2))]


def brute_unsat():
    for S in combinations(range(N),N//3):
        S=set(S)
        if all(len(S&r)==1 for r in ROWS):
            return False
    return True


def main():
    verify_carrier()
    adj=conflict_graph()
    C=[claws(v,adj) for v in range(N)]
    counts=[len(c) for c in C]
    assert counts == [3,6,4,5,4,4,6,6,6,4,6,4,6,5,4,6,4,5]
    assert min(counts)>=3

    I=set.intersection(*C[0])
    U=set.union(*C[0])
    Z=adj[0]-U
    assert I=={16}
    assert Z=={17}

    assert brute_unsat()

    print("R5 E52 general claw-core forcing: PASS")
    print("claw_counts=",counts)
    print("at_vertex_0: intersection={16}, outside_union={17}")
    print("therefore x16=1-x0 and x17=0 in every witness")
    print("independent_bruteforce_verdict=UNSAT")


if __name__ == "__main__":
    main()
