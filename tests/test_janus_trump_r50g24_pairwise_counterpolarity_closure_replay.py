from functools import lru_cache

import janus_trump_r50g24_pairwise_counterpolarity_closure_replay as r50g24


@lru_cache(maxsize=1)
def result():
    return r50g24.run()


def test_r50g24_replays_exact_frozen_30_without_family_expansion():
    out = result()
    assert out["frozen_skeleton_count"] == 30
    assert out["no_source_family_expansion"] is True
    assert out["same_pivot_R47J"] == 1
    assert out["new_variables_added"] is False
    assert out["mutation_grammar"] == "TWO_ADDITIVE_BINARY_CLAUSES_OVER_EXISTING_VARIABLES_ONLY"


def test_r50g24_exact_pairwise_counts_match_sealed_janus_receipt():
    out = result()
    assert out["first_clause_candidate_count"] == 360
    assert out["first_transition_break_count"] == 122
    assert out["second_direct_debt_available_count"] == 122
    assert out["pair_trial_count"] == 1774
    assert out["R47J_replay_failure_partition"] == {}
    assert out["strong_candidate_count"] == 0


def test_r50g24_replacement_cycle_partition_is_exact():
    out = result()
    assert out["first_replacement_partition"] == {
        "R33:BLOCKED_CLAUSE_ELIMINATION": 88,
        "R33:BOUNDED_VARIABLE_ELIMINATION": 34,
    }
    assert out["second_debt_partition"] == {
        "NONTAUTOLOGICAL_OPPOSITE_BLOCKER_SUPPORT": 88,
        "PIVOT_TOUCH_REQUIRED_FOR_DIRECT_ADDITIVE_BVE_BLOCK": 34,
    }
    assert out["final_first_transition_partition"] == {
        "R33:BLOCKED_CLAUSE_ELIMINATION": 887,
        "R33:BOUNDED_VARIABLE_ELIMINATION": 786,
        "R33:PURE_LITERAL_AUTARKY": 94,
        "R33:UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE": 7,
    }
    assert out["BCE_plus_BVE_final_first_count"] == 1673
    assert out["BCE_plus_BVE_final_first_fraction"] > 0.94


def test_r50g24_promotes_only_structural_debt_not_universal_claim():
    out = result()
    assert out["next_gate"] == "R50G25_BCE_BVE_REPLACEMENT_CYCLE_STRUCTURAL_DEBT"
    fw = out["firewall"]
    assert fw["FINITE_PAIRWISE_NEGATIVE_IMPLIES_ALL_PAIRWISE_MUTATIONS_FAIL"] is False
    assert fw["FINITE_PAIRWISE_NEGATIVE_IMPLIES_UNIVERSAL_ALL_DIRECT5"] is False
    assert fw["BCE_BVE_DOMINANCE_IS_A_THEOREM_OUTSIDE_THIS_REPLAY"] is False
    assert fw["ALL_DIRECT5_V7_HUB_CYCLE_ELIMINATED"] is False
    assert fw["V7_IMMEDIATE_BVE_CASE_ELIMINATED"] is False
    assert fw["U_MU"] == "OPEN"
    assert fw["SAT_IN_P"] == "NOT_PROVED"
    assert fw["P_VS_NP"] == "OPEN"
    assert fw["TRUMP_finished"] is False
