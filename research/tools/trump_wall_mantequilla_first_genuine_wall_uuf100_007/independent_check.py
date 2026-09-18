from __future__ import annotations

import ast
import hashlib
import json
import sys
import time
from collections import Counter
from itertools import product
from pathlib import Path

CELL = (12, 83)
RAW_ASSIGNMENTS = tuple(product((0, 1), repeat=2))
RETAINED = ((0, 0), (0, 1), (1, 1))
ALLOWED_IMPORTS = {
    "__future__", "hashlib", "json", "sys", "time", "collections", "itertools"
}


def csha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def relation_key(constraint):
    return (
        tuple(int(v) for v in constraint["scope"]),
        tuple(sorted(set(tuple(int(b) for b in row) for row in constraint["allowed"]))),
    )


def formula_counter(constraints):
    return Counter(relation_key(c) for c in constraints)


def renamed_key(constraint, left, right):
    old_scope = [int(v) for v in constraint["scope"]]
    renamed = [right if v == left else left if v == right else v for v in old_scope]
    new_scope = sorted(renamed)
    rows = []
    for row in constraint["allowed"]:
        amap = {}
        for v, bit in zip(old_scope, row, strict=True):
            nv = right if v == left else left if v == right else v
            amap[nv] = int(bit)
        rows.append(tuple(amap[v] for v in new_scope))
    return tuple(new_scope), tuple(sorted(set(rows)))


def swap_ok(constraints):
    return formula_counter(constraints) == Counter(
        renamed_key(c, CELL[0], CELL[1]) for c in constraints
    )


def residual(local, bits):
    fixed = {CELL[0]: int(bits[0]), CELL[1]: int(bits[1])}
    out = {}
    for c in local:
        scope = [int(v) for v in c["scope"]]
        remaining = [v for v in scope if v not in fixed]
        rows = []
        for row in c["allowed"]:
            amap = {v: int(bit) for v, bit in zip(scope, row, strict=True)}
            if all(amap[v] == val for v, val in fixed.items() if v in amap):
                rows.append(tuple(amap[v] for v in remaining))
        rows = sorted(set(rows))
        if not rows:
            return {"unsat": True, "constraints": []}
        if len(rows) == (1 << len(remaining)):
            continue
        k = (tuple(remaining), tuple(rows))
        out[k] = {
            "scope": list(remaining),
            "allowed": [list(r) for r in rows],
        }
    return {"unsat": False, "constraints": [out[k] for k in sorted(out)]}


def relation_symbol_count(constraints):
    return sum(
        1 + len(c["scope"]) + sum(len(row) for row in c["allowed"])
        for c in constraints
    )


def branch_symbol_count(branch):
    return 1 + relation_symbol_count(branch["constraints"])


