from itertools import product

F=[(1,2),(1,-2),(-1,3),(-3,4),(-3,-4)]


def rank2(A):
    A=[row[:] for row in A]
    n=len(A); m=len(A[0]); r=0
    for c in range(m):
        p=next((i for i in range(r,n) if A[i][c]&1),None)
        if p is None: continue
        A[r],A[p]=A[p],A[r]
        for i in range(n):
            if i!=r and (A[i][c]&1):
                A[i]=[x^y for x,y in zip(A[i],A[r])]
        r+=1
    return r


def sat(a):
    return all(any(a[abs(l)] if l>0 else 1-a[abs(l)] for l in C) for C in F)


def build_affine():
    vars_=[1,2,3,4]
    n=2*len(F)
    M0=[[0]*n for _ in range(n)]
    As={v:[[0]*n for _ in range(n)] for v in vars_}
    s=0
    for C in F:
        M0[s][s]=M0[s+1][s+1]=1
        coords=[(s,s+1),(s+1,s)]
        for lit,(r,c) in zip(C,coords):
            v=abs(lit)
            if lit>0:
                M0[r][c]^=1
                As[v][r][c]^=1
            else:
                As[v][r][c]^=1
        s+=2
    return M0,[As[v] for v in vars_]


def homogenized_basis():
    M0,As=build_affine(); n=len(M0)
    B0=[[0]*(n+1) for _ in range(n+1)]
    B0[0][0]=1
    for i in range(n):
        for j in range(n): B0[i+1][j+1]=M0[i][j]
    Bs=[B0]
    for A in As:
        B=[[0]*(n+1) for _ in range(n+1)]
        for i in range(n):
            for j in range(n): B[i+1][j+1]=A[i][j]
        Bs.append(B)
    return Bs


def kron(A,X):
    n=len(A); d=len(X)
    R=[[0]*(len(A[0])*d) for _ in range(n*d)]
    for i in range(n):
        for j in range(len(A[0])):
            if A[i][j]&1:
                for a in range(d):
                    for b in range(d): R[i*d+a][j*d+b]^=X[a][b]&1
    return R


def xor_all(ms):
    R=[row[:] for row in ms[0]]
    for M in ms[1:]:
        for i in range(len(R)):
            R[i]=[x^y for x,y in zip(R[i],M[i])]
    return R


def main():
    # Boolean UNSAT check.
    for vals in product((0,1),repeat=4):
        assert not sat(dict(zip([1,2,3,4],vals)))

    Bs=homogenized_basis()
    # Every scalar GF(2) combination is singular.
    best=0
    for coeffs in product((0,1),repeat=5):
        M=[[0]*len(Bs[0]) for _ in range(len(Bs[0]))]
        for b,B in zip(coeffs,Bs):
            if b:
                M=[[x^y for x,y in zip(rx,ry)] for rx,ry in zip(M,B)]
        best=max(best,rank2(M))
    assert best < len(Bs[0]), (best,len(Bs[0]))

    I=[[1,0],[0,1]]
    Z=[[0,0],[0,0]]
    # Exact 2x2 blow-up witness from v1.5, order y0,x1,x2,x3,x4.
    Xs=[I, [[1,1],[1,0]], Z, Z, [[1,1],[0,0]]]
    Blow=xor_all([kron(B,X) for B,X in zip(Bs,Xs)])
    r=rank2(Blow)
    assert r==len(Blow)==22,(r,len(Blow))
    print(f'PASS: formula UNSAT; scalar max-rank={best}/11; explicit 2x2 blow-up rank={r}/22 FULL')

if __name__=='__main__': main()
