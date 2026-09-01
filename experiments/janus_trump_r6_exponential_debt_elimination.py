#!/usr/bin/env python3
"""TRUMP R6 — exponential-debt elimination spider.

R6 is a theorem-path hygiene pass.  It walks every line of the current
TRUMP execution lineage used by the P-vs-NP experiments, marks source-level
constructs that can carry exponential/unbounded worst-case debt, and requires
one of two resolutions for every hit:

  * POLYNOMIAL_BOUND_PROVED
  * QUARANTINED_FROM_P_EQUALS_NP_CANDIDATE_PATH

R6 does NOT prove P=NP.  Quarantining every known exponential primitive can
leave the surviving theorem-candidate path incomplete; in that case the only
admissible verdict is that debt elimination succeeded but theorem closure did
not.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRE = ROOT / "research/JANUS_TRUMP_R6_EXPONENTIAL_DEBT_ELIMINATION_PREREGISTRATION_2026-09-01.json"

TARGETS = [
    ROOT / "experiments/janus_trump_p_vs_np_direct_challenge_r0.py",
    ROOT / "experiments/janus_trump_osiris_r3_natural_residuals.py",
    ROOT / "experiments/janus_trump_osiris_r3b_proof_carrying_recovery.py",
    ROOT / "experiments/janus_trump_osiris_r4_roi_gate.py",
    ROOT / "experiments/janus_trump_osiris_r5_fehlerbild_positive_roi_discovery.py",
]

ALLOWED_RESOLUTIONS = {
    "POLYNOMIAL_BOUND_PROVED",
    "QUARANTINED_FROM_P_EQUALS_NP_CANDIDATE_PATH",
}


@dataclass(frozen=True)
class Rule:
    rule_id: str
    debt_class: str
    regex: str
    reason: str


RULES = [
    Rule(
        "R6-DPLL-BINARY-RECURSION",
        "BINARY_RECURSIVE_SEARCH",
        r"ans\s*=\s*rec\(restrict_cnf\(f,v,True\)\)\s+or\s+rec\(restrict_cnf\(f,v,False\)\)",
        "DPLL recursively explores both truth branches; no global polynomial bound is present.",
    ),
    Rule(
        "R6-ROBDD-LOW-BRANCH",
        "ROBDD_BRANCHING_WITH_CAP_ONLY",
        r"\blo\s*=\s*rec\(restrict_cnf\(f,v,False\)",
        "ROBDD recursively expands the low branch; the finite cap is a resource guard, not a polynomial proof.",
    ),
    Rule(
        "R6-ROBDD-HIGH-BRANCH",
        "ROBDD_BRANCHING_WITH_CAP_ONLY",
        r"\bhi\s*=\s*rec\(restrict_cnf\(f,v,True\)",
        "ROBDD recursively expands the high branch; representation size may grow exponentially.",
    ),
    Rule(
        "R6-DP-POS-LOOP",
        "DAVIS_PUTNAM_RESOLVENT_CROSS_PRODUCT_WITH_CAP_ONLY",
        r"for\s+a\s+in\s+pos\s*:",
        "Davis-Putnam elimination enters the positive-clause side of a resolvent cross product.",
    ),
    Rule(
        "R6-DP-NEG-LOOP",
        "DAVIS_PUTNAM_RESOLVENT_CROSS_PRODUCT_WITH_CAP_ONLY",
        r"for\s+b\s+in\s+neg\s*:",
        "Nested with the positive loop, this forms a resolvent cross product with unproved global representation bound.",
    ),
    Rule(
        "R6-EXP-VERIFIER-PROXY",
        "EXPONENTIAL_VERIFICATION_PROXY",
        r"1\s*<<\s*len\(vs\)",
        "The accounting proxy explicitly contains 2^n.",
    ),
    Rule(
        "R6-EXACT-SEARCH-BINARY-LOOP",
        "BINARY_RECURSIVE_SEARCH",
        r"for\s+val\s+in\s+\(False,\s*True\)\s*:",
        "A binary assignment expansion is potentially exponential when coupled to recursive exact search; experimental probes are quarantined too.",
    ),
    Rule(
        "R6-EXACT-SEARCH-RECURSIVE-CALL",
        "EXACT_SEARCH_WITNESS_FALLBACK_OR_WING",
        r"hit\s*=\s*rec\(i\s*\+\s*1,\s*a\)",
        "Exact witness search recurses one assignment level deeper with no global polynomial bound.",
    ),
    Rule(
        "R6-SEPARATOR-ASSIGNMENT-PRODUCT",
        "EXHAUSTIVE_SEPARATOR_ASSIGNMENT_ENUMERATION",
        r"product\(\(False,\s*True\),\s*repeat=len\(sep_order\)\)",
        "Enumerates all 2^|S| separator assignments.",
    ),
    Rule(
        "R6-DPLL-CALL",
        "EXACT_DPLL_FALLBACK_OR_VERIFIER",
        r"\bdpll\(",
        "Any exact DPLL call used as fallback/oracle/verifier carries the unresolved worst-case search debt of DPLL.",
    ),
    Rule(
        "R6-EXACT-SEARCH-CALL",
        "EXACT_SEARCH_WITNESS_FALLBACK_OR_WING",
        r"\bexact_search_witness\(",
        "Calls into the exact binary witness search unless a separate polynomial proof replaces it.",
    ),
    Rule(
        "R6-R3B-CANDIDATE-CALL",
        "EXACT_SEARCH_WITNESS_FALLBACK_OR_WING",
        r"\br3b_candidate\(",
        "R3B candidate may enter exact meet wings or proof-carrying exact fallback and is therefore theorem-path tainted until globally bounded.",
    ),
]

# No global polynomial theorem has been supplied for any hazard class at the R6
# freeze point.  Therefore every detected hazard is quarantined rather than
# falsely promoted.  Future versions may populate this only with a concrete
# machine-checkable proof reference.
POLYNOMIAL_BOUND_PROOFS: dict[str, dict] = {}

SAFE_STRUCTURAL_PRIMITIVES = [
    "canon",
    "restrict_cnf",
    "variables",
    "formula_status",
    "verify_sat",
    "formula_digest",
    "unit_close",
    "occurrence_pivot",
    "build_primal_graph",
    "graph_signature",
    "_components_without",
    "_greedy_split",
    "split_by_separator",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def resolution_for(rule: Rule) -> tuple[str, dict | None]:
    proof = POLYNOMIAL_BOUND_PROOFS.get(rule.rule_id)
    if proof is not None:
        return "POLYNOMIAL_BOUND_PROVED", proof
    return "QUARANTINED_FROM_P_EQUALS_NP_CANDIDATE_PATH", None


def scan_file(path: Path) -> tuple[dict, list[dict]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    hits: list[dict] = []
    for line_no, code in enumerate(lines, start=1):
        for rule in RULES:
            if re.search(rule.regex, code):
                resolution, proof = resolution_for(rule)
                hits.append({
                    "file": rel(path),
                    "line": line_no,
                    "code": code.strip(),
                    "rule_id": rule.rule_id,
                    "debt_class": rule.debt_class,
                    "reason": rule.reason,
                    "resolution": resolution,
                    "polynomial_bound_proof": proof,
                })
    meta = {
        "file": rel(path),
        "line_count": len(lines),
        "sha256": sha256_text(text),
        "hazard_hits": len(hits),
    }
    return meta, hits


def audit() -> dict:
    prereg = json.loads(PRE.read_text(encoding="utf-8"))
    assert prereg["status"] == "FROZEN_BEFORE_R6_EXECUTION"
    assert prereg["P_VS_NP_before_R6"] == "OPEN"
    assert set(prereg["allowed_resolutions"]) == ALLOWED_RESOLUTIONS

    file_meta = []
    hits = []
    for path in TARGETS:
        meta, row_hits = scan_file(path)
        file_meta.append(meta)
        hits.extend(row_hits)

    # A single source line may match more than one valid debt rule (for example
    # a DPLL definition/call context); preserve all classifications but derive a
    # unique source-location count too.
    unique_locations = sorted({(h["file"], h["line"]) for h in hits})
    resolution_counts: dict[str, int] = {}
    class_counts: dict[str, int] = {}
    for h in hits:
        resolution_counts[h["resolution"]] = resolution_counts.get(h["resolution"], 0) + 1
        class_counts[h["debt_class"]] = class_counts.get(h["debt_class"], 0) + 1

    unresolved = [h for h in hits if h["resolution"] not in ALLOWED_RESOLUTIONS]
    unquarantined_without_proof = [
        h for h in hits
        if h["resolution"] != "QUARANTINED_FROM_P_EQUALS_NP_CANDIDATE_PATH"
        and h["resolution"] != "POLYNOMIAL_BOUND_PROVED"
    ]
    bound_proved = [h for h in hits if h["resolution"] == "POLYNOMIAL_BOUND_PROVED"]
    quarantined = [h for h in hits if h["resolution"] == "QUARANTINED_FROM_P_EQUALS_NP_CANDIDATE_PATH"]

    # Quarantining all current exact/exhaustive terminal mechanisms leaves only
    # structural preprocessing/witness-checking primitives.  Those are useful,
    # but they are not a total arbitrary-CNF SAT decider.
    candidate_path = {
        "surviving_safe_structural_primitives": SAFE_STRUCTURAL_PRIMITIVES,
        "quarantined_hazard_hits": len(quarantined),
        "polynomial_bound_proved_hazard_hits": len(bound_proved),
        "has_terminal_arbitrary_cnf_sat_decider_after_quarantine": False,
        "has_terminal_arbitrary_cnf_unsat_decider_after_quarantine": False,
        "total_for_arbitrary_cnf": False,
        "interpretation": "R6 successfully prevents known exponential/unbounded primitives from carrying P=NP theorem authority, but no total solver survives the quarantine."
    }

    obligations = {
        "ALL_TARGET_FILES_SCANNED_LINE_BY_LINE": len(file_meta) == len(TARGETS) and all(m["line_count"] > 0 for m in file_meta),
        "ALL_DETECTED_DEBT_HAS_ALLOWED_RESOLUTION": len(unresolved) == 0 and len(unquarantined_without_proof) == 0,
        "NO_FINITE_CAP_ACCEPTED_AS_POLYNOMIAL_PROOF": len(bound_proved) == 0,
        "KNOWN_EXPONENTIAL_DEBT_QUARANTINED": len(quarantined) > 0 and len(quarantined) == len(hits),
        "CANDIDATE_PATH_NONEMPTY": len(SAFE_STRUCTURAL_PRIMITIVES) > 0,
        "CANDIDATE_PATH_TOTAL_FOR_ARBITRARY_CNF": candidate_path["total_for_arbitrary_cnf"],
        "TOTAL_CORRECTNESS_EVERY_INPUT_PROVED": False,
        "END_TO_END_POLYNOMIAL_BOUND_PROVED": False,
        "FORMAL_OR_MACHINE_CHECKABLE_GLOBAL_P_EQUALS_NP_PROOF": False,
    }

    elimination_pass = (
        obligations["ALL_TARGET_FILES_SCANNED_LINE_BY_LINE"]
        and obligations["ALL_DETECTED_DEBT_HAS_ALLOWED_RESOLUTION"]
        and obligations["NO_FINITE_CAP_ACCEPTED_AS_POLYNOMIAL_PROOF"]
        and obligations["KNOWN_EXPONENTIAL_DEBT_QUARANTINED"]
    )
    closure_ready = all(obligations.values())

    if closure_ready:
        verdict = "R6_P_VS_NP_CLOSURE_CANDIDATE_READY_FOR_FORMAL_REVIEW"
        pnp = "CLOSURE_REVIEW"
    elif elimination_pass:
        verdict = "R6_DEBT_ELIMINATION_PASS__THEOREM_PATH_INCOMPLETE__P_VS_NP_OPEN"
        pnp = "OPEN"
    else:
        verdict = "R6_DEBT_ELIMINATION_FAIL__UNRESOLVED_EXECUTION_DEBT__P_VS_NP_OPEN"
        pnp = "OPEN"

    return {
        "schema": "JANUS/TRUMP/R6/EXPONENTIAL_DEBT_ELIMINATION/RESULT/v1.0",
        "status": "FROZEN_R6_RESULT",
        "verdict": verdict,
        "P_VS_NP": pnp,
        "closure_ready": closure_ready,
        "elimination_pass": elimination_pass,
        "scan": {
            "files_scanned": len(file_meta),
            "lines_scanned": sum(m["line_count"] for m in file_meta),
            "file_manifest": file_meta,
            "hazard_rule_count": len(RULES),
            "hazard_hits": len(hits),
            "unique_hazard_source_locations": len(unique_locations),
            "debt_class_counts": dict(sorted(class_counts.items())),
            "resolution_counts": dict(sorted(resolution_counts.items())),
        },
        "hazards": hits,
        "candidate_proof_path_after_quarantine": candidate_path,
        "closure_obligations": obligations,
        "blocking_obligations": [k for k, ok in obligations.items() if not ok],
        "highest_admissible_claim": (
            "R6 line-scanned the current theorem-relevant TRUMP execution lineage and quarantined every detected source-level exponential/unbounded-debt primitive from P=NP theorem authority. This removes known exponential debt from the candidate proof path only by making that path incomplete: no total arbitrary-CNF SAT/UNSAT decider survives. Therefore P vs NP remains OPEN."
        ),
        "next_gate": (
            "Construct a total arbitrary-CNF terminal mechanism using only primitives with proved polynomial bounds, or supply machine-checkable global polynomial bounds for currently quarantined primitives. Then rerun R6 before any P=NP closure claim."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    result = audit()
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "verdict": result["verdict"],
        "P_VS_NP": result["P_VS_NP"],
        "elimination_pass": result["elimination_pass"],
        "closure_ready": result["closure_ready"],
        "scan": result["scan"],
        "blocking_obligations": result["blocking_obligations"],
    }, indent=2))
    return 0 if result["elimination_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