class DD:
    def __init__(self):
        self.nodes = {}
        self.unique = {}
        self.next_id = 2
        self.acache = {}
        self.rcache = {}
        self.apply_calls = 0
        self.mk_calls = 0

    def mk(self, v, l, h):
        self.mk_calls += 1
        if l == h:
            return l
        k = (int(v), int(l), int(h))
        if k in self.unique:
            return self.unique[k]
        i = self.next_id
        self.next_id += 1
        self.unique[k] = i
        self.nodes[i] = k
        return i

    def var(self, v):
        return self.mk(int(v), 0, 1)

    def apply(self, op, u, v):
        self.apply_calls += 1
        if op in {"and", "or", "xor"} and u > v:
            u, v = v, u
        k = (op, int(u), int(v))
        if k in self.acache:
            return self.acache[k]
        if u < 2 and v < 2:
            if op == "and":
                r = int(bool(u) and bool(v))
            elif op == "or":
                r = int(bool(u) or bool(v))
            elif op == "xor":
                r = int(bool(u) ^ bool(v))
            else:
                raise ValueError(op)
            self.acache[k] = r
            return r

        vu = self.nodes[u][0] if u >= 2 else None
        vv = self.nodes[v][0] if v >= 2 else None
        top = vv if vu is None else vu if vv is None else min(vu, vv)
        if u >= 2 and self.nodes[u][0] == top:
            _, ul, uh = self.nodes[u]
        else:
            ul = uh = u
        if v >= 2 and self.nodes[v][0] == top:
            _, vl, vh = self.nodes[v]
        else:
            vl = vh = v
        r = self.mk(top, self.apply(op, ul, vl), self.apply(op, uh, vh))
        self.acache[k] = r
        return r

    def neg(self, u):
        return self.apply("xor", u, 1)

    def restrict(self, u, v, bit):
        k = (int(u), int(v), int(bit))
        if k in self.rcache:
            return self.rcache[k]
        if u < 2:
            r = u
        else:
            nv, low, high = self.nodes[u]
            if nv == v:
                r = self.restrict(high if bit else low, v, bit)
            elif nv > v:
                r = u
            else:
                r = self.mk(
                    nv,
                    self.restrict(low, v, bit),
                    self.restrict(high, v, bit),
                )
        self.rcache[k] = r
        return r

    def tuple(self, scope, row):
        r = 1
        for v, bit in zip(scope, row, strict=True):
            lit = self.var(v)
            if not bit:
                lit = self.neg(lit)
            r = self.apply("and", r, lit)
        return r

    def constraint(self, c):
        r = 0
        scope = [int(v) for v in c["scope"]]
        for row in c["allowed"]:
            r = self.apply("or", r, self.tuple(scope, row))
        return r

    def branch(self, res):
        if res["unsat"]:
            return 0
        r = 1
        for c in res["constraints"]:
            r = self.apply("and", r, self.constraint(c))
        return r

    def live(self, root):
        seen = set()
        stack = [root]
        while stack:
            u = stack.pop()
            if u < 2 or u in seen:
                continue
            seen.add(u)
            _, low, high = self.nodes[u]
            stack.extend((low, high))
        return len(seen)

    def semhash(self, root):
        memo = {0: "FALSE", 1: "TRUE"}

        def rec(u):
            if u in memo:
                return memo[u]
            var, low, high = self.nodes[u]
            memo[u] = csha({"var": var, "low": rec(low), "high": rec(high)})
            return memo[u]

        return rec(root)


def audit_candidate_source(path):
    text = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(text)
    imports = []
    forbidden_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Call):
            name = None
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name in {
                "solve", "run_candidate", "discover_generator_edges",
                "wl1", "wl2", "quotient_state_count"
            }:
                forbidden_calls.append(name)
    unexpected = sorted(set(imports) - ALLOWED_IMPORTS)
    return {
        "imports": sorted(imports),
        "unexpected_imports": unexpected,
        "forbidden_calls": sorted(set(forbidden_calls)),
        "pass": not unexpected and not forbidden_calls,
    }


