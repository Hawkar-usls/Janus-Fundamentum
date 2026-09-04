import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4


ESCAPE_WITH_SAFE_PREFIX = r33.canonical_formula([
    [-7, -8, -10], [-6, -8, -9], [-5, -6, -8, 10], [-5, 7, -10], [-5, 7, -8],
    [-4, -6, -8, 10], [-4, -6, -7], [-4, 5, -7, 9], [-4, 5, -7, 10], [-4, 7, -8, 9],
    [-3, -7, -8], [-3, -5, -8], [-3, -5, 8, 10], [-3, -4, 8], [-3, 4, 8],
    [-3, 9, 10], [3, -8, 10], [3, -4, 10], [3, 4, -8, -9], [3, 5, -7, 10],
    [3, 6, -8], [4, -7], [4, 5, -6], [5, -7, 8, 9], [6, 7, -10], [6, 8, -10], [7, 9, -10],
])


def test_first_rule_conformance_on_frozen_controls():
    controls = [r33.easy_redundant_tail(), r33.blocked_clause_control(), r33.bve_control()]
    for f in controls:
        assert r50g4.verify_first_rule_conformance(f)


def test_every_authorized_microstep_strictly_descends_mu_and_stays_w4():
    f = r33.easy_redundant_tail()
    for _ in range(32):
        s = r50g4.micro_r33_status(f)
        if s["status"] != "AUTHORIZED_R33_MICROSTEP":
            break
        assert tuple(s["mu_after"]) < tuple(s["mu_before"])
        assert r50g4.max_width(s["after"]) <= 4
        f = s["after"]


def test_known_batch_escape_factors_into_safe_microsteps_then_immediate_bve_escape():
    rr = r50g4.verify_prefix_factorization(ESCAPE_WITH_SAFE_PREFIX)
    assert rr["safe_prefix_length"] == 2
    assert len(rr["factorization_rows"]) == 2
    assert all(tuple(row["mu_after"]) < tuple(row["mu_before"]) for row in rr["factorization_rows"])
    assert rr["tail_status"] == "IMMEDIATE_BVE_W4_ESCAPE"


def test_refined_controller_accepts_first_safe_prefix_step_instead_of_batch_rollback():
    s = r50g4.micro_r33_status(ESCAPE_WITH_SAFE_PREFIX)
    assert s["status"] == "AUTHORIZED_R33_MICROSTEP"
    assert s["rule"] == "BLOCKED_CLAUSE_ELIMINATION"
    step = r50g4.refined_exact_step(ESCAPE_WITH_SAFE_PREFIX)
    assert step["kind"] == "NONTERMINAL"
    assert step["lane"] == "R33_EXACT_W4_MICROSTEP"
    assert tuple(step["mu_after"]) < tuple(step["mu_before"])


def test_firewall():
    fw = r50g4.firewall()
    assert fw["HEURISTIC_AUTHORITY"] is False
    assert fw["LEARNED_SELECTOR"] is False
    assert fw["PROBABILISTIC_AUTHORITY"] is False
    assert fw["BRUTE_FORCE_SAT_TRANSITION_AUTHORITY"] is False
    assert fw["PREFIX_CLOSURE_PROVES_U_MU"] is False
    assert fw["OLD_GUARDED_U_PROVED"] is False
    assert fw["SAT_IN_P"] == "NOT_PROVED"
    assert fw["P_VS_NP"] == "OPEN"
    assert fw["TRUMP_finished"] is False
