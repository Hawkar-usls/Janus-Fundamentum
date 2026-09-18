from __future__ import annotations

import hashlib
import json
import sys
import time
from collections import Counter

PAIR = (40, 240)
RAW_ASSIGNMENTS = ((0, 0), (0, 1), (1, 0), (1, 1))
RETAINED = ((0, 0), (0, 1), (1, 1))
LANGUAGE = "OR_OF_CANONICAL_RESIDUAL_CSP_BRANCHES"


def canonical_sha(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def relation_key(constraint):
    scope = tuple(int(v) for v in constraint["scope"])
    rows = tuple(sorted(set(tuple(int(b) for b in row) for row in constraint["allowed"])))
    return scope, rows


def formula_counter(constraints):
    return Counter(relation_key(c) for c in constraints)


def renamed_key(constraint, left, right):
    old_scope = [int(v) for v in constraint["scope"]]
    renamed = [right if v == left else left if v == right else v for v in old_scope]
    new_scope = sorted(renamed)
    rows = []
    for row in constraint["allowed"]:
        assignment = {}
        for v, bit in zip(old_scope, row, strict=True):
            nv = right if v == left else left if v == right else v
            assignment[nv] = int(bit)
        rows.append(tuple(assignment[v] for v in new_scope))
    return tuple(new_scope), tuple(sorted(set(rows)))


def exact_swap_invariant(constraints):
    original = formula_counter(constraints)
    swapped = Counter(renamed_key(c, PAIR[0], PAIR[1]) for c in constraints)
    return original == swapped


def canonical_residual(local_constraints, bits):
    fixed = {PAIR[0]: int(bits[0]), PAIR[1]: int(bits[1])}
    residual = {}
    for c in local_constraints:
        scope = [int(v) for v in c["scope"]]
        remaining = [v for v in scope if v not in fixed]
        surviving = []
        for row in c["allowed"]:
            amap = {v: int(bit) for v, bit in zip(scope, row, strict=True)}
            if all(amap[v] == val for v, val in fixed.items() if v in amap):
                surviving.append(tuple(amap[v] for v in remaining))
        rows = sorted(set(surviving))
        if not rows:
            return {"unsat": True, "constraints": []}
        if len(rows) == (1 << len(remaining)):
            continue
        key = (tuple(remaining), tuple(rows))
        residual[key] = {
            "scope": list(remaining),
            "allowed": [list(row) for row in rows],
        }
    constraints = [residual[k] for k in sorted(residual)]
    return {"unsat": False, "constraints": constraints}


def relation_symbol_count(constraints):
    total = 0
    for c in constraints:
        total += 1
        total += len(c["scope"])
        total += sum(len(row) for row in c["allowed"])
    return total


def branch_symbol_count(branch):
    return 1 + relation_symbol_count(branch["constraints"])


def branch_key(branch):
    return json.dumps(branch, sort_keys=True, separators=(",", ":"))


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: candidate.py SEALED_BUNDLE.json OUTPUT.json")

    t0 = time.perf_counter()
    bundle_path, output_path = sys.argv[1], sys.argv[2]
    with open(bundle_path, "r", encoding="utf-8") as fh:
        bundle = json.load(fh)

    payload_sha = bundle.get("payload_sha256")
    payload = dict(bundle)
    payload.pop("payload_sha256", None)
    if canonical_sha(payload) != payload_sha:
        raise RuntimeError("SEALED_BUNDLE_PAYLOAD_SHA_MISMATCH")
    if tuple(bundle["frozen_witness"]["cell"]) != PAIR:
        raise RuntimeError("FROZEN_PAIR_MISMATCH")

    reduced = bundle["reduced_csp"]
    constraints = list(reduced["constraints"])
    cell = set(PAIR)
    local = [c for c in constraints if cell.intersection(map(int, c["scope"]))]
    exterior = [c for c in constraints if not cell.intersection(map(int, c["scope"]))]
    boundary = sorted({
        int(v)
        for c in local
        for v in c["scope"]
        if int(v) not in cell
    })

    full_swap_ok = exact_swap_invariant(constraints)
    raw = {bits: canonical_residual(local, bits) for bits in RAW_ASSIGNMENTS}
    mixed_equal = branch_key(raw[(0, 1)]) == branch_key(raw[(1, 0)])

    retained_branches = []
    for bits in RETAINED:
        retained_branches.append({
            "internal_assignment": [int(bits[0]), int(bits[1])],
            "residual": raw[bits],
            "residual_sha256": canonical_sha(raw[bits]),
        })

    local_symbols = relation_symbol_count(local)
    raw_symbols = sum(branch_symbol_count(raw[b]) for b in RAW_ASSIGNMENTS)
    compressed_symbols = sum(branch_symbol_count(raw[b]) for b in RETAINED)
    analytic_bound = 3 * (local_symbols + 1)

    verdict = "PASS_CONSTRUCTIVE_BRIDGE"
    failure_reason = None
    if not full_swap_ok or not mixed_equal:
        verdict = "FAIL_NONLOCAL_INFORMATION_REQUIRED"
        failure_reason = "FROZEN_SWAP_WITNESS_NOT_REPRODUCED_FROM_SEALED_REDUCED_CSP"
    elif compressed_symbols > analytic_bound:
        verdict = "FAIL_CLOSURE_BLOWUP"
        failure_reason = "MEASURED_INTERFACE_EXCEEDS_PREREGISTERED_SCOPED_LINEAR_BOUND"

    result = {
        "artifact_id": "JANUS-TRUMP-WALL-MANTEQUILLA-LOCAL-EXACT-INTERFACE-UF250-020-CANDIDATE-v1",
        "language": LANGUAGE,
        "verdict": verdict,
        "failure_reason": failure_reason,
        "sealed_bundle_payload_sha256": payload_sha,
        "source": "UF250_020",
        "frozen_cell": list(PAIR),
        "full_reduced_swap_invariant": full_swap_ok,
        "local_constraint_count": len(local),
        "exterior_constraint_count": len(exterior),
        "boundary_variables": boundary,
        "boundary_variable_count": len(boundary),
        "raw_branch_count": 4,
        "retained_branch_count": 3,
        "mixed_branch_residuals_equal": mixed_equal,
        "raw_branch_residual_sha256": {
            f"{a}{b}": canonical_sha(raw[(a, b)]) for a, b in RAW_ASSIGNMENTS
        },
        "interface": {
            "semantics": "EXISTS_x40_x240_LOCAL_CSP",
            "branches": retained_branches,
            "exactness_method": "STRUCTURAL_SHANNON_TWO_VAR_PLUS_EXACT_SWAP_RESIDUAL_IDENTITY",
        },
        "accounting": {
            "local_input_symbol_count": local_symbols,
            "raw_four_branch_residual_symbol_count": raw_symbols,
            "compressed_interface_symbol_count": compressed_symbols,
            "preregistered_scoped_linear_bound": analytic_bound,
            "interface_within_bound": compressed_symbols <= analytic_bound,
            "internal_assignments_constructed": 4,
            "boundary_cube_assignments_enumerated": 0,
            "sat_solver_invocations": 0,
            "full_transposition_searches": 0,
            "detector_imports": [],
            "wl_imports": [],
            "e3_imports": [],
        },
        "claim_ceiling": "ONE_FROZEN_TWO_VARIABLE_EXACT_SYMMETRY_CELL__LOCAL_INTERFACE_ONLY",
        "candidate_runtime_seconds": time.perf_counter() - t0,
    }
    result["candidate_semantic_digest_sha256"] = canonical_sha({
        "language": result["language"],
        "sealed_bundle_payload_sha256": payload_sha,
        "frozen_cell": result["frozen_cell"],
        "full_reduced_swap_invariant": full_swap_ok,
        "boundary_variables": boundary,
        "mixed_branch_residuals_equal": mixed_equal,
        "interface": result["interface"],
        "accounting_without_runtime": {
            k: v for k, v in result["accounting"].items()
        },
        "verdict": verdict,
    })

    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps({
        "verdict": verdict,
        "boundary_variable_count": len(boundary),
        "local_constraint_count": len(local),
        "compressed_interface_symbol_count": compressed_symbols,
        "mixed_branch_residuals_equal": mixed_equal,
        "full_reduced_swap_invariant": full_swap_ok,
        "candidate_semantic_digest_sha256": result["candidate_semantic_digest_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