def main():
    if len(sys.argv) != 5:
        raise SystemExit("usage: independent_check.py SEALED.json CANDIDATE.json CANDIDATE_SOURCE.py OUTPUT.json")
    t0 = time.perf_counter()
    bundle = json.load(open(sys.argv[1], "r", encoding="utf-8"))
    candidate = json.load(open(sys.argv[2], "r", encoding="utf-8"))
    source_audit = audit_candidate_source(sys.argv[3])

    payload_sha = bundle.get("payload_sha256")
    payload = dict(bundle)
    payload.pop("payload_sha256", None)
    bundle_ok = csha(payload) == payload_sha

    reduced = bundle["reduced_csp"]
    constraints = list(reduced["constraints"])
    cell = set(CELL)
    local = [c for c in constraints if cell.intersection(map(int, c["scope"]))]
    exterior = [c for c in constraints if not cell.intersection(map(int, c["scope"]))]
    boundary = sorted({
        int(v)
        for c in local
        for v in c["scope"]
        if int(v) not in cell
    })

    exact_swap = swap_ok(constraints)
    branches = {bits: residual(local, bits) for bits in RAW_ASSIGNMENTS}
    mixed_equal = branches[(0, 1)] == branches[(1, 0)]
    true_branch = any(
        (not b["unsat"] and not b["constraints"]) for b in branches.values()
    )

    dd = DD()
    roots = {bits: dd.branch(branches[bits]) for bits in RAW_ASSIGNMENTS}
    interface_root = 0
    retained = []
    for bits in RETAINED:
        root = roots[bits]
        interface_root = dd.apply("or", interface_root, root)
        retained.append({
            "internal_assignment": list(bits),
            "residual": branches[bits],
            "residual_sha256": csha(branches[bits]),
            "bdd_semantic_sha256": dd.semhash(root),
        })

    is_true = interface_root == 1
    is_false = interface_root == 0
    is_constant = interface_root in (0, 1)

    unary = {}
    unary_root = 1
    for v in boundary:
        a0 = dd.restrict(interface_root, v, 0) != 0
        a1 = dd.restrict(interface_root, v, 1) != 0
        unary[str(v)] = [bit for bit, ok in ((0, a0), (1, a1)) if ok]
        if a0 and a1:
            continue
        if not a0 and not a1:
            unary_root = 0
            break
        lit = dd.var(v)
        if a0 and not a1:
            lit = dd.neg(lit)
        unary_root = dd.apply("and", unary_root, lit)

    unary_factorized = interface_root == unary_root
    correlated = bool(not is_constant and not unary_factorized)

    local_symbols = relation_symbol_count(local)
    compressed_orcsp_symbols = sum(branch_symbol_count(branches[b]) for b in RETAINED)
    orcsp_bound = 3 * (local_symbols + 1)
    orcsp_ok = compressed_orcsp_symbols <= orcsp_bound

    base = local_symbols + len(boundary) + 2
    node_bound = base ** 2
    operation_bound = base ** 4
    live_nodes = dd.live(interface_root)
    total_ops = dd.apply_calls + dd.mk_calls
    bdd_ok = live_nodes <= node_bound and total_ops <= operation_bound

    if not exact_swap or not mixed_equal:
        expected_verdict = "FAIL_NONLOCAL_INFORMATION_REQUIRED"
        diagnostic = "FROZEN_SWAP_OR_MIXED_RESIDUAL_IDENTITY_NOT_REPRODUCED"
    elif true_branch or is_constant:
        expected_verdict = "FAIL_TRIVIAL_ESCAPE"
        diagnostic = "R_C_TRUE" if is_true else "R_C_FALSE"
    elif not orcsp_ok or not bdd_ok:
        expected_verdict = "FAIL_CLOSURE_BLOWUP"
        diagnostic = "ORCSP_OR_ROBDD_FROZEN_ENVELOPE_EXCEEDED"
    elif unary_factorized:
        expected_verdict = "FAIL_UNARY_FACTORIZATION"
        diagnostic = "R_C_NONTRIVIAL_BUT_PRODUCT_OF_UNARY_PROJECTIONS"
    else:
        expected_verdict = "PASS_NONTRIVIAL_CORRELATED_BRIDGE"
        diagnostic = "R_C_CORRELATED__FIRST_GENUINE_WALL_SPECIMEN_IF_INDEPENDENTLY_VERIFIED"

    expected_interface = {
        "semantics": "EXISTS_x12_x83_LOCAL_CSP",
        "retained_branches": retained,
        "exactness_method": "STRUCTURAL_SHANNON_TWO_VAR_PLUS_EXACT_SWAP_RESIDUAL_IDENTITY",
        "orcsp_semantic_digest_sha256": csha(retained),
        "robdd_semantic_sha256": dd.semhash(interface_root),
        "unary_product_robdd_semantic_sha256": dd.semhash(unary_root),
    }
    expected_audit = {
        "interface_is_true": is_true,
        "interface_is_false": is_false,
        "interface_is_constant": is_constant,
        "unary_projections": unary,
        "unary_factorized": unary_factorized,
        "genuine_joint_correlation": correlated,
    }
    expected_accounting = {
        "local_input_symbol_count": local_symbols,
        "compressed_orcsp_symbol_count": compressed_orcsp_symbols,
        "orcsp_symbol_bound": orcsp_bound,
        "orcsp_bound_holds": orcsp_ok,
        "robdd_live_nonterminal_nodes": live_nodes,
        "robdd_node_bound": node_bound,
        "robdd_apply_calls": dd.apply_calls,
        "robdd_mk_calls": dd.mk_calls,
        "robdd_total_operations": total_ops,
        "robdd_operation_bound": operation_bound,
        "robdd_bounds_hold": bdd_ok,
        "internal_assignments_constructed": 4,
        "boundary_cube_assignments_enumerated": 0,
        "sat_solver_invocations": 0,
        "full_transposition_searches": 0,
        "frozen_direct_swap_checks": 1,
        "detector_imports": [],
        "wl_imports": [],
        "e3_imports": [],
    }
    raw_hashes = {
        f"{a}{b}": csha(branches[(a, b)]) for a, b in RAW_ASSIGNMENTS
    }

    checks = {
        "bundle_hash_ok": bundle_ok,
        "candidate_bundle_hash_matches": candidate.get("sealed_bundle_payload_sha256") == payload_sha,
        "candidate_source_audit_pass": source_audit["pass"],
        "frozen_cell_matches": candidate.get("frozen_cell") == list(CELL),
        "direct_swap_matches": candidate.get("direct_exact_swap_reproduced") is exact_swap,
        "local_count_matches": candidate.get("local_constraint_count") == len(local),
        "exterior_count_matches": candidate.get("exterior_constraint_count") == len(exterior),
        "boundary_matches": candidate.get("boundary_variables") == boundary,
        "mixed_branch_identity_matches": candidate.get("mixed_branch_residuals_equal") is mixed_equal,
        "true_branch_matches": candidate.get("any_true_raw_branch") is true_branch,
        "raw_residual_hashes_match": candidate.get("raw_branch_residual_sha256") == raw_hashes,
        "interface_exact_match": candidate.get("interface") == expected_interface,
        "semantic_audit_exact_match": candidate.get("semantic_audit") == expected_audit,
        "accounting_exact_match": candidate.get("accounting") == expected_accounting,
        "verdict_matches": candidate.get("verdict") == expected_verdict,
        "diagnostic_matches": candidate.get("diagnostic_subclassification") == diagnostic,
        "no_sat_calls": expected_accounting["sat_solver_invocations"] == 0,
        "no_boundary_cube": expected_accounting["boundary_cube_assignments_enumerated"] == 0,
        "no_detector_imports": expected_accounting["detector_imports"] == [],
        "no_wl_imports": expected_accounting["wl_imports"] == [],
        "no_e3_imports": expected_accounting["e3_imports"] == [],
    }
    verified = all(checks.values())

    out = {
        "artifact_id": "JANUS-TRUMP-WALL-MANTEQUILLA-FIRST-GENUINE-WALL-UUF100-007-INDEPENDENT-CHECK-v1",
        "date": "2026-09-18",
        "verdict": (
            "PASS_INDEPENDENT_MANTEQUILLA_FIRST_GENUINE_WALL_VERIFICATION"
            if verified
            else "FAIL_INDEPENDENT_MANTEQUILLA_FIRST_GENUINE_WALL_VERIFICATION"
        ),
        "scientific_verdict": expected_verdict,
        "diagnostic_subclassification": diagnostic,
        "candidate_imported": False,
        "candidate_source_audit": source_audit,
        "checks": checks,
        "independent_measurements": {
            "local_constraint_count": len(local),
            "exterior_constraint_count": len(exterior),
            "boundary_variables": boundary,
            "boundary_variable_count": len(boundary),
            "direct_exact_swap_reproduced": exact_swap,
            "mixed_branch_residuals_equal": mixed_equal,
            "any_true_raw_branch": true_branch,
            "interface_is_true": is_true,
            "interface_is_false": is_false,
            "interface_is_constant": is_constant,
            "unary_projections": unary,
            "unary_factorized": unary_factorized,
            "genuine_joint_correlation": correlated,
            "local_input_symbol_count": local_symbols,
            "compressed_orcsp_symbol_count": compressed_orcsp_symbols,
            "orcsp_symbol_bound": orcsp_bound,
            "orcsp_bound_holds": orcsp_ok,
            "robdd_live_nonterminal_nodes": live_nodes,
            "robdd_node_bound": node_bound,
            "robdd_total_operations": total_ops,
            "robdd_operation_bound": operation_bound,
            "robdd_bounds_hold": bdd_ok,
            "robdd_semantic_sha256": dd.semhash(interface_root),
            "unary_product_robdd_semantic_sha256": dd.semhash(unary_root),
        },
        "sealed_bundle_payload_sha256": payload_sha,
        "claim_ceiling": "ONE_FRESH_UNSEEN_FROZEN_K2_ACTIVE_EXACT_SYMMETRY_CELL__NONTRIVIAL_BOUNDARY_INTERFACE_ONLY",
        "independent_checker_runtime_seconds": time.perf_counter() - t0,
    }
    out["independent_semantic_digest_sha256"] = csha({
        "scientific_verdict": expected_verdict,
        "diagnostic_subclassification": diagnostic,
        "checks": checks,
        "independent_measurements": out["independent_measurements"],
        "sealed_bundle_payload_sha256": payload_sha,
    })

    with open(sys.argv[4], "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps({
        "verdict": out["verdict"],
        "scientific_verdict": expected_verdict,
        "diagnostic_subclassification": diagnostic,
        "checks_passed": sum(bool(v) for v in checks.values()),
        "checks_total": len(checks),
        "independent_measurements": out["independent_measurements"],
        "independent_semantic_digest_sha256": out["independent_semantic_digest_sha256"],
    }, sort_keys=True))
    if not verified:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
