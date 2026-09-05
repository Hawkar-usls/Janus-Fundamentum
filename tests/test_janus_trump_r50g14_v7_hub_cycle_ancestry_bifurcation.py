import janus_trump_r50g14_v7_hub_cycle_ancestry_bifurcation as r14


def test_direct5_control():
    rows = r14.source_ancestry_controls()["DIRECT5"]
    assert any(r["type"] == "DIRECT5" for r in rows)
    assert all(r["geometry"]["resolvent_width"] in (5, 6) for r in rows)


def test_rup6_control():
    rows = r14.source_ancestry_controls()["RUP6_DROP_HUB"]
    hit = next(r for r in rows if r["type"] == "RUP6_DROP_HUB")
    assert hit["removed_hub_literal"] == 7
    assert hit["geometry"]["positive_width"] == 4
    assert hit["geometry"]["negative_width"] == 4
    assert hit["geometry"]["overlap"] == 0
    assert r14.rup6_control()["independent_replay"] is True


def test_cycle_bifurcation():
    assert r14.cycle_label_bifurcation(["DIRECT5", "DIRECT5"]) == "ALL_DIRECT5_CYCLE"
    assert r14.cycle_label_bifurcation(["DIRECT5", "RUP6_DROP_HUB"]) == "RUP_BEARING_CYCLE"


def test_firewall_and_regression():
    out = r14.run()
    fw = out["firewall"]
    assert fw["V6_IMMEDIATE_BVE_CASE_ELIMINATED"] is True
    assert fw["V7_IMMEDIATE_BVE_CASE_ELIMINATED"] is False
    assert fw["IMMEDIATE_BVE_CASE_ELIMINATED"] is False
    assert fw["U_MU"] == "OPEN"
    assert fw["SAT_IN_P"] == "NOT_PROVED"
    assert fw["P_VS_NP"] == "OPEN"
    assert fw["TRUMP_finished"] is False
