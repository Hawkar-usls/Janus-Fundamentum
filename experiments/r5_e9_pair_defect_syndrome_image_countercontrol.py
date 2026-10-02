#!/usr/bin/env python3
from itertools import product

D2=((0,1,2),(3,4,5),(6,7,8),(9,10,11))
D3=((0,3,6),(1,4,9),(2,7,10),(5,8,11))
PAIRS=((0,4),(1,3),(2,5),(6,9),(7,11),(8,10))

def nae(vals):
    return len(set(vals))>1

def models():
    out=[]
    for a in product((0,1),repeat=12):
        if all(nae(tuple(a[v] for v in e)) for e in D2+D3):
            out.append(a)
    return out

def syndrome(a):
    return tuple(1 ^ a[u] ^ a[v] for u,v in PAIRS)

def maj(x,y,z):
    return tuple(1 if a+b+c>=2 else 0 for a,b,c in zip(x,y,z))

def delta_witness(S):
    sets=[{i for i,b in enumerate(s) if b} for s in S]
    table={frozenset(X) for X in sets}
    for X in sets:
        for Y in sets:
            diff=X^Y
            for u in diff:
                if not any(
                    frozenset(X ^ ({u} if u==v else {u,v})) in table
                    for v in diff
                ):
                    return tuple(sorted(X)),tuple(sorted(Y)),u,tuple(sorted(diff))
    return None

def main():
    M=models()
    S={syndrome(a) for a in M}
    assert len(M)==450
    assert len(S)==55

    # Linearity / partition audit.
    for e in D2:
        for f in D3:
            assert len(set(e)&set(f))<=1
    all_tri=D2+D3
    for u,v in PAIRS:
        assert all(len({u,v}&set(e))<=1 for e in all_tri)

    h1=(1,1,1,1,0,1); h2=(1,1,1,1,1,0)
    assert h1 in S and h2 in S
    assert tuple(a&b for a,b in zip(h1,h2)) not in S

    d1=(1,1,1,0,0,0); d2=(0,1,0,1,0,0)
    assert d1 in S and d2 in S
    assert tuple(a|b for a,b in zip(d1,d2)) not in S

    a1=(1,1,1,0,0,0); a2=(1,1,1,1,0,1); a3=(0,0,1,0,1,0)
    assert all(x in S for x in (a1,a2,a3))
    assert tuple(a^b^c for a,b,c in zip(a1,a2,a3)) not in S

    b1=(1,1,1,0,0,0); b2=(1,1,1,1,0,1); b3=(1,1,1,1,1,0)
    assert all(x in S for x in (b1,b2,b3))
    assert maj(b1,b2,b3) not in S

    dw=delta_witness(S)
    assert dw==((2,), (0,1,2,3,5), 3, (0,1,3,5))

    print("PAIR_DEFECT_SYNDROME_IMAGE_SIZE = 55 / 64")
    print("AFFINE_CLOSURE = FAIL")
    print("HORN_CLOSURE = FAIL")
    print("DUAL_HORN_CLOSURE = FAIL")
    print("BIJUNCTIVE_CLOSURE = FAIL")
    print("DELTA_MATROID_SYMMETRIC_EXCHANGE = FAIL")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
