from experiments.janus_trump_r7c_open49_poly_kernel_assault import (
    candidate_source_firewall,
    polynomial_kernel_closure,
    solve_bipartite_matching_cnf,
    solve_renamable_horn,
    target_cases,
)
from experiments.janus_trump_p_vs_np_direct_challenge_r0 import canon, f_php


def test_target_is_exactly_r7b_open49():
    assert len(target_cases()) == 49


def test_failed_literal_closure_can_prove_local_unsat_without_recursive_search():
    # x=False forces y and ~y; x=True forces z and ~z.
    f = canon(((1, 2), (1, -2), (-1, 3), (-1, -3)))
    c = polynomial_kernel_closure(f)
    assert c.contradiction is True
    assert c.certificate["type"] == "FAILED_LITERAL_BOTH_VALUES_CONTRADICT"


def test_renamable_horn_solves_nonhorn_monotone_example():
    f = canon(((1, 2, 3), (1, 4, 5), (2, 4, 6)))
    r = solve_renamable_horn(f)
    assert r["status"] == "SAT"
    assert r["class"] == "RENAMABLE_HORN"


def test_matching_recognizer_proves_pigeonhole_unsat():
    r = solve_bipartite_matching_cnf(f_php(3))
    assert r["status"] == "UNSAT"
    assert r["class"] == "BIPARTITE_MATCHING_CNF"


def test_candidate_source_has_no_quarantined_fallback_tokens():
    fw = candidate_source_firewall()
    assert fw["pass"] is True
    assert fw["forbidden_hits"] == []
