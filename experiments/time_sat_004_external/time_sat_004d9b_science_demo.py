#!/usr/bin/env python3
"""JANUS 004D9B: small, falsifiable, source-bound mathematical demonstration.

Same-administrator development example, NOT a discovery, blind holdout, external
replication, novel inference rule or performance claim. Independently enumerate
the full truth table and verify every JANUS-derived XOR and resolution DAG.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import itertools
import json
from pathlib import Path
import sys

DIRECT = Path(__file__).resolve().parents[1] / "direct"
sys.path.insert(0, str(DIRECT))
from janus_time_sat_004d4d_paged_support import extract_paged_mixed_xor
from janus_time_sat_004d7_rank_gate import source_rank_experiment
from janus_time_sat_004d6_replay import replay_all

# XOR(x,y,z)=1: the four forbidden even-parity assignments, encoded in CNF.
XOR3_ONE = [[1, 2, 3], [1, -2, -3], [-1, 2, -3], [-1, -2, 3]]

def cases():
    return {
        "guarded_source_derived_rank": {
            "n": 4,
            "rows": [[4] + c for c in XOR3_ONE] + [[-4]],
            "explanation": "Resolution on unit -w exposes x XOR y XOR z = 1; no new information beyond source CNF."
        },
        "explicit_xor_no_increment": {
            "n": 3,
            "rows": XOR3_ONE,
            "explanation": "Source already contains complete XOR mask; derived-rank gain must be zero."
        },
        "linear_combination_no_increment": {
            "n": 4,
            "rows": [[4 if abs(v)==3 else v for v in c] for c in XOR3_ONE]
                    + [[3, -4], [-3, 4]],
            "explanation": "An implied x XOR y XOR z is a combination of known source XOR equations."
        },
        "not_every_cnf_is_parity": {
            "n": 3,
            "rows": [[1, 2, 3], [-1, 2, 3]],
            "explanation": "Ordinary CNF has a resolvent but no full parity mask; no false XOR admission."
        }
    }

def satisfying_assignments(rows, n):
    if not 1 <= n <= 8:
        raise ValueError("Only tiny exhaustive examples allowed")
    out = []
    for values in itertools.product((False, True), repeat=n):
        if all(any(values[abs(l)-1] == (l > 0) for l in clause) for clause in rows):
            out.append(values)
    return out

def independent_rank(equations, n, augmented):
    """Pure integer elimination independent of JANUS rank-gate implementation."""
    pivots = {}
    for eq in sorted(equations):
        support, rhs = eq
        mask = 0
        for v in support:
            mask ^= 1 << (v-1)
        if augmented:
            mask |= rhs << n
        while mask:
            k = mask.bit_length()-1
            if k not in pivots:
                pivots[k] = mask
                break
            mask ^= pivots[k]
    return len(pivots)

def examine(name, instance):
    n, rows = instance["n"], instance["rows"]
    models = satisfying_assignments(rows, n)
    source = extract_paged_mixed_xor(rows, n)
    if source["status"] != "SOURCE_PARTITION_VERIFIED":
        raise AssertionError(source["status"])
    result = source_rank_experiment(rows, n)
    if result["status"] != "SOURCE_PROOF_REPLAY_AND_EXACT_GF2_RANK_PASS":
        raise AssertionError(result["status"])
    if not replay_all(rows, n, result["resolution_evidence"]):
        raise AssertionError("Independent exact-resolution verifier rejected proof DAG")
    known = {(tuple(e["variables"]), e["rhs"]) for e in source["equations"]}
    found = {(tuple(e["variables"]), e["rhs"]) for e in result["additional_parity_keys"]}
    for support, rhs in known | found:
        if not all((sum(int(model[v-1]) for v in support) & 1) == rhs for model in models):
            raise AssertionError("Brute-force counterexample to claimed source-entailed XOR")
    rank = result["independent_rank_analysis"]
    for augmented, prefix in ((False, "coefficient"), (True, "augmented")):
        base = independent_rank(known, n, augmented)
        new = independent_rank(known | found, n, augmented)
        if base != rank["explicit_source_GF2_" + prefix + "_rank"]:
            raise AssertionError("Independent original GF2 rank disagreement")
        if new-base != rank["independent_new_" + prefix + "_rank"]:
            raise AssertionError("Independent incremental GF2 rank disagreement")
    raw = json.dumps({"n": n, "rows": rows}, sort_keys=True, separators=(",", ":")).encode()
    return {
        "case": name, "original_source_sha256": sha256(raw).hexdigest(),
        "source_rows": rows, "n": n, "total_assignments_exhausted": 1 << n,
        "satisfying_assignments": len(models),
        "explicit_xor": [{"variables": list(s), "rhs": r} for s, r in sorted(known)],
        "derived_xor": [{"variables": list(s), "rhs": r} for s, r in sorted(found)],
        "source_resolution_proof_steps": result["source_resolution_new_clause_count"],
        "coefficient_rank_increment": rank["independent_new_coefficient_rank"],
        "augmented_rank_increment": rank["independent_new_augmented_rank"],
        "independent_truth_table_entailment": "PASS",
        "independent_resolution_dag_replay": "PASS",
        "interpretation": instance["explanation"]
    }

def demonstrate():
    records = [examine(k, v) for k,v in cases().items()]
    by_name = {r["case"]: r for r in records}
    if not (by_name["guarded_source_derived_rank"]["coefficient_rank_increment"] >= 1
            and by_name["explicit_xor_no_increment"]["coefficient_rank_increment"] == 0
            and by_name["linear_combination_no_increment"]["coefficient_rank_increment"] == 0
            and not by_name["not_every_cnf_is_parity"]["derived_xor"]):
        raise AssertionError("Frozen illustrative positive/negative expectations not met")
    return {
        "schema": "JANUS-TIME-SAT-004D9B-MINIMAL-MATH-CLEAN-ROOM-CHECK-V1",
        "verification_scope": "EXHAUSTIVE_TRUTH_TABLE_AND_INDEPENDENT_PROOF_REPLAY_SAME_ADMIN_SYNTHETIC",
        "algorithm_class": "classical bounded resolution, full parity mask, exact GF2 rank",
        "logical_novelty_over_original_CNF": "NONE_ALL_DERIVED_CONSTRAINTS_ARE_ENTAILED",
        "possible_novelty_over_EXPLICIT_XOR_EXTRACTION_ONLY": True,
        "independent_third_party_validation": "NOT_PERFORMED",
        "end_to_end_solver_speedup": "NOT_MEASURED",
        "examples": records
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    report=demonstrate()
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n")
    print(json.dumps({"status":"SYNTHETIC_MATH_REPLAY_PASS",
                      "cases":[{"case":x["case"],"rank_delta":x["coefficient_rank_increment"],
                                "derived":len(x["derived_xor"])} for x in report["examples"]]},
                     sort_keys=True))
if __name__=="__main__":
    main()
