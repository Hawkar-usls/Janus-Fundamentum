from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g_smallest_first_exact_deadcore_falsifier as r50g
import janus_trump_r50g2_guarded_full_smallest_first_deadcore as r50g2


def test_architectural_firewall_is_fail_closed():
    fw = r50g2.firewall(False, False)
    assert fw["ARCHITECTURAL_LAW"] == "PRODUCER_MAY_PROPOSE__INVARIANT_DECIDES_AUTHORITY"
    assert fw["GUARDED_U"] == "OPEN"
    assert fw["NO_DEADCORE_FOUND_IMPLIES_U"] is False
    assert fw["GENERATED_POOL_SMALLEST_IS_GLOBAL_MINIMUM"] is False
    assert fw["FINITE_SEARCH_PROVES_P_EQUALS_NP"] is False
    assert fw["SAT_IN_P"] == "NOT_PROVED"
    assert fw["P_VS_NP"] == "OPEN"
    assert fw["TRUMP_finished"] is False


def test_candidate_key_is_v_c_l_hash_smallest_first():
    a = {"CLV": [20, 60, 6], "hash": "b"}
    b = {"CLV": [18, 55, 7], "hash": "a"}
    c = {"CLV": [21, 59, 6], "hash": "a"}
    assert sorted((a, b, c), key=r50g2.candidate_key) == [a, c, b]


def test_mixed_width_generators_keep_direct_sat_witness():
    for profile in ("3CNF", "W34", "W234", "W4_CONTROL"):
        f, a = r50g.make_planted(50_900_001, 8, 26, profile)
        assert r33.eval_formula(f, a)
        assert r50g2.max_width(f) <= (3 if profile == "3CNF" else 4)


def test_guarded_open_audit_rejects_state_with_existing_authorized_door():
    # This small SAT formula has obvious exact simplification/elimination doors;
    # it must never be mislabeled as a guarded OPEN deadcore.
    f = r50g2.canon([
        (1, 2, 3),
        (-1, 4, 5),
        (1, -4, 5),
        (-1, 2, -5),
    ])
    out = r50g2.exact_guarded_open_test(f)
    assert not out.get("open", False)


def test_r33_authority_status_never_authorizes_width_gt4_successor():
    # Contract-level check over deterministic generated samples: whenever R33
    # reports an authorized nonterminal successor, it must remain persisted W4.
    for seed in range(50_910_000, 50_910_020):
        f, _ = r50g.make_planted(seed, 10, 34, "3CNF")
        if r50g2.max_width(f) > 4:
            continue
        status = r50g2._r33_authority_status(f)
        if status["status"] == "AUTHORIZED_W4_REDUCTION":
            assert r50g2.max_width(status["after"]) <= 4
        if status["status"] == "REJECTED_W4_DOMAIN_ESCAPE":
            assert r50g2.max_width(status["after"]) > 4
