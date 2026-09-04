from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47x_cap_projection_coverage_one_swap_falsifier as r47x
import janus_trump_r48q_width4_full_frozen_frontier_falsifier as r48q

GATE = "JANUS_TRUMP_R48Y_DIRECT_ENTRY_WIDTH4_HARD_ORIGINAL_KILLER"
EXPECTED_HASH = "eb13be26c29c106cf172db0be435aaf852d1e1248fced151c5356791f70024da"
EXPECTED_CLV = (114, 342, 30)
WIDTH_CAP = 4


def compact(record):
    return {
        "covered": bool(record["covered"]),
        "root_hash": record["root_hash"],
        "root_CLV": record["root_CLV"],
        "root_max_width": int(record["root_max_width"]),
        "candidate_probe_count": int(record["candidate_probe_count"]),
        "selected_step_count": len(record["selected_path"]),
        "selected_pivots": [int(x["var"]) for x in record["selected_path"]],
        "persisted_widths": [int(x["final_max_width"]) for x in record["selected_path"]],
        "max_persisted_width": int(record["max_persisted_width"]),
        "terminal": record["terminal"],
        "obstruction": record["obstruction"],
    }


def run():
    original, _, _ = r47x.load_center_original()
    original = r33.canonical_formula(original)
    h = r48q.formula_hash(original)
    c = tuple(r33.measure(original))
    w = r48q.max_width(original)
    if h != EXPECTED_HASH:
        raise AssertionError(("R48Y_HASH_DRIFT", h))
    if c != EXPECTED_CLV:
        raise AssertionError(("R48Y_CLV_DRIFT", c))
    if w != 3:
        raise AssertionError(("R48Y_INPUT_WIDTH_DRIFT", w))
    r47x.validate_exact_3cnf(original)

    record = r48q.run_width4_root(original, {
        "kind": "DIRECT_EXACT_3CNF_ENTRY",
        "source": "R47K_MUTATED_ORIGINAL",
        "source_hash": h,
        "preprocessing_before_controller": False,
    })
    out = {
        "gate": GATE,
        "verdict": (
            "DIRECT_HARD_ORIGINAL_REACHES_CERTIFIED_TERMINAL_UNDER_WIDTH4_CHAIN__FINITE_ONLY"
            if record["covered"]
            else "EXPLICIT_DIRECT_ENTRY_WIDTH4_OBSTRUCTION_FOUND"
        ),
        "width_cap": WIDTH_CAP,
        "input": {
            "hash": h,
            "CLV": list(c),
            "max_width": w,
            "preprocessing_before_controller": False,
        },
        "width4": compact(record),
        "interpretation": {
            "single_hard_original_only": True,
            "coverage_proves_universal_direct_W4_step": False,
            "obstruction_refutes_direct_entry_W4_controller": True,
            "obstruction_refutes_all_preprocessed_W4_routes": False,
        },
        "firewall": {
            "DIRECT_W4_STEP_COVERAGE": "OPEN_UNLESS_REFUTED_BY_THIS_GATE",
            "UNIVERSAL_WIDTH_4_COVERAGE": "NOT_PROVED",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    a = ap.parse_args()
    out = run()
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": out["gate"],
        "verdict": out["verdict"],
        "input": out["input"],
        "selected_pivots": out["width4"]["selected_pivots"],
        "persisted_widths": out["width4"]["persisted_widths"],
        "max_persisted_width": out["width4"]["max_persisted_width"],
        "terminal": out["width4"]["terminal"],
        "obstruction": None if out["width4"]["obstruction"] is None else {
            "kind": out["width4"]["obstruction"]["kind"],
            "state_hash": out["width4"]["obstruction"]["state_hash"],
            "state_CLV": out["width4"]["obstruction"]["state_CLV"],
            "state_max_width": out["width4"]["obstruction"]["state_max_width"],
        },
        "firewall": out["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
