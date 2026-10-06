#!/usr/bin/env python3
"""R5 E93: parent-delta loop reduction for p=1,h=1 with hole at x-neighbour.

Boundary order:
    A,B,C,E,V
where E is the conditioned check-side port on a check incident to the special
boundary variable x, and V is x's variable-side boundary port.

Assume E=0 conditioning gives the p=1 U2,4-twist family:
    {1,2,4,19,21,22} in raw five-bit coordinates.

Universal exact semantics:
  * E=1,V=1 is impossible because check E would receive both external 1 and x=1.
  * E85 signed balance with a=3t+1 implies for E=1,V=0 that the number k of
    selected A/B/C check ports satisfies k=0 mod 3, hence only k=0 or 3:
        raw mask 8 or raw mask 15.

If the raw parent is delta, E83 says twisting V gives an ordinary matroid M.
Its E=0 deletion is U2,4, so E is not a coloop and rank(M)=2.

  * raw 15 twists to all five elements -> not a rank-2 basis.
  * raw 8 twists to the basis {E,V}.  With no other semantically possible
    E-containing bases, U2,4 plus {E,V} violates basis exchange.

Therefore a delta parent can have NO E=1 feasible state. E must be a loop in
the canonical matroid. The only possible raw delta parent is the six-state
E=0 family itself.

E92 is the exact one-state near miss: it adds raw state 8 and therefore fails
delta exchange.

P_VS_NP remains OPEN.
"""

from itertools import combinations

E_ZERO_RAW=frozenset({1,2,4,19,21,22})
U24=frozenset(
    (1<<i)|(1<<j)
    for i,j in combinations((0,1,2,4),2)
)

def basis_exchange_failure(B,n=5):
    B=set(B)
    sizes={x.bit_count() for x in B}
    if len(sizes)!=1:
        return ("not_equicardinal",tuple(sorted(sizes)))
    for X in B:
        for Y in B:
            for e in range(n):
                if not ((X>>e)&1) or ((Y>>e)&1):
                    continue
                if not any(
                    ((Y>>f)&1) and not ((X>>f)&1)
                    and (X^(1<<e)^(1<<f)) in B
                    for f in range(n)
                ):
                    return X,Y,e
    return None

def possible_e1_raw_masks():
    out=[]
    # E bit is 3. V bit is 4.
    for mask in range(32):
        if not ((mask>>3)&1):
            continue
        v=(mask>>4)&1
        k=sum((mask>>i)&1 for i in (0,1,2))

        # E=1,V=1 is locally impossible at the check incident to x.
        if v:
            continue

        # signed invariant:
        # phi = -(1+k) == -(3t+1) == -1 mod 3
        if k % 3:
            continue
        out.append(mask)
    return frozenset(out)

def main():
    assert possible_e1_raw_masks()==frozenset({8,15})

    canonical_e0=frozenset(x^(1<<4) for x in E_ZERO_RAW)
    assert canonical_e0==U24
    assert {x.bit_count() for x in canonical_e0}=={2}
    assert basis_exchange_failure(canonical_e0) is None

    # raw15 -> canonical31, cardinality five, impossible in rank 2.
    assert (15^(1<<4))==31
    assert (15^(1<<4)).bit_count()==5

    # raw8 -> canonical basis {E,V}.
    extra=8^(1<<4)
    assert extra==24 and extra.bit_count()==2
    one_extra=canonical_e0|{extra}
    fail=basis_exchange_failure(one_extra)
    assert fail is not None

    # No E=1 states => E is a loop; U2,4 plus loop is a valid matroid.
    loop_parent=canonical_e0
    assert basis_exchange_failure(loop_parent) is None

    print("R5 E93 parent-delta x-neighbour-hole loop reduction: PASS")
    print("semantically possible E=1 raw states = {8,15}")
    print("raw15 forbidden by rank-2 equicardinality")
    print("raw8 forbidden by matroid basis exchange when it is the sole E-basis")
    print("therefore any delta parent must make E a loop")
    print("next target: realize or exclude the exact six-state raw loop family in C4-free cubic geometry")
    print("P_VS_NP remains OPEN")

if __name__=="__main__":
    main()
