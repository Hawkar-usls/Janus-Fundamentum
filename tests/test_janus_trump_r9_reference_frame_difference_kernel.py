import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments"
if str(EXP) not in sys.path:
    sys.path.insert(0, str(EXP))

import janus_trump_r9_reference_frame_difference_kernel as r9


def test_r9_candidate_firewall_has_no_hidden_search():
    assert r9.candidate_firewall()["pass"]


def test_r9a_tseitin_reference_frame_exact_radius_zero():
    frame = r9.compile_tseitin_frame(0)
    sat_charges, unsat_charges = r9.torus.charge_patterns(0)
    sat = r9.r9a_state(0, sat_charges, frame)
    unsat = r9.r9a_state(0, unsat_charges, frame)
    assert sat["terminal"] == "SAT" and sat["exact_replay"]
    assert unsat["terminal"] == "UNSAT" and unsat["exact_replay"]
    assert sat["frame_sha256"] == unsat["frame_sha256"]


def test_r9b_two_frozen_open_worlds_reconstruct_exactly():
    d = r9.r9b_extract_open_worlds()
    assert len(d["rows"]) == 2
    assert d["all_exact_reconstruction"]
    assert d["all_same_sibling_frame"]
    assert [row["global_index"] for row in d["rows"]] == [3, 7]


def test_r9c_never_promotes_general_cnf_without_bridge_rule():
    assert not r9.compose_gate("GENERAL_CNF", "TWO_SAT", 7)["terminal_composition_admitted"]
    assert not r9.compose_gate("GENERAL_CNF", "HORN", 7)["terminal_composition_admitted"]
    assert r9.compose_gate("TWO_SAT", "TWO_SAT", 7)["terminal_composition_admitted"]
