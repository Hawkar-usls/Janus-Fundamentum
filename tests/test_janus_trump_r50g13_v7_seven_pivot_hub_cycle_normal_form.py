import janus_trump_r50g13_v7_seven_pivot_hub_cycle_normal_form as r13


def test_fixed_point_free_function_has_cycle_control():
    out = r13.combinatorial_control()
    assert out["first_cycle"] == [1, 2, 1]
    assert out["cycle_length"] == 2


def test_cycle_finder_handles_long_cycle():
    mapping = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 1}
    cycle = r13.first_cycle(mapping)
    assert cycle == [1, 2, 3, 4, 5, 6, 7, 1]


def test_widest_clause_is_deterministic():
    f = r13.canon([(1, 2, 3, 4, 5), (-1, 2, 3, 4, 6), (1, 2, 3)])
    c = r13.widest_clause(f)
    assert len(c) == 5
    assert c == sorted([cl for cl in f if len(cl) == 5])[0]


def test_firewall_constants():
    assert r13.SOURCE_V == 7
    assert r13.WIDTH_CAP == 4
