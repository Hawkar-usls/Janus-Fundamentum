#!/usr/bin/env python3
from experiments.janus_trump_r6_exponential_debt_elimination import audit


def test_r6_scans_full_target_lineage():
    r = audit()
    assert r["scan"]["files_scanned"] == 5
    assert r["scan"]["lines_scanned"] > 0
    assert r["scan"]["hazard_hits"] > 0


def test_r6_detects_core_exponential_debt_classes():
    r = audit()
    classes = set(r["scan"]["debt_class_counts"])
    assert "BINARY_RECURSIVE_SEARCH" in classes
    assert "EXHAUSTIVE_SEPARATOR_ASSIGNMENT_ENUMERATION" in classes
    assert "EXACT_DPLL_FALLBACK_OR_VERIFIER" in classes
    assert "EXACT_SEARCH_WITNESS_FALLBACK_OR_WING" in classes


def test_r6_quarantines_without_fake_polynomial_proof():
    r = audit()
    assert r["elimination_pass"] is True
    assert r["scan"]["resolution_counts"].get("POLYNOMIAL_BOUND_PROVED", 0) == 0
    assert r["scan"]["resolution_counts"]["QUARANTINED_FROM_P_EQUALS_NP_CANDIDATE_PATH"] == r["scan"]["hazard_hits"]


def test_r6_does_not_close_p_vs_np_when_total_solver_is_gone():
    r = audit()
    assert r["candidate_proof_path_after_quarantine"]["total_for_arbitrary_cnf"] is False
    assert r["closure_ready"] is False
    assert r["P_VS_NP"] == "OPEN"
    assert "CANDIDATE_PATH_TOTAL_FOR_ARBITRARY_CNF" in r["blocking_obligations"]
