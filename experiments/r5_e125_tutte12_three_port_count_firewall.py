#!/usr/bin/env python3
"""E125: exact SUPPORT_c versus modular extension-count masks on E64/E123.

No general solver claim. E65 already proves transpose SAT asymmetry; this
replay adds exact three-port multiplicities and dual E18/KLOC3 cleanliness.
"""
from itertools import combinations, product

from r5_e64_connected_postquotient_nullity_firewall import (
    rank_q, tutte12_incidence, verify_square_cubic_linear,
)
from r5_e65_transpose_asymmetry_quantized_defect import (
    gf2_rref_basis, transpose,
)
from r5_e123_e64_tutte12_post_e18_kloc3_rebind import (
    kernel_coordinate_rows,
)

ALPHABET = (-1, 2)


def exact_witnesses_from_binary_coset(M):
    """Enumerate x=1+k, Ak=0 mod 2; |x|=n/3 iff Exact-One.

    This is an exponential finite checker (2^d), NOT a polynomial algorithm.
    """
    n = len(M)
    assert n % 3 == 0
    _, free, basis = gf2_rref_basis(M)
    assert len(free) == len(basis) == 14
    all_bits = (1 << n) - 1
    answer = []
    for mask in range(1 << len(basis)):
        x = all_bits
        for j, k in enumerate(basis):
            if (mask >> j) & 1:
                x ^= k
        if x.bit_count() == n // 3:
            # Verify witness independently over the integers, not just GF(2).
            assert all(
                sum(M[i][j] for j in range(n) if (x >> j) & 1) == 1
                for i in range(n)
            )
            answer.append(x)
    return answer


def three_port_counts(M, solutions):
    """Count satisfying extensions selecting each of a check's three ports."""
    n = len(M)
    out = []
    for row in M:
        ports = [j for j, a in enumerate(row) if a]
        assert len(ports) == 3
        ct = tuple(sum((x >> j) & 1 for x in solutions) for j in ports)
        assert sum(ct) == len(solutions)
        out.append(ct)
    return out


def dual_local_projection_check(M):
    """Verify transpose fixture's E18 and KLOC<=3 exactly.

    Kernel-coordinate rows have integer entries for this frozen fixture.
    For each nonproportional pair u,v and third row w, determine whether
    w belongs to span{u,v} by integer cross-multiplication. If yes,
    test every {-1,2}^3 corner against its exact dependence.
    Otherwise projection rank 3 gives all corners automatically.
    """
    B_frac = kernel_coordinate_rows(M)
    assert all(z.denominator == 1 for row in B_frac for z in row)
    B = [[int(z) for z in row] for row in B_frac]
    n = len(B)
    d = len(B[0])
    assert d == 14
    assert all(any(row) for row in B)

    dependent = 0
    total = 0
    for i, j in combinations(range(n), 2):
        u, v = B[i], B[j]
        pair_piv = None
        for a in range(d):
            for b in range(a + 1, d):
                det = u[a] * v[b] - u[b] * v[a]
                if det:
                    pair_piv = (a, b, det)
                    break
            if pair_piv is not None:
                break
        assert pair_piv is not None, "E18 proportional pair"
        a, b, det = pair_piv
        for k in range(j + 1, n):
            total += 1
            w = B[k]
            alpha = w[a] * v[b] - w[b] * v[a]
            beta = u[a] * w[b] - u[b] * w[a]
            if all(
                det * w[t] == alpha * u[t] + beta * v[t]
                for t in range(d)
            ):
                dependent += 1
                assert any(
                    alpha * x + beta * y - det * z == 0
                    for x, y, z in product(ALPHABET, repeat=3)
                ), "KLOC3 incompatible dependent triple"
    assert total == 39711
    assert dependent == 63
    return dependent


def main():
    R = tutte12_incidence()
    RT = transpose(R)
    for M in (R, RT):
        verify_square_cubic_linear(M, expected_girth=12)
        assert rank_q(M) == 49
        assert len(M) == 63

    # E65 contains earlier exact transpose asymmetry. This E125
    # independently replays it via the binary top-shell characterization.
    witnesses_R = exact_witnesses_from_binary_coset(R)
    witnesses_RT = exact_witnesses_from_binary_coset(RT)
    assert len(witnesses_R) == 0
    assert len(witnesses_RT) == 36

    count_R = three_port_counts(R, witnesses_R)
    count_RT = three_port_counts(RT, witnesses_RT)
    assert set(count_R) == {(0, 0, 0)}
    assert set(count_RT) == {(12, 12, 12)}

    # True Boolean masks disagree, but count mod 2 and mod 3 cannot
    # distinguish either orientation: every port coefficient is 0.
    exact_mask_R = tuple(tuple(int(z > 0) for z in ct) for ct in count_R)
    exact_mask_RT = tuple(tuple(int(z > 0) for z in ct) for ct in count_RT)
    assert set(exact_mask_R) == {(0, 0, 0)}
    assert set(exact_mask_RT) == {(1, 1, 1)}
    assert all(z % 2 == 0 and z % 3 == 0 for ct in count_RT for z in ct)

    # E123 already proves E18/KLOC3-clean for R. Extend to transpose.
    assert dual_local_projection_check(RT) == 63

    print("R5 E125 three-port extension-count firewall: PASS")
    print("R: n=63 rank_Q=49 nullity_Q=14 Exact-One=0 SUPPORT_c=000 for all c")
    print("R^T: same n/rank/girth, Exact-One=36, per-check ports=(12,12,12)")
    print("R^T SUPPORT_c=111 for all c; counts mod 2 AND mod 3=(0,0,0)")
    print("R^T: E18-clean; KLOC1/2/3-clean; dependent KLOC3 triples=63")
    print("Finite exponential enumeration only; universal symbolic SUPPORT_c OPEN")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
