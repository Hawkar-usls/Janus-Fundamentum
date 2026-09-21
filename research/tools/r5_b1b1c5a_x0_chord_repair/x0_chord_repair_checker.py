#!/usr/bin/env python3
"""C5A finite checker: semantics-neutral X0-X0 chord repair.

Builds the frozen one-clause inverse-Golovach role instance from C4,
varies only the six possible edges among four differently precolored X0
anchors, and checks induced P7s.

This is a proof-replay checker for the frozen finite role instance, not a
coloring algorithm.
"""
from itertools import combinations

ANCHORS=("x0c1","x0c2","x0c3","x0c4")
ANCHOR_PAIRS=tuple(combinations(ANCHORS,2))
UNIVERSAL_P7=("b1","z2","b2","z3","x0c4","zp3","bp2")

def build(anchor_edges):
    V=set()
    E=set()
    def add(*vs):
        V.update(vs)
    def edge(a,b):
        E.add(tuple(sorted((a,b))))

    add("s1","s2","p","m","n0","sel1","sel2","w")
    for a,b in (
        ("s1","s2"),("s1","p"),("p","m"),("m","n0"),("n0","s2"),
        ("s2","sel1"),("s2","sel2"),("sel1","w"),("sel2","w"),
    ):
        edge(a,b)

    add(*ANCHORS)
    for a,b in anchor_edges:
        edge(a,b)

    variables=("x1","x2","x3")
    bverts=("b1","b2","bp1","bp2")
    add(*variables,*bverts)

    # permuted variable list {2,3}: source edge to s1, X0 anchor color 4
    for x in variables:
        edge(x,"s1")
        edge(x,"x0c4")
        for b in bverts:
            edge(x,b)

    # permuted b-list {1,4}: source edge to s2, X0 anchor color 3
    for b in bverts:
        edge(b,"s2")
        edge(b,"x0c3")

    zverts=("z1","z2","z3","zp1","zp2","zp3")
    add(*zverts)

    # D_C copied from the two clause P5s and occurrence edges.
    D={
        "z1":("b1","x1"),
        "z2":("b1","b2","x2"),
        "z3":("b2","x3"),
        "zp1":("bp1","x1"),
        "zp2":("bp1","bp2","x2"),
        "zp3":("bp2","x3"),
    }

    # Permuted selector/base lists M_h.
    M={
        "z1":{3,4},
        "z2":{1,3,4},
        "z3":{1,3},
        "zp1":{2,4},
        "zp2":{1,2,4},
        "zp3":{1,2},
    }

    for z,neighbors in D.items():
        for u in neighbors:
            edge(z,u)
        for color in {1,2,3,4}-M[z]:
            edge(z,f"x0c{color}")

    return V,E

def adjacent(E,a,b):
    return tuple(sorted((a,b))) in E

def is_induced_path(E,path):
    if len(set(path)) != len(path):
        return False
    for i in range(len(path)-1):
        if not adjacent(E,path[i],path[i+1]):
            return False
    for i in range(len(path)):
        for j in range(i+2,len(path)):
            if adjacent(E,path[i],path[j]):
                return False
    return True

def main():
    receipts=[]
    for mask in range(1<<len(ANCHOR_PAIRS)):
        chosen=[
            ANCHOR_PAIRS[i]
            for i in range(len(ANCHOR_PAIRS))
            if (mask>>i)&1
        ]
        _,E=build(chosen)
        universal=is_induced_path(E,UNIVERSAL_P7)
        receipts.append((mask,tuple(chosen),universal))
        assert universal, (mask,chosen)

    # Complete cross-color closure is mask 63 and still fails.
    _,Efull=build(ANCHOR_PAIRS)
    assert is_induced_path(Efull,UNIVERSAL_P7)

    print({
        "status":"PASS_FINITE_REPLAY",
        "legal_X0_internal_graphs_checked":len(receipts),
        "all_64_fail_P7":all(r[2] for r in receipts),
        "universal_anchor_internal_edge_independent_P7":UNIVERSAL_P7,
        "complete_K4_X0_closure_still_fails":True,
    })

if __name__=="__main__":
    main()
