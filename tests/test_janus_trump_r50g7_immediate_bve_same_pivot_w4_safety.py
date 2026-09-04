from experiments import janus_trump_r50g7_immediate_bve_same_pivot_w4_safety as r50g7


def test_frozen_core_is_w4_normalization_fixed():
    original, shifted = r50g7.frozen_shifted_core()
    assert r50g7.max_width(original) <= 4
    assert r50g7.max_width(shifted) <= 4
    assert min(r50g7.r33.variables(shifted)) > r50g7.PIVOT


def test_source_firewall_never_promotes_from_finite_no_find():
    fw = r50g7.firewall(False, False)
    assert fw["FINITE_NO_FIND_IMPLIES_THEOREM"] is False
    assert fw["LOCAL_SAME_PIVOT_W4_SAFETY"] == "OPEN"
    assert fw["REACHABLE_SAME_PIVOT_W4_SAFETY"] == "OPEN"
    assert fw["SAT_IN_P"] == "NOT_PROVED"
    assert fw["P_VS_NP"] == "OPEN"


def test_algebraic_family_is_deterministic_on_small_prefix():
    a = r50g7.search_algebraic_family(2)
    b = r50g7.search_algebraic_family(2)
    assert a == b
    assert a["exact_eligible_candidates_tested"] <= 2


def test_any_reported_local_witness_is_exact_wide_survivor():
    out = r50g7.search_algebraic_family(2)
    w = out["first_local_wide_survivor"]
    if w is not None:
        assert w["independent_replay_pass"] is True
        assert w["terminal"] is None
        assert w["final_width"] > 4
        assert w["same_pivot_machine_safe"] is False
