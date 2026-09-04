from experiments import janus_trump_r50g6_immediate_bve_same_pivot_terminality_theorem as r50g6


def test_first_frozen_immediate_bve_witness_is_exact_and_terminal_in_r50g5():
    f, provenance, proof = r50g6.first_frozen_immediate_bve_state()
    assert r50g6.max_width(f) <= 4
    assert proof["applicable"] is True
    assert proof["same_pivot_terminal"] is True
    assert proof["terminal"] == "DIRECT_EMPTY_CNF"
    assert provenance["worker"] in range(5)


def test_frozen_nonterminal_component_certificate_is_fail_closed():
    cert = r50g6.certify_nonterminal_component()
    assert cert["core_max_width"] <= 4
    # These are the exact preconditions for using the core in the composition proof.
    # If either drifts, the composition gate must report PRECONDITION_FAILED rather
    # than silently substitute another core.
    assert isinstance(cert["normalization_nonterminal"], bool)
    assert isinstance(cert["normalization_unchanged"], bool)


def test_disjoint_composition_never_claims_reachability_without_proof():
    out = r50g6.exact_disjoint_composition_test()
    assert out["reachability_of_composite"] == "NOT_ESTABLISHED"
    if out["preconditions_pass"]:
        assert out["composite"]["max_width"] <= 4
        assert out["composite"]["micro_status"] == "IMMEDIATE_BVE_W4_ESCAPE"
        assert out["composite"]["independent_replay_pass"] is True


def test_firewall_changes_only_with_exact_counterexample_status():
    fw = r50g6.firewall(local_refuted=True, reachable_counterexample_count=0)
    assert fw["STRONG_LOCAL_TERMINALITY_THEOREM"] == "REFUTED"
    assert fw["REACHABLE_TERMINALITY_THEOREM"] == "OPEN"
    assert fw["IMMEDIATE_BVE_CASE_ELIMINATED"] is False
    assert fw["SAT_IN_P"] == "NOT_PROVED"
    assert fw["P_VS_NP"] == "OPEN"
