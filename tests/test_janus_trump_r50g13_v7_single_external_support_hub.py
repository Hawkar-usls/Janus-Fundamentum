import janus_trump_r50g13_v7_single_external_support_hub as r13


def test_hub_polarity_and_guard_controls():
    out = r13.hub_polarity_and_guard_controls()
    assert out["opposite_hub_supports_force_rup_conflict"] is True
    assert out["unguarded_opposite_hub_clause_forces_rup_conflict"] is True
    assert out["guarded_opposite_hub_clause_control_no_conflict"] is True


def test_frozen_v7_replay_is_regression_only():
    out = r13.replay_frozen_boundary()
    assert out["frozen_roots"] == 400
    assert out["v7_immediate_BVE"] == 9
    assert out["v7_same_pivot_wide_survivor"] == 0
    assert out["interpretation"] == "FINITE_REGRESSION_ONLY"


def test_firewalls_remain_closed():
    out = r13.run()
    fw = out["firewall"]
    assert fw["V6_IMMEDIATE_BVE_CASE_ELIMINATED"] is True
    assert fw["V7_IMMEDIATE_BVE_CASE_ELIMINATED"] is False
    assert fw["IMMEDIATE_BVE_CASE_ELIMINATED"] is False
    assert fw["U_MU"] == "OPEN"
    assert fw["SAT_IN_P"] == "NOT_PROVED"
    assert fw["P_VS_NP"] == "OPEN"
    assert fw["TRUMP_finished"] is False
