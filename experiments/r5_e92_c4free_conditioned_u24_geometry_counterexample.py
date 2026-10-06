#!/usr/bin/env python3
"""R5 E92: C4-free conditioned-U2,4 geometry counterexample.

This is an explicit full square-cubic-linear source:
  24 ExactOne checks
  24 cubic variables
  every row/column degree = 3
  Tanner graph connected
  Tanner graph C4-free.

Inside it, take checks 0..18 and variables 0..17 as a cluster.
Boundary:
  check-side free ports at checks 0,1,2,17;
  variable-side free port on variable 17 (x);
  conditioning check-side port 17 to 0 gives a four-port exact boundary
  relation equal to the p=1 twist of U_{2,4}.

The raw five-port exact boundary family is
    {1,2,4,8,19,21,22}
and FAILS symmetric exchange. Thus this is NOT a nonbinary delta parent.

Scientific meaning:
  C4-free source geometry alone does not exclude conditioned U2,4.
  Any universal binary theorem must use the parent's delta-matroid axiom.

P_VS_NP remains OPEN.
"""

from itertools import combinations

# 17 cubic cluster variables, listed by their three incident checks.
CLUSTER_CUBICS = (
    (0,2,18),
    (0,6,13),
    (1,9,14),
    (1,10,16),
    (2,3,4),
    (3,5,12),
    (3,9,15),
    (4,7,11),
    (4,8,14),
    (5,6,7),
    (5,11,17),
    (6,10,15),
    (7,12,18),
    (8,9,10),
    (8,13,16),
    (11,12,13),
    (14,15,16),
)

# Variable 17 is the special degree-2-in-cluster variable x.
# Its third edge goes to outside check 19.
X_CHECKS = (17,18,19)

# Complete the cluster to a 24x24 cubic C4-free source.
# Outside vars W0..W5 are variable indices 18..23.
# W0,W1,W2,W3 connect back to cluster checks 0,1,2,17.
OUTSIDE_INTERNAL_CHECK = (0,1,2,17)
OUTSIDE_EDGES = (
    (0,4),(0,5),
    (1,2),(1,3),(1,4),
    (2,0),(2,1),(2,4),
    (3,1),(3,2),(3,5),
    (4,0),(4,3),(4,5),
)

EXPECTED_RAW = frozenset({1,2,4,8,19,21,22})
EXPECTED_CONDITIONED = frozenset({1,2,4,11,13,14})
EXPECTED_U24 = frozenset(
    (1<<i) | (1<<j)
    for i,j in combinations(range(4),2)
)

def full_source_variables():
    out=[set(t) for t in CLUSTER_CUBICS]
    out.append(set(X_CHECKS))
    for j in range(6):
        ns=set()
        if j < 4:
            ns.add(OUTSIDE_INTERNAL_CHECK[j])
        for oi,wj in OUTSIDE_EDGES:
            if wj==j:
                ns.add(19+oi)
        out.append(ns)
    return tuple(frozenset(x) for x in out)

def verify_full_source():
    V=full_source_variables()
    assert len(V)==24
    assert all(len(x)==3 for x in V)

    check_degrees=[
        sum(i in nbrs for nbrs in V)
        for i in range(24)
    ]
    assert check_degrees == [3]*24

    # Two variables sharing two checks is exactly a Tanner C4.
    for i,j in combinations(range(24),2):
        assert len(V[i] & V[j]) <= 1

    # Connected bipartite Tanner graph.
    adj={}
    for i in range(24):
        adj[("c",i)]=[]
        adj[("v",i)]=[]
    for j,nbrs in enumerate(V):
        for i in nbrs:
            adj[("v",j)].append(("c",i))
            adj[("c",i)].append(("v",j))

    seen=set()
    stack=[("c",0)]
    while stack:
        u=stack.pop()
        if u in seen:
            continue
        seen.add(u)
        stack.extend(adj[u])
    assert len(seen)==48
    return V

