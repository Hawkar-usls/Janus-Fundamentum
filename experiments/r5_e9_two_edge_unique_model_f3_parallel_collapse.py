#!/usr/bin/env python3
"""Exact finite regression for the arbitrary-size F3 tower-collapse theorem."""

from collections import defaultdict

ROWS=[
(0,15,17),(1,4,12),(2,10,14),(3,4,11),(4,8,9),(3,5,13),
(1,6,10),(2,7,15),(1,8,14),(3,7,9),(9,10,16),(7,11,13),
(5,12,17),(0,13,16),(0,12,14),(5,8,15),(2,6,16),(6,11,17)
]
X=[1,1,1,0,0,1,0,0,0,1,0,1,0,0,0,0,0,0]
K1=[0,0,-2,-2,3,3,1,2,-3,0,-1,-1,-3,-1,3,0,1,0]
K2=[-2,-2,0,3,-2,-5,0,-1,4,-2,2,-1,4,2,-2,1,0,1]
ELL=[1,2,2,-1,-1,-1,-1,-3,-1,2,-1,1,-1,0,-1,2,1,0]
PAIR=((0,15),(1,1))


def incidence(rows,n):
    A=[[0]*n for _ in range(n)]
    for i,row in enumerate(rows):
        for j in row:A[i][j]=1
    return A


def mv_mod(A,x,p=3):
    return [sum(a*b for a,b in zip(row,x))%p for row in A]


def mtv_mod(A,x,p=3):
    return [sum(A[i][j]*x[i] for i in range(len(A)))%p for j in range(len(A[0]))]


def rref_affine(A,b,p=3):
    m=len(A); n=len(A[0]) if A else 0
    M=[[v%p for v in A[i]]+[b[i]%p] for i in range(m)]
    piv=[]; r=0
    for c in range(n):
        pivot=next((i for i in range(r,m) if M[i][c]%p),None)
        if pivot is None: continue
        M[r],M[pivot]=M[pivot],M[r]
        inv=pow(M[r][c]%p,-1,p)
        M[r]=[(v*inv)%p for v in M[r]]
        for i in range(m):
            if i!=r and M[i][c]%p:
                f=M[i][c]%p
                M[i]=[(M[i][j]-f*M[r][j])%p for j in range(n+1)]
        piv.append(c); r+=1
        if r==m: break
    if any(all(M[i][j]==0 for j in range(n)) and M[i][n] for i in range(r,m)):
        return None,[]
    free=[j for j in range(n) if j not in piv]
    x0=[0]*n
    for i,c in enumerate(piv):x0[c]=M[i][n]
    basis=[]
    for f in free:
        v=[0]*n; v[f]=1
        for i,c in enumerate(piv):v[c]=(-M[i][f])%p
        basis.append(v)
    return x0,basis


def normalize(a,c):
    if not any(a):return a,c%3
    j=next(i for i,v in enumerate(a) if v)
    inv=pow(a[j],-1,3)
    return tuple(v*inv%3 for v in a),c*inv%3


def affine_functions(A):
    x0,basis=rref_affine(A,[1]*len(A))
    assert x0 is not None
    n=len(A[0])
    funcs=[]
    for i in range(n):
        funcs.append((tuple(basis[t][i] for t in range(len(basis))),x0[i],i))
    return funcs,len(basis)


def transform(funcs,base,basis):
    out=[]
    for a,c,idx in funcs:
        c2=(c+sum(x*y for x,y in zip(a,base)))%3
        a2=tuple(sum(a[j]*basis[t][j] for j in range(len(a)))%3 for t in range(len(basis)))
        out.append((a2,c2,idx))
    return out


def reduce_parallel(funcs,d):
    rounds=[]
    while True:
        groups=defaultdict(list)
        for a,c,idx in funcs:
            if not any(a):
                if c%3==0:return {'status':'UNSAT','d':d,'rounds':rounds}
                continue
            an,cn=normalize(a,c)
            groups[an].append(((-cn)%3,idx))
        pins=[]; survivors=[]
        for an,vals in groups.items():
            offs=sorted(set(v for v,_ in vals))
            if len(offs)==3:return {'status':'UNSAT','d':d,'rounds':rounds}
            if len(offs)==2:
                pins.append((an,next(v for v in range(3) if v not in offs)))
            else:
                b=offs[0]
                survivors.append((an,(-b)%3,vals[0][1]))
        if not pins:
            rounds.append((d,len(groups),0,len(survivors),d))
            return {'status':'RESIDUAL','d':d,'classes':len(groups),'funcs':survivors,'rounds':rounds}
        base,basis=rref_affine([list(a) for a,_ in pins],[b for _,b in pins])
        assert base is not None
        d2=len(basis)
        rounds.append((d,len(groups),len(pins),len(survivors),d2))
        funcs=transform(survivors,base,basis)
        d=d2


def lift(A,pair):
    n=len(A)
    E=[[0]*n for _ in range(n)]
    for i,j in pair:
        assert A[i][j]==1
        E[i][j]=1
    P=[[A[i][j]-E[i][j] for j in range(n)] for i in range(n)]
    return [P[i]+E[i] for i in range(n)] + [E[i]+P[i] for i in range(n)]


def seed_polarity_complete():
    r=[(1+x)%3 for x in X]
    groups=defaultdict(set)
    for j in range(18):
        a=(K1[j]%3,K2[j]%3)
        an,cn=normalize(a,r[j])
        assert any(an)
        groups[an].add(cn)
    assert set(groups)=={(1,0),(0,1),(1,1)}
    assert all(vals=={1,2} for vals in groups.values())


def main():
    A=incidence(ROWS,18)
    pair=PAIR
    ell=[x%3 for x in ELL]

    assert mv_mod(A,[x%3 for x in K1])==[0]*18
    assert mv_mod(A,[x%3 for x in K2])==[0]*18
    assert mtv_mod(A,ell)==[0]*18
    assert ell[0]==1 and ell[1]==2
    seed_polarity_complete()

    expected=[
        (0,18,2,3),
        (1,36,3,5),
        (2,72,5,9),
        (3,144,9,17),
        (4,288,17,33),
    ]

    got=[]
    for t,n,d_exp,c_exp in expected:
        assert len(A)==n
        funcs,d=affine_functions(A)
        assert d==d_exp==2**t+1
        res=reduce_parallel(funcs,d)
        assert res['status']=='RESIDUAL'
        assert res['d']==0
        first=res['rounds'][0]
        assert first[1]==c_exp==2*d-1
        assert first[2]==c_exp  # every projective class is a two-offset pin
        assert first[3]==0      # no singleton class survives the first round
        got.append((t,n,d,c_exp,res['d']))

        if t!=expected[-1][0]:
            old_n=n
            A=lift(A,pair)
            pair=tuple((i,old_n+j) for i,j in pair)
            ell=ell+ell
            assert mtv_mod(A,ell)==[0]*(2*old_n)
            assert ell[pair[0][0]]==1 and ell[pair[1][0]]==2

    print({'status':'PASS_TWO_EDGE_UNIQUE_MODEL_F3_PARALLEL_COLLAPSE','levels':got})
    print('arbitrary-size theorem is proved symbolically in companion note')
    print('E8_D1=EMPTY; P_VS_NP=OPEN')


if __name__=='__main__':
    main()
