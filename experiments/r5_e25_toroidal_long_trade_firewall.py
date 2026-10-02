#!/usr/bin/env python3
"""Exact finite controls for R5 E25.

For the R5 E10 toroidal family with 3|k:
  * nullity_Q(A_k)=2;
  * the whole rational kernel is the residue-constant space
        y_{i,j}=u_{i-j mod 3},  u0+u1+u2=0;
  * every nonzero integer kernel trade has support at least 2n/3;
  * the non-Boolean integer solution with residue values (2,-1,0) is converted
    to the Boolean witness (1,0,0) by the global trade (-1,+1,0), whose support
    is exactly 2n/3.

Thus bounded/local-support trade descent is not universal even on SAT carriers.
P_VS_NP remains OPEN.
"""

from fractions import Fraction


def rank_q(M):
    A = [[Fraction(x) for x in row] for row in M]
    if not A:
        return 0
    m, n = len(A), len(A[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if A[i][c]), None)
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        z = A[r][c]
        A[r] = [x/z for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [A[i][j]-f*A[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def toroidal_matrix(k):
    n = k*k
    A = [[0]*n for _ in range(n)]
    def vid(i,j):
        return (i % k)*k + (j % k)
    for i in range(k):
        for j in range(k):
            r = vid(i,j)
            for v in (vid(i,j), vid(i+1,j), vid(i,j+1)):
                A[r][v] = 1
    return A


def vec_from_residues(k, vals):
    return [vals[(i-j) % 3] for i in range(k) for j in range(k)]


def matvec(A, x):
    return [sum(a*b for a,b in zip(row,x)) for row in A]


def phi(x):
    return sum(v*(v-1) for v in x)


def support(x):
    return sum(v != 0 for v in x)


def check_k(k):
    assert k % 3 == 0
    A = toroidal_matrix(k)
    n = k*k
    rank = rank_q(A)
    assert rank == n-2

    u = vec_from_residues(k, (1,-1,0))
    v = vec_from_residues(k, (1,0,-1))
    assert matvec(A,u) == [0]*n
    assert matvec(A,v) == [0]*n
    assert rank_q([[u[j],v[j]] for j in range(n)]) == 2

    # Since the displayed residue space is two-dimensional and nullity is two,
    # it is the entire rational kernel.  Any nonzero residue triple summing zero
    # has at least two nonzero entries, hence any nonzero integer trade has
    # support at least 2n/3.  The displayed u attains the bound.
    assert support(u) == 2*n//3

    x_bad = vec_from_residues(k, (2,-1,0))
    x_sat = vec_from_residues(k, (1,0,0))
    assert matvec(A,x_bad) == [1]*n
    assert matvec(A,x_sat) == [1]*n
    assert all(a in (0,1) for a in x_sat)
    assert any(a not in (0,1) for a in x_bad)

    move = [b-a for a,b in zip(x_bad,x_sat)]
    assert move == [-z for z in u]
    assert matvec(A,move) == [0]*n
    assert support(move) == 2*n//3
    assert phi(x_sat) == 0
    assert phi(x_bad) == 4*n//3

    return n, rank, support(move), phi(x_bad)


def main():
    print("R5 E25 toroidal long-trade controls: PASS")
    for k in (3,6,9):
        n, rank, supp, defect = check_k(k)
        print(f"  k={k}: n={n}, rank={rank}, nullity=2, min nonzero trade support={2*n//3}, witness move support={supp}, bad defect={defect}")
    print("Conclusion: no universal constant/log-support trade-descent theorem")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
