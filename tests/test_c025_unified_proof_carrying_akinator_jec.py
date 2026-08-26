from experiments.direct.janus_unified_proof_carrying_akinator_jec import solve_fail_closed


def test_sat_units():
    r = solve_fail_closed([[1], [-1, 2]])
    assert r["status"] == "SAT"
    assert r["scientific_boundary"]["heuristic_promotion"] is False


def test_unsat_units():
    r = solve_fail_closed([[1], [-1]])
    assert r["status"] == "UNSAT"
    assert r["scientific_boundary"]["general_sat_oracle"] is False


def test_fail_closed_no_certified_move():
    r = solve_fail_closed([
        [1, 2, 3],
        [-1, -2, 3],
        [-1, 2, -3],
        [1, -2, -3],
    ])
    if r["status"] == "OPEN":
        assert r["reason"] == "NO_CERTIFIED_MOVE"
        assert "DISCOVER_MACRO" in r["missing_bridge"]
    assert r["scientific_boundary"]["heuristic_promotion"] is False


def test_no_false_unsat_on_xor_like_sat_core():
    r = solve_fail_closed([[1, 2], [-1, -2]])
    assert r["status"] != "UNSAT"


def test_no_false_sat_on_unsat_2var_core():
    # all four assignments forbidden
    r = solve_fail_closed([
        [1, 2],
        [1, -2],
        [-1, 2],
        [-1, -2],
    ])
    assert r["status"] in {"UNSAT", "OPEN"}
    assert r["status"] != "SAT"
