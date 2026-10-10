#!/usr/bin/env python3
"""Independent replay for the E8 Cauchy-Binet Boolean selector.

Checks:
1. Exact selector identity on deterministic integer matrices.
2. Exhaustive GF(2) falsifier for the 3-variable NAE truth table.
3. Explicit GF(3) control showing the GF(2) falsifier is field-specific.
"""

from itertools import combinations, product
from random import Random


def det_int(M):
    """Bareiss exact determinant for small integer matrices."""
    n = len(M)
    if n == 0:
        return 1
    A = [list(map(int, row)) for row in M]
    sign = 1
    prev = 1
    for k in range(n - 1):
        if A[k][k] == 0:
            pivot = next((r for r in range(k + 1, n) if A[r][k] != 0), None)
            if pivot is None:
                return 0
            A[k], A[pivot] = A[pivot], A[k]
            sign *= -1
        pivot = A[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                A[i][j] = (A[i][j] * pivot - A[i][k] * A[k][j]) // prev
        prev = pivot
    return sign * A[n - 1][n - 1]


def matmul(A, B):
    return [[sum(a * b for a, b in zip(row, col)) for col in zip(*B)] for row in A]


def selector_A(n):
    A = [[0] * (2 * n) for _ in range(n)]
    for i in range(n):
        A[i][2 * i] = 1
        A[i][2 * i + 1] = 1
    return A


def selected_minor(B, bits):
    rows = [B[2 * i + bits[i]] for i in range(len(bits))]
    return det_int(rows)


def replay_selector_identity():
    rng = Random(0xE8C0B1)
    receipts = []
    for n in range(1, 6):
        A = selector_A(n)
        for trial in range(12):
            B = [[rng.randint(-3, 3) for _ in range(n)] for __ in range(2 * n)]
            lhs = det_int(matmul(A, B))
            rhs = sum(selected_minor(B, bits) for bits in product((0, 1), repeat=n))
            assert lhs == rhs, (n, trial, lhs, rhs)
        receipts.append((n, 12))
    return receipts


def det3_mod(rows, p):
    a = rows
    return (
        a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
        - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
        + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])
    ) % p


ASSIGN3 = list(product((0, 1), repeat=3))


def support_mask_mod(rows, p):
    mask = 0
    values = []
    for idx, bits in enumerate(ASSIGN3):
        d = det3_mod([rows[2 * i + bits[i]] for i in range(3)], p)
        values.append(d)
        if d:
            mask |= 1 << idx
    return mask, values


def exhaustive_gf2_nae_falsifier():
    # Assignment order: 000,001,010,011,100,101,110,111.
    # NAE3 is true exactly on indices 1..6 => mask 0b01111110 = 126.
    target = 0b01111110
    reachable = set()
    for code in range(1 << 18):
        rows = []
        for r in range(6):
            v = (code >> (3 * r)) & 0b111
            rows.append([(v >> j) & 1 for j in range(3)])
        mask, _ = support_mask_mod(rows, 2)
        reachable.add(mask)
    assert target not in reachable
    assert len(reachable) == 244
    return len(reachable), target


def gf3_control():
    # Explicit control found independently: NAE3 support is representable over GF(3).
    rows = [
        [1, 0, 0], [1, 1, 1],
        [0, 1, 0], [1, 1, 2],
        [1, 2, 0], [0, 0, 1],
    ]
    mask, values = support_mask_mod(rows, 3)
    assert mask == 0b01111110
    assert values[0] == 0 and values[7] == 0
    assert all(values[i] != 0 for i in range(1, 7))
    return values


def main():
    receipts = replay_selector_identity()
    reachable_count, target = exhaustive_gf2_nae_falsifier()
    gf3_values = gf3_control()
    print("E8_CAUCHY_BINET_BOOLEAN_SELECTOR replay: PASS")
    print("selector identity trials:", receipts)
    print("GF(2) reachable 3-variable support masks:", reachable_count, "/ 256")
    print("GF(2) NAE target mask absent:", target)
    print("GF(3) NAE control determinant values:", gf3_values)
    print("NOTE: selector identity is symbolic via Cauchy-Binet; finite checks are replay only.")


if __name__ == "__main__":
    main()
