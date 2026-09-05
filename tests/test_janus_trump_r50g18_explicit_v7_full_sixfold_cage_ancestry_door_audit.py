import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g10_wide_fixpoint_forces_alternate_certified_door as r50g10
import janus_trump_r50g18_explicit_v7_full_sixfold_cage_ancestry_door_audit as r18


def test_source_is_exact_v7_w4_pre_bve_clean():
    assert list(r33.measure(r18.SOURCE)) == [11, 32, 7]
    assert set(r33.variables(r18.SOURCE)) == set(range(1, 8))
    assert max(len(c) for c in r18.SOURCE) == 4
    assert r50g10.exact_pre_bve_clean(r18.SOURCE)


def test_expected_cage_is_exact_v6_l30():
    assert list(r33.measure(r18.EXPECTED_CAGE)) == [10, 30, 6]
    assert set(r33.variables(r18.EXPECTED_CAGE)) == set(range(2, 8))
    assert r18.R in r18.EXPECTED_CAGE


def test_parent_pair_generates_all_variable_width6_clause():
    p = r33.canonical_clause((1, 2, 3, 4))
    n = r33.canonical_clause((-1, 5, 6, 7))
    u = (set(p) - {1}) | (set(n) - {-1})
    assert not any(-x in u for x in u)
    assert r33.canonical_clause(u) == r18.R


def test_firewall_is_local_until_reachability_is_proved():
    assert r18.GATE.endswith("ANCESTRY_AND_DOOR_AUDIT")
    assert r18.PIVOT == 1
