from __future__ import annotations

from janus_trump_osiris_r5_fehlerbild_positive_roi_discovery import (
    R5_RULE_ID,
    _r5_witness,
    evaluate_row,
    r5_spiral_candidate,
)
from janus_trump_p_vs_np_direct_challenge_r0 import canon


def test_pretruth_witness_has_no_answer_fields():
    cnf = canon([(1, 2), (-1, 2), (3, -4), (-3, 4)])
    source = {"family": "TEST", "arena": "UNIT"}
    w = _r5_witness(source, cnf)
    assert w["frozen_rule_id"] == R5_RULE_ID
    assert w["truth"] is None
    assert w["exact_result"] is None
    assert w["spiral_result"] is None
    assert w["delta_w"] is None


def test_disconnected_separator_is_exact():
    # First component is an explicit 2-variable contradiction; second is SAT.
    cnf = canon([
        (1, 2), (1, -2), (-1, 2), (-1, -2),
        (-3, 4), (3, -4),
    ])
    source = {"family": "TEST_DISCONNECTED", "arena": "UNIT"}
    w = _r5_witness(source, cnf)
    c = r5_spiral_candidate(cnf, w)
    assert c.mode == "R5_EMPTY_SEPARATOR_DOUBLE_SPIRAL"
    assert c.separator == []
    assert c.terminal == "UNSAT"


def test_articulation_separator_is_exact():
    # x2 is the only primal articulation between the left and right clauses.
    cnf = canon([(1, 2), (-1, 2), (-2, 3), (-2, -3)])
    source = {"family": "TEST_ARTICULATION", "arena": "UNIT"}
    w = _r5_witness(source, cnf)
    c = r5_spiral_candidate(cnf, w)
    assert c.mode == "R5_ARTICULATION_DOUBLE_SPIRAL"
    assert c.separator == [2]
    assert c.terminal in {"SAT", "UNSAT"}


def test_fehlerbild_evaluation_requires_same_world():
    cnf = canon([
        (1, 2), (1, -2), (-1, 2), (-1, -2),
        (-3, 4), (3, -4),
    ])
    source = {"family": "TEST_EVAL", "arena": "UNIT"}
    row = {"source": source, "cnf": cnf, "pretruth_witness": _r5_witness(source, cnf)}
    result = evaluate_row(row)
    assert result["checks"]["terminal_agreement"] is True
    assert result["checks"]["oracle_agreement"] is True
    assert result["checks"]["exact_sat_replay"] is True
    assert result["checks"]["spiral_sat_replay"] is True
    assert isinstance(result["fehlerbild"]["delta_w_exact_minus_spiral"], int)
