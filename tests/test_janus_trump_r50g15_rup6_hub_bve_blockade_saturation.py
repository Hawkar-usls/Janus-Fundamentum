from __future__ import annotations

import janus_trump_r50g15_rup6_hub_bve_blockade_saturation as r15


def test_rup6_requires_opposite_hub_unit_witness_control():
    row = r15.rup6_unit_witness_control()
    assert row["RUP_conflict"] is True
    assert row["independent_UP_replay"] is True
    assert row["opposite_hub_unit_witness"] == [1, -6] or row["opposite_hub_unit_witness"] == [-6, 1]


def test_2x2_is_under_saturated_and_forces_bve():
    row = r15.under_saturated_2x2_control()["ledger"]
    assert row["positive_count"] == 2
    assert row["negative_count"] == 2
    assert row["distinct_nontaut_resolvent_count"] < row["removed_count"]
    assert row["bve_accepted_for_hub"] is True


def test_3x2_is_unique_minimal_integer_boundary_and_local_blockade_realizer():
    bound = r15.integer_saturation_boundary()
    assert bound["minimum_total_hub_occurrences"] == 5
    assert bound["unique_minimal_integer_pair"]["p"] == 3
    assert bound["unique_minimal_integer_pair"]["n"] == 2
    row = r15.minimal_3x2_blockade_control()["ledger"]
    assert row["distinct_nontaut_resolvent_count"] == row["removed_count"] == 5
    assert row["bve_accepted_for_hub"] is False


def test_firewall_does_not_promote_v7_or_p_np():
    out = r15.run()
    fw = out["firewall"]
    assert fw["RUP_BEARING_V7_HUB_CYCLE_ELIMINATED"] is False
    assert fw["V7_IMMEDIATE_BVE_CASE_ELIMINATED"] is False
    assert fw["U_MU"] == "OPEN"
    assert fw["SAT_IN_P"] == "NOT_PROVED"
    assert fw["P_VS_NP"] == "OPEN"
    assert fw["TRUMP_finished"] is False
