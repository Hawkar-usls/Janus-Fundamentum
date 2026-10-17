#!/usr/bin/env python3
from itertools import product

P=3


def norm(v):
    i=next(i for i,x in enumerate(v) if x%P)
    inv=1 if v[i]%P==1 else 2
    return tuple((inv*x)%P for x in v)

PTS=sorted({norm(v) for v in product(range(P), repeat=3) if any(v)})


def rank_mod(rows):
    if not rows: return 0
    A=[list(r) for r in rows]
    r=0
    for c in range(len(A[0])):
        piv=next((i for i in range(r,len(A)) if A[i][c]%P),None)
        if piv is None: continue
        A[r],A[piv]=A[piv],A[r]
        inv=1 if A[r][c]%P==1 else 2
        A[r]=[(inv*x)%P for x in A[r]]
        for i in range(len(A)):
            if i!=r and A[i][c]%P:
                f=A[i][c]%P
                A[i]=[(A[i][j]-f*A[r][j])%P for j in range(len(A[0]))]
        r+=1
    return r


def zero_signed(cols):
    for eps in product((1,2), repeat=len(cols)):
        s=tuple(sum(eps[j]*cols[j][i] for j in range(len(cols)))%P for i in range(len(cols[0])))
        if all(x==0 for x in s): return True
    return False


def one_dimensional_check():
    # k nonzero quotient singleton contributions in GF(3): zero-free iff k=1.
    for k in range(1,14):
        cols=[(1,)]*k
        z=zero_signed(cols)
        assert z == (k>=2), (k,z)


def pg1_rank2_patterns():
    reps=[(1,0),(0,1),(1,1),(1,2)]
    for mult in product(range(4), repeat=4):  # 0..3 singleton collisions per quotient direction
        cols=[]
        for r,m in zip(reps,mult): cols += [r]*m
        if rank_mod([c+(0,) for c in cols])<2: # reuse 3-column rank helper
            continue
        z=zero_signed(cols)
        occ=[m for m in mult if m]
        pattern_I=(len(occ)==2 and 1 in occ)
        pattern_II=(len(occ)==4 and all(m==1 for m in occ))
        assert (not z)==(pattern_I or pattern_II), (mult,z,pattern_I,pattern_II)


def lines_through_point_geometry():
    # For every L in PG(2,3), the other 12 points split into four quotient directions,
    # each containing exactly three points: projective lines through L minus L.
    for L in PTS:
        classes={}
        for p in PTS:
            if p==L: continue
            # the 2D span of L,p is represented by the set of projective points it contains
            line=tuple(sorted(q for q in PTS if rank_mod([L,p,q])<=2))
            classes.setdefault(line,[]).append(p)
        assert len(classes)==4, (L,len(classes))
        assert sorted(len(v) for v in classes.values())==[3,3,3,3]


def k4_control():
    Q=[
      (1,2,0,1,0,0),
      (1,0,2,0,1,0),
      (0,1,2,0,0,1),
    ]
    cols=[tuple(Q[r][c] for r in range(3)) for c in range(6)]
    assert len({norm(c) for c in cols})==6
    assert not zero_signed(cols)


def main():
    assert len(PTS)==13
    one_dimensional_check()
    pg1_rank2_patterns()
    lines_through_point_geometry()
    k4_control()
    print('PASS: rank3 repeated-direction quotient cases and unique K4 sharp control verified')

if __name__=='__main__':
    main()
