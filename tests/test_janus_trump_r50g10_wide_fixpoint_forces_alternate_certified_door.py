from __future__ import annotations

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g10_wide_fixpoint_forces_alternate_certified_door as r50g10


def test_r50g9_source_is_pre_bve_clean_immediate_escape():
    source = r50g10.build_r50g9_source()
    assert r50g10.max_width(source) <= 4
    assert r50g10.exact_pre_bve_clean(source)
    status = r50g4.micro_r33_status(source)
    assert status["status"] == "IMMEDIATE_BVE_W4_ESCAPE"


def test_pre_bve_clean_source_has_only_bipolar_variables():
    source = r50g10.build_r50g9_source()
    for y in r33.variables(source):
        row = r50g10.exact_door_row(source, int(y))
        assert row["chi_star"] >= 0


def test_r50g9_witness_has_alternate_door_and_frontier_hit():
    w = r50g10.profile_r50g9_witness()
    assert w["same_pivot_final_width"] > 4
    assert w["same_pivot_terminal"] is None
    assert w["all_alternate_doors"]["open_door_count"] > 0
    assert w["support_frontier_open_door_count"] > 0


def test_closed_row_characterization_if_present():
    w = r50g10.profile_r50g9_witness()
    for row in w["all_alternate_doors"]["rows"]:
        if row["closed_door_certificate"]:
            assert row["chi_star"] >= 5
            assert row["r47j_terminal"] is None
            assert row["r47j_final_width"] > 4
