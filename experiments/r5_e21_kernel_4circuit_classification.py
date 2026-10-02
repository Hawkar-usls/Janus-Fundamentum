#!/usr/bin/env python3
"""Exact finite classification for R5 E21.

Classifies every local relation

    R(c) = { y in {-1,2}^4 : c.y = 0 }

with all four coefficients of c nonzero, up to coordinate permutation.
Also verifies an abstract strictness firewall KLOC-3 < KLOC-4.

Dependency-free; exact Fraction arithmetic only.
P_VS_NP remains OPEN.
"""

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, permutations, product

SIGMA = (-1, 2)
PTS = [tuple(v) for v in product(SIGMA, repeat=4)]
PTIDX = {p: i for i, p in enumerate(PTS)}
E = [tuple(1 if j == i else 0 for j in range(4)) for i in range(4)]
PERMS = list(permutations(range(4)))


def rref(rows):
    A = [[Fraction(x) for x in row] for row in rows]
    if not A:
        return tuple()
    m, n = len(A), len(A[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if A[i][c]), None)
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        z = A[r][c]
        A[r] = [x / z for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return tuple(tuple(row) for row in A if any(row))


def rank(rows):
    return len(rref(rows))


def in_span(basis, v):
    return rank(list(basis) + [v]) == len(basis)


def canonical_span(vectors):
    return rref(vectors)


def permute_relation(R, perm):
    out = []
    for idx in R:
        p = PTS[idx]
        q = tuple(p[perm[j]] for j in range(4))
        out.append(PTIDX[q])
    return tuple(sorted(out))


def orbit_key(R):
    return min(permute_relation(R, p) for p in PERMS)


def bits(idx):
    return ''.join('1' if x == 2 else '0' for x in PTS[idx])


def classify_relations():
    # For a coefficient vector c, R(c) consists of the alphabet points in the
    # hyperplane c^perp.  If H=span(R(c)), then dim(H)<=3 and R(c)=H cap Sigma^4.
    # Thus every possible relation is obtained from a subspace H spanned by at
    # most three alphabet points.  Conversely, a generic c in H^perp realizes
    # exactly H cap Sigma^4.  Requiring every coefficient c_i != 0 is equivalent
    # to excluding subspaces H that contain a standard basis vector e_i.
    subspaces = {tuple(): 0}
    for r in (1, 2, 3):
        for inds in combinations(range(len(PTS)), r):
            H = canonical_span([PTS[i] for i in inds])
            if len(H) <= 3:
                subspaces[H] = len(H)

    relations = {}
    for H, dim in subspaces.items():
        if any(in_span(H, e) for e in E):
            continue
        R = tuple(i for i, p in enumerate(PTS) if in_span(H, p))
        relations[R] = dim

    orbits = defaultdict(list)
    for R, dim in relations.items():
        orbits[orbit_key(R)].append((R, dim))

    assert len(relations) == 114
    assert len(orbits) == 17
    assert Counter(len(k) for k in orbits) == Counter(
        {0: 1, 1: 3, 2: 5, 3: 5, 4: 2, 6: 1}
    )
    return relations, orbits


def check_kloc_strictness():
    # K = {y in Q^4 : y1+y2+y3+y4=0}, represented by y=B t.
    B = [
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
        (-1, -1, -1),
    ]

    # Every three-coordinate projection is all Q^3.
    for S in combinations(range(4), 3):
        assert rank([B[i] for i in S]) == 3

    # But no alphabet vector has coordinate sum zero:
    # sum(y) = -4 + 3*k for k entries equal to 2, never zero.
    assert [y for y in PTS if sum(y) == 0] == []


def main():
    relations, orbits = classify_relations()
    check_kloc_strictness()

    print('R5 E21 exact controls: PASS')
    print(f'eligible 4-circuit relations: {len(relations)}')
    print(f'S4 relation orbits: {len(orbits)}')
    print('orbit-size distribution:')
    dist = Counter(len(k) for k in orbits)
    for size in sorted(dist):
        print(f'  |R|={size}: {dist[size]} orbits')
    print('canonical orbit representatives:')
    for R in sorted(orbits, key=lambda z: (len(z), z)):
        print(f"  |R|={len(R)}: {[bits(i) for i in R]}")
    print('KLOC strictness: every 3-projection compatible, 4-projection empty')


if __name__ == '__main__':
    main()
