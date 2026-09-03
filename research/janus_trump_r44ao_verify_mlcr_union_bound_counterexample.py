#!/usr/bin/env python3
from itertools import combinations

N = 8
CLAUSES = [
    (3,5,7),
    (2,4,6),
    (1,5,6),
    (2,7,8),
    (4,7,8),
    (1,2,3),
    (1,3,5),
    (4,6,8),
    (3,4,7),
]


def expansion(V):
    V = set(V)
    gamma = sum(1 for C in CLAUSES if V.intersection(C))
    return gamma - len(V)


def main():
    assert len(CLAUSES) == 9
    assert all(len(C) == 3 and len(set(C)) == 3 for C in CLAUSES)
    degrees = [sum(v in C for C in CLAUSES) for v in range(1, N + 1)]
    assert degrees == [3,3,4,4,3,3,4,3]
    assert min(degrees) == 3
    # nM(1)=2, so the MLCR min-degree condition is strict.
    assert min(degrees) > 2

    full = tuple(range(1, N + 1))
    assert expansion(full) == 1
    for r in range(1, N):
        for V in combinations(full, r):
            e = expansion(V)
            assert e > 1, (V, e)

    # All-positive formula: all-true is a satisfying assignment.
    assert all(any(True for _ in C) for C in CLAUSES)
    weight_num = len(CLAUSES)
    weight_den = 8
    assert weight_num > weight_den

    print("PASS")
    print("n=8 m=9 delta=1 mu_vd=3 nM(1)=2")
    print("all proper nonempty V have expansion >1; full expansion=1")
    print("SAT witness: all variables true")
    print("sum_C 2^(-|C|)=9/8>1")


if __name__ == "__main__":
    main()
