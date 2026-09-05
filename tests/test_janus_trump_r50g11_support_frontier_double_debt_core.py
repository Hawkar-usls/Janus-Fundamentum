import janus_trump_r50g10_wide_fixpoint_forces_alternate_certified_door as r50g10
import janus_trump_r50g11_support_frontier_double_debt_core as r50g11


def test_w4_chi_cap_and_exact_geometry_controls():
    chi6 = r50g11.chi_bad_pair_certificate([(1, 2, 3, 4), (-1, 5, 6, 7)], 1)
    assert chi6["chi_star"] == 6
    assert chi6["geometry"] == "4x4_RESIDUAL_3PLUS3_OVERLAP_0"

    chi5 = r50g11.chi_bad_pair_certificate([(1, 2, 3, 4), (-1, 5, 6)], 1)
    assert chi5["chi_star"] == 5
    assert chi5["geometry"] == "4x3_RESIDUAL_3PLUS2_OVERLAP_0"


def test_r50g9_two_halves_of_door_complementarity():
    source = r50g10.build_r50g9_source()

    # Pivot 2 closes R49H at chi*=5 but R47J returns to W4.
    d2 = r50g10.exact_door_row(source, 2)
    c2 = r50g11.chi_bad_pair_certificate(source, 2)
    assert c2["chi_star"] == 5
    assert d2["r49h_authorized"] is False
    assert d2["r47j_safe"] is True

    # Pivot 3 has an R49H door while its R47J lane remains wide.
    d3 = r50g10.exact_door_row(source, 3)
    r3 = r50g11.r47j_wide_debt_certificate(source, 3)
    assert d3["r49h_authorized"] is True
    assert d3["r47j_safe"] is False
    assert r3["terminal"] is None
    assert r3["final_width"] > 4


def test_r50g9_support_frontier_is_fully_hit_with_exact_partition():
    row = r50g11.profile_r50g9_support_frontier()
    assert row["frontier_size"] == 12
    assert row["none"] == 0
    assert row["both"] == 0
    assert row["r49h_only"] == 9
    assert row["r47j_only"] == 3
    assert row["all_frontier_hit"] is True


def test_r50g9_source_is_not_all_doors_closed():
    source = r50g10.build_r50g9_source()
    out = r50g11.all_closed_dependency_core(source, 1)
    assert out["all_alternate_doors_closed"] is False
    assert out["first_open"] is not None
