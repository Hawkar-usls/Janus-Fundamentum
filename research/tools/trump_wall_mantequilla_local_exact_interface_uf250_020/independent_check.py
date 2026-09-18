from __future__ import annotations

import ast
import hashlib
import json
import sys
import time
from collections import Counter

PAIR = (40, 240)
RAW = ((0, 0), (0, 1), (1, 0), (1, 1))
KEEP = ((0, 0), (0, 1), (1, 1))
ALLOWED_IMPORT_ROOTS = {"__future__", "ast", "hashlib", "json", "sys", "time", "collections"}


def sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def semantic_relation(c):
    scope = tuple(int(x) for x in c["scope"])
    rows = tuple(sorted(set(tuple(int(b) for b in row) for row in c["allowed"])))
    return scope, rows


def swapped_relation(c):
    old_scope = [int(x) for x in c["scope"]]
    renamed = [PAIR[1] if x == PAIR[0] else PAIR[0] if x == PAIR[1] else x for x in old_scope]
    new_scope = sorted(renamed)
    out = []
    for row in c["allowed"]:
        d = {}
        for x, bit in zip(old_scope, row, strict=True):
            y = PAIR[1] if x == PAIR[0] else PAIR[0] if x == PAIR[1] else x
            d[y] = int(bit)
        out.append(tuple(d[x] for x in new_scope))
    return tuple(new_scope), tuple(sorted(set(out)))


def verify_swap(constraints):
    before = Counter(semantic_relation(c) for c in constraints)
    after = Counter(swapped_relation(c) for c in constraints)
    return before == after


def eliminate_one_assignment(local, pair_bits):
    assignment = {PAIR[0]: int(pair_bits[0]), PAIR[1]: int(pair_bits[1])}
    unique = {}
    for c in local:
        scope = [int(x) for x in c["scope"]]
        rem = [x for x in scope if x not in assignment]
        projected_rows = []
        for row in c["allowed"]:
            row_map = {x: int(bit) for x, bit in zip(scope, row, strict=True)}
            matches = True
            for x, val in assignment.items():
                if x in row_map and row_map[x] != val:
                    matches = False
                    break
            if matches:
                projected_rows.append(tuple(row_map[x] for x in rem))
        projected_rows = sorted(set(projected_rows))
        if not projected_rows:
            return {"unsat": True, "constraints": []}
        if len(projected_rows) == 2 ** len(rem):
            continue
        key = (tuple(rem), tuple(projected_rows))
        unique[key] = {
            "scope": list(rem),
            "allowed": [list(row) for row in projected_rows],
        }
    return {"unsat": False, "constraints": [unique[k] for k in sorted(unique)]}


def count_symbols(constraints):
    ans = 0
    for c in constraints:
        ans += 1 + len(c["scope"])
        ans += sum(len(row) for row in c["allowed"])
    return ans


def count_branch(branch):
    return 1 + count_symbols(branch["constraints"])


def audit_candidate_source(path):
    text = open(path, "r", encoding="utf-8").read()
    tree = ast.parse(text)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    roots = {name.split(".", 1)[0] for name in imports}
    forbidden_imports = sorted(roots - ALLOWED_IMPORT_ROOTS)
    forbidden_tokens = [
        "research.tools",
        "pysat",
        "z3",
        "subprocess",
        "importlib",
        "requests",
        "urllib",
        "socket",
    ]
    token_hits = [token for token in forbidden_tokens if token in text]
    return {
        "imports": sorted(imports),
        "forbidden_imports": forbidden_imports,
        "forbidden_token_hits": token_hits,
        "pass": not forbidden_imports and not token_hits,
    }


