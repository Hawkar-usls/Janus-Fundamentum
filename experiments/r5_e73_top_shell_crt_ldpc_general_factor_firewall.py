#!/usr/bin/env python3
"""R5 E73 exact controls: cross-field synchronization collapses at the F2 top shell.

For every square cubic 0/1 matrix A and every binary vector k, put x=1-k.
Because each row and column of A has sum three, the following are equivalent:

  (1) A k = 0 (mod 2) and |k| = 2n/3;
  (2) A k = 2*1 over the integers;
  (3) A k = 2*1 (mod 6);
  (4) A k = 0 (mod 2) and A k = 2*1 (mod 3);
  (5) A x = 1 over the integers (Exact-One).

The only nontrivial implication is (1)->(2): binary parity makes every integer
row sum of A k equal to 0 or 2.  Column cubicity gives

    sum_i (A k)_i = 3|k| = 2n.

All n summands are at most two, so every one must be exactly two.  Therefore
F3 adds no pruning after a binary codeword has reached the E58 top shell.

Coding view.  C=ker_F2(A) and A*1=1 over F2, so the syndrome-one coset is
1+C and

    delta_1(A) := min{|x| : A x = 1 mod 2}
                = n - max{|k| : k in C}
                >= n/3.

Exact-One is equivalent to equality delta_1(A)=n/3.

Factor/Holant view.  In the cubic Tanner graph, an Exact-One witness is exactly
a General Factor with degree list {1} on check vertices and {0,3} on variable
vertices.  Equivalently it is a feasible assignment for the 3-regular
bipartite Holant signature pair ExactOne_3 | Equality_3.

This checker exhausts SAT/UNSAT n=12 controls, a connected linear n=9 positive
control, and the actual frozen E12 n=102 hardness target.  On the latter the
binary kernel has dimension 12, so all 4096 codewords are replayed exactly.

Scientific ceiling: this is an exact equivalence/firewall.  It does NOT give a
polynomial algorithm.  It shows that the naive F2+F3 cross-field attack does
not shrink the decisive shell; the remaining difficulty is the same all-or-none
{0,3} variable constraint / top-shell codeword problem.  P_VS_NP remains OPEN.
"""

from itertools import product

from r5_e17_hardness_kernel_quotient import (
    natural_target_matrix,
    rx_fixture,
    source_matrix,
    transform_rx,
)
from r5_e61_two_level_kernel_hoffman_regular_set import (
    P_SAT,
    Q_SAT,
    P_UNSAT,
    Q_UNSAT,
    build_A,
)


def matvec(A, x):
    return [sum(a * b for a, b in zip(row, x)) for row in A]


def verify_square_cubic(A, require_linear=False):
    n = len(A)
    assert n > 0 and all(len(row) == n for row in A)
    assert all(v in (0, 1) for row in A for v in row)
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))
    if require_linear:
        for a in range(n):
            for b in range(a + 1, n):
                assert sum(A[i][a] * A[i][b] for i in range(n)) <= 1


def gf2_kernel_basis(A):
    m = len(A)
    n = len(A[0])
    rows = []
    for row in A:
        z = 0
        for j, v in enumerate(row):
            if v & 1:
                z |= 1 << j
        rows.append(z)

    pivots = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if (rows[i] >> c) & 1), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(m):
            if i != r and ((rows[i] >> c) & 1):
                rows[i] ^= rows[r]
        pivots.append(c)
        r += 1
        if r == m:
            break

    free = [c for c in range(n) if c not in pivots]
    basis = []
    for f in free:
        v = 1 << f
        for rr, p in enumerate(pivots):
            if (rows[rr] >> f) & 1:
                v |= 1 << p
        basis.append(v)
    return basis


def enumerate_kernel_words(A):
    basis = gf2_kernel_basis(A)
    words = []
    for mask in range(1 << len(basis)):
        v = 0
        for j, b in enumerate(basis):
            if (mask >> j) & 1:
                v ^= b
        words.append(v)
    return basis, words


def bits_from_mask(mask, n):
    return [(mask >> j) & 1 for j in range(n)]


def equivalence_flags(A, k):
    n = len(A)
    Ak = matvec(A, k)
    x = [1 - z for z in k]

    top_shell_binary = (
        all(v % 2 == 0 for v in Ak)
        and 3 * sum(k) == 2 * n
    )
    integer_two = Ak == [2] * n
    mod_six = all(v % 6 == 2 for v in Ak)
    synchronized_2_3 = all((v % 2 == 0) and (v % 3 == 2) for v in Ak)
    exact_one = matvec(A, x) == [1] * n

    return top_shell_binary, integer_two, mod_six, synchronized_2_3, exact_one


def check_pointwise_equivalence(A):
    n = len(A)
    witness_count = 0
    for k in product((0, 1), repeat=n):
        flags = equivalence_flags(A, k)
        assert len(set(flags)) == 1
        witness_count += int(flags[0])
    return witness_count


def factor_degree_profile(A, x):
    """Select all three Tanner incidences of every variable with x_j=1."""
    n = len(A)
    check_degrees = [0] * n
    variable_degrees = [0] * n
    for i in range(n):
        for j in range(n):
            if A[i][j] and x[j]:
                check_degrees[i] += 1
                variable_degrees[j] += 1
    return check_degrees, variable_degrees


