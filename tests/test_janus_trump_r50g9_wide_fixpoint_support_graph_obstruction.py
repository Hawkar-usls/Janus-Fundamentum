from experiments import janus_trump_r50g9_wide_fixpoint_support_graph_obstruction as r50g9


def test_degree_one_each_polarity_is_bve_pressure_defect():
    f = ((1, 2, 3, 4), (-1, 5, 6))
    row = r50g9.exact_bve_pressure(f, 1)
    assert row["p"] == 1
    assert row["n"] == 1
    assert row["q"] == 1
    assert row["m"] == 2
    assert row["q"] < row["m"]
    assert row["would_frozen_BVE_accept"] is True


def test_frozen_normalization_fixpoint_obeys_pressure_lemmas():
    control = r50g9.frozen_narrow_fixpoint_control()
    assert control["all_bipolar"] is True
    assert control["all_q_ge_p_plus_n"] is True
    assert control["all_p_n_ge_2"] is True
    assert control["variables"] > 0


def test_wide_clause_gets_distinct_primary_bce_supports():
    c = (1, 2, 3, 4, 5)
    f = [c]
    for i in range(1, 6):
        f.append((-i, 10 + i))
    cert = r50g9.wide_clause_support_pressure(tuple(f), c)
    assert cert["BCE_support_complete"] is True
    assert cert["distinct_primary_BCE_supports"] == 5
    assert cert["all_literals_balanced_2_by_2"] is False


def test_balanced_2x2_arithmetic_identity():
    assert 2 * 2 == 2 + 2
