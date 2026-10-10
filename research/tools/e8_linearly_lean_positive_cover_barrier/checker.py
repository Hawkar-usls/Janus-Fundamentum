#!/usr/bin/env python3
import itertools
from fractions import Fraction


def parity_cnf(vars_, charge):
    clauses = []
    for bits in itertools.product((0, 1), repeat=len(vars_)):
        if sum(bits) % 2 != charge:
            clause = []
            for v, bit in zip(vars_, bits):
                clause.append(v + 1 if bit == 0 else -(v + 1))
            clauses.append(tuple(clause))
    return clauses


def k4_tseitin():
    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    inc = {v: [] for v in range(4)}
    for i, (u, v) in enumerate(edges):
        inc[u].append(i)
        inc[v].append(i)
    charges = [1, 0, 0, 0]
    clauses = []
    blocks = []
    for v in range(4):
        block = parity_cnf(inc[v], charges[v])
        blocks.append(block)
        clauses.extend(block)
    return clauses, blocks


def signed_matrix(clauses, nvars):
    A = []
    for clause in clauses:
        row = [0] * nvars
        for lit in clause:
            row[abs(lit) - 1] = 1 if lit > 0 else -1
        A.append(row)
    return A


def rank_q(A):
    M = [[Fraction(x) for x in row] for row in A]
    if not M:
        return 0
    m, n = len(M), len(M[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if M[i][c]), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        p = M[r][c]
        M[r] = [x / p for x in M[r]]
        for i in range(m):
            if i != r and M[i][c]:
                q = M[i][c]
                M[i] = [a - q * b for a, b in zip(M[i], M[r])]
        r += 1
        if r == m:
            break
    return r


def falsified(clause, assignment):
    for lit in clause:
        bit = assignment[abs(lit) - 1]
        truth = bit == 1
        if lit < 0:
            truth = not truth
        if truth:
            return 0
    return 1


def main():
    clauses, blocks = k4_tseitin()
    assert len(clauses) == 16
    A = signed_matrix(clauses, 6)

    # Strict positive dual certificate y=all ones: A^T y=0 and full column rank.
    for j in range(6):
        assert sum(row[j] for row in A) == 0
    assert rank_q(A) == 6

    # Local parity block forces its three coordinates to zero in the linear-autarky cone.
    blockA = signed_matrix(blocks[0], 6)
    support = sorted({abs(lit) - 1 for c in blocks[0] for lit in c})
    local = [[row[j] for j in support] for row in blockA]
    assert sorted(local) == sorted([[1,1,1],[1,-1,-1],[-1,1,-1],[-1,-1,1]])
    # These explicit row-pair sums certify z_i>=0 and z_i<=0 for each local coordinate.
    pair_sums = {tuple(a+b for a,b in zip(local[i], local[j])) for i in range(4) for j in range(i+1,4)}
    for k in range(3):
        plus = tuple(2 if i == k else 0 for i in range(3))
        minus = tuple(-2 if i == k else 0 for i in range(3))
        assert plus in pair_sums
        assert minus in pair_sums

    # Three-assignment Farkas functional against nonnegative exact-cover identity.
    a0 = (0,1,0,0,0,0)
    a1 = (0,1,0,0,1,0)
    a2 = (0,1,0,0,1,1)
    Lvals = []
    for clause in clauses:
        L = -falsified(clause, a0) + falsified(clause, a1) - falsified(clause, a2)
        assert L >= 0
        Lvals.append(L)
    assert set(Lvals) <= {0,1}
    assert sum(Lvals) == 1
    assert -1 + 1 - 1 == -1  # L(1)=-1

    # Odd-charge parity contradiction replay.
    for assignment in itertools.product((0,1), repeat=6):
        assert any(falsified(c, assignment) for c in clauses)

    print("PASS K4 odd-Tseitin is linearly-lean: rank(A)=6 and A^T*1=0")
    print("PASS local parity block explicitly forces all three autarky coordinates to zero")
    print("PASS 3-assignment Farkas functional forbids nonnegative exact constant cover")


if __name__ == '__main__':
    main()
