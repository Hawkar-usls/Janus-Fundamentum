from functools import lru_cache

import janus_trump_r50g25b_source_realizability_minimum_joint_debt as r50g25b


@lru_cache(maxsize=1)
def result():
    return r50g25b.run()


def test_r50g25b_replays_the_sealed_r50g25a_ge3_frontier():
    out = result()
    assert out["parent_unique_post_DP_states"] == 1212
    assert out["parent_ge3_unique_states"] == 991
    assert out["parent_ge3_weighted_occurrences"] == 1317


def test_r50g25b_exact_minimum_histograms_partition_all_parent_states():
    out = result()
    unique_hist = {int(k): v for k, v in out["exact_minimum_cover_unique_histogram"].items()}
    weighted_hist = {int(k): v for k, v in out["exact_minimum_cover_weighted_histogram"].items()}
    assert sum(unique_hist.values()) == 1212
    assert sum(weighted_hist.values()) == 1673
    assert sum(v for k, v in unique_hist.items() if k >= 3) == 991
    assert sum(v for k, v in weighted_hist.items() if k >= 3) == 1317
    assert min(k for k, v in unique_hist.items() if v and k >= 3) >= 3


def test_r50g25b_source_realizability_partition_is_total_on_ge3_states():
    out = result()
    assert sum(out["source_realizability_unique_partition"].values()) == 991
    assert sum(out["source_realizability_weighted_partition"].values()) == 1317
    assert out["exact_minimum_source_realizable_unique_count"] <= 991
    assert out["exact_minimum_source_realizable_weighted_count"] <= 1317


def test_r50g25b_next_gate_is_predeclared_branch_only():
    out = result()
    allowed = {
        "R50G25C_DYNAMIC_REPLACEMENT_ESCAPE_AFTER_SOURCE_REALIZED_MINIMUM_JOINT_DEBT",
        "R50G25C_SOURCE_PREIMAGE_OBSTRUCTION_FORENSICS",
    }
    assert out["next_gate"] in allowed
    assert out["all_ge3_minimum_covers_source_realizable"] is (
        out["exact_minimum_source_realizable_unique_count"] == 991
    )


def test_r50g25b_preserves_static_vs_dynamic_firewall():
    out = result()
    contract = out["interpretation_contract"]
    assert contract["exact_minimum_is_static_incidence_cover_only"] is True
    assert contract["source_realized_cover_is_dynamic_BCE_BVE_closure_proof"] is False
    assert contract["source_realized_cover_is_hard_core_proof"] is False
    assert contract["recorded_post_cover_R33_behavior_is_next_gate_evidence_only"] is True
    assert contract["minimum_generalizes_outside_sealed_states"] is False
    fw = out["firewall"]
    assert fw["ALL_DIRECT5_V7_HUB_CYCLE_ELIMINATED"] is False
    assert fw["U_MU"] == "OPEN"
    assert fw["SAT_IN_P"] == "NOT_PROVED"
    assert fw["P_VS_NP"] == "OPEN"
    assert fw["TRUMP_finished"] is False