def raw_boundary_family():
    # Cluster variables 0..16 are cubic and variable 17 is x.
    active=[frozenset(t) for t in CLUSTER_CUBICS]
    active.append(frozenset({17,18}))  # only internal incidences of x

    # Boundary check bits in order A,B,C,E at checks 0,1,2,17.
    bpos={0:0,1:1,2:2,17:3}
    family=set()

    # Enumerate all 2^18 internal variable assignments.
    for mask in range(1<<18):
        sums=[0]*19
        for j,nbrs in enumerate(active):
            if (mask>>j)&1:
                for c in nbrs:
                    sums[c]+=1

        bits=[0,0,0,0]
        ok=True
        for c in range(19):
            if c in bpos:
                if sums[c] > 1:
                    ok=False
                    break
                bits[bpos[c]] = 1-sums[c]
            elif sums[c] != 1:
                ok=False
                break
        if not ok:
            continue

        # Equality makes the variable-side boundary bit equal x.
        v=(mask>>17)&1
        f=bits[0] | (bits[1]<<1) | (bits[2]<<2) | (bits[3]<<3) | (v<<4)
        family.add(f)

    return frozenset(family)

def condition_e_zero(raw):
    out=set()
    for f in raw:
        if (f>>3)&1:
            continue
        # project bit3 away; old bit4 becomes new bit3.
        out.add((f & 0b111) | ((f>>4)<<3))
    return frozenset(out)

def symmetric_exchange_failure(F,n):
    F=set(F)
    for X in F:
        for Y in F:
            diff=X^Y
            for u in range(n):
                if not ((diff>>u)&1):
                    continue
                ok=False
                for v in range(n):
                    if not ((diff>>v)&1):
                        continue
                    Z=X^(1<<u)
                    if v!=u:
                        Z^=(1<<v)
                    if Z in F:
                        ok=True
                        break
                if not ok:
                    return X,Y,u
    return None

def main():
    verify_full_source()

    raw=raw_boundary_family()
    assert raw == EXPECTED_RAW

    conditioned=condition_e_zero(raw)
    assert conditioned == EXPECTED_CONDITIONED
    assert symmetric_exchange_failure(conditioned,4) is None

    # Canonical twist by the surviving variable-side coordinate (bit3)
    # gives every two-subset of a four-element ground set: U_{2,4}.
    canonical=frozenset(x ^ (1<<3) for x in conditioned)
    assert canonical == EXPECTED_U24

    fail=symmetric_exchange_failure(raw,5)
    assert fail == (19,8,3)

    # Frozen v=1 near classes exhibit sigma=4, beyond E90/E91 low-sigma lanes.
    qab={
        frozenset({2,3,4}),frozenset({5,6,7}),frozenset({8,9,10}),
        frozenset({11,12,13}),frozenset({14,15,16})
    }
    qac={
        frozenset({1,10,16}),frozenset({3,9,15}),frozenset({4,8,14}),
        frozenset({5,6,7}),frozenset({11,12,13})
    }
    qbc={
        frozenset({0,6,13}),frozenset({3,5,12}),frozenset({4,7,11}),
        frozenset({8,9,10}),frozenset({14,15,16})
    }
    sigma=15-len(qab|qac|qbc)
    assert sigma==4

    print("R5 E92 C4-free conditioned-U2,4 geometry counterexample: PASS")
    print("full source: 24x24 square/cubic/connected/C4-free")
    print("raw 5-port family:", sorted(raw))
    print("condition E=0 ->", sorted(conditioned))
    print("canonical conditioned matroid = U2,4")
    print("raw parent delta failure:", fail)
    print("v=1 shared-savings sigma=4")
    print("GEOMETRY_ONLY_CONDITIONED_U24_EXCLUSION = FALSIFIED")
    print("parent-delta obstruction remains the valid frontier")
    print("P_VS_NP remains OPEN")

if __name__=="__main__":
    main()
