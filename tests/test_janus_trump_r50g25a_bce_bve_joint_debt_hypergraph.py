from functools import lru_cache

import janus_trump_r50g25a_bce_bve_joint_debt_hypergraph as r50g25a


@lru_cache(maxsize=1)
def result():
    return r50g25a.run()


def test_r50g25a_requires_exact_r50g24_parent_replay_first():
    out = result()
    assert out["parent_pair_trial_count"] == 1774
    assert out["target_occurrence_count"] == 1673
    assert out["target_first_rules"] == [
        "R33:BLOCKED_CLAUSE_ELIMINATION",
        "R33:BOUNDED_VARIABLE_ELIMINATION",
    ]


def test_r50g25a_deduplicates_states_but_preserves_weighted_occurrences():
    out = result()
    assert 1 <= out["unique_post_DP_state_count"] <= 1673
    assert sum(out["first_rule_occurrence_partition"].values()) == 1673
    assert sum(out["first_rule_unique_state_partition"].values()) == out["unique_post_DP_state_count"]
    assert sum(out["snapshot_binary_incidence_cover_weighted_partition"].values()) == 1673
    assert sum(out["snapshot_binary_incidence_cover_unique_partition"].values()) == out["unique_post_DP_state_count"]


def test_static_joint_debt_is_never_promoted_to_dynamic_sufficiency():
    out = result()
    contract = out["interpretation_contract"]
    assert contract["snapshot_cover_is_necessary_not_sufficient"] is True
    assert contract["post_DP_cover_is_source_reachability_proof"] is False
    assert contract["covering_existing_BVE_incidence_debt_guarantees_BVE_disabled"] is False
    assert contract["covering_existing_BCE_support_debt_guarantees_no_new_BCE"] is False
    assert contract["static_debt_cover_closes_dynamic_replacement_cycle"] is False


def test_r50g25a_keeps_global_firewall_closed():
    out = result()
    fw = out["firewall"]
    assert fw["R50G25A_PROVES_THREE_CLAUSES_SUFFICIENT"] is False
    assert fw["R50G25A_PROVES_THREE_CLAUSES_NECESSARY_UNIVERSALLY"] is False
    assert fw["ALL_DIRECT5_V7_HUB_CYCLE_ELIMINATED"] is False
    assert fw["U_MU"] == "OPEN"
    assert fw["SAT_IN_P"] == "NOT_PROVED"
    assert fw["P_VS_NP"] == "OPEN"
    assert fw["TRUMP_finished"] is False
