import time

import janus_trump_r15f_incremental_independent_semantic_control as r15f


def test_r15f_tiny_projection_truth_table():
    assert r15f.tiny_incremental_control()


def test_r15f_assumption_encoding():
    bridge = (2, 5, 9)
    assert r15f.assumptions_for_mask(bridge, 0) == [-2, -5, -9]
    assert r15f.assumptions_for_mask(bridge, 5) == [2, -5, 9]


def test_r15f_model_replay_accepts_and_rejects():
    cnf = ((1, 2), (-1, 3))
    assert r15f.replay_model(cnf, [2, -3], [-1, 2, -3])
    assert not r15f.replay_model(cnf, [2, -3], [1, 2, -3])


def test_r15f_incremental_two_solver_names_available():
    cnf = ((1, 2), (-1, 3))
    bridge = (2, 3)
    for name in (r15f.ORIGINAL_SOLVER, r15f.CANDIDATE_SOLVER):
        out = r15f.incremental_allowed_masks(cnf, bridge, name, time.monotonic() + 10.0, "TEST")
        assert out["status"] == "COMPLETE"
        assert out["allowed_masks"] == [1, 2, 3]
        assert out["sat_model_replay_failures"] == []


def test_r15f_claim_ceiling_remains_open():
    assert r15f.EXPECTED_ALLOWED == 287
    assert r15f.EXPECTED_TRUTH_SHA == "acf8828272994c0ad05a44590aa4335e1828d5b7d3e3d4f438b0d497cfcad92f"
