import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g15_rup6_hub_bve_blockade_saturation as r50g15
import janus_trump_r50g17_v6_wide6_all_variable_bve_saturation_cage as r17


def test_integer_boundary_is_exact_3x2():
    b = r17.integer_boundary()
    assert b["minimum_total_occurrences"] == 5
    assert b["minimum_oriented_pair"] == {"p": 3, "n": 2}


def test_wide6_row_collapses_at_minimal_boundary():
    old = r50g15.minimal_3x2_blockade_control()
    f = r33.canonical_formula(old["formula"])
    R = r33.canonical_clause((1, 2, 3, 4, 5, 6))
    p = r17.oriented_profile(f, R, 6)
    assert p["p"] == 3
    assert p["n"] == 2
    assert p["wide_row_distinct_nontaut"] == 1
    assert p["bve_accepted"] is False


def test_under_saturated_2x2_forces_bve():
    old = r50g15.under_saturated_2x2_control()
    f = r33.canonical_formula(old["formula"])
    R = r33.canonical_clause((1, 2, 3, 4, 5, 6))
    p = r17.oriented_profile(f, R, 6)
    assert p["p"] == 2
    assert p["n"] == 2
    assert p["bve_accepted"] is True


def test_theorem_does_not_promote_v7():
    assert r17.GATE.endswith("ALL_VARIABLE_BVE_SATURATION_CAGE")
    # Sixfold saturation is a necessary obstruction shape, not an impossibility proof.
    assert r17.integer_boundary()["equivalent"] == "(p-2)(n-1) >= 1"
