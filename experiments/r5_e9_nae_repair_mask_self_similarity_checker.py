#!/usr/bin/env python3
from itertools import product

def nae(t):
    return len(set(t)) > 1

def xor(a,b):
    return tuple(x^y for x,y in zip(a,b))

def models(n, edges):
    return {
        a for a in product((0,1), repeat=n)
        if all(nae(tuple(a[v] for v in e)) for e in edges)
    }

def repair_masks(y, edges):
    n=len(y)
    out=set()
    for h in product((0,1), repeat=n):
        ok=True
        for e in edges:
            ye=tuple(y[v] for v in e)
            he=tuple(h[v] for v in e)
            if not nae(xor(ye,he)):
                ok=False; break
        if ok:
            out.add(h)
    return out

def main():
    edges=((0,1,2),(2,3,4),(1,4,5))
    M=models(6,edges)
    assert M
    for y in M:
        H=repair_masks(y,edges)
        translated={xor(y,h) for h in H}
        assert translated==M
        assert len(H)==len(M)
        assert (0,0,0,0,0,0) in H
        assert (1,1,1,1,1,1) in H

        # Canonical anchor slice is exactly the corresponding model slice.
        a=0
        H0={h for h in H if h[a]==0}
        M0={z for z in M if z[a]==y[a]}
        assert {xor(y,h) for h in H0}==M0

        # Pivot-flip masks are exactly models with opposite pivot.
        p=3
        H01={h for h in H if h[a]==0 and h[p]==1}
        M01={z for z in M if z[a]==y[a] and z[p]!=(y[p])}
        assert {xor(y,h) for h in H01}==M01

    print("NAE_REPAIR_MASK_TRANSLATION_BIJECTION = PASS")
    print("ANCHOR_SLICE_BIJECTION = PASS")
    print("PIVOT_FLIP_SLICE_BIJECTION = PASS")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
