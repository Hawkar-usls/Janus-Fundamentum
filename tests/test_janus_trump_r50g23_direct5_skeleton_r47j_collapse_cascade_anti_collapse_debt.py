from functools import lru_cache

import janus_trump_r50g23_direct5_skeleton_r47j_collapse_cascade_anti_collapse_debt as r50g23


@lru_cache(maxsize=1)
def result():
    return r50g23.run()


def test_exact_r50g22_clean_set_is_30_and_not_expanded():
    out = result()
    assert out["selected_source_count"] == 30
    assert out["no_source_family_expansion"] is True
    assert out["r50g22_family_replayed_only_to_recover_exact_set"] == 11520


def test_all_30_same_pivot_r47j_replay_and_direct_empty_terminal():
    out = result()
    assert out["all_same_pivot_R47J_terminal_direct_empty"] is True
    assert out["all_independent_R47J_replays_pass"] is True
    assert len(out["skeleton_ledgers"]) == 30
    for row in out["skeleton_ledgers"]:
        assert row["terminal"] == "DIRECT_EMPTY_CNF"
        assert row["R47J_independent_replay_pass"] is True
        assert row["transition_count"] >= 1
        assert row["transition_labels"]


def test_direct_blocking_debt_classes_are_fail_closed_and_necessary_only():
    pure = r50g23.direct_blocking_debt({
        "phase": "R33",
        "record": {"rule": "PURE_LITERAL_AUTARKY", "literal": 3},
    })
    assert pure["debt_class"] == "OPPOSITE_POLARITY_OCCURRENCE"
    assert pure["required_literal"] == -3
    assert pure["minimum_added_clause_count_lower_bound"] == 1

    bve = r50g23.direct_blocking_debt({
        "phase": "R33",
        "record": {"rule": "BOUNDED_VARIABLE_ELIMINATION", "var": 4},
    })
    assert bve["debt_class"] == "PIVOT_TOUCH_REQUIRED_FOR_DIRECT_ADDITIVE_BVE_BLOCK"
    assert bve["required_variable"] == 4

    subsumption = r50g23.direct_blocking_debt({
        "phase": "R33",
        "record": {"rule": "SUBSUMPTION"},
    })
    assert subsumption["debt_class"] == "DIRECT_ADDITIVE_BLOCK_IMPOSSIBLE_AT_SAME_STATE"

    rup = r50g23.direct_blocking_debt({"phase": "RUP", "record": {}})
    assert rup["debt_class"] == "DIRECT_ADDITIVE_BLOCK_IMPOSSIBLE_AT_SAME_STATE"


def test_r50g23_keeps_all_universal_firewalls_closed():
    out = result()
    fw = out["firewall"]
    assert fw["FINITE_30_COMMON_CASCADE_IMPLIES_UNIVERSAL_ALL_DIRECT5"] is False
    assert fw["NECESSARY_DIRECT_BLOCKING_DEBT_IS_SUFFICIENT_ANTI_COLLAPSE"] is False
    assert fw["ALL_DIRECT5_V7_HUB_CYCLE_ELIMINATED"] is False
    assert fw["V7_IMMEDIATE_BVE_CASE_ELIMINATED"] is False
    assert fw["IMMEDIATE_BVE_CASE_ELIMINATED"] is False
    assert fw["U_MU"] == "OPEN"
    assert fw["SAT_IN_P"] == "NOT_PROVED"
    assert fw["P_VS_NP"] == "OPEN"
    assert fw["TRUMP_finished"] is False
