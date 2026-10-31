#!/usr/bin/env python3

LINES=[
(1,15,12),(2,14,4),(3,2,8),(4,3,9),(5,4,6),
(6,12,10),(7,1,3),(8,9,15),(9,7,5),(10,8,7),
(11,5,2),(12,13,14),(13,11,1),(14,6,11),(15,10,13)
]
Z=[-1,1,0,1,-1,1,2,0,0,-1,1,1,1,-1,1]


def incidence(lines,n=15):
    A=[[0]*n for _ in range(n)]
    for i,line in enumerate(lines):
        for j in line:
            A[i][j-1]=1
    assert all(sum(row)==3 for row in A)
    assert all(sum(A[i][j] for i in range(n))==3 for j in range(n))
    # linearity
    supports=[set(j-1 for j in line) for line in lines]
    assert all(len(supports[i]&supports[j])<=1 for i in range(n) for j in range(i))
    return A


def mv(A,x):
    return [sum(a*b for a,b in zip(row,x)) for row in A]


def main():
    A=incidence(LINES)
    n=len(A)
    assert mv(A,Z)==[1]*n

    b=[1 if z>=1 else 0 for z in Z]
    B={i for i,v in enumerate(b) if v}
    weights=mv(A,b)
    assert set(weights)<={1,2}
    T={i for i,w in enumerate(weights) if w==2}
    assert len(T)==3*len(B)-n

    p=[max(z-1,0) if b[i] else 0 for i,z in enumerate(Z)]
    q=[0 if b[i] else -z for i,z in enumerate(Z)]
    assert all(v>=0 for v in p+q)
    assert len(T)==3*(sum(q)-sum(p))

    F=sum(abs(2*z-1) for z in Z)
    assert F==25
    assert F*3==n+6*len(B)+12*sum(p) # exact integer form of n/3+2|B|+4||p||1

    r=[p[i] if b[i] else q[i] for i in range(n)]
    mcount=[0]*n
    reconstructed=[None]*n

    for row_idx,line in enumerate(LINES):
        idx=[j-1 for j in line]
        w=weights[row_idx]
        minority_bit=1 if w==1 else 0
        minorities=[i for i in idx if b[i]==minority_bit]
        assert len(minorities)==1
        m=minorities[0]
        uv=[i for i in idx if i!=m]
        tau=1 if w==2 else 0
        assert r[m]-r[uv[0]]-r[uv[1]]==tau
        mcount[m]+=1

    # Bijection reconstruction for fixed b.
    for i in range(n):
        reconstructed[i]=(1+r[i]) if b[i] else -r[i]
    assert reconstructed==Z
    assert mv(A,reconstructed)==[1]*n

    assert sum(mcount)==n
    assert sum((2*mcount[i]-3)*r[i] for i in range(n))==len(T)

    # Transversal lower-bound/equality logic on this source.
    # Any size-n/3 hitting set has exactly n incidences and therefore exactly one hit per row.
    sat_size=n//3
    assert 3*sat_size==n

    print('PASS: threshold is NAE transversal')
    print('PASS: |T| = 3|B|-n')
    print('PASS: F = n/3 + 2|B| + 4||p||1')
    print('PASS: all minority add/copy equations hold and reconstruct z exactly')
    print('PASS: oriented-Levi divergence identity')
    print('P_VS_NP=OPEN; E8_D1=EMPTY')


if __name__=='__main__':
    main()
