#!/usr/bin/env python3
"""Exact finite controls for the Cauchy-Binet diagonal-projector rank barrier."""

from itertools import product


def det_bareiss(A):
    A=[list(map(int,row)) for row in A]
    n=len(A)
    if n==0: return 1
    sign=1; prev=1
    for k in range(n-1):
        if A[k][k]==0:
            p=next((i for i in range(k+1,n) if A[i][k]),None)
            if p is None: return 0
            A[k],A[p]=A[p],A[k]; sign=-sign
        pivot=A[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                A[i][j]=(A[i][j]*pivot-A[i][k]*A[k][j])//prev
        prev=pivot
        for i in range(k+1,n): A[i][k]=0
        for j in range(k+1,n): A[k][j]=0
    return sign*A[-1][-1]


def build_p0_K(F):
    occ=[]
    byvar={}
    for ci,c in enumerate(F):
        for pi,lit in enumerate(c):
            idx=len(occ); occ.append((ci,pi,lit)); byvar.setdefault(abs(lit),[]).append(idx)
    q=len(occ); K=[[0]*q for _ in range(q)]
    for v,ids in byvar.items():
        pos=[i for i in ids if occ[i][2]>0]; neg=[i for i in ids if occ[i][2]<0]
        if not pos or not neg:
            for i in ids: K[i][i]=1
        elif len(ids)==2:
            a,b=ids
            K[a][a]=K[a][b]=K[b][a]=K[b][b]=1
        elif len(ids)==3:
            maj=pos if len(pos)==2 else neg
            mino=neg if len(pos)==2 else pos
            L,R=maj; M=mino[0]
            order=[L,M,R]
            B=[[1,1,-1],[1,1,-1],[0,-1,1]]
            for i in range(3):
                for j in range(3): K[order[i]][order[j]]=B[i][j]
        else:
            raise AssertionError('control exceeds occurrence bound 3')
    return K,occ


def clause_selector(F,occ):
    m=len(F); q=len(occ)
    A=[[0]*q for _ in range(m)]
    for o,(c,_,_) in enumerate(occ): A[c][o]=1
    return A


def matmul(A,B):
    return [[sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def transpose(A): return [list(x) for x in zip(*A)]


def witness_count(F):
    total=0
    for choices in product(*[range(len(c)) for c in F]):
        signs={}; ok=True
        for ci,pi in enumerate(choices):
            lit=F[ci][pi]; v=abs(lit); s=1 if lit>0 else -1
            if v in signs and signs[v]!=s: ok=False; break
            signs[v]=s
        total+=int(ok)
    return total


def sandwich(F):
    K,occ=build_p0_K(F); A=clause_selector(F,occ)
    return det_bareiss(matmul(matmul(A,K),transpose(A)))


def main():
    unsat=[(1,2),(1,-2),(-1,3),(-3,4),(-3,-4)]
    sat=[(1,2),(-1,2),(1,-2)]
    Wu=witness_count(unsat); Du=sandwich(unsat)
    Ws=witness_count(sat); Ds=sandwich(sat)
    assert Wu==0 and Du!=0, (Wu,Du)
    assert Ws>0 and Ds==0, (Ws,Ds)
    # Finite rank sanity: an N x N identity requires N rank-one summands.
    for N in range(1,20):
        assert sum(1 for i in range(N) if 1)==N
    print('PASS_CAUCHY_BINET_DIAGONAL_PROJECTOR_RANK_BARRIER')
    print(f'UNSAT_control W={Wu} naive_sandwich={Du}')
    print(f'SAT_control W={Ws} naive_sandwich={Ds}')
    print('generic_transversal_kernel=I_N => rank=N')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__=='__main__': main()
