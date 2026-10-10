#!/usr/bin/env python3
from itertools import product


def nand3(a,b,c):
    return not (a and b and c)


def projected(c):
    out=set()
    for p,q,r,s in product((0,1), repeat=4):
        ok=any(
            nand3(a,p,q) and nand3(a^c,r,s)
            for a in (0,1)
        )
        if ok:
            out.add((p,q,r,s))
    return out


R0=projected(0)
R1=projected(1)
ALL=set(product((0,1),repeat=4))
assert R0==ALL
assert R1==ALL-{(1,1,1,1)}

# Direct witness choices used in the proof.
for p,q,r,s in ALL:
    assert nand3(0,p,q) and nand3(0,r,s)

for p,q,r,s in R1:
    if (p,q)!=(1,1):
        a=1
    else:
        assert (r,s)!=(1,1)
        a=0
    assert nand3(a,p,q) and nand3(a^1,r,s)

assert not any(nand3(a,1,1) and nand3(a^1,1,1) for a in (0,1))

print('PASS')
print('same_polarity_projection=TRUE4')
print('opposite_polarity_projection=NAND4')
print('ordinary_CNF_interpretation=(x|A|B)&(~x|C|D) -> (A|B|C|D)')
print('one_coherence_pivot=CLASSICAL_DP_REPACKAGING')
print('E8_D1=EMPTY P_VS_NP=OPEN')
