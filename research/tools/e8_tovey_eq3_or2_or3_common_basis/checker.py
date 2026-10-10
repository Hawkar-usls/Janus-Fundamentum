#!/usr/bin/env python3
from fractions import Fraction
from itertools import product


def inv_transpose(T):
    a,b=T[0]; c,d=T[1]
    det=a*d-b*c
    assert det
    # T^{-T} = (T^{-1})^T
    return [[Fraction(d,det),Fraction(-c,det)], [Fraction(-b,det),Fraction(a,det)]]


def rank1_sym(v,k):
    x,y=v
    return [x**(k-w)*y**w for w in range(k+1)]


def sub(a,b): return [x-y for x,y in zip(a,b)]
def add(a,b): return [x+y for x,y in zip(a,b)]


def parity(sig):
    even_ok=all(sig[w]==0 for w in range(1,len(sig),2))
    odd_ok=all(sig[w]==0 for w in range(0,len(sig),2))
    out=[]
    if even_ok: out.append('even')
    if odd_ok: out.append('odd')
    return tuple(out)


def signatures(T):
    # q=T e0, p=T(e0+e1)
    q=(Fraction(T[0][0]),Fraction(T[1][0]))
    p=(Fraction(T[0][0]+T[0][1]),Fraction(T[1][0]+T[1][1]))
    or2=sub(rank1_sym(p,2),rank1_sym(q,2))
    or3=sub(rank1_sym(p,3),rank1_sym(q,3))
    S=inv_transpose(T)
    u=(S[0][0],S[1][0]); v=(S[0][1],S[1][1])
    eq3=add(rank1_sym(u,3),rank1_sym(v,3))
    return or2,or3,eq3


def main():
    candidates=0
    values=(-2,-1,0,1,2)
    for a,b,c,d in product(values,repeat=4):
        if a*d-b*c==0: continue
        T=[[a,b],[c,d]]
        o2,o3,e3=signatures(T)
        if parity(o2) and parity(o3):
            candidates+=1
            assert not parity(e3),(T,o2,o3,e3)
    assert candidates>0

    # Exact controls for the two forced dual-basis families in the proof.
    for q0 in (1,2,-1):
        for q1 in (1,3,-2):
            for T,po3 in [([[q0,-2*q0],[q1,0]],'even'), ([[q0,0],[q1,-2*q1]],'odd')]:
                o2,o3,e3=signatures(T)
                assert 'odd' in parity(o2)
                assert po3 in parity(o3)
                assert not parity(e3)
                assert e3[0]!=0 and e3[1]!=0

    print('PASS_TOVEY_EQ3_OR2_OR3_COMMON_BASIS_MATCHGATE_BARRIER')
    print('finite_rational_candidate_controls=',candidates)
    print('COMMON_BASIS_ROUTE=CLOSED_IN_CHARACTERISTIC_ZERO_SCOPE')
    print('P_VS_NP=OPEN E8_D1=EMPTY')


if __name__=='__main__': main()