def main():
    if len(sys.argv) != 5:
        raise SystemExit("usage: independent_check.py BUNDLE.json CANDIDATE.json CANDIDATE.py OUTPUT.json")
    t0 = time.perf_counter()
    bundle_path, candidate_path, candidate_source_path, output_path = sys.argv[1:]

    bundle = json.load(open(bundle_path, "r", encoding="utf-8"))
    candidate = json.load(open(candidate_path, "r", encoding="utf-8"))

    payload_hash = bundle.get("payload_sha256")
    payload = dict(bundle)
    payload.pop("payload_sha256", None)
    bundle_hash_ok = sha(payload) == payload_hash

    reduced = bundle["reduced_csp"]
    constraints = list(reduced["constraints"])
    cell = set(PAIR)
    local = [c for c in constraints if cell.intersection(int(x) for x in c["scope"])]
    exterior = [c for c in constraints if not cell.intersection(int(x) for x in c["scope"])]
    boundary = sorted({
        int(x)
        for c in local
        for x in c["scope"]
        if int(x) not in cell
    })

    swap_ok = verify_swap(constraints)
    branches = {bits: eliminate_one_assignment(local, bits) for bits in RAW}
    mixed_equal = sha(branches[(0, 1)]) == sha(branches[(1, 0)])

    expected_interface = {
        "semantics": "EXISTS_x40_x240_LOCAL_CSP",
        "branches": [
            {
                "internal_assignment": [a, b],
                "residual": branches[(a, b)],
                "residual_sha256": sha(branches[(a, b)]),
            }
            for a, b in KEEP
        ],
        "exactness_method": "STRUCTURAL_SHANNON_TWO_VAR_PLUS_EXACT_SWAP_RESIDUAL_IDENTITY",
    }

    local_symbols = count_symbols(local)
    raw_symbols = sum(count_branch(branches[b]) for b in RAW)
    compressed_symbols = sum(count_branch(branches[b]) for b in KEEP)
    bound = 3 * (local_symbols + 1)

    source_audit = audit_candidate_source(candidate_source_path)
    accounting = candidate.get("accounting", {})
    checks = {
        "bundle_hash_ok": bundle_hash_ok,
        "candidate_bundle_hash_matches": candidate.get("sealed_bundle_payload_sha256") == payload_hash,
        "frozen_cell_matches": candidate.get("frozen_cell") == list(PAIR),
        "full_swap_invariant": swap_ok,
        "candidate_swap_matches": candidate.get("full_reduced_swap_invariant") is swap_ok,
        "mixed_residual_identity": mixed_equal,
        "candidate_mixed_identity_matches": candidate.get("mixed_branch_residuals_equal") is mixed_equal,
        "boundary_matches": candidate.get("boundary_variables") == boundary,
        "local_count_matches": candidate.get("local_constraint_count") == len(local),
        "exterior_count_matches": candidate.get("exterior_constraint_count") == len(exterior),
        "interface_exact_match": candidate.get("interface") == expected_interface,
        "local_symbols_match": accounting.get("local_input_symbol_count") == local_symbols,
        "raw_symbols_match": accounting.get("raw_four_branch_residual_symbol_count") == raw_symbols,
        "compressed_symbols_match": accounting.get("compressed_interface_symbol_count") == compressed_symbols,
        "linear_bound_matches": accounting.get("preregistered_scoped_linear_bound") == bound,
        "linear_bound_holds": compressed_symbols <= bound,
        "four_internal_assignments_only": accounting.get("internal_assignments_constructed") == 4,
        "boundary_cube_zero": accounting.get("boundary_cube_assignments_enumerated") == 0,
        "sat_solver_zero": accounting.get("sat_solver_invocations") == 0,
        "full_transposition_search_zero": accounting.get("full_transposition_searches") == 0,
        "detector_imports_zero": accounting.get("detector_imports") == [],
        "wl_imports_zero": accounting.get("wl_imports") == [],
        "e3_imports_zero": accounting.get("e3_imports") == [],
        "candidate_source_audit_pass": source_audit["pass"],
    }
    all_pass = all(checks.values()) and candidate.get("verdict") == "PASS_CONSTRUCTIVE_BRIDGE"

    result = {
        "artifact_id": "JANUS-TRUMP-WALL-MANTEQUILLA-LOCAL-EXACT-INTERFACE-UF250-020-INDEPENDENT-CHECK-v1",
        "verdict": (
            "PASS_INDEPENDENT_MANTEQUILLA_LOCAL_EXACT_INTERFACE_VERIFICATION"
            if all_pass
            else "FAIL_INDEPENDENT_MANTEQUILLA_LOCAL_EXACT_INTERFACE_VERIFICATION"
        ),
        "candidate_imported": False,
        "checks": checks,
        "candidate_source_audit": source_audit,
        "independent_measurements": {
            "local_constraint_count": len(local),
            "exterior_constraint_count": len(exterior),
            "boundary_variable_count": len(boundary),
            "boundary_variables": boundary,
            "local_input_symbol_count": local_symbols,
            "raw_four_branch_residual_symbol_count": raw_symbols,
            "compressed_interface_symbol_count": compressed_symbols,
            "scoped_linear_bound": bound,
            "full_swap_invariant": swap_ok,
            "mixed_branch_residuals_equal": mixed_equal,
            "raw_branch_residual_sha256": {
                f"{a}{b}": sha(branches[(a, b)]) for a, b in RAW
            },
        },
        "sealed_bundle_payload_sha256": payload_hash,
        "claim_ceiling": "ONE_FROZEN_TWO_VARIABLE_EXACT_SYMMETRY_CELL__LOCAL_INTERFACE_ONLY",
        "independent_checker_runtime_seconds": time.perf_counter() - t0,
    }
    result["independent_semantic_digest_sha256"] = sha({
        "checks": checks,
        "independent_measurements": result["independent_measurements"],
        "sealed_bundle_payload_sha256": payload_hash,
        "verdict": result["verdict"],
    })

    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps({
        "verdict": result["verdict"],
        "checks_passed": sum(1 for x in checks.values() if x),
        "checks_total": len(checks),
        "compressed_interface_symbol_count": compressed_symbols,
        "scoped_linear_bound": bound,
        "independent_semantic_digest_sha256": result["independent_semantic_digest_sha256"],
    }, sort_keys=True))

    if not all_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
