#!/usr/bin/env python3
from fractions import Fraction
from itertools import combinations
from math import gcd

A=(
 (0,1,0,1,0,-1),
 (-1,0,0,0,1,1),
 (0,0,1,-1,-1,0),
 (1,-1,-1,0,0,0),
 (-1,0,-1,0,0,-1),
 (0,1,0,0,-1,1),
 (1,0,0,-1,1,0),
 (0,-1,1,1,0,0),
)
BASIS=(0,1,2,4,5,6)
EXTRA_KILL=3
EXTRA_REDUNDANT=7
MOD=13
CHAR=(4,11,3,3,9,1)

def det_int(M):
    A=[list(map(int,row)) for row in M]
    n=len(A)
    sign=1
    prev=1
    for k in range(n-1):
        if A[k][k]==0:
            sw=next((i for i in range(k+1,n) if A[i][k]!=0),None)
            if sw is None:
                return 0
            A[k],A[sw]=A[sw],A[k]
            sign*=-1
        p=A[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                A[i][j]=(A[i][j]*p-A[i][k]*A[k][j])//prev
        prev=p
        for i in range(k+1,n):
            A[i][k]=0
    return sign*A[-1][-1]

def solve_fraction(M,b):
    A=[[Fraction(v) for v in row]+[Fraction(rhs)] for row,rhs in zip(M,b)]
    n=len(A)
    for c in range(n):
        p=next(i for i in range(c,n) if A[i][c])
        A[c],A[p]=A[p],A[c]
        q=A[c][c]
        A[c]=[v/q for v in A[c]]
        for i in range(n):
            if i==c: continue
            q=A[i][c]
            if q:
                A[i]=[u-q*v for u,v in zip(A[i],A[c])]
    return tuple(A[i][-1] for i in range(n))

def lower(row):
    return 1-sum(1 for a in row if a==-1)

def signed_nae_ok(x,row):
    vals=[]
    for bit,a in zip(x,row):
        if a==1: vals.append(bit)
        elif a==-1: vals.append(1-bit)
    return len(set(vals))>1

def snf_audit(B):
    assert abs(det_int(B))==13
    # gcd of all 5x5 minors = product of first five SNF invariants.
    g=0
    for rs in combinations(range(6),5):
        for cs in combinations(range(6),5):
            minor=[[B[i][j] for j in cs] for i in rs]
            g=gcd(g,abs(det_int(minor)))
    assert g==1
    # Together with |det|=13 prime this forces SNF=(1,1,1,1,1,13).

def torsion_character(B):
    for j in range(6):
        assert sum(CHAR[i]*B[i][j] for i in range(6))%MOD==0

def side_dp(target):
    # DP over Z_13 residues; stores all words only because final count is 2.
    states={0:[()]}
    for w in CHAR:
        nxt={}
        for r,words in states.items():
            for word in words:
                for bit in (0,1):
                    rr=(r+w*bit)%MOD
                    nxt.setdefault(rr,[]).append(word+(bit,))
        states=nxt
    return states.get(target,[])

def main():
    B=[A[i] for i in BASIS]
    ell=[lower(A[i]) for i in BASIS]

    snf_audit(B)
    torsion_character(B)

    ell_charge=sum(c*l for c,l in zip(CHAR,ell))%MOD
    assert ell_charge==4
    target=(-ell_charge)%MOD
    assert target==9

    side_words=side_dp(target)
    assert side_words==[
        (0,0,0,0,1,0),
        (1,1,1,1,0,1),
    ]

    lifts=[]
    for s in side_words:
        rhs=[l+b for l,b in zip(ell,s)]
        x=solve_fraction(B,rhs)
        assert all(v.denominator==1 for v in x)
        xi=tuple(int(v) for v in x)
        assert all(v in (0,1) for v in xi)
        assert all(signed_nae_ok(xi,A[i]) for i in BASIS)
        lifts.append(xi)

    assert lifts==[
        (1,0,0,1,0,1),
        (0,1,1,0,1,0),
    ]
    assert lifts[1]==tuple(1-v for v in lifts[0])

    # One omitted signed NAE row kills both basis models.
    assert all(not signed_nae_ok(x,A[EXTRA_KILL]) for x in lifts)
    # The other omitted row accepts both; it is irrelevant to Boolean NO once row 3 is added.
    assert all(signed_nae_ok(x,A[EXTRA_REDUNDANT]) for x in lifts)

    print("ACTIVE_BASIS_DETERMINANT = 13")
    print("ACTIVE_BASIS_SNF = 1,1,1,1,1,13")
    print("TORSION_CHARACTER_MOD_13 = 4,11,3,3,9,1")
    print("SIDE_CODE_CONGRUENCE = w.s == 9 mod 13")
    print("CONGRUENCE_COMPATIBLE_BINARY_SIDE_WORDS = 2")
    print("BOOLEAN_LIFTS = 2 (COMPLEMENT PAIR)")
    print("ONE_EXTRA_ROW_KILLS_BOTH = PASS")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
