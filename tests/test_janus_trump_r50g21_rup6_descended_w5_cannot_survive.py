import janus_trump_r50g21_rup6_descended_w5_cannot_survive as r50g21


def test_r50g18_realizes_proper_hub_support_case_and_child_is_rup_reducible():
    out = r50g21.proper_hub_witness_case_r50g18()
    assert out["creation_step"] == 7
    assert out["removed_hub_literal"] == 2
    assert out["proper_z_witness"]["support"] != out["child_C"]
    assert out["chosen_missing_literal"] in out["child_C"]
    assert out["child_one_literal_deletion_rup_valid"] is True
    assert out["independent_full_pass_replay"] is True


def test_opposite_full_twin_dual_support_forces_child_rup():
    out = r50g21.abstract_twin_dual_support_control()
    assert out["UP_conflict"] is True
    assert out["independent_UP_replay"] is True
    assert abs(out["R_side_witness"][1]) == 1
    assert abs(out["twin_side_witness"][1]) == 1


def test_source_dichotomy_is_exhaustive_and_ancestry_reduces_to_direct5():
    d = r50g21.source_case_dichotomy_contract()
    a = r50g21.r50g14_ancestry_collapse_contract()
    assert d["exhaustive"] is True
    assert a["prior_exact_labels"] == ["DIRECT5", "RUP6_DROP_HUB"]
    assert a["remaining_surviving_label"] == "DIRECT5"
    assert a["remaining_cycle_class"] == "ALL_DIRECT5_CYCLE"


def test_r50g21_firewalls_promote_only_rup_branch_elimination():
    out = r50g21.run()
    fw = out["firewall"]
    assert fw["RUP6_DESCENDED_NOVEL_W5_SURVIVOR"] == "ELIMINATED_BY_SOURCE_DICHOTOMY"
    assert fw["RUP6_DROP_HUB_SURVIVING_V7_EDGE_ELIMINATED"] is True
    assert fw["RUP_BEARING_V7_HUB_CYCLE_ELIMINATED"] is True
    assert fw["V7_SURVIVING_HUB_CYCLE_CLASS"] == "ALL_DIRECT5_ONLY"
    assert fw["ALL_DIRECT5_V7_HUB_CYCLE_ELIMINATED"] is False
    assert fw["V7_IMMEDIATE_BVE_CASE_ELIMINATED"] is False
    assert fw["U_MU"] == "OPEN"
    assert fw["SAT_IN_P"] == "NOT_PROVED"
    assert fw["P_VS_NP"] == "OPEN"
    assert fw["TRUMP_finished"] is False
