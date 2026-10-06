#!/usr/bin/env python3
"""R5 E94: E92 six-state-preserving C4-free 2-switch cube.

E93 says that in the x-neighbour-hole lane a delta parent would have to have
exactly the six E=0 raw states

    TARGET6 = {1,2,4,19,21,22}

and no E=1 state.  E92 gives a 19-check/18-variable C4-free geometry with
those six states plus exactly one extra raw state 8.

E94 exhausts the complete connected component of E92 under one elementary
degree-preserving 2-switch on two cubic variables, subject to:
  * the same check/variable degree sequence,
  * Tanner C4-freeness,
  * preservation of all six TARGET6 states at every step.

Exact result:
  * component size = 64;
  * BFS layer sizes = 1,6,15,20,15,6,1;
  * every one of the 64 states has the exact same raw family
        {1,2,4,8,19,21,22};
  * every C4-free one-switch neighbour preserving TARGET6 stays inside those
    64 states.

Thus the E92 extra state 8 is invariant on this entire target-preserving local
trade component.  This is an exact finite firewall, NOT yet a universal proof:
another disconnected degree-sequence component might still realize exactly
TARGET6.

P_VS_NP remains OPEN.
"""

from collections import Counter, deque
from itertools import combinations

from r5_e92_c4free_conditioned_u24_geometry_counterexample import (
    CLUSTER_CUBICS,
)

TARGET6 = frozenset({1,2,4,19,21,22})
RAW7 = frozenset({1,2,4,8,19,21,22})
X_CHECKS = frozenset({17,18})
PORTS = {0:0,1:1,2:2,17:3}


def canonical(triples):
    return tuple(sorted(tuple(sorted(e)) for e in triples))


def c4free(triples):
    return all(
        len(triples[i] & triples[j]) <= 1
        for i,j in combinations(range(len(triples)),2)
    )


def feasible_mask(triples, mask):
    v=(mask>>4)&1
    required=set()

    for c in range(19):
        b=((mask>>PORTS[c])&1) if c in PORTS else 0
        need=1-b-(1 if (v and c in X_CHECKS) else 0)
        if need not in (0,1):
            return False
        if need:
            required.add(c)

    required=frozenset(required)
    avail=[e for e in triples if e <= required]
    bypoint={c:[] for c in required}
    for e in avail:
        for c in e:
            bypoint[c].append(e)

    memo={}
    def rec(rem):
        if not rem:
            return True
        if rem in memo:
            return memo[rem]
        p=min(
            rem,
            key=lambda z: sum(e <= rem for e in bypoint[z])
        )
        for e in bypoint[p]:
            if e <= rem and rec(rem-e):
                memo[rem]=True
                return True
        memo[rem]=False
        return False

    return rec(required)


def raw_family(triples):
    return frozenset(
        m for m in range(32)
        if feasible_mask(triples,m)
    )


def preserves_target6(triples):
    return all(feasible_mask(triples,m) for m in TARGET6)


def switch_neighbors(triples):
    T=list(triples)
    seen=set()

    for i,j in combinations(range(len(T)),2):
        e1,e2=T[i],T[j]
        for a in e1:
            for b in e2:
                if a==b or b in e1 or a in e2:
                    continue

                n1=frozenset((e1-{a})|{b})
                n2=frozenset((e2-{b})|{a})
                if len(n1)!=3 or len(n2)!=3:
                    continue

                N=T.copy()
                N[i]=n1
                N[j]=n2

                # Check only pairs touched by the switch.
                if len(n1 & n2)>1:
                    continue
                ok=True
                for k,e in enumerate(N):
                    if k in (i,j):
                        continue
                    if len(n1&e)>1 or len(n2&e)>1:
                        ok=False
                        break
                if not ok:
                    continue

                key=canonical(N)
                if key in seen:
                    continue
                seen.add(key)
                yield tuple(frozenset(x) for x in N)


def main():
    start=tuple(frozenset(x) for x in CLUSTER_CUBICS)
    assert c4free(start)
    assert raw_family(start)==RAW7

    q=deque([(start,0)])
    visited={canonical(start)}
    layers=Counter({0:1})
    preserving_edges=0

    while q:
        state,d=q.popleft()

        # Strong invariant on every reached state.
        assert c4free(state)
        assert raw_family(state)==RAW7

        for nb in switch_neighbors(state):
            if not preserves_target6(nb):
                continue

            preserving_edges += 1

            # The crucial firewall: every target-preserving local neighbour
            # still realizes the forbidden E=1 state 8.
            assert feasible_mask(nb,8)

            # In fact the full raw family stays exactly RAW7.
            assert raw_family(nb)==RAW7

            key=canonical(nb)
            if key in visited:
                continue
            visited.add(key)
            layers[d+1]+=1
            q.append((nb,d+1))

    expected=Counter({0:1,1:6,2:15,3:20,4:15,5:6,6:1})
    assert layers==expected
    assert len(visited)==64

    # Undirected directed-edge count; cube Q6 has 64*6 directed edges.
    assert preserving_edges==64*6

    print("R5 E94 six-state-preserving switch cube: PASS")
    print("target-preserving component size=64")
    print("BFS layers=", dict(sorted(layers.items())))
    print("target-preserving directed switches=", preserving_edges)
    print("every component state raw family=", sorted(RAW7))
    print("extra raw state 8 is invariant throughout the entire local trade cube")
    print("scientific ceiling: disconnected degree-sequence components remain open")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
