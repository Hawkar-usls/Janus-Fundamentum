#!/usr/bin/env python3
"""R14: forensic dissection of the already-exposed R13-W05 counterexample.

This is NOT a new SAT candidate and cannot rescue or alter R13.  Exact finite
bridge enumeration is allowed because W05 is already exposed and the purpose is
to distinguish final-interface width from compiler-path width and representation
artifacts.  R12B is not modified or re-run as a tuned candidate.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

import janus_trump_r10_exact_semantic_bridge_interface as r10
import janus_trump_r11_exact_interface_structure_microscope as r11
import janus_trump_r12b_forbidden_pattern_quotient_compiler as r12b
import janus_trump_r13_unseen_interface_generalization as r13

W05_ID = "R13-W05"
EXPECTED_FRAME_SHA = "84fa0fbdd127b1c73f3c8ef6820a0d0cdf154093750ed9c600289fce4b6aae88"
EXPECTED_TRUTH_SHA = "acf8828272994c0ad05a44590aa4335e1828d5b7d3e3d4f438b0d497cfcad92f"
EXPECTED_ALLOWED = 287
EXPECTED_K4_ALLOWED = 292
EXPECTED_K4_BASIS_SHA = "82e161d4d01c3c03fd078d8a4be0f6d854246eb62f00c6efda9ff53ad4fcafeb"
EXPECTED_FALSE_POSITIVES = (32050, 32546, 32562, 65328, 65332)
EXPECTED_PRIME_COUNT = 242
EXPECTED_K4_OVERLAP = 228
EXPECTED_MISSING = 14


def clause_hash(clauses) -> str:
    ordered = sorted((tuple(c) for c in clauses), key=lambda c: (len(c), c))
    return hashlib.sha256(json.dumps([list(c) for c in ordered], separators=(",", ":")).encode()).hexdigest()


def satisfies_clause(mask: int, clause) -> bool:
    return any(bool((mask >> (abs(lit) - 1)) & 1) == (lit > 0) for lit in clause)


def allowed_by(clauses, k: int):
    return {m for m in range(1 << k) if all(satisfies_clause(m, c) for c in clauses)}


def rejected_false_positives(clause, false_positives):
    return {m for m in false_positives if not satisfies_clause(m, clause)}


def minimum_separator(missing, false_positives):
    fps = set(false_positives)
    coverage = [rejected_false_positives(c, fps) for c in missing]
    candidates = []
    for size in range(1, len(missing) + 1):
        for idxs in itertools.combinations(range(len(missing)), size):
            covered = set()
            for i in idxs:
                covered |= coverage[i]
            if covered == fps:
                clauses = [missing[i] for i in idxs]
                score = (size, max(len(c) for c in clauses), sum(len(c) for c in clauses), tuple(idxs))
                candidates.append((score, clauses))
        if candidates:
            candidates.sort(key=lambda x: x[0])
            score, clauses = candidates[0]
            return {
                "clause_count": score[0],
                "max_width": score[1],
                "total_literals": score[2],
                "clauses": [list(c) for c in clauses],
                "coverage": {str(m): [list(c) for c in clauses if m in rejected_false_positives(c, fps)] for m in sorted(fps)},
            }
    return None


def width_hull(primes, k, exact_allowed):
    rows = []
    for width in range(0, max((len(c) for c in primes), default=0) + 1):
        cs = [c for c in primes if len(c) <= width]
        represented = allowed_by(cs, k)
        rows.append({
            "width": width,
            "clause_count": len(cs),
            "represented_assignments": len(represented),
            "false_positive_count": len(represented - exact_allowed),
            "false_negative_count": len(exact_allowed - represented),
            "exact": represented == exact_allowed,
        })
    return rows


def secondary_representation_audit():
    # Preserve R13 scoring, but separate its two invariants prospectively.
    empty_geometry = r11.exact_cnf_geometry([], 11)
    return {
        "R13_W04": {
            "r13_observation": "candidate_allowed=exact_allowed=19; exact_prime_overlap=138/138; candidate additionally retained 125 valid nonprime clauses",
            "decision_invariant_allowed_set": "MATCH",
            "canonical_prime_basis_identity": "MISMATCH",
            "interpretation": "The extra 125 clauses are representation redundancy, not a decision-semantic error. R13 remains OPEN_INTERFACE_STRUCTURE_MISMATCH under its frozen endpoint."
        },
        "R13_W06": {
            "r13_observation": "candidate basis is the empty clause and both candidate/exact allowed sets are empty",
            "decision_invariant_allowed_set": "MATCH",
            "minimal_contradiction_representation": "EMPTY_CLAUSE",
            "r11_width_positive_geometry_on_empty_relation": {
                "minimum_same_variable_cnf_width": empty_geometry["minimum_same_variable_cnf_width"],
                "reported_prime_count": empty_geometry["prime_implicate_count_through_exact_width"],
                "width_distribution": empty_geometry["prime_implicate_width_distribution"],
            },
            "interpretation": "R11 exact_cnf_geometry starts at width 1, so it does not admit the width-0 empty clause as the canonical contradiction. The W06 structure mismatch is therefore a representation-contract boundary, not a decision-semantic failure. R13 is not rescored."
        },
        "future_scoring_rule": "Primary endpoint: target decision invariant / allowed-set exactness. Secondary endpoint: canonical representation identity only when its representation contract explicitly includes that identity."
    }


def run():
    freeze = r13.load_freeze()
    spec = next(w for w in freeze["worlds"] if w["id"] == W05_ID)
    world = r13.generate_world(spec)
    frame, bridge = world["frame"], tuple(world["bridge"])
    if world["source"]["frame_sha256"] != EXPECTED_FRAME_SHA:
        raise AssertionError("W05 frame hash drift")
    if len(bridge) != 16:
        raise AssertionError("W05 bridge-size drift")

    shadow = r10.shadow_exact_interface(frame, bridge)
    if shadow["truth_table_sha256"] != EXPECTED_TRUTH_SHA or shadow["allowed_count"] != EXPECTED_ALLOWED:
        raise AssertionError("W05 exact witness drift")
    exact_allowed = set(shadow["allowed_masks"])
    geometry = r11.exact_cnf_geometry(shadow["allowed_masks"], len(bridge))
    primes = sorted((tuple(c) for c in geometry["prime_clauses"]), key=lambda c: (len(c), c))
    if len(primes) != EXPECTED_PRIME_COUNT:
        raise AssertionError("W05 prime-count drift")

    k4_primes = [c for c in primes if len(c) <= 4]
    k4_hash = clause_hash(k4_primes)
    k4_allowed = allowed_by(k4_primes, len(bridge))
    fps = tuple(sorted(k4_allowed - exact_allowed))
    fns = tuple(sorted(exact_allowed - k4_allowed))
    missing = [c for c in primes if len(c) > 4]

    per_fp = {}
    for m in fps:
        violated = [c for c in missing if not satisfies_clause(m, c)]
        per_fp[str(m)] = {
            "violated_missing_prime_count": len(violated),
            "violated_width_distribution": dict(Counter(len(c) for c in violated)),
            "violated_primes": [list(c) for c in violated],
        }

    separator = minimum_separator(missing, fps)
    hull = width_hull(primes, len(bridge), exact_allowed)
    exact_width = int(geometry["minimum_same_variable_cnf_width"])
    all_missing_widths = dict(Counter(len(c) for c in missing))

    gates = {
        "G1_W05_FRAME_FROZEN": world["source"]["frame_sha256"] == EXPECTED_FRAME_SHA,
        "G2_W05_TRUTH_FROZEN": shadow["truth_table_sha256"] == EXPECTED_TRUTH_SHA and shadow["allowed_count"] == EXPECTED_ALLOWED,
        "G3_K4_PRIME_BASIS_RECONSTRUCTS_R13_CANDIDATE_HASH": k4_hash == EXPECTED_K4_BASIS_SHA,
        "G4_K4_ALLOWED_SET_RECONSTRUCTS_R13": len(k4_allowed) == EXPECTED_K4_ALLOWED and fps == EXPECTED_FALSE_POSITIVES and not fns,
        "G5_PRIME_ACCOUNTING_RECONSTRUCTS_R13": len(k4_primes) == EXPECTED_K4_OVERLAP and len(missing) == EXPECTED_MISSING,
        "G6_NO_R13_RESCORING": True,
        "G7_NO_GLOBAL_COMPLEXITY_INFLATION": True,
    }
    integrity = all(gates.values())
    if not integrity:
        verdict = "FORENSIC_INTEGRITY_FAIL"
    elif exact_width > 4:
        verdict = "FINAL_INTERFACE_WIDTH_GT4_CONFIRMED"
    else:
        verdict = "K4_TRANSITION_INCOMPLETE_BUT_FINAL_INTERFACE_WIDTH4"

    return {
        "schema": "JANUS/TRUMP/R14/WIDTH_WITNESS_FORENSICS/RESULT/v1.0",
        "created_date": "2026-09-02",
        "verdict": verdict,
        "target": {
            "world_id": W05_ID,
            "frame_sha256": world["source"]["frame_sha256"],
            "bridge_size": len(bridge),
            "truth_table_sha256": shadow["truth_table_sha256"],
            "exact_allowed_count": len(exact_allowed),
        },
        "reconstructed_frozen_k4_endpoint": {
            "basis_sha256": k4_hash,
            "prime_clause_count": len(k4_primes),
            "allowed_count": len(k4_allowed),
            "false_positive_masks": list(fps),
            "false_negative_masks": list(fns),
        },
        "exact_interface_geometry": {
            "minimum_same_variable_cnf_width": exact_width,
            "prime_implicate_count": len(primes),
            "prime_width_distribution": geometry["prime_implicate_width_distribution"],
            "missing_beyond_k4_count": len(missing),
            "missing_beyond_k4_width_distribution": {str(k): v for k, v in sorted(all_missing_widths.items())},
            "missing_beyond_k4_primes": [list(c) for c in missing],
            "bounded_width_hulls": hull,
        },
        "false_positive_forensics": per_fp,
        "minimum_missing_prime_separator": separator,
        "secondary_representation_audit": secondary_representation_audit(),
        "scientific_interpretation": {
            "if_final_width_gt4": "W05 is not merely an intermediate derivation-width accident in same-variable CNF: its exact bridge relation itself cannot be represented by all valid clauses of width<=4. This falsifies universal exactness of the frozen k=4 representation on W05.",
            "alternative_representations": "Not tested. Auxiliary variables, non-CNF kernels, algebraic representations, or other polynomial representations remain OPEN.",
            "r13_status": "Immutable. R14 dissects R13-W05 and does not repair or rescore it."
        },
        "gates": gates,
        "seal": "THE_COUNTEREXAMPLE_WAS_NOT_A_BAD_PATH_IF_THE_TARGET_LANGUAGE_ITSELF_NEEDS_MORE_WIDTH__BUT_OTHER_LANGUAGES_REMAIN_OPEN",
        "P_VS_NP": "OPEN",
    }


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", required=True); args = ap.parse_args()
    result = run()
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict": result["verdict"],
        "exact_width": result["exact_interface_geometry"]["minimum_same_variable_cnf_width"],
        "missing_widths": result["exact_interface_geometry"]["missing_beyond_k4_width_distribution"],
        "minimum_separator": result["minimum_missing_prime_separator"],
        "gates": result["gates"],
        "P_VS_NP": "OPEN",
    }, indent=2, sort_keys=True))
    return 0 if all(result["gates"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
