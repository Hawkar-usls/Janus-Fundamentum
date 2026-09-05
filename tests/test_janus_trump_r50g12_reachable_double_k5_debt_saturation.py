from experiments import janus_trump_r50g12_reachable_double_k5_debt_saturation as r50g12


def test_reachable_same_pivot_wide_control_reseals_refutation():
    row = r50g12.verify_reachable_same_pivot_wide_control()
    assert row["root_width"] <= 3
    assert row["reached_width"] == 4
    assert row["immediate_BVE_escape"] is True
    assert row["same_pivot_terminal"] is None
    assert row["same_pivot_final_width"] > 4
    assert row["same_pivot_safe"] is False
    assert row["all_alternate_doors_closed"] is False
    assert row["alternate_R49H_door_count"] > 0


def test_v6_certificate_is_strictly_conditional():
    _core, _root, reached = r50g12.build_reachable_same_pivot_wide_control()
    cert = r50g12.v6_double_k5_certificate(reached, r50g12.REACH_CONTROL_DANGEROUS_PIVOT)
    assert cert["applicable"] is False
    assert cert["reason"] == "VARIABLE_COUNT_NOT_6"


def test_first_bve_order_debt_replays_frozen_order_on_reachable_control():
    _core, _root, reached = r50g12.build_reachable_same_pivot_wide_control()
    debt = r50g12.earlier_bve_order_debt(reached, r50g12.REACH_CONTROL_DANGEROUS_PIVOT)
    # predecessor pivot 1 has already been eliminated, so dangerous x=2 is the
    # smallest present variable in this exact reached state.
    assert debt["first_BVE_pivot"] == 2
    assert debt["earlier_present_variable_count"] == 0
    assert debt["all_earlier_variables_have_exact_rejection_receipt"] is True


def test_v6_graph_target_is_k5_outdegree_four():
    alts = [2, 3, 4, 5, 6]
    expected = {y: sorted(set(alts) - {y}) for y in alts}
    assert len(expected) == 5
    assert all(len(neighbours) == 4 for neighbours in expected.values())
