from experiments import janus_trump_r50g12_v6_rup_external_support_elimination as r50g12


def test_internal_support_forces_rup_but_external_pair_does_not():
    out = r50g12.internal_external_pair_controls()
    assert out["internal_support_forces_rup_conflict"] is True
    assert out["external_support_pair_alone_does_not_force_conflict"] is True


def test_r50g9_wide_fixedpoint_obeys_external_support_bound():
    out = r50g12.r50g9_fixedpoint_control()
    audit = out["wide_clause_audit"]
    assert audit["clause_width"] == 5
    assert audit["formula_variable_count"] >= 6
    assert audit["external_formula_variables"]
    assert audit["every_nonblocking_support_has_external_variable"] is True


def test_v7_boundary_normal_form_is_exact_bound():
    out = r50g12.v7_boundary_normal_form()
    assert out["derived_final_variable_count"] == 6
    assert out["derived_final_max_width"] == 5
    assert out["widest_clause_external_variable_count"] == 1
