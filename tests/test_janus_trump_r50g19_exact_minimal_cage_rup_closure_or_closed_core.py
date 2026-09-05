import janus_trump_r50g18_explicit_v7_full_sixfold_cage_ancestry_door_audit as r18
import janus_trump_r50g19_exact_minimal_cage_rup_closure_or_closed_core as r19


def test_r50g18_cage_extracts_six_head_witness_families():
    hg = r19.extract_exact_minimal_hypergraph(r18.EXPECTED_CAGE, r18.R)
    assert hg["variables"] == [2, 3, 4, 5, 6, 7]
    assert {e["head"] for e in hg["edges"]} == set(hg["variables"])
    assert hg["distinct_witness_clause_count"] >= 6


def test_r50g18_has_full_rup_closure():
    out = r19.closure_dichotomy(r18.EXPECTED_CAGE, r18.R)
    assert out["outcome"] == "FULL_RUP_CLOSURE_WITNESS"
    assert out["certificate"]["UP_conflict"] is True
    assert out["certificate"]["independent_UP_replay"] is True
    assert out["certificate"]["full"] is True


def test_abstract_two_component_hypergraph_yields_proper_closed_core():
    ctl = r19.abstract_closed_core_control()
    assert not any(x["full"] for x in ctl["closures"])
    assert [1, 2, 3] in [x["closure"] for x in ctl["closures"]]
    assert [4, 5, 6] in [x["closure"] for x in ctl["closures"]]


def test_universal_firewall_remains_open():
    assert r19.GATE.endswith("CLOSED_SUPPORT_CORE")
