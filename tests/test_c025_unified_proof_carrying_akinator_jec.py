import itertools
import random

from experiments.direct.janus_unified_proof_carrying_akinator_jec import (
    apply_or_pair_via_b2_and,
    canon_cnf,
    eliminate_var_capped,
    solve_fail_closed,
    verify_or_pair_macro,
    verify_total_assignment,
)


def brute_sat(clauses):
    cnf = canon_cnf(clauses)
    variables = sorted({abs(l) for c in cnf for l in c})
    for bits in itertools.product((0, 1), repeat=len(variables)):
        a = dict(zip(variables, bits))
        if verify_total_assignment(cnf, a):
            return True, a
    return False, None


def test_sat_units():
    r = solve_fail_closed([[1], [-1, 2]])
    assert r["status"] == "SAT"
    assert r["scientific_boundary"]["heuristic_promotion"] is False


def test_unsat_units():
    r = solve_fail_closed([[1], [-1]])
    assert r["status"] == "UNSAT"
    assert r["scientific_boundary"]["general_sat_oracle"] is False


def test_no_false_unsat_on_xor_like_sat_core():
    r = solve_fail_closed([[1, 2], [-1, -2]])
    assert r["status"] == "SAT"
    assert verify_total_assignment(canon_cnf([[1, 2], [-1, -2]]), r["witness"])


def test_no_false_sat_on_unsat_2var_core():
    r = solve_fail_closed([
        [1, 2],
        [1, -2],
        [-1, 2],
        [-1, -2],
    ])
    assert r["status"] == "UNSAT"


def test_exact_elimination_is_existential_projection():
    before = canon_cnf([
        [1, 2, 3],
        [-1, 2, -3],
        [1, -2, 3],
        [-1, -2, -3],
    ])
    after, stats = eliminate_var_capped(before, 1, raw_cap=10_000)
    assert after is not None
    assert stats["aborted"] is False

    for b2, b3 in itertools.product((0, 1), repeat=2):
        remaining = {2: b2, 3: b3}
        projected = verify_total_assignment(after, remaining)
        exists = any(
            verify_total_assignment(before, {1: b1, 2: b2, 3: b3})
            for b1 in (0, 1)
        )
        assert projected == exists


def test_b2_or_pair_macro_is_conservative():
    before = canon_cnf([
        [1, 2, 3],
        [1, 2, -3],
        [-1, 4],
    ])
    after, cert = apply_or_pair_via_b2_and(before, 1, 2, 5)
    assert verify_or_pair_macro(before, after, cert)

    for bits in itertools.product((0, 1), repeat=4):
        old = {i + 1: bits[i] for i in range(4)}
        old_truth = verify_total_assignment(before, old)
        # e <-> ((not a) AND (not b))
        e = int((not bool(old[1])) and (not bool(old[2])))
        extended = dict(old)
        extended[5] = e
        assert verify_total_assignment(after, extended) == old_truth


def test_explicit_xor_gf2_lane():
    xor_one = [
        [1, 2, 3],
        [1, -2, -3],
        [-1, 2, -3],
        [-1, -2, 3],
    ]
    r = solve_fail_closed(xor_one)
    assert r["status"] == "SAT"
    assert verify_total_assignment(canon_cnf(xor_one), r["witness"])


def test_small_random_exactness_against_truth_table():
    rng = random.Random(20260826)
    for case in range(60):
        n = 4
        clauses = []
        for _ in range(10):
            variables = rng.sample(range(1, n + 1), 3)
            clause = [v if rng.randrange(2) else -v for v in variables]
            clauses.append(clause)
        expected, _ = brute_sat(clauses)
        r = solve_fail_closed(clauses, cap_exponent=2, extension_exponent=1)
        assert r["scientific_boundary"]["heuristic_promotion"] is False
        if r["status"] == "OPEN":
            continue
        assert (r["status"] == "SAT") == expected, (case, clauses, r)
        if r["status"] == "SAT":
            assert verify_total_assignment(canon_cnf(clauses), r["witness"])


def test_tiny_cap_can_only_refuse_not_guess():
    hardish = [
        [1, 2, 3, 4], [-1, -2, 3, 4], [1, -2, -3, 4], [-1, 2, -3, 4],
        [1, 2, -3, -4], [-1, -2, -3, -4], [1, -2, 3, -4], [-1, 2, 3, -4],
    ]
    expected, _ = brute_sat(hardish)
    r = solve_fail_closed(hardish, cap_exponent=1, extension_exponent=0)
    if r["status"] != "OPEN":
        assert (r["status"] == "SAT") == expected
    assert r["scientific_boundary"]["random_branch"] is False
    assert r["scientific_boundary"]["semantic_equivalence_oracle"] is False


if __name__ == "__main__":
    for name, value in sorted(globals().items()):
        if name.startswith("test_") and callable(value):
            value()
    print("PASS: C025 unified adversarial tests")
