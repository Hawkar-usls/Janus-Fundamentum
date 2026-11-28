#!/usr/bin/env python3
"""SC23: exact SUPPORT_c versus modular extension-count masks on E64/E123.

No general solver claim. E65 already proves transpose SAT asymmetry; this
replay adds exact three-port multiplicities and dual E18/KLOC3 cleanliness.
"""
from collections import Counter
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

from r5_e122_post_e18_kloc3_clean_small_nullity_unsat import lift_matrix as e122_lift_matrix
from r5_e127_tutte12_affine_support_nullity_descent import (
    affine_closure, signed_matrix, propagate, quotient,
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


def transpose_affine_signature_check(M):
    """Replay E127's complete affine closure on *SAT transpose* orientation.

    The UNSAT orientation's identical signature is already certified by E127.
    We do NOT claim quotient tensors are isomorphic, only these summary values.
    """
    n = len(M)
    clauses = [[j for j, v in enumerate(row) if v] for row in M]
    observed = Counter()
    for ports in clauses:
        for chosen in ports:
            initial = {j: int(j == chosen) for j in ports}
            out = affine_closure(clauses, n, initial)
            assert out is not None
            vals, unknown, comps, parity, compid, qtern = out
            sizes = tuple(sorted((len(comp) for comp in comps), reverse=True))
            B, rhs = signed_matrix(comps, qtern)
            r = rank_q(B)
            assert rank_q([row + [rhs[i]] for i, row in enumerate(B)]) == r
            observed[(len(unknown), len(comps), len(qtern), sizes, r, len(comps)-r)] += 1

    expected_sizes = (2,) * 12 + (1,) * 32
    expected = (56, 44, 48, expected_sizes, 34, 10)
    assert observed == Counter({expected: 189})
    return observed


def e122_all_one_check_pin_xor_exhaustion():
    """Polynomial local UNSAT route for the frozen E122 q36 carrier.

    Any solution satisfies exactly one of the three choices at every check.
    We classify the *first* contradiction at unit propagation or XOR parity.
    No exponential kernel enumeration is used for this E122 certificate.
    """
    A = e122_lift_matrix()
    n = len(A)
    assert n == 36
    clauses = [[j for j, val in enumerate(row) if val] for row in A]
    counts = Counter()
    by_check = Counter()
    for ports in clauses:
        local = Counter()
        for chosen in ports:
            init = {j: int(j == chosen) for j in ports}
            vals = propagate(clauses, n, init)
            if vals is None:
                reason = "UP"
            elif quotient(clauses, vals) is None:
                reason = "XOR"
            else:
                raise AssertionError("E122 pin branch survived UP+XOR")
            counts[reason] += 1
            local[reason] += 1
        assert sum(local.values()) == 3
        by_check[(local["UP"], local["XOR"])] += 1
    assert counts == Counter({"UP": 90, "XOR": 18})
    assert by_check == Counter({(3,0):18, (2,1):18})
    return counts, by_check


def rational_pin_rank_audit(M):
    """Explain the apparent E127 d=14 -> 10 descent by 7 forced pins.

    The kernel coordinate matrix B parametrizes y=3*x-1 in ker_Q(M).
    Restriction of its rows to the seven UP-fixed variables has rank four.
    The target affine values (-1 or 2) are Q-consistent on every branch.
    """
    B = kernel_coordinate_rows(M)
    n = len(M)
    clauses = [[j for j, a in enumerate(row) if a] for row in M]
    for ports in clauses:
        for chosen in ports:
            initial = {j: int(j == chosen) for j in ports}
            vals = propagate(clauses, n, initial)
            assert vals is not None
            fixed = [j for j, v in enumerate(vals) if v is not None]
            assert len(fixed) == 7
            local = [B[j] for j in fixed]
            assert rank_q(local) == 4
            targets = [3 * vals[j] - 1 for j in fixed]
            assert rank_q([row + [targets[k]] for k,row in enumerate(local)]) == 4
    return 14-4


def main():
    R = tutte12_incidence()
    RT = transpose(R)
    for M in (R, RT):
        verify_square_cubic_linear(M, expected_girth=12)
        assert rank_q(M) == 49
        assert len(M) == 63

    # E65 contains earlier exact transpose asymmetry. This SC23
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

    # E122 is solved for every one-check pin by immediate UP/XOR contradiction.
    e122_all_one_check_pin_xor_exhaustion()

    # E123 already proves E18/KLOC3-clean for R. Extend to transpose.
    assert dual_local_projection_check(RT) == 63
    # Check the seven pinned coordinates alone already remove rank four.
    assert rational_pin_rank_audit(R) == 10
    assert rational_pin_rank_audit(RT) == 10

    # Extend E127's UNSAT local-closure signature to SAT-transpose control.
    assert len(transpose_affine_signature_check(RT)) == 1

    print("R5 SC23 three-port extension-count firewall: PASS")
    print("E122 q36: 108/108 one-check branches fail (UP=90, XOR=18)")
    print("R: n=63 rank_Q=49 nullity_Q=14 Exact-One=0 SUPPORT_c=000 for all c")
    print("R^T: same n/rank/girth, Exact-One=36, per-check ports=(12,12,12)")
    print("R^T SUPPORT_c=111 for all c; counts mod 2 AND mod 3=(0,0,0)")
    print("R^T: E18-clean; KLOC1/2/3-clean; dependent KLOC3 triples=63")
    print("E127 UNSAT R and SC23 SAT R^T: identical 189 local affine profiles")
    print("all pinned branches: unknown=56 XOR-components=44 ternaries=48")
    print("all signed quotient matrices: rank_Q=34, residual rational nullity=10")
    print("all 189 pins per orientation: 7 fixed sites, pin projection rank=4")
    print("d=14 -> d=10 already from pins; no further Q-nullity gain from XOR")
    print("Finite exponential enumeration only; universal symbolic SUPPORT_c OPEN")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
