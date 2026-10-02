#!/usr/bin/env python3
from itertools import product, combinations
from fractions import Fraction

EDGES = [
    (2,5,6),
    (1,4,7),
    (5,7,9),
    (0,3,7),
    (4,6,9),
    (2,4,8),
    (3,8,9),
    (0,5,8),
    (1,3,6),
]
TERMINALS = (0,1,2)
N = 10


def rref(mat):
    a = [[Fraction(x) for x in row] for row in mat]
    rows, cols = len(a), len(a[0])
    pivot_row = 0
    pivots = []
    for col in range(cols-1):
        p = next((r for r in range(pivot_row, rows) if a[r][col]), None)
        if p is None:
            continue
        a[pivot_row], a[p] = a[p], a[pivot_row]
        scale = a[pivot_row][col]
        a[pivot_row] = [v/scale for v in a[pivot_row]]
        for r in range(rows):
            if r != pivot_row and a[r][col]:
                scale = a[r][col]
                a[r] = [a[r][c]-scale*a[pivot_row][c] for c in range(cols)]
        pivots.append(col)
        pivot_row += 1
        if pivot_row == rows:
            break
    return a, pivots


def main():
    deg = [0]*N
    pairs = set()
    for e in EDGES:
        assert len(e) == 3 and len(set(e)) == 3
        for v in e:
            deg[v] += 1
        for p in combinations(sorted(e), 2):
            assert p not in pairs, f"nonlinear repeated pair {p}"
            pairs.add(p)
    assert deg == [2,2,2,3,3,3,3,3,3,3], deg

    sols = []
    for bits in product((0,1), repeat=N):
        if all(sum(bits[v] for v in e) == 1 for e in EDGES):
            sols.append(bits)
    proj = {tuple(s[t] for t in TERMINALS) for s in sols}
    assert proj == {(0,0,0),(1,1,1)}, proj
    assert set(sols) == {
        (0,0,0,0,0,0,1,1,1,0),
        (0,0,0,1,1,1,0,0,0,0),
        (1,1,1,0,0,0,0,0,0,1),
    }

    # Exact rational row reduction of Ax=1.
    aug = []
    for e in EDGES:
        row = [0]*N + [1]
        for v in e:
            row[v] = 1
        aug.append(row)
    rr, pivots = rref(aug)
    assert len(pivots) == 8, pivots

    # Independently verify the claimed 2-parameter affine solution family by
    # substituting a grid of rational values; and verify every RREF equation.
    tests = [Fraction(-2), Fraction(-1,2), Fraction(0), Fraction(1,3), Fraction(1), Fraction(2)]
    for q in tests:
        for r in tests:
            x = [None]*N
            x[0]=x[1]=x[2]=x[9]=q
            x[3]=x[4]=x[5]=1-r-q
            x[6]=x[7]=x[8]=r
            assert all(sum(x[v] for v in e) == 1 for e in EDGES)
            for row in rr:
                lhs = sum(row[i]*x[i] for i in range(N))
                assert lhs == row[-1]

    print("PASS: linear cubic EQ3 regularizer")
    print("degrees:", deg)
    print("rank(A)=8, affine dimension=2")
    print("Boolean projection:", sorted(proj))
    print("Boolean extensions:", len(sols))


if __name__ == "__main__":
    main()
