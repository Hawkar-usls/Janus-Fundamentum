#!/usr/bin/env python3
"""R5 E96: four target-derived state8 parity candidates and defect signatures.

Label the six E93 target states:
  0=XA, 1=XB, 2=XC, 3=QAB, 4=QAC, 5=QBC.

Their boundary masks have two independent GF(2) dependencies:
  D1 = {XA,XB,QAC,QBC}
  D2 = {XA,XC,QAB,QBC}.
XORing the corresponding four internal witnesses gives two kernel corrections
h1,h2.  Adding span<h1,h2> to the E95 even-occurrence candidate gives four
canonical parity candidates for the same raw boundary state 8.

At a base E95 defect check, the three incident membership supports form a
partition of the six labels into three EVEN parts.  There are 31 unlabeled
such partitions.

Exact exhaustive classification:
  * 5 partitions are repaired by none of the three nonzero corrections;
  * those 5 are exactly the coarsenings of the opposite-pair partition
        {XA,QBC}, {XB,QAC}, {XC,QAB};
  * 8 partitions are repaired by all three nonzero corrections;
  * the remaining 18 split 6/6/6 among the three two-correction signatures.

Therefore, if no rigid opposite-pair defect occurs, failure of all four
canonical parity candidates requires defect checks exhibiting all three
pair-signature types simultaneously.

This is a universal six-state finite-algebra firewall.  It does not yet prove
those residual geometric patterns impossible.

P_VS_NP remains OPEN.
"""

from collections import Counter
from itertools import product

U=frozenset(range(6))
D1=frozenset({0,1,4,5})
D2=frozenset({0,2,3,5})
NONZERO=((0,1),(1,0),(1,1))
OPPOSITE=(
    frozenset({0,5}),
    frozenset({1,4}),
    frozenset({2,3}),
)


def canonical_partition(blocks):
    return tuple(sorted(
        (tuple(sorted(b)) for b in blocks)
    ))


def even_partitions():
    out=set()
    for assignment in product(range(3), repeat=6):
        blocks=[
            frozenset(i for i,x in enumerate(assignment) if x==k)
            for k in range(3)
        ]
        if all(len(b)%2==0 for b in blocks):
            out.add(canonical_partition(blocks))
    return tuple(sorted(out))


def selected(support,a,b):
    # E95 base bit is 1 because support size is even at a defect.
    return (
        1
        ^ (a & (len(support & D1)%2))
        ^ (b & (len(support & D2)%2))
    )


def repair_signature(partition):
    blocks=[frozenset(b) for b in partition]
    good=[]
    for a,b in NONZERO:
        if sum(selected(S,a,b) for S in blocks)==1:
            good.append((a,b))
    return tuple(good)


def opposite_coarsenings():
    # Assign each of the three indivisible opposite pairs to one of 3 bins.
    out=set()
    for assignment in product(range(3), repeat=3):
        bins=[set(),set(),set()]
        for atom,k in zip(OPPOSITE,assignment):
            bins[k].update(atom)
        out.add(canonical_partition(frozenset(x) for x in bins))
    return out


def main():
    parts=even_partitions()
    assert len(parts)==31

    counts=Counter(repair_signature(p) for p in parts)

    all3=tuple(NONZERO)
    p01_10=((0,1),(1,0))
    p10_11=((1,0),(1,1))
    p01_11=((0,1),(1,1))

    assert counts[()] == 5
    assert counts[all3] == 8
    assert counts[p01_10] == 6
    assert counts[p10_11] == 6
    assert counts[p01_11] == 6
    assert sum(counts.values())==31

    rigid={
        p for p in parts
        if repair_signature(p)==()
    }
    assert rigid==opposite_coarsenings()
    assert len(rigid)==5

    # Global consequence when no rigid defect is present:
    # the only proper repair signatures are the three 2-subsets of NONZERO.
    # Any two distinct such signatures intersect; all three have empty
    # intersection.  Thus global failure requires all three conflict types.
    assert set(p01_10)&set(p10_11)=={(1,0)}
    assert set(p01_10)&set(p01_11)=={(0,1)}
    assert set(p10_11)&set(p01_11)=={(1,1)}
    assert set(p01_10)&set(p10_11)&set(p01_11)==set()

    print("R5 E96 target-kernel defect signature firewall: PASS")
    print("even defect partitions=31")
    print("repair signature counts=", dict(counts))
    print("rigid partitions=5, exactly opposite-pair coarsenings")
    print("opposite pairs: (XA,QBC), (XB,QAC), (XC,QAB)")
    print("without a rigid defect, global four-candidate failure requires all three pair-signature types")
    print("next target: geometry-kill rigid opposite-pair defects and the three-signature conflict")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
