#!/usr/bin/env python3
"""R5 all-size F3 exactification and connected high-corank obstruction.

RESEARCH GOAL IS STILL A PROVEN UNIVERSAL POLYNOMIAL SolveLinearCubicXSAT.
THIS SCRIPT DOES NOT CONSTRUCT THAT ALGORITHM.

Theorem A (ANY 3-positive-literal Exact-One instance, not a subclass):
For x in {0,1}^n, each row of length three has integer sum in {0,1,2,3}.
Thus Ax=1 over the integers IFF Ax=1 in F3: the only possible
integer in {0,1,2,3} congruent to 1 mod 3 is exactly 1.
The BINARY DOMAIN x_j in {0,1} remains essential.
For square row+column cubic matrices, 3*sum(x)=n; reject 3∤n.

Unlike the F2 equation Ax=1, which ALWAYS admits x=all-ones for
odd row degree three, this F3 equation is an informative polynomial
linear pre-filter. It is NOT enough to solve SAT, however:
  - A fully legal n12 SAT example and a fully legal n12 UNSAT example
    BOTH have F3 rank 11 and have CONSISTENT F3 affine equations.
  - In the UNSAT example every F3 affine solution has a coordinate 2.

Theorem B: There exist arbitrarily large CONNECTED cubic LINEAR square
positive Exact-One SAT instances with F3 nullity >= (2/9)n.
Build k>=3 disjoint 9x9 3x3-affine-grid incidence blocks, each with
F3 rank 6, then join the blocks in a cycle by k degree-preserving
two-incidence switches. Each switch is an F3 RANK-ONE matrix update;
the resulting rank is <=6k+k=7k, so F3 nullity >=2k.
The switched columns have x_j=0 in a fixed explicit SAT witness,
so that witness remains valid. For k>=3, the chosen row/column
incidences are disjoint, switches preserve pairwise linearity,
and the ring is connected. Finite independent checks k=3..6 see
rank exactly 7k; this extra equality is NOT needed for the theorem.

Therefore an "F3 Gaussian elimination then enumerate all 3^d
parameters" method still has an exponential candidate space for
legal CONNECTED SAT inputs. A clever solver may use their structure,
so this does NOT prove all polynomial algorithms impossible.

A tiny fully sound/complete but EXPONENTIAL reference enumerator is
included only as a verification oracle for future polynomial claims.
NO polynomial worst-case runtime is claimed for this reference.
P versus NP remains OPEN.
"""
from collections import Counter
from itertools import combinations,product

GRID9 = (
    (0,1,2),(0,3,6),(0,4,8),
    (3,4,5),(1,4,7),(1,5,6),
    (6,7,8),(2,5,8),(2,3,7),
)
SAT12 = (
    (0,2,7),(0,1,9),(1,2,5),(0,3,10),
    (4,10,11),(4,5,9),(3,4,6),(1,7,11),
    (3,5,8),(6,7,9),(6,8,10),(2,8,11),
)
UNSAT12 = (
    (0,7,9),(1,4,11),(1,2,9),(3,5,6),
    (4,5,7),(5,10,11),(2,4,6),(1,6,7),
    (0,2,8),(8,9,10),(0,3,10),(3,8,11),
)
GRID_SAT_COLUMNS=(2,5,8)


def incidence(rows):
    n=len(rows)
    assert n>0
    A=[[0]*n for _ in range(n)]
    for i,cols in enumerate(rows):
        assert len(cols)==3 and len(set(cols))==3
        for j in cols:
            assert 0<=j<n
            A[i][j]=1
    return A


def connected_incidence(A):
    n=len(A)
    seen={0}
    stack=[0]
    while stack:
        u=stack.pop()
        if u<n:
            nxt=(n+j for j,v in enumerate(A[u]) if v)
        else:
            nxt=(i for i in range(n) if A[i][u-n])
        for v in nxt:
            if v not in seen:
                seen.add(v);stack.append(v)
    return len(seen)==2*n


def assert_legal(A,connected=True):
    n=len(A)
    assert len(A)==n and all(len(r)==n for r in A)
    assert all(sum(r)==3 for r in A)
    assert all(sum(A[i][j] for i in range(n))==3 for j in range(n))
    assert all(
        sum(A[i][j]*A[k][j] for j in range(n))<=1
        for i in range(n) for k in range(i+1,n)
    )
    assert all(
        sum(A[i][j]*A[i][l] for i in range(n))<=1
        for j in range(n) for l in range(j+1,n)
    )
    if connected:assert connected_incidence(A)


