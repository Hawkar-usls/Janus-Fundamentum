#!/usr/bin/env python3
from itertools import product, combinations
from math import gcd

B=(
 (-1,-1,-1, 0),
 ( 1, 1, 0,-1),
 ( 1, 0, 1,-1),
 ( 0, 1, 1,-1),
)
ELL=(-2,0,0,0)
W=(1,2,2,2)  # left torsion character mod 3

def det_int(M):
    A=[list(map(int,row)) for row in M]
    n=len(A); sign=1; prev=1
    for k in range(n-1):
        if A[k][k]==0:
            sw=next((i for i in range(k+1,n) if A[i][k]),None)
            if sw is None: return 0
            A[k],A[sw]=A[sw],A[k]; sign*=-1
        p=A[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                A[i][j]=(A[i][j]*p-A[i][k]*A[k][j])//prev
        prev=p
        for i in range(k+1,n):
            A[i][k]=0
    return sign*A[-1][-1]

def side_word(x):
    out=[]
    for row,ell in zip(B,ELL):
        v=sum(a*b for a,b in zip(row,x))-ell
        if v not in (0,1):
            return None
        out.append(v)
    return tuple(out)

def signed_nae_rows_ok(x):
    return side_word(x) is not None

def orientation_relation():
    out=set()
    for q,a,b,c in product((0,1),repeat=4):
        # q=0 -> exactly one of a,b,c; q=1 -> exactly two.
        if a+b+c == 1+q:
            out.add((q,a,b,c))
    return out

def main():
    assert det_int(B)==-3

    # gcd of 3x3 minors is 1; together with |det|=3 prime:
    # SNF(B)=(1,1,1,3).
    g=0
    for rs in combinations(range(4),3):
        for cs in combinations(range(4),3):
            minor=[[B[i][j] for j in cs] for i in rs]
            g=gcd(g,abs(det_int(minor)))
    assert g==1

    # Explicit left torsion character.
    for j in range(4):
        assert sum(W[i]*B[i][j] for i in range(4))%3==0
    ell_charge=sum(W[i]*ELL[i] for i in range(4))%3
    assert ell_charge==1

    image={}
    for x in product((0,1),repeat=4):
        s=side_word(x)
        if s is not None:
            image.setdefault(s,[]).append(x)

    target=orientation_relation()
    assert set(image)==target
    assert len(target)==6
    assert all(len(v)==1 for v in image.values())

    # Torsion equation:
    # W.(ELL+s)=0 mod3  <=> q+2(a+b+c)=2 mod3,
    # which on Boolean bits is exactly a+b+c=1+q.
    for s in product((0,1),repeat=4):
        torsion_ok=(sum(W[i]*(ELL[i]+s[i]) for i in range(4))%3==0)
        assert torsion_ok == (s in target)

    # Clause-level orientation decoder:
    # source bits alpha_i = side_i XOR q satisfy positive 1-in-3.
    for q,a,b,c in target:
        alpha=(a^q,b^q,c^q)
        assert sum(alpha)==1

    print("SIGNED_NAE_BLOCK_DET = -3")
    print("SIGNED_NAE_BLOCK_SNF = 1,1,1,3")
    print("TORSION_CHARACTER_MOD3 = 1,2,2,2")
    print("BOOLEAN_SIDE_SLICE_SIZE = 6")
    print("SIDE_SLICE = ORIENTATION_LIFT_OF_POSITIVE_1_IN_3")
    print("INTERNAL_BOOLEAN_LIFT_PER_SIDE_WORD = UNIQUE")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
