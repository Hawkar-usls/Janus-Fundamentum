#!/usr/bin/env python3
"""Exact regression audit: Boben (v_3) graph reduction is not Exact-One preserving.

Checks two explicit legal adjacent reductions:
  9_3 SAT -> 8_3 UNSAT
 10_3 UNSAT -> 9_3 SAT

All graph checks are exact and dependency-free; witness counts are exhaustive for
these tiny frozen controls.
"""

from itertools import product


def matrix_from_supports(n, supports):
    A = [[0] * n for _ in range(n)]
    for i, row in enumerate(supports):
        for j in row:
            A[i][j] = 1
    return A


def validate_carrier(A):
    n = len(A)
    assert all(len(row) == n for row in A)
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))

    supports = [{j for j, bit in enumerate(row) if bit} for row in A]
    for i in range(n):
        for k in range(i):
            assert len(supports[i] & supports[k]) <= 1

    seen = {('r', 0)}
    stack = [('r', 0)]
    while stack:
        typ, u = stack.pop()
        if typ == 'r':
            for c, bit in enumerate(A[u]):
                if bit and ('c', c) not in seen:
                    seen.add(('c', c))
                    stack.append(('c', c))
        else:
            for r in range(n):
                if A[r][u] and ('r', r) not in seen:
                    seen.add(('r', r))
                    stack.append(('r', r))
    assert len(seen) == 2 * n


def exact_one(A, x):
    return all(sum(bit * x[j] for j, bit in enumerate(row)) == 1 for row in A)


def all_witnesses(A):
    n = len(A)
    return [x for x in product((0, 1), repeat=n) if exact_one(A, x)]


def reduce_adjacent(A, remove_row, remove_col, pairs):
    """Delete an adjacent row/column and reconnect remaining neighbors.

    pairs are old-index (row, column) new edges.  The caller freezes the legal
    Boben pairing; this routine independently checks that it uses precisely the
    remaining neighbor sets and yields a valid carrier.
    """
    n = len(A)
    assert A[remove_row][remove_col] == 1

    rem_cols = {j for j in range(n) if A[remove_row][j] and j != remove_col}
    rem_rows = {i for i in range(n) if A[i][remove_col] and i != remove_row}
    assert len(rem_cols) == len(rem_rows) == 2
    assert {r for r, _ in pairs} == rem_rows
    assert {c for _, c in pairs} == rem_cols

    rows = [i for i in range(n) if i != remove_row]
    cols = [j for j in range(n) if j != remove_col]
    rmap = {old: new for new, old in enumerate(rows)}
    cmap = {old: new for new, old in enumerate(cols)}

    B = [[A[r][c] for c in cols] for r in rows]
    for r, c in pairs:
        assert A[r][c] == 0, 'Boben reconnection must not create a parallel edge'
        B[rmap[r]][cmap[c]] = 1

    validate_carrier(B)
    return B


def supports(A):
    return [tuple(j for j, bit in enumerate(row) if bit) for row in A]


def control_sat_to_unsat():
    src_supports = [
        (0, 2, 4),
        (0, 1, 6),
        (2, 6, 8),
        (1, 3, 4),
        (4, 5, 7),
        (2, 3, 5),
        (3, 6, 7),
        (0, 7, 8),
        (1, 5, 8),
    ]
    A = matrix_from_supports(9, src_supports)
    validate_carrier(A)
    ws = all_witnesses(A)
    assert len(ws) == 1
    assert tuple(i for i, bit in enumerate(ws[0]) if bit) == (1, 2, 7)

    B = reduce_adjacent(A, 0, 2, [(2, 4), (5, 0)])
    expected_reduced = [
        (0, 1, 5),
        (3, 5, 7),
        (1, 2, 3),
        (3, 4, 6),
        (0, 2, 4),
        (2, 5, 6),
        (0, 6, 7),
        (1, 4, 7),
    ]
    assert supports(B) == expected_reduced
    wB = all_witnesses(B)
    assert len(wB) == 0
    return len(ws), len(wB)


def control_unsat_to_sat():
    src_supports = [
        (0, 3, 5),
        (0, 1, 2),
        (2, 4, 7),
        (2, 3, 6),
        (0, 4, 9),
        (1, 4, 5),
        (6, 7, 9),
        (3, 7, 8),
        (1, 6, 8),
        (5, 8, 9),
    ]
    A = matrix_from_supports(10, src_supports)
    validate_carrier(A)
    ws = all_witnesses(A)
    assert len(ws) == 0

    B = reduce_adjacent(A, 2, 2, [(1, 7), (3, 4)])
    expected_reduced = [
        (0, 2, 4),
        (0, 1, 6),
        (2, 3, 5),
        (0, 3, 8),
        (1, 3, 4),
        (5, 6, 8),
        (2, 6, 7),
        (1, 5, 7),
        (4, 7, 8),
    ]
    assert supports(B) == expected_reduced
    wB = all_witnesses(B)
    assert len(wB) == 1
    assert tuple(i for i, bit in enumerate(wB[0]) if bit) == (1, 2, 8)
    return len(ws), len(wB)


def local_adjacent_relation():
    tuples = []
    for a, b, c, d, s in product((0, 1), repeat=5):
        eq3 = (a == b == s)
        ex1 = (c + d + s == 1)
        if eq3 and ex1:
            tuples.append((a, b, c, d))
    tuples = sorted(set(tuples))
    assert tuples == [(0, 0, 0, 1), (0, 0, 1, 0), (1, 1, 0, 0)]

    # A Cartesian product across either Boben pairing would have size
    # |R1|*|R2|.  Because the relation has prime cardinality 3, factorization
    # would force one factor to have one tuple.  But projections onto both
    # paired coordinate-pairs have >1 tuple, ruling that out.
    for pairing in [((0, 2), (1, 3)), ((0, 3), (1, 2))]:
        p1 = {tuple(t[i] for i in pairing[0]) for t in tuples}
        p2 = {tuple(t[i] for i in pairing[1]) for t in tuples}
        assert len(p1) > 1 and len(p2) > 1
        assert len(p1) * len(p2) != len(tuples)
    return tuples


def main():
    r1 = control_sat_to_unsat()
    r2 = control_unsat_to_sat()
    rel = local_adjacent_relation()
    print('PASS R5_E9_BOBEN_REDUCTION_SEMANTIC_AUDIT')
    print('SAT_TO_UNSAT witness_counts =', r1)
    print('UNSAT_TO_SAT witness_counts =', r2)
    print('adjacent_contracted_relation =', rel)
    print('NAIVE_BOBEN_EXACTONE_PRESERVATION = FALSIFIED_BOTH_DIRECTIONS')
    print('BOBEN_SEMANTIC_LIFT_STATE_GROWTH = OPEN')
    print('P_VS_NP = OPEN')


if __name__ == '__main__':
    main()
