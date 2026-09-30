#!/usr/bin/env python3
"""Exact regression for the affine-F3 parallel-saturation quotient.

Finite controls only.  The arbitrary-size correctness proof is in the companion
research note.
"""

from collections import defaultdict
from itertools import combinations

P = 3

SAT_ROWS = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
    (3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
    (6,9,15),(7,8,15),(7,11,12),
]
PERM_P = [5,7,9,10,3,1,14,2,4,6,12,13,8,0,11]
PERM_Q = [12,9,14,11,13,10,7,3,1,0,2,5,6,8,4]


def matrix_from_rows(rows, n):
    return [[int(j + 1 in row) for j in range(n)] for row in rows]


def singular_unsat_matrix():
    n = 15
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in (i, PERM_P[i], PERM_Q[i]):
            A[i][j] = 1
    return A


def rref_affine(A, b, p=P):
    m = len(A)
    n = len(A[0]) if A else 0
    M = [[x % p for x in A[i]] + [b[i] % p] for i in range(m)]
    pivots = []
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if M[i][c] % p), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        inv = pow(M[r][c] % p, -1, p)
        M[r] = [(x * inv) % p for x in M[r]]
        for i in range(m):
            if i != r and M[i][c] % p:
                f = M[i][c] % p
                M[i] = [(M[i][j] - f * M[r][j]) % p for j in range(n + 1)]
        pivots.append(c)
        r += 1
    if any(all(M[i][j] == 0 for j in range(n)) and M[i][n] for i in range(r, m)):
        return None, []
    free = [j for j in range(n) if j not in pivots]
    x0 = [0] * n
    for i, c in enumerate(pivots):
        x0[c] = M[i][n]
    basis = []
    for f in free:
        v = [0] * n
        v[f] = 1
        for i, c in enumerate(pivots):
            v[c] = (-M[i][f]) % p
        basis.append(v)
    return x0, basis


def affine_functions(A):
    n = len(A[0])
    x0, basis = rref_affine(A, [1] * len(A))
    assert x0 is not None
    funcs = []
    for i in range(n):
        a = tuple(basis[t][i] % 3 for t in range(len(basis)))
        funcs.append((a, x0[i] % 3, i))
    return funcs, len(basis)


def normalize(a, c):
    if not any(a):
        return a, c % 3
    j = next(i for i, v in enumerate(a) if v)
    inv = pow(a[j], -1, 3)
    return tuple((v * inv) % 3 for v in a), (c * inv) % 3


def transform(funcs, base, basis):
    out = []
    for a, c, idx in funcs:
        c2 = (c + sum(x * y for x, y in zip(a, base))) % 3
        a2 = tuple(
            sum(a[j] * basis[t][j] for j in range(len(a))) % 3
            for t in range(len(basis))
        )
        out.append((a2, c2, idx))
    return out


def reduce_parallel(funcs, d):
    rounds = []
    while True:
        groups = defaultdict(list)
        for a, c, idx in funcs:
            if not any(a):
                if c % 3 == 0:
                    return {'status': 'UNSAT', 'reason': 'zero_constant', 'd': d, 'rounds': rounds}
                continue
            an, cn = normalize(a, c)
            forbidden = (-cn) % 3
            groups[an].append((forbidden, idx))

        pins = []
        survivors = []
        duplicate_removed = 0
        for an, vals in groups.items():
            offsets = sorted(set(v for v, _ in vals))
            if len(offsets) == 3:
                return {
                    'status': 'UNSAT', 'reason': 'three_offset_parallel_class',
                    'd': d, 'rounds': rounds, 'parallel_classes': len(groups),
                }
            if len(offsets) == 2:
                allowed = next(v for v in range(3) if v not in offsets)
                pins.append((an, allowed))
            else:
                b = offsets[0]
                survivors.append((an, (-b) % 3, vals[0][1]))
                duplicate_removed += len(vals) - 1

        if not pins:
            rounds.append({
                'd_in': d, 'parallel_classes': len(groups), 'pins': 0,
                'survivors': len(survivors), 'duplicates_removed': duplicate_removed,
                'd_out': d,
            })
            return {
                'status': 'RESIDUAL', 'd': d, 'funcs': survivors,
                'parallel_classes': len(groups), 'rounds': rounds,
            }

        base, pin_basis = rref_affine(
            [list(a) for a, _ in pins], [b for _, b in pins]
        )
        if base is None:
            return {'status': 'UNSAT', 'reason': 'inconsistent_pins', 'd': d, 'rounds': rounds}
        d_new = len(pin_basis)
        rounds.append({
            'd_in': d, 'parallel_classes': len(groups), 'pins': len(pins),
            'survivors': len(survivors), 'duplicates_removed': duplicate_removed,
            'd_out': d_new,
        })
        funcs = transform(survivors, base, pin_basis)
        d = d_new


def exact_witness_count(A):
    n = len(A[0])
    if n % 3:
        return 0
    count = 0
    for C in combinations(range(n), n // 3):
        S = set(C)
        if all(sum(row[j] for j in S) == 1 for row in A):
            count += 1
    return count


def main():
    # Synthetic two-offset class: x=0 and x=1 are forbidden, hence x=2 is pinned.
    synthetic = [
        ((1, 0), 0, 0),   # zero at x=0
        ((1, 0), 2, 1),   # zero at x=1
        ((0, 1), 0, 2),   # y != 0 survives
    ]
    syn = reduce_parallel(synthetic, 2)
    assert syn['status'] == 'RESIDUAL'
    assert syn['d'] == 1
    assert syn['rounds'][0]['pins'] == 1
    assert len(syn['funcs']) == 1

    # Synthetic full parallel class is an exact cover / UNSAT terminal.
    full = [
        ((1,), 0, 0),
        ((1,), 1, 1),
        ((1,), 2, 2),
    ]
    full_res = reduce_parallel(full, 1)
    assert full_res['status'] == 'UNSAT'
    assert full_res['reason'] == 'three_offset_parallel_class'

    # PG15 positive control: only duplicate hyperplanes disappear.
    A_sat = matrix_from_rows(SAT_ROWS, 15)
    funcs_sat, d_sat = affine_functions(A_sat)
    assert d_sat == 4
    sat = reduce_parallel(funcs_sat, d_sat)
    assert sat['status'] == 'RESIDUAL'
    assert sat['d'] == 4
    assert sat['parallel_classes'] == 11
    assert len(sat['funcs']) == 11
    assert sat['rounds'][0]['pins'] == 0
    assert sat['rounds'][0]['duplicates_removed'] == 4
    assert exact_witness_count(A_sat) == 4

    # Frozen singular UNSAT: one-dimensional affine space is covered by all
    # three offsets of one normalized normal.
    A_unsat = singular_unsat_matrix()
    funcs_unsat, d_unsat = affine_functions(A_unsat)
    assert d_unsat == 1
    unsat = reduce_parallel(funcs_unsat, d_unsat)
    assert unsat['status'] == 'UNSAT'
    assert unsat['reason'] == 'three_offset_parallel_class'
    assert exact_witness_count(A_unsat) == 0

    print({
        'status': 'PASS_AFFINE_F3_PARALLEL_SATURATION_QUOTIENT',
        'synthetic_pin_dimension': '2->1',
        'PG15_dimension': sat['d'],
        'PG15_parallel_simple_constraints': len(sat['funcs']),
        'PG15_exact_witnesses': 4,
        'singular_unsat_terminal': unsat['reason'],
        'E8_D1': 'EMPTY',
        'P_VS_NP': 'OPEN',
    })


if __name__ == '__main__':
    main()
