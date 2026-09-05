import janus_trump_r50g20_rup6_phase_collapse_to_v6_w5_core as r50g20


def test_r50g18_scope_correction_is_internal_Ht_not_H0():
    out = r50g20.r50g18_scope_correction_and_selector_control()
    p = out["internal_Ht_literal2_profile"]
    assert out["H0_exact_3x2_all_six"] is True
    assert out["internal_touch_step"] == 7
    assert (p["p"], p["n"], p["distinct_nontaut_resolvents"]) == (2, 1, 1)
    assert p["measure_before"] == [10, 24, 6]
    assert p["measure_after"] == [8, 16, 5]
    assert p["bve_accepted"] is True


def test_r50g18_full_clause_entry_has_all_six_rup_deletions():
    out = r50g20.r50g18_scope_correction_and_selector_control()["selector_and_collapse"]
    assert out["entry"]["H0_R33_fixed"] is True
    assert out["entry"]["all_six_one_literal_deletions_rup_valid"] is True
    assert len(out["entry"]["per_literal"]) == 6
    assert out["first_wide_clause_touch"]["step"] == 7
    assert out["first_wide_clause_touch"]["removed_literal"] == 2
    assert out["final_max_width"] <= 5
    assert out["independent_replay_pass"] is True


def test_selector_follows_minimum_variable_under_renaming_and_sign_flips():
    rows = r50g20.transformed_selector_controls()
    assert len(rows) == 4
    for row in rows:
        R = row["transformed_wide_clause"]
        touch = row["audit"]["first_wide_clause_touch"]
        assert abs(touch["removed_literal"]) == min(abs(x) for x in R)
        assert row["audit"]["final_max_width"] <= 5
        assert row["audit"]["independent_replay_pass"] is True


def test_v7_corollary_keeps_ancestry_firewall_and_global_firewalls():
    out = r50g20.run()
    fw = out["firewall"]
    assert fw["RUP6_PHASE_ENTRY_WIDTH_COLLAPSE"] == "PROVED_FROM_FROZEN_SOURCE_DEFINITIONS"
    assert fw["RUP6_AS_TERMINAL_WIDTH6_V7_OBSTRUCTION_ELIMINATED"] is True
    assert fw["V7_UNSAFE_DESCENDANT_AFTER_RUP6"] == "V6_W5_OR_SAFE"
    assert fw["RUP6_DESCENDED_W5_EQUALS_HISTORICAL_DIRECT5"] is False
    assert fw["RUP_BEARING_V7_HUB_CYCLE_ELIMINATED"] is False
    assert fw["V7_IMMEDIATE_BVE_CASE_ELIMINATED"] is False
    assert fw["U_MU"] == "OPEN"
    assert fw["SAT_IN_P"] == "NOT_PROVED"
    assert fw["P_VS_NP"] == "OPEN"
    assert fw["TRUMP_finished"] is False
