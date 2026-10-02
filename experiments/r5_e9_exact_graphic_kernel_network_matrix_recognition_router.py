#!/usr/bin/env python3
"""Exact finite regression for the graphic-kernel/network normalization router.

Positive control: the q=11 Paley minus-two kernel, represented through a
nontrivial row-basis transform, normalizes to exactly the same network matrix
as its reduced graph incidence representation.

Negative control: the canonical PG15 rational kernel normalizes to a 4x15
{0,+-1} representation, but no one of the 125 labelled trees on five vertices
and 16 tree orientations realizes all columns as directed tree paths.
"""

from fractions import Fraction
from itertools import product
import heapq


def inv_q(M):
    n = len(M)
    a = [[Fraction(M[i][j]) for j in range(n)] +
         [Fraction(int(i == j)) for j in range(n)] for i in range(n)]
    for c in range(n):
        p = next((i for i in range(c, n) if a[i][c]), None)
        if p is None:
            raise ValueError("singular")
        a[c], a[p] = a[p], a[c]
        z = a[c][c]
        a[c] = [x / z for x in a[c]]
        for i in range(n):
            if i != c and a[i][c]:
                z = a[i][c]
                a[i] = [a[i][j] - z * a[c][j] for j in range(2 * n)]
    return [row[n:] for row in a]


def matmul(A, B):
    BT = list(zip(*B))
    return [[sum(x * y for x, y in zip(row, col)) for col in BT] for row in A]


def rank_q(M):
    a = [[Fraction(x) for x in row] for row in M]
    m = len(a)
    n = len(a[0]) if m else 0
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if a[i][c]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        z = a[r][c]
        a[r] = [x / z for x in a[r]]
        for i in range(r + 1, m):
            if a[i][c]:
                z = a[i][c]
                a[i] = [a[i][j] - z * a[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def columns(M, ids):
    return [[M[i][j] for j in ids] for i in range(len(M))]


def pivot_columns(M):
    r = len(M)
    chosen = []
    current_rank = 0
    for j in range(len(M[0])):
        trial = chosen + [j]
        rr = rank_q(columns(M, trial))
        if rr > current_rank:
            chosen = trial
            current_rank = rr
            if current_rank == r:
                break
    assert current_rank == r
    return chosen


def normalize(M, pivots):
    MT = columns(M, pivots)
    return matmul(inv_q(MT), M)


def paley11_reduced_incidence():
    q = 11
    C = []
    d = 1
    while d not in C:
        C.append(d)
        d = (-2 * d) % q
    variables = [(x, d) for d in C for x in range(q)]
    root = q - 1
    D = [[0] * len(variables) for _ in range(q - 1)]
    for j, (u, d) in enumerate(variables):
        v = (u + d) % q
        if u != root:
            D[u][j] -= 1
        if v != root:
            D[v][j] += 1
    return D


def positive_paley_control():
    D = paley11_reduced_incidence()
    assert rank_q(D) == 10

    # Deterministic nonsingular lower-triangular change of kernel basis.
    S = [[Fraction(int(i == j)) for j in range(10)] for i in range(10)]
    for i in range(1, 10):
        S[i][i - 1] = Fraction(i + 1)
    R = matmul(S, D)

    piv = pivot_columns(R)
    F = normalize(R, piv)
    Dnorm = normalize(D, piv)
    assert F == Dnorm
    assert all(x in (-1, 0, 1) for row in F for x in row)
    return piv, F


def tree_from_prufer(seq, n=5):
    deg = [1] * n
    for x in seq:
        deg[x] += 1
    leaves = [i for i, d in enumerate(deg) if d == 1]
    heapq.heapify(leaves)
    edges = []
    for x in seq:
        leaf = heapq.heappop(leaves)
        edges.append((leaf, x))
        deg[leaf] -= 1
        deg[x] -= 1
        if deg[x] == 1:
            heapq.heappush(leaves, x)
    a = heapq.heappop(leaves)
    b = heapq.heappop(leaves)
    edges.append((a, b))
    return edges


def reduced_incidence(edges, bits, root=4):
    D = [[0] * 4 for _ in range(4)]
    for j, (a, b) in enumerate(edges):
        u, v = ((a, b) if ((bits >> j) & 1) == 0 else (b, a))
        if u != root:
            D[u][j] -= 1
        if v != root:
            D[v][j] += 1
    return D


def possible_path_vectors(D, root=4):
    Di = inv_q(D)
    out = set()
    for u in range(5):
        for v in range(5):
            if u == v:
                continue
            c = [[Fraction(0)] for _ in range(4)]
            if u != root:
                c[u][0] -= 1
            if v != root:
                c[v][0] += 1
            z = matmul(Di, c)
            out.add(tuple(z[i][0] for i in range(4)))
    return out


def pg15_normalized():
    B = [
        [-1, -1,  0,  0],
        [-1,  0, -1,  0],
        [ 2,  1,  1,  0],
        [-1, -1, -1,  1],
        [-1, -1,  0,  0],
        [-1,  0, -1,  0],
        [-1,  0,  0, -1],
        [ 1,  0,  0,  0],
        [ 1,  0,  1, -1],
        [ 1,  1,  0, -1],
        [ 0,  0,  0,  1],
        [ 1,  0,  0,  0],
        [ 0,  1,  0,  0],
        [ 0,  0,  1,  0],
        [ 0,  0,  0,  1],
    ]
    R = [list(row) for row in zip(*B)]
    piv = pivot_columns(R)
    F = normalize(R, piv)
    assert all(x in (-1, 0, 1) for row in F for x in row)
    return piv, F


def small_network_realizable(F):
    wanted = [tuple(F[i][j] for i in range(4)) for j in range(len(F[0]))]
    for seq in product(range(5), repeat=3):
        edges = tree_from_prufer(seq, 5)
        for bits in range(16):
            D = reduced_incidence(edges, bits)
            try:
                paths = possible_path_vectors(D)
            except ValueError:
                continue
            if all(c in paths for c in wanted):
                return True, (seq, bits)
    return False, None


def main():
    piv, F = positive_paley_control()
    ppiv, PF = pg15_normalized()
    ok, realization = small_network_realizable(PF)
    assert not ok and realization is None

    print("Exact graphic-kernel network router regression: PASS")
    print(f"Paley11 pivot columns = {piv}")
    print("Paley11 normalized kernel == normalized incidence = PASS")
    print(f"PG15 pivot columns = {ppiv}")
    print("PG15 entries are 0,+-1 but exhaustive 5-vertex network realization = REJECT")


if __name__ == "__main__":
    main()
