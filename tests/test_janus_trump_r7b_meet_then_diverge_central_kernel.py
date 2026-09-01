#!/usr/bin/env python3
from experiments.janus_trump_r7b_meet_then_diverge_central_kernel import (
    candidate_source_firewall,
    meet_then_diverge_candidate,
    verify_sat,
)


def test_2sat_sat_diverges_to_replayable_model():
    cnf = ((1, 2), (-1, 2), (1, -2))
    c = meet_then_diverge_candidate(cnf)
    assert c.meet_exact
    assert c.candidate_poly_only
    assert c.terminal == "SAT"
    assert verify_sat(cnf, c.witness)


def test_2sat_unsat_terminal_without_fallback():
    cnf = ((1, 2), (-1, 2), (1, -2), (-1, -2))
    c = meet_then_diverge_candidate(cnf)
    assert c.meet_exact
    assert c.candidate_poly_only
    assert c.terminal == "UNSAT"


def test_general_core_abstains_instead_of_searching():
    cnf = ((1, 2, 3), (-1, -2, -3))
    c = meet_then_diverge_candidate(cnf)
    assert c.meet_exact
    assert c.candidate_poly_only
    assert c.terminal == "OPEN"
    assert c.certificate["type"] == "UNSUPPORTED_OR_FAILED_COMPONENT"


def test_candidate_source_has_no_quarantined_search_calls():
    fw = candidate_source_firewall()
    assert fw["pass"], fw
    assert fw["forbidden_hits"] == []
