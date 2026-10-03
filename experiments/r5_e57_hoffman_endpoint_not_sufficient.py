#!/usr/bin/env python3
"""R5 E57 negative control: lambda_min=-3 / singularity is not sufficient.

Construct a simple linear square-cubic carrier A=I+P+Q on n=12 with:
  * row/column weight 3;
  * linearity (any two columns meet in at most one row);
  * rank(A)=11 over R, hence A is singular;
  * an explicit full-support real/integer kernel vector;
  * G=A^T A-3I is a simple 6-regular conflict graph;
  * lambda_min(G)=-3 exactly;
  * alpha(G)=3 < 4=n/3;
  * therefore no Exact-One solution.

This kills the shortcuts
  singular(A) => SAT,
  lambda_min(G)=-3 => SAT,
and even
  full-support ker_R(A) != empty => SAT.
"""
import itertools

P = [6, 3, 7, 10, 11, 1, 4, 8, 9, 5, 2, 0]
Q = [3, 4, 5, 8, 7, 0, 9, 6, 2, 11, 1, 10]

# Twice a rational null vector.  All coordinates are nonzero.
Z = [-1, -1, 2, -1, 2, 2, 2, -4, 2, -4, -1, 2]


def build_A(p, q):
    n = len(p)
    assert sorted(p) == list(range(n))
    assert sorted(q) == list(range(n))
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        cols = (i, p[i], q[i])
        assert len(set(cols)) == 3
        for j in cols:
            A[i][j] = 1
    return A


def matvec(A, x):
    return [sum(a * b for a, b in zip(row, x)) for row in A]


def transpose(A):
    return [list(col) for col in zip(*A)]


def matmul(A, B):
    BT = transpose(B)
    return [[sum(a * b for a, b in zip(row, col)) for col in BT] for row in A]


def rank_mod(A, p):
    M = [[v % p for v in row] for row in A]
    m = len(M)
    n = len(M[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if M[i][c] % p), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        inv = pow(M[r][c], -1, p)
        M[r] = [(v * inv) % p for v in M[r]]
        for i in range(m):
            if i != r and M[i][c] % p:
                k = M[i][c] % p
                M[i] = [(a - k * b) % p for a, b in zip(M[i], M[r])]
        r += 1
    return r


def conflict_graph(A):
    n = len(A)
    ATA = matmul(transpose(A), A)
    G = [[ATA[i][j] - (3 if i == j else 0) for j in range(n)] for i in range(n)]
    return ATA, G


def independent(G, S):
    return all(G[i][j] == 0 for i, j in itertools.combinations(S, 2))


def independence_number(G):
    n = len(G)
    best = 0
    witnesses = []
    for r in range(n + 1):
        found = []
        for S in itertools.combinations(range(n), r):
            if independent(G, S):
                found.append(S)
        if found:
            best = r
            witnesses = found
        else:
            break
    return best, witnesses


def exact_one_exists(A):
    n = len(A)
    if n % 3:
        return False
    for S in itertools.combinations(range(n), n // 3):
        x = [0] * n
        for j in S:
            x[j] = 1
        if matvec(A, x) == [1] * n:
            return True
    return False


def main():
    A = build_A(P, Q)
    n = len(A)

    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))

    ATA, G = conflict_graph(A)

    # Linearity: off-diagonal Gram entries are 0/1.
    assert all(ATA[i][i] == 3 for i in range(n))
    assert all(ATA[i][j] in (0, 1) for i in range(n) for j in range(n) if i != j)

    # Full-support kernel witness.  Hence rank_R(A) <= 11.
    assert all(z != 0 for z in Z)
    assert matvec(A, Z) == [0] * n

    # A nonzero 11x11 minor exists modulo 5, so rank_R(A) >= 11.
    # Combined with the kernel witness: rank_R(A)=11 exactly.
    assert rank_mod(A, 5) == 11

    # G is simple 6-regular and G+3I=A^T A is PSD.
    assert all(G[i][i] == 0 for i in range(n))
    assert all(G[i][j] in (0, 1) for i in range(n) for j in range(n) if i != j)
    assert all(sum(row) == 6 for row in G)

    # A Z=0 => (A^T A-3I)Z=-3Z.  Since A^T A is PSD,
    # no eigenvalue of G is below -3.  Therefore lambda_min(G)=-3 exactly.
    assert matvec(G, Z) == [-3 * z for z in Z]

    alpha, witnesses = independence_number(G)
    assert alpha == 3
    assert alpha < n // 3
    assert not exact_one_exists(A)

    print("R5 E57 Hoffman endpoint insufficiency: PASS")
    print(f"n={n}, rank(A)=11, nullity=1, lambda_min(G)=-3, alpha(G)={alpha}<4")
    print("full-support real kernel witness exists, but Exact-One is UNSAT")


if __name__ == "__main__":
    main()
