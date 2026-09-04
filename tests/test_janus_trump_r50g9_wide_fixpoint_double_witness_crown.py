from experiments import janus_trump_r50g9_wide_fixpoint_double_witness_crown as r50g9


def test_frozen_core_is_certified_fixpoint_and_has_2x2_degree():
    row = r50g9.frozen_core_regression()
    assert row["max_width"] <= 4
    assert row["variable_count"] == 20
    assert row["all_variables_have_2x2_polarity_degree"] is True
    assert row["resolvent_surplus_variables"] + row["literal_inflation_equality_variables"] == 20


def test_every_frozen_core_variable_has_exact_bve_rejection_certificate():
    _sealed, core = r50g9.r47j.load_counterexample()
    core = r50g9.canon(core)
    r50g9.verify_certified_normalization_fixpoint(core)
    for v in r50g9.r33.variables(core):
        cert = r50g9.bve_fixedpoint_rejection_certificate(core, int(v))
        assert cert["positive_occurrences"] >= 2
        assert cert["negative_occurrences"] >= 2
        assert cert["unique_nontaut_resolvent_count"] >= cert["removed_parent_count"]
        assert cert["rejection_kind"] in {"RESOLVENT_SURPLUS", "LITERAL_INFLATION_EQUALITY"}
        if cert["rejection_kind"] == "LITERAL_INFLATION_EQUALITY":
            assert cert["resolvent_literal_sum"] > cert["parent_literal_sum"]
            assert cert["inherited_resolvent_duplicates"] == 0


def test_rup_escape_receipts_are_conflict_free_on_frozen_core_clause():
    _sealed, core = r50g9.r47j.load_counterexample()
    core = r50g9.canon(core)
    clause = max(core, key=len)
    rows = r50g9.rup_escape_receipts_for_clause(core, clause)
    assert len(rows) == len(clause)
    assert all(row["candidate_conflict"] is False for row in rows)
    assert all(row["independent_conflict"] is False for row in rows)


def test_full_gate_preserves_epistemic_boundary():
    out = r50g9.run()
    assert out["reachable_replay"]["frozen_roots"] == 400
    assert out["reachable_replay"]["immediate_BVE_states"] == 29
    assert out["reachable_replay"]["final_nonterminal_wide_states"] == 0
    assert out["firewall"]["DOUBLE_WITNESS_CROWN_IMPOSSIBILITY_THEOREM"] == "OPEN"
    assert out["firewall"]["IMMEDIATE_BVE_CASE_ELIMINATED"] is False
    assert out["firewall"]["SAT_IN_P"] == "NOT_PROVED"
    assert out["firewall"]["P_VS_NP"] == "OPEN"