def check_factor_holant_witness(A, x):
    check_degrees, variable_degrees = factor_degree_profile(A, x)
    assert check_degrees == [1] * len(A)
    assert all(v in (0, 3) for v in variable_degrees)

    # Equality_3 on every variable vertex means its three incident edge bits
    # are all x_j; ExactOne_3 on every check vertex is exactly degree one.
    for j, d in enumerate(variable_degrees):
        assert d == 3 * x[j]


def exact_shell_profile(A):
    n = len(A)
    basis, words = enumerate_kernel_words(A)
    max_weight = max(v.bit_count() for v in words)
    top = 2 * n // 3 if (2 * n) % 3 == 0 else None
    top_words = [v for v in words if top is not None and v.bit_count() == top]

    # Since A*1=1 over F2, the complete syndrome-one coset is 1+C.
    # Complementing a codeword changes weight w to n-w.
    delta_one = n - max_weight
    assert delta_one * 3 >= n

    for v in top_words:
        k = bits_from_mask(v, n)
        assert all(equivalence_flags(A, k))
        x = [1 - z for z in k]
        check_factor_holant_witness(A, x)

    return {
        "dimension": len(basis),
        "code_size": len(words),
        "max_weight": max_weight,
        "top_weight": top,
        "top_words": len(top_words),
        "delta_one": delta_one,
    }


def small_controls():
    A_sat = build_A(P_SAT, Q_SAT)
    A_unsat = build_A(P_UNSAT, Q_UNSAT)
    verify_square_cubic(A_sat, require_linear=True)
    verify_square_cubic(A_unsat, require_linear=True)

    sat_pointwise = check_pointwise_equivalence(A_sat)
    unsat_pointwise = check_pointwise_equivalence(A_unsat)
    sat_profile = exact_shell_profile(A_sat)
    unsat_profile = exact_shell_profile(A_unsat)

    assert sat_pointwise == sat_profile["top_words"] == 1
    assert unsat_pointwise == unsat_profile["top_words"] == 0
    assert sat_profile["delta_one"] == len(A_sat) // 3 == 4
    assert unsat_profile["delta_one"] > len(A_unsat) // 3

    # Independent connected linear positive control with a unique exact cover
    # {1,7,8}.  It also freezes the theorem away from the E61 permutation data.
    s9 = [
        (0, 5, 8),
        (0, 1, 4),
        (1, 2, 3),
        (0, 3, 7),
        (4, 7, 8),
        (1, 5, 6),
        (2, 4, 6),
        (2, 5, 7),
        (3, 6, 8),
    ]
    A9 = source_matrix(9, s9)
    verify_square_cubic(A9, require_linear=True)
    q9_pointwise = check_pointwise_equivalence(A9)
    q9_profile = exact_shell_profile(A9)
    assert q9_pointwise == q9_profile["top_words"] == 1

    exact9 = []
    for x in product((0, 1), repeat=9):
        if matvec(A9, x) == [1] * 9:
            exact9.append(tuple(i for i, z in enumerate(x) if z))
    assert exact9 == [(1, 7, 8)]

    return sat_profile, unsat_profile, q9_profile


def e12_hardness_control():
    q, source_sets = rx_fixture()
    assert q == 6
    B = natural_target_matrix(transform_rx(q, source_sets))
    verify_square_cubic(B, require_linear=True)
    assert len(B) == 102

    profile = exact_shell_profile(B)
    assert profile["dimension"] == 12
    assert profile["code_size"] == 4096
    assert profile["top_weight"] == 68
    assert profile["max_weight"] == 60
    assert profile["top_words"] == 0
    assert profile["delta_one"] == 42
    assert profile["delta_one"] > len(B) // 3

    # The source fixture itself is an independent UNSAT witness for the E12
    # reduction.  Exhaustion costs only 2^6.
    R = source_matrix(q, source_sets)
    source_exact = 0
    for x in product((0, 1), repeat=q):
        source_exact += int(matvec(R, x) == [1] * q)
    assert source_exact == 0

    return profile


def main():
    sat12, unsat12, q9 = small_controls()
    e12 = e12_hardness_control()

    print("R5 E73 top-shell CRT / LDPC / General-Factor firewall: PASS")
    print("equivalence: F2 top shell <=> Ak=2*1 over Z <=> Ak=2 mod 6 <=> F2+F3 same-support <=> Exact-One")
    print("coding identity: delta_1(A)=n-maxwt(ker_F2 A)>=n/3; equality iff Exact-One SAT")
    print("factor identity: check degrees {1}, variable degrees {0,3}; Holant ExactOne_3 | Equality_3")
    print("SAT12:", sat12)
    print("UNSAT12:", unsat12)
    print("linear Q9 SAT control:", q9)
    print("E12 N=102 UNSAT hardness target:", e12)
    print("cross-field conclusion: F3 contributes no extra pruning once an F2 codeword reaches weight 2n/3")
    print("scientific ceiling: exact equivalence/firewall only; P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
