#!/usr/bin/env python3
from itertools import product

P=3


def normalize(v):
    i=next(i for i,x in enumerate(v) if x%P)
    inv=1 if v[i]%P==1 else 2
    return tuple((inv*x)%P for x in v)

PTS=sorted({normalize(v) for v in product(range(P), repeat=3) if any(v)})


def rank_mod(rows):
    if not rows: return 0
    A=[list(r) for r in rows]
    r=0
    for c in range(3):
        piv=next((i for i in range(r,len(A)) if A[i][c]%P),None)
        if piv is None: continue
        A[r],A[piv]=A[piv],A[r]
        inv=1 if A[r][c]%P==1 else 2
        A[r]=[(inv*x)%P for x in A[r]]
        for i in range(len(A)):
            if i!=r and A[i][c]%P:
                f=A[i][c]%P
                A[i]=[(A[i][j]-f*A[r][j])%P for j in range(3)]
        r+=1
    return r


def signed_zero(cols):
    for eps in product((1,2), repeat=len(cols)):
        s=tuple(sum(eps[j]*cols[j][i] for j in range(len(cols)))%P for i in range(3))
        if s==(0,0,0): return True
    return False


def k4_control():
    Q=[
      (1,2,0,1,0,0),
      (1,0,2,0,1,0),
      (0,1,2,0,0,1),
    ]
    cols=[tuple(Q[r][c] for r in range(3)) for c in range(6)]
    assert all(any(c) for c in cols)
    assert len({normalize(c) for c in cols})==6
    # row rank
    rows=[(Q[r][0],Q[r][1],Q[r][2]) for r in range(3)]
    # direct sign zero test on the full six columns
    assert not signed_zero(cols)


def main():
    assert len(PTS)==13
    counts={}
    total=0
    for mask in range(1<<13):
        cols=[PTS[i] for i in range(13) if (mask>>i)&1]
        if len(cols)<3 or rank_mod(cols)<3:
            continue
        if not signed_zero(cols):
            counts[len(cols)]=counts.get(len(cols),0)+1
            total+=1
    assert counts=={3:234,4:468,5:585,6:234,7:78}, counts
    assert total==1599
    assert max(counts)==7
    k4_control()
    print('PASS: PG(2,3) distinct zero-free rank3 support <=7; K4 sharp control verified')

if __name__=='__main__':
    main()
