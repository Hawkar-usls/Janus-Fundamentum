#!/usr/bin/env python3
"""Independent finite role-graph checker for
R5_B1B1A_SUBDIVIDED_WALL_SOURCE_EMBEDDING_GATE_V1.

This checker validates only the fixed P7 role-pattern obligations after
the arbitrary-N false-twin reduction. It does not check mim-width or
the CSZ source-lineage proof.
"""
from itertools import permutations, combinations

V = ("A","B","r","s1","s2","p","m","n0","alpha","w")
E = {
    frozenset(x) for x in [
        ("A","B"),("A","r"),("B","r"),
        ("A","s1"),("B","s1"),
        ("r","s2"),("r","m"),
        ("s1","s2"),("s1","p"),
        ("s2","n0"),("s2","alpha"),
        ("p","m"),("m","n0"),("alpha","w"),
    ]
}
D = {"A","B","r"}

def adjacent(a,b):
    return frozenset((a,b)) in E

def induced_path(seq):
    if len(set(seq)) != len(seq):
        return False
    for i in range(len(seq)-1):
        if not adjacent(seq[i],seq[i+1]):
            return False
    for i in range(len(seq)):
        for j in range(i+2,len(seq)):
            if adjacent(seq[i],seq[j]):
                return False
    return True

def canonical(seq):
    t=tuple(seq)
    r=tuple(reversed(t))
    return min(t,r)

def all_paths(k):
    out=set()
    for seq in permutations(V,k):
        if induced_path(seq):
            out.add(canonical(seq))
    return sorted(out)

p7=all_paths(7)
p6=all_paths(6)
p5=all_paths(5)

expected_p6 = sorted([
    canonical(("p","m","n0","s2","alpha","w")),
    canonical(("p","m","r","s2","alpha","w")),
    canonical(("m","p","s1","s2","alpha","w")),
])

assert p7 == [], p7
assert p6 == expected_p6, (p6, expected_p6)
assert all(not ({path[0],path[-1]} <= D) for path in p5), p5
assert all(path[0] not in D and path[-1] not in D for path in p6), p6

print({
    "status":"PASS",
    "role_vertex_count":len(V),
    "induced_P7_count":len(p7),
    "induced_P6_patterns":p6,
    "induced_P5_count":len(p5),
    "P6_endpoints_outside_D":True,
    "P5_no_both_endpoints_in_D":True,
})
