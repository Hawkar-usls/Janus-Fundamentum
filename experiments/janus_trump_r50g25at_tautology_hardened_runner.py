from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r50g25at_affine_core_plus_defect_polynomial_door as at

EXPECTED_AS_DEFECT = (8, 12, 14, 15, 16)
ORIGINAL_EXTRACT = at.extract_affine_core
EXTRACTION_TRACE = []


def is_tautology(clause):
    s = set(int(lit) for lit in clause)
    return any(-lit in s for lit in s)


def hardened_extract(formula):
    source = at.canonical(formula)
    tautologies = [tuple(c) for c in source if is_tautology(c)]
    effective = [tuple(c) for c in source if not is_tautology(c)]

    result = ORIGINAL_EXTRACT(effective)
    result["tautology_count"] = len(tautologies)
    result["tautology_check_pass"] = True
    result["tautologies_dropped_as_semantic_true"] = [list(c) for c in tautologies]
    result["source_clause_count_before_tautology_drop"] = len(source)
    result["effective_clause_count_after_tautology_drop"] = len(effective)
    result["explicit_tautology_policy"] = "DETECT_AND_DROP_AS_ALWAYS_TRUE_BEFORE_AFFINE_GROUPING"

    EXTRACTION_TRACE.append({
        "tautology_count": len(tautologies),
        "defects": [tuple(c) for c in result["defects"]],
        "recognized_equation_count": int(result["recognized_equation_count"]),
        "affine_clause_count": int(result["affine_clause_count"]),
    })
    return result


def run_hardened():
    at.extract_affine_core = hardened_extract
    result = at.run()

    hardening_failures = []
    if len(EXTRACTION_TRACE) != result.get("candidate_count_audited", 0):
        hardening_failures.append({
            "kind": "TAUTOLOGY_HARDENING_TRACE_COUNT_MISMATCH",
            "trace_count": len(EXTRACTION_TRACE),
            "candidate_count": result.get("candidate_count_audited"),
        })

    for i, row in enumerate(result.get("rows", [])):
        if i >= len(EXTRACTION_TRACE):
            break
        trace = EXTRACTION_TRACE[i]
        row["result"]["extraction"]["tautology_count"] = trace["tautology_count"]
        row["result"]["extraction"]["tautology_check_pass"] = True
        row["result"]["extraction"]["explicit_tautology_policy"] = "DETECT_AND_DROP_AS_ALWAYS_TRUE_BEFORE_AFFINE_GROUPING"

    observed_as_defects = EXTRACTION_TRACE[0]["defects"] if EXTRACTION_TRACE else []
    if observed_as_defects != [EXPECTED_AS_DEFECT]:
        hardening_failures.append({
            "kind": "AS_EXACT_DEFECT_MISMATCH",
            "expected": [list(EXPECTED_AS_DEFECT)],
            "observed": [list(c) for c in observed_as_defects],
        })

    result["hardening"] = {
        "status": "PASS" if not hardening_failures else "FAIL",
        "explicit_tautology_handling": True,
        "tautology_policy": "DETECT_AND_DROP_AS_ALWAYS_TRUE_BEFORE_AFFINE_GROUPING",
        "tautology_counts_by_candidate": [t["tautology_count"] for t in EXTRACTION_TRACE],
        "AS_exact_defect_expected": list(EXPECTED_AS_DEFECT),
        "AS_exact_defect_observed": [list(c) for c in observed_as_defects],
        "AS_exact_defect_match": observed_as_defects == [EXPECTED_AS_DEFECT],
        "failures": hardening_failures,
    }

    if hardening_failures:
        result["falsifiers"].extend(hardening_failures)
        result["falsifier_count"] = len(result["falsifiers"])
        result["verdict"] = at.FAIL

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("JANUS_TRUMP_R50G25AT_RESULT.json"))
    args = parser.parse_args()
    result = run_hardened()
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": result["gate"],
        "verdict": result["verdict"],
        "falsifier_count": result["falsifier_count"],
        "hardening_status": result.get("hardening", {}).get("status"),
        "AS_exact_defect_match": result.get("hardening", {}).get("AS_exact_defect_match"),
    }, sort_keys=True))
    raise SystemExit(0 if result["verdict"] == at.PASS and result.get("hardening", {}).get("status") == "PASS" else 1)


if __name__ == "__main__":
    main()
