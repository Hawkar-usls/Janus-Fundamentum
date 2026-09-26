from itertools import product


def det_mod2(A):
    A=[row[:] for row in A]
    n=len(A); r=0
    for c in range(n):
        p=next((i for i in range(r,n) if A[i][c]&1),None)
        if p is None: continue
        A[r],A[p]=A[p],A[r]
        for i in range(n):
            if i!=r and (A[i][c]&1):
                A[i]=[x^y for x,y in zip(A[i],A[r])]
        r+=1
    return int(r==n)


def sat_eval(F,a):
    return all(any(a[abs(l)] if l>0 else 1-a[abs(l)] for l in C) for C in F)


def clause_block(C,a):
    fs=[]
    for lit in C:
        v=a[abs(lit)]
        fs.append((1^v) if lit>0 else v)
    if len(C)==2:
        f1,f2=fs
        return [[1,f1],[f2,1]]
    if len(C)==3:
        f1,f2,f3=fs
        return [[1,f1,0],[0,1,f2],[f3,0,1]]
    raise ValueError('only 2/3 clauses')


def blockdiag(blocks):
    N=sum(len(B) for B in blocks)
    M=[[0]*N for _ in range(N)]
    s=0
    for B in blocks:
        for i,row in enumerate(B):
            for j,v in enumerate(row): M[s+i][s+j]=v&1
        s+=len(B)
    return M


def rank_bound(F):
    occ={}
    for C in F:
        for lit in C: occ[abs(lit)]=occ.get(abs(lit),0)+1
    return max(occ.values(),default=0),occ


def check(F):
    assert all(len(C) in (2,3) for C in F)
    mx,occ=rank_bound(F)
    assert mx<=3,occ
    vars_=sorted(occ)
    sat_any=False; nonsing_any=False
    for vals in product((0,1),repeat=len(vars_)):
        a=dict(zip(vars_,vals))
        s=sat_eval(F,a)
        d=det_mod2(blockdiag([clause_block(C,a) for C in F]))
        assert d==int(s),(F,a,s,d)
        sat_any|=s; nonsing_any|=bool(d)
    assert sat_any==nonsing_any
    print(f'vars={len(vars_)} clauses={len(F)} maxocc={mx} SAT={int(sat_any)} NONSING={int(nonsing_any)} PASS')


def main():
    controls=[
        [(1,2)],
        [(1,2,3)],
        [(1,2),(-1,3),(2,-3)],
        [(1,2,3),(-1,2),(-2,3),(-3,1)],
        [(1,2),(-1,3),(2,-3),(-2,1)],
    ]
    for F in controls: check(F)
    print('PASS: 2/3-clause GF(2) blocks give exact SAT indicator with direction rank bounded by occurrence count <=3')

if __name__=='__main__': main()
