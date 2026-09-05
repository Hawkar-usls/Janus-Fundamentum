from __future__ import annotations

import janus_trump_r50g13_v7_single_external_support_hub_cycle as r50g13


def test_hub_polarity_control_forces_rup():
    out = r50g13.hub_polarity_controls()
    assert out["opposite_polarities_force_single_literal_RUP_conflict"] is True
    assert out["independent_UP_replay"] is True
    assert out["shielded_resolvent_is_tautological"] is True


def test_functional_graph_control_has_nontrivial_cycle():
    out = r50g13.graph_control()
    cycle = out["cycle"]
    assert cycle[0] == cycle[-1]
    assert len(cycle) >= 3


def test_frozen_replay_has_no_v7_wide_survivor():
    out = r50g13.frozen_replay_regression()
    assert out["frozen_roots"] == 400
    assert out["v7_bucket"]["same_pivot_wide_survivor"] == 0


def test_firewalls_stay_open_beyond_v6():
    out = r50g13.run()
    fw = out["firewall"]
    assert fw["V6_IMMEDIATE_BVE_CASE_ELIMINATED"] is True
    assert fw["V7_IMMEDIATE_BVE_CASE_ELIMINATED"] is False
    assert fw["IMMEDIATE_BVE_CASE_ELIMINATED"] is False
    assert fw["U_MU"] == "OPEN"
    assert fw["SAT_IN_P"] == "NOT_PROVED"
    assert fw["P_VS_NP"] == "OPEN"
    assert fw["TRUMP_finished"] is False
