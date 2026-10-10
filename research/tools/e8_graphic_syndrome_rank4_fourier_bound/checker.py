#!/usr/bin/env python3
from itertools import product, combinations


def projective_points(r):
    pts=[]
    seen=set()
    for v in product(range(3), repeat=r):
        if all(x==0 for x in v):
            continue
        first=next(x for x in v if x)
        w=v if first==1 else tuple((2*x)%3 for x in v)
        if w not in seen:
            seen.add(w); pts.append(w)
    return pts


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))%3


def zero_count_bruteforce(cols):
    r=len(cols[0]) if cols else 0
    z=0
    for eps in product((1,2), repeat=len(cols)):
        s=[0]*r
        for e,c in zip(eps,cols):
            for i,x in enumerate(c):
                s[i]=(s[i]+e*x)%3
        if all(x==0 for x in s):
            z+=1
    return z


def zero_count_fourier(cols):
    r=len(cols[0]) if cols else 0
    m=len(cols)
    total=0
    for lam in product(range(3), repeat=r):
        z=sum(dot(lam,c)==0 for c in cols)
        total += (2**z) * ((-1)**(m-z))
    assert total % (3**r)==0
    return total//(3**r)


def main():
    # Replay the character identity on deterministic subsets in ranks 2,3,4.
    for r,maxm in [(2,4),(3,7),(4,8)]:
        pts=projective_points(r)
        for m in range(1,min(maxm,len(pts))+1):
            # a few deterministic windows, avoiding exponential subset sweeps
            starts=sorted(set([0, max(0,(len(pts)-m)//2), len(pts)-m]))
            for st in starts:
                cols=pts[st:st+m]
                assert zero_count_fourier(cols)==zero_count_bruteforce(cols)

    # Projective geometry parameters.
    assert len(projective_points(2))==4
    assert len(projective_points(3))==13
    assert len(projective_points(4))==40
    P4=(3**4-1)//2
    H4=(3**3-1)//2
    assert (P4,H4)==(40,13)

    # Exact threshold used by the theorem.
    assert 2**19 <= 2*P4*(2**H4)
    assert 2**20 > 2*P4*(2**H4)
    lower20=(2**20 - 2*P4*(2**H4))
    assert lower20>0

    # Consistency of the coarse bound in lower ranks.
    # r=2: hyperplanes contain one projective point; m>=5 impossible anyway,
    # and threshold says any hypothetical distinct support of size 5 has a zero.
    P2=(3**2-1)//2; H2=(3**1-1)//2
    assert (P2,H2)==(4,1)
    assert 2**5 > 2*P2*(2**H2)

    # r=3 threshold m=9; v5.9 exact enumeration improves to <=7.
    P3=(3**3-1)//2; H3=(3**2-1)//2
    assert (P3,H3)==(13,4)
    assert 2**9 > 2*P3*(2**H3)

    print('PASS: Fourier signed-zero identity and rank4 hyperplane bound')
    print('PG(3,3): 40 points / 40 hyperplanes / 13 points per hyperplane')
    print('m>=20 projectively distinct rank4 columns => signed zero exists')
    print('therefore zero-free distinct rank4 support has m<=19')


if __name__=='__main__':
    main()
