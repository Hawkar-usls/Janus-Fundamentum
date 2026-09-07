from __future__ import annotations

import argparse
import json
from pathlib import Path

SOURCE = Path(__file__).with_name("janus_trump_r50g25aw_defect_component_decomposition.py")
BAD = '"recursive_separator_or_treewidth_rescue_inside_AW": false,'
GOOD = '"recursive_separator_or_treewidth_rescue_inside_AW": False,'


def load_single_token_fixed_namespace():
    source = SOURCE.read_text(encoding="utf-8")
    count = source.count(BAD)
    if count != 1:
        raise AssertionError(("AW_PLUMBING_FIX_SOURCE_DRIFT", count))
    corrected = source.replace(BAD, GOOD, 1)
    if corrected.count(BAD) != 0:
        raise AssertionError("AW_PLUMBING_FIX_REPLACEMENT_INCOMPLETE")
    ns = {
        "__name__": "janus_trump_r50g25aw_single_token_fixed",
        "__file__": str(SOURCE),
    }
    exec(compile(corrected, str(SOURCE), "exec"), ns, ns)
    return ns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    ns = load_single_token_fixed_namespace()
    result = ns["aggregate"](args.input_dir)
    result["technical_plumbing_fix"] = {
        "kind": "SINGLE_TOKEN_PYTHON_BOOLEAN_FIX",
        "source_file": SOURCE.name,
        "bad_token": "false",
        "replacement_token": "False",
        "replacement_count": 1,
        "scientific_contract_changed": False,
        "candidate_artifacts_recomputed": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict": result["verdict"],
        "candidate_count_audited": result["candidate_count_scientifically_audited_to_stop"],
        "residual_count": result["residual_count_audited_to_stop"],
        "maximum_B_component": result["maximum_B_component_observed"],
        "minimum_budget_slack": result["minimum_budget_slack_observed"],
        "failure_count": result["failure_count"],
        "single_token_fix": True,
    }, sort_keys=True))
    raise SystemExit(0 if result["failure_count"] == 0 else 1)


if __name__ == "__main__":
    main()
