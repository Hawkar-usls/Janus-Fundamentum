from experiments import janus_trump_r50g9_explicit_wide_fixpoint_ancestry_counterexample as r50g9


def test_frozen_parent_geometry():
    assert len(r50g9.POS_PARENT) == 4
    assert len(r50g9.NEG_PARENT) == 3
    assert len(r50g9.WIDE) == 5
    assert r50g9.PIVOT == 1


def test_source_is_immediate_bve_escape_on_frozen_pivot():
    _sealed, core = r50g9.r47j.load_counterexample()
    source = r50g9.canon(list(core) + [r50g9.POS_PARENT, r50g9.NEG_PARENT])
    assert r50g9.max_width(source) <= 4
    s = r50g9.r50g4.micro_r33_status(source)
    assert s["status"] == "IMMEDIATE_BVE_W4_ESCAPE"
    d = r50g9.r50g4.first_r33_micro_candidate(source)
    assert d["rule"] == "BOUNDED_VARIABLE_ELIMINATION"
    assert d["var"] == 1
    assert tuple(r50g9.WIDE) in {tuple(c) for c in d["resolvents"]}


def test_gate_is_fail_closed_about_reachability():
    out = r50g9.run()
    assert out["interpretation"]["witness_reachability_under_U_mu"] == "NOT_ESTABLISHED"
    assert out["firewall"]["FINITE_SEARCH_IMPLIES_REACHABILITY"] is False
    if out["final"]["local_wide_fixpoint_witness"]:
        assert out["interpretation"]["local_wide_ancestry_impossibility"] == "REFUTED"
        assert out["final"]["max_width"] > 4
        assert out["final"]["terminal"] is None
        assert len(out["final"]["support_certificate"]) == 5