def gf3_rref_affine(A):
    n=len(A)
    M=[list(row)+[1] for row in A]
    piv=[]
    line=0
    for j in range(n):
        k=next((i for i in range(line,n) if M[i][j]%3),None)
        if k is None:continue
        M[line],M[k]=M[k],M[line]
        scale=1 if M[line][j]%3==1 else 2
        M[line]=[(scale*v)%3 for v in M[line]]
        for i in range(n):
            if i!=line:
                factor=M[i][j]%3
                if factor:
                    M[i]=[(a-factor*b)%3
                          for a,b in zip(M[i],M[line])]
        piv.append(j);line+=1
        if line==n:break
    consistent=all(any(M[i][j] for j in range(n))
                   or M[i][-1]==0 for i in range(n))
    particular=None
    basis=[]
    if consistent:
        particular=[0]*n
        for i,p in enumerate(piv):particular[p]=M[i][-1]
        for j in range(n):
            if j in piv:continue
            v=[0]*n;v[j]=1
            for i,p in enumerate(piv):v[p]=(-M[i][j])%3
            basis.append(tuple(v))
        assert all(sum(A[i][j]*particular[j]
                       for j in range(n))%3==1 for i in range(n))
    return len(piv),consistent,particular,basis


def exact_reference_solver(A):
    """Sound+complete reference; EXPONENTIAL 3^nullity, NOT P-TIME."""
    assert_legal(A)
    n=len(A)
    if n%3:return None,0
    rank,consistent,particular,basis=gf3_rref_affine(A)
    if not consistent:return None,0
    checked=0
    for coeffs in product(range(3),repeat=len(basis)):
        checked+=1
        x=[(particular[j]+sum(t*v[j] for t,v in zip(coeffs,basis)))%3
           for j in range(n)]
        if 2 not in x:
            assert all(sum(A[i][j]*x[j] for j in range(n))==1
                       for i in range(n))
            return tuple(j for j,t in enumerate(x) if t==1),checked
    return None,checked


def ring_linear_cubic(k):
    assert k>=3
    n=9*k
    A=[[0]*n for _ in range(n)]
    for block in range(k):
        for r,cols in enumerate(GRID9):
            for c in cols:A[9*block+r][9*block+c]=1
    for block in range(k):
        neighbor=(block+1)%k
        r,c=9*block+3,9*block+3
        s,d=9*neighbor+0,9*neighbor+0
        assert A[r][c]==A[s][d]==1
        assert A[r][d]==A[s][c]==0
        A[r][c]=A[s][d]=0
        A[r][d]=A[s][c]=1
    return A


def verify():
    grid=incidence(GRID9)
    assert_legal(grid)
    r,consistent,particular,basis=gf3_rref_affine(grid)
    assert r==6 and consistent and len(basis)==3
    witness=[int(i in GRID_SAT_COLUMNS) for i in range(9)]
    assert all(sum(row[j]*witness[j] for j in range(9))==1
               for row in grid)
    print("AFFINE_GRID9_F3_RANK6_NULLITY3_SAT PASS",flush=True)

    for label,rows,expected in (
        ("SAT12",SAT12,(0,5,6,11)),
        ("UNSAT12",UNSAT12,None),
    ):
        A=incidence(rows)
        assert_legal(A)
        rank,consistent,particular,basis=gf3_rref_affine(A)
        assert rank==11 and consistent and len(basis)==1
        solution,checked=exact_reference_solver(A)
        assert solution==expected,(label,solution,expected)
        if expected is None:
            assert checked==3
            assert set(particular)=={0,1,2}
            # all-ones is F3 kernel: the three solutions are
            # particular, particular+1, particular+2.
            assert all(sum(row)%3==0 for row in A)
        else:
            assert all(sum(A[i][j] for j in solution)==1
                       for i in range(12))
        print(label,"F3_CONSISTENT_RANK11",
              "EXACT_BOOL",solution,"CHECKED",checked,
              "PASS",flush=True)

    for k in (3,4,5,6):
        A=ring_linear_cubic(k)
        assert_legal(A)
        r,_,_,basis=gf3_rref_affine(A)
        assert r==7*k,(k,r)
        assert len(basis)==2*k
        W={9*i+j for i in range(k) for j in GRID_SAT_COLUMNS}
        assert len(W)==3*k
        assert all(sum(row[j] for j in W)==1 for row in A)
        print("CONNECTED_LINEAR_RING",{
            "n":9*k, "F3_rank":r, "F3_nullity":len(basis),
            "proven_all_k_nullity_lower_bound":2*k,
            "explicit_exact_one_cover_size":len(W),
            "bruteforce_affine_candidates":3**len(basis)
        },flush=True)
    print("UNIVERSAL_GF3_BINARY_EQUIVALENCE=PROVED")
    print("CONNECTED_ALL_K_GF3_NULLITY_LINEAR=PROVED")
    print("F3_GAUSSIAN_PLUS_ENUMERATION_POLYNOMIAL=FALSE_AS_BOUND")
    print("UNIVERSAL_POLYNOMIAL_SolveLinearCubicXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    verify()
