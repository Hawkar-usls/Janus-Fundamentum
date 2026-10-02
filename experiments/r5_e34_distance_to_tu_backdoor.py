#!/usr/bin/env python3
"""Finite exact controls for R5 E34 distance-to-TU backdoor.

Checks small 0/1 systems A x = 1 where A is not TU but deleting one marked
variable-column gives a TU matrix.  Exhaustive branching on that one variable is
compared with full Boolean brute force.

The theorem note proves the general O(2^t poly(n)) algorithm using LP integrality
of the TU residual.

P_VS_NP remains OPEN.
"""

from itertools import combinations, product


def det_int(M):
    n=len(M)
    if n==0:
        return 1
    if n==1:
        return M[0][0]
    out=0
    for j,a in enumerate(M[0]):
        sub=[row[:j]+row[j+1:] for row in M[1:]]
        out += ((-1)**j)*a*det_int(sub)
    return out


def is_tu_bruteforce(A):
    m=len(A)
    n=len(A[0]) if m else 0
    kmax=min(m,n)
    for k in range(1,kmax+1):
        for rs in combinations(range(m),k):
            for cs in combinations(range(n),k):
                M=[[A[i][j] for j in cs] for i in rs]
                if det_int(M) not in (-1,0,1):
                    return False
    return True


def matvec(A,x):
    return [sum(a*b for a,b in zip(row,x)) for row in A]


def brute(A):
    n=len(A[0])
    rhs=[1]*len(A)
    for x in product((0,1),repeat=n):
        if matvec(A,x)==rhs:
            return True,x
    return False,None


def branch_on_columns(A,S):
    m=len(A); n=len(A[0]); rhs=[1]*m
    T=[j for j in range(n) if j not in S]
    AT=[[row[j] for j in T] for row in A]
    assert is_tu_bruteforce(AT)

    for bits in product((0,1),repeat=len(S)):
        b=rhs[:]
        for rr in range(m):
            b[rr]-=sum(A[rr][j]*bits[k] for k,j in enumerate(S))

        # Small-control stand-in for the theorem's TU LP solver:
        # brute-force the residual and compare exactly.
        for xt in product((0,1),repeat=len(T)):
            if matvec(AT,xt)==b:
                x=[0]*n
                for k,j in enumerate(S): x[j]=bits[k]
                for k,j in enumerate(T): x[j]=xt[k]
                return True,tuple(x)
    return False,None


def check_case(name,A,S):
    assert not is_tu_bruteforce(A)
    sat0,w0=brute(A)
    sat1,w1=branch_on_columns(A,S)
    assert sat0==sat1
    if sat0:
        assert matvec(A,w1)==[1]*len(A)
    print(f"{name}: full_TU=False, delete={S}, residual_TU=True, SAT={sat0}, witness={w1}")


def main():
    # Odd-cycle incidence: determinant 2, one-column deletion is TU, Exact-One UNSAT.
    A_unsat=[
        [1,1,0],
        [0,1,1],
        [1,0,1],
    ]
    check_case("triangle_unsat",A_unsat,(0,))

    # Same non-TU triangle minor plus a universal fourth column.
    # x4=1, x1=x2=x3=0 is an Exact-One witness.
    A_sat=[
        [1,1,0,1],
        [0,1,1,1],
        [1,0,1,1],
    ]
    check_case("triangle_plus_selector_sat",A_sat,(0,))

    # Two disjoint odd-cycle blocks need two backdoor columns.
    A2=[]
    for block in range(2):
        for row in ((1,1,0),(0,1,1),(1,0,1)):
            A2.append(([0]*3*block)+list(row)+([0]*3*(1-block)))
    check_case("two_triangle_blocks",A2,(0,3))

    print("R5 E34 distance-to-TU backdoor controls: PASS")
    print("Scientific ceiling: P_VS_NP remains OPEN.")


if __name__ == "__main__":
    main()
