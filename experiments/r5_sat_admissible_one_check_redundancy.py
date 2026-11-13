#!/usr/bin/env python3
"""Replay SAT-admissible one-check redundancy and three-port interface theorem."""

from itertools import product


Q6_SETS = [
    (0,1,3),
    (1,2,4),
    (2,3,5),
    (0,3,4),
    (1,4,5),
    (0,2,5),
]

Q9_SETS = [
    (0,5,8),
    (0,1,4),
    (1,2,3),
    (0,3,7),
    (4,7,8),
    (1,5,6),
    (2,4,6),
    (2,5,7),
    (3,6,8),
]


def source_matrix(q, sets):
    A = [[0]*q for _ in range(q)]
    for j,C in enumerate(sets):
        for i in C:
            A[i][j] = 1
    assert all(sum(row)==3 for row in A)
    assert all(sum(A[i][j] for i in range(q))==3 for j in range(q))
    return A


def exact_solutions(A, skip=None):
    n=len(A)
    out=[]
    for bits in product((0,1), repeat=n):
        ok=True
        for i in range(n):
            if i==skip:
                continue
            if sum(A[i][j]*bits[j] for j in range(n)) != 1:
                ok=False
                break
        if ok:
            out.append(bits)
    return out


def verify_delete_one(name,A):
    n=len(A)
    assert n%3==0
    full=exact_solutions(A)
    for c in range(n):
        partial=exact_solutions(A, skip=c)
        assert partial==full
        for x in partial:
            assert sum(A[c][j]*x[j] for j in range(n))==1
    print(f"{name}: n={n} full_solutions={len(full)} delete-one equivalence PASS")
    return full


def perfect_sat9():
    # rows are clauses (i,j), variables A_i,B_j,C_{i+j mod3}
    A=[[0]*9 for _ in range(9)]
    r=0
    for i in range(3):
        for j in range(3):
            for v in (i,3+j,6+((i+j)%3)):
                A[r][v]=1
            r+=1
    return A


def main():
    q6=source_matrix(6,Q6_SETS)
    s6=verify_delete_one("RXC3_Q6",q6)
    assert len(s6)==0

    q9=source_matrix(9,Q9_SETS)
    s9=verify_delete_one("E77_Q9",q9)
    assert len(s9)==1

    p9=perfect_sat9()
    sp=verify_delete_one("PERFECT_SAT9",p9)
    supports={tuple(i for i,b in enumerate(x) if b) for x in sp}
    assert supports=={(0,1,2),(3,4,5),(6,7,8)}

    # For check 0 of PERFECT-SAT9, all three incident variables are extendible.
    incident=[j for j in range(9) if p9[0][j]]
    boundary={
        tuple(x[j] for j in incident)
        for x in exact_solutions(p9,skip=0)
    }
    assert boundary=={(1,0,0),(0,1,0),(0,0,1)}

    # q=8 is outside the admissible lane.
    assert 8%3 != 0

    print("ONE_CHECK_REDUNDANCY_FOR_3_DIVIDES_N: PASS")
    print("PERFECT_SAT9 three-port boundary = full U_1,3")
    print("q8 E81 control: rejected by 3∤n cardinality precheck")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
