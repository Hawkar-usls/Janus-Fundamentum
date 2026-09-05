from functools import lru_cache

import janus_trump_r50g25c_source_preimage_obstruction_forensics as r50g25c


@lru_cache(maxsize=1)
def result():
    return r50g25c.run()


def test_r50g25c_replays_exact_parent_partition():
    out = result()
    assert out["ge3_unique_state_count"] == 991
    assert out["ge3_weighted_occurrence_count"] == 1317
    assert out["exact_preimage_unique_count"] == 312
    assert out["exact_state_mismatch_unique_count"] == 679
    assert out["exact_state_mismatch_weighted_count"] == 892


def test_r50g25c_mismatch_classification_is_total():
    out = result()
    total_unique = (
        out["subsumption_only_normal_form_preimage_unique_count"]
        + out["genuine_DP_noncommutation_unique_count"]
        + out["R47J_replay_failure_unique_count"]
    )
    total_weighted = (
        out["subsumption_only_normal_form_preimage_weighted_count"]
        + out["genuine_DP_noncommutation_weighted_count"]
        + out["R47J_replay_failure_weighted_count"]
    )
    assert total_unique == 679
    assert total_weighted == 892


def test_r50g25c_predeclared_next_gate_only():
    out = result()
    assert out["next_gate"] in {
        "R50G25D_DYNAMIC_REPLACEMENT_AFTER_SOURCE_NORMALIZED_MINIMUM_JOINT_DEBT",
        "R50G25D_NONCOMMUTING_DP_PREIMAGE_OBSTRUCTION",
    }
    expected = (
        out["subsumption_only_normal_form_preimage_unique_count"] == 679
        and out["genuine_DP_noncommutation_unique_count"] == 0
        and out["R47J_replay_failure_unique_count"] == 0
    )
    assert out["all_679_mismatches_explained_by_subsumption_normal_form"] is expected


def test_r50g25c_keeps_normal_form_vs_dynamic_firewall_closed():
    out = result()
    contract = out["interpretation_contract"]
    assert contract["subsumption_only_normal_form_preimage_is_exact_state_preimage"] is False
    assert contract["subsumption_only_normal_form_preimage_is_source_lift_under_actual_DP_semantics"] is True
    assert contract["original_debt_resolution_is_no_new_escape_proof"] is False
    assert contract["actual_first_rule_partition_is_dynamic_next_gate_evidence"] is True
    fw = out["firewall"]
    assert fw["ALL_DIRECT5_V7_HUB_CYCLE_ELIMINATED"] is False
    assert fw["U_MU"] == "OPEN"
    assert fw["SAT_IN_P"] == "NOT_PROVED"
    assert fw["P_VS_NP"] == "OPEN"
    assert fw["TRUMP_finished"] is False
