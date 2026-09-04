from __future__ import annotations

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50f_wide_clause_survival_certificate_and_clearance_repair as r50f


def test_dp_subsumption_kills_raw_wide_resolvent_with_witness():
    f = r33.canonical_formula([
        (1, 2, 3, 4),
        (-1, 5, 6, 7),
        (2, 3),
    ])
    cert = r50f.dp_subsumption_certificate(f, 1)
    assert cert["event"]["wide_before_count"] >= 1
    assert cert["event"]["wide_after_count"] == 0
    assert cert["all_omitted_wide_have_subsumption_witness"] is True
    assert cert["event"]["metadata"]["omitted_wide_subsumption_witnesses"]


def test_r33_history_is_replayed_exactly_with_wide_inventory_events():
    f = r33.canonical_formula([
        (1,),
        (-1, 2, 3, 4, 5, 6),
        (2, 3),
    ])
    result = r33.simplify(f)
    final_formula, events = r50f.replay_r33_history(f, result)
    assert final_formula == r33.canonical_formula(result["final_formula"])
    assert events
    assert all(e["before_hash"] and e["after_hash"] for e in events)


def test_wide_clearance_certificate_is_replay_authority_not_predictor():
    f = r33.canonical_formula([
        (1, 2, 3, 4),
        (-1, 5, 6, 7),
        (2, 3),
        (-2, 8),
        (-3, 8),
    ])
    cert = r50f.wide_clearance_certificate(f, 1)
    assert cert["certificate_pass"] is True
    assert cert["exact_dp_replay_pass"] is True
    assert cert["macro_independent_replay_pass"] is True
    assert cert["final_wide_empty"] is True
    assert "REPLAYABLE_WIDE_CLEARANCE_LEDGER" in cert["repair_contract"]


def test_firewall_remains_open():
    fw = r50f.firewall()
    assert fw["WIDE_CLEARANCE_CERTIFICATE_IS_PREDICTOR"] is False
    assert fw["R50F_ADDS_NEW_SAT_PROOF_RULE"] is False
    assert fw["R50F_FINITE_12_PROVES_TOP2_TRANSFER"] is False
    assert fw["TOP2_UNIVERSAL_COVERAGE"] == "OPEN"
    assert fw["SAT_IN_P"] == "NOT_PROVED"
    assert fw["P_VS_NP"] == "OPEN"
    assert fw["TRUMP_finished"] is False


if __name__ == "__main__":
    test_dp_subsumption_kills_raw_wide_resolvent_with_witness()
    test_r33_history_is_replayed_exactly_with_wide_inventory_events()
    test_wide_clearance_certificate_is_replay_authority_not_predictor()
    test_firewall_remains_open()
    print("R50F_TESTS=4 PASS")
