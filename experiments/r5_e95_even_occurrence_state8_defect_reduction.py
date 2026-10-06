#!/usr/bin/env python3
"""R5 E95: universal even-occurrence candidate for the forbidden raw state 8.

Assume the E93 x-neighbour-hole parent has the six required raw states

    TARGET6 = {1,2,4,19,21,22}

with boundary order A,B,C,E,V and E=0 in all six states.

Choose one internal exact-cover witness for each of the six states.  For every
active variable j let w_j be the number of chosen witnesses containing j, and
set

    e_j = 1  iff  w_j is even.

Universal parity calculation:
  * at A,B,C: internal degree 2, internally covered in exactly 3/6 states,
    hence the e-sum is odd and therefore exactly 1;
  * at E: its two internal neighbours are x and y.  x is selected in exactly
    the three V=1 states and y in exactly the three V=0 states, so e_x=e_y=0;
  * at every ordinary check: internal degree 3 and it is covered in all six
    target states, so the e-sum is odd, hence either 1 or 3;
  * x has odd occurrence count 3, so the variable-side boundary value is V=0.

Therefore if no ordinary check has e-sum=3, e is an exact witness for raw
state 8 (A=B=C=0,E=1,V=0), contradicting the E93 delta-parent requirement.

Any six-state parent avoiding raw8 must therefore have a triple-even defect:
an ordinary check whose three incident variables all have even w_j.

At such a check the three membership supports partition the six target states,
so the sorted occurrence-size pattern is necessarily one of

    (0,0,6), (0,2,4), (2,2,2).

The checker replays the theorem on E92.  Its chosen TARGET6 witnesses have no
defect, and the even-occurrence variables are exactly an exact cover for the
extra raw state 8.

P_VS_NP remains OPEN.
"""

from itertools import combinations

from r5_e92_c4free_conditioned_u24_geometry_counterexample import (
    CLUSTER_CUBICS,
)

TARGET6=frozenset({1,2,4,19,21,22})
X_CHECKS=frozenset({17,18})
PORTS={0:0,1:1,2:2,17:3}


def cover_for_mask(triples, mask):
    v=(mask>>4)&1
    required=set()

    for c in range(19):
        b=((mask>>PORTS[c])&1) if c in PORTS else 0
        need=1-b-(1 if (v and c in X_CHECKS) else 0)
        if need not in (0,1):
            return None
        if need:
            required.add(c)

    required=frozenset(required)
    avail=[(j,e) for j,e in enumerate(triples) if e <= required]
    bypoint={c:[] for c in required}
    for j,e in avail:
        for c in e:
            bypoint[c].append((j,e))

    def rec(rem, chosen):
        if not rem:
            if v:
                return tuple(chosen)+(17,)
            return tuple(chosen)

        p=min(
            rem,
            key=lambda z: sum(e <= rem for _,e in bypoint[z])
        )
        for j,e in bypoint[p]:
            if e <= rem:
                out=rec(rem-e, chosen+(j,))
                if out is not None:
                    return out
        return None

    return rec(required,())


def exact_boundary_mask(triples, selected):
    selected=set(selected)
    sums=[0]*19

    for j,e in enumerate(triples):
        if j in selected:
            for c in e:
                sums[c]+=1

    x=17 in selected
    for c in X_CHECKS:
        if x:
            sums[c]+=1

    bits=[0,0,0,0]
    for c in range(19):
        if c in PORTS:
            if sums[c] > 1:
                return None
            bits[PORTS[c]]=1-sums[c]
        elif sums[c] != 1:
            return None

    return (
        bits[0]
        | (bits[1]<<1)
        | (bits[2]<<2)
        | (bits[3]<<3)
        | (int(x)<<4)
    )


def even_partition_types():
    vals=set()
    for a in range(0,7,2):
        for b in range(0,7,2):
            for c in range(0,7,2):
                if a+b+c==6:
                    vals.add(tuple(sorted((a,b,c))))
    return vals


def main():
    cubics=tuple(frozenset(x) for x in CLUSTER_CUBICS)

    covers={}
    for m in sorted(TARGET6):
        cov=cover_for_mask(cubics,m)
        assert cov is not None
        assert exact_boundary_mask(cubics,cov)==m
        covers[m]=cov

    # Occurrence count among the chosen six witness covers.
    w=[0]*18
    for cov in covers.values():
        for j in cov:
            w[j]+=1

    # x is exactly the V=1 variable: three occurrences.
    assert w[17]==3

    # At E=check17 the other internal neighbour is cubic variable 10 in E92.
    e_neighbour=[
        j for j,t in enumerate(cubics)
        if 17 in t
    ]
    assert e_neighbour==[10]
    assert w[10]==3

    even_selected={
        j for j,count in enumerate(w)
        if count % 2 == 0
    }

    # E92 has no ordinary triple-even defect for this witness choice.
    defects=[]
    for c in range(19):
        if c in (0,1,2,17):
            continue
        incident=[
            j for j,t in enumerate(cubics)
            if c in t
        ]
        if c in X_CHECKS:
            incident.append(17)
        assert len(incident)==3
        s=sum(j in even_selected for j in incident)
        assert s in (1,3)
        if s==3:
            defects.append(c)

    assert defects==[]

    # Therefore the even-occurrence candidate is an exact raw8 witness.
    assert exact_boundary_mask(cubics,even_selected)==8

    # Local defect occurrence-size classification.
    assert even_partition_types()=={
        (0,0,6),
        (0,2,4),
        (2,2,2),
    }

    print("R5 E95 even-occurrence state8 defect reduction: PASS")
    print("chosen TARGET6 cover occurrence counts:", w)
    print("even-occurrence selected variables:", sorted(even_selected))
    print("ordinary triple-even defects:", defects)
    print("E92 even-occurrence candidate boundary mask=8")
    print("universal defect size types: (0,0,6), (0,2,4), (2,2,2)")
    print("next target: prove every hypothetical delta parent admits a defect-free choice, or kill all defect types")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
