from __future__ import annotations

import hashlib
import json
import sys
import time
from collections import Counter
from itertools import product

CELL = (12, 83)
RAW_ASSIGNMENTS = tuple(product((0, 1), repeat=2))
RETAINED = ((0, 0), (0, 1), (1, 1))
LANGUAGE = "OR_OF_CANONICAL_RESIDUAL_CSP_BRANCHES_PLUS_CANONICAL_ROBDD"


def csha(obj) -> str:
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
        amap = {}
        for v, bit in zip(old_scope, row, strict=True):
            nv = right if v == left else left if v == right else v
            amap[nv] = int(bit)
        rows.append(tuple(amap[v] for v in new_scope))
    return tuple(new_scope), tuple(sorted(set(rows)))


def exact_swap_invariant(constraints, left, right):
    return formula_counter(constraints) == Counter(
        renamed_key(c, left, right) for c in constraints
    )


def canonical_residual(local_constraints, bits):
    fixed = {CELL[0]: int(bits[0]), CELL[1]: int(bits[1])}
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
    return {
        "unsat": False,
        "constraints": [residual[k] for k in sorted(residual)],
    }


def relation_symbol_count(constraints):
    return sum(
        1 + len(c["scope"]) + sum(len(row) for row in c["allowed"])
        for c in constraints
    )


def branch_symbol_count(branch):
    return 1 + relation_symbol_count(branch["constraints"])


class ROBDD:
    def __init__(self):
        self.nodes = {}
        self.unique = {}
        self.next_id = 2
        self.apply_cache = {}
        self.restrict_cache = {}
        self.apply_calls = 0
        self.mk_calls = 0

    def mk(self, var, low, high):
        self.mk_calls += 1
        if low == high:
            return low
        key = (int(var), int(low), int(high))
        if key in self.unique:
            return self.unique[key]
        nid = self.next_id
        self.next_id += 1
        self.unique[key] = nid
        self.nodes[nid] = key
        return nid

    def var(self, v):
        return self.mk(int(v), 0, 1)

    def apply(self, op, u, v):
        self.apply_calls += 1
        if op in {"and", "or", "xor"} and u > v:
            u, v = v, u
        key = (op, int(u), int(v))
        if key in self.apply_cache:
            return self.apply_cache[key]
        if u < 2 and v < 2:
            if op == "and":
                out = int(bool(u) and bool(v))
            elif op == "or":
                out = int(bool(u) or bool(v))
            elif op == "xor":
                out = int(bool(u) ^ bool(v))
            else:
                raise ValueError(op)
            self.apply_cache[key] = out
            return out

        vu = self.nodes[u][0] if u >= 2 else None
        vv = self.nodes[v][0] if v >= 2 else None
        if vu is None:
            top = vv
        elif vv is None:
            top = vu
        else:
            top = min(vu, vv)

        if u >= 2 and self.nodes[u][0] == top:
            _, ul, uh = self.nodes[u]
        else:
            ul = uh = u
        if v >= 2 and self.nodes[v][0] == top:
            _, vl, vh = self.nodes[v]
        else:
            vl = vh = v

        low = self.apply(op, ul, vl)
        high = self.apply(op, uh, vh)
        out = self.mk(top, low, high)
        self.apply_cache[key] = out
        return out

    def neg(self, u):
        return self.apply("xor", u, 1)

    def restrict(self, u, var, bit):
        key = (int(u), int(var), int(bit))
        if key in self.restrict_cache:
            return self.restrict_cache[key]
        if u < 2:
            out = u
        else:
            node_var, low, high = self.nodes[u]
            if node_var == var:
                out = self.restrict(high if bit else low, var, bit)
            elif node_var > var:
                out = u
            else:
                out = self.mk(
                    node_var,
                    self.restrict(low, var, bit),
                    self.restrict(high, var, bit),
                )
        self.restrict_cache[key] = out
        return out

    def tuple_bdd(self, scope, row):
        root = 1
        for v, bit in zip(scope, row, strict=True):
            lit = self.var(v)
            if not bit:
                lit = self.neg(lit)
            root = self.apply("and", root, lit)
        return root

    def constraint_bdd(self, constraint):
        root = 0
        scope = [int(v) for v in constraint["scope"]]
        for row in constraint["allowed"]:
            root = self.apply("or", root, self.tuple_bdd(scope, row))
        return root

    def residual_bdd(self, residual):
        if residual["unsat"]:
            return 0
        root = 1
        for c in residual["constraints"]:
            root = self.apply("and", root, self.constraint_bdd(c))
        return root

    def live_nodes(self, root):
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

    def semantic_hash(self, root):
        memo = {0: "FALSE", 1: "TRUE"}

        def rec(u):
            if u in memo:
                return memo[u]
            var, low, high = self.nodes[u]
            memo[u] = csha({"var": var, "low": rec(low), "high": rec(high)})
            return memo[u]

        return rec(root)


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: candidate.py SEALED_BUNDLE.json OUTPUT.json")
    t0 = time.perf_counter()
    bundle = json.load(open(sys.argv[1], "r", encoding="utf-8"))
    payload_sha = bundle.get("payload_sha256")
    payload = dict(bundle)
    payload.pop("payload_sha256", None)
    if csha(payload) != payload_sha:
        raise RuntimeError("SEALED_BUNDLE_PAYLOAD_SHA_MISMATCH")
    if tuple(bundle["frozen_witness"]["cell"]) != CELL:
        raise RuntimeError("FROZEN_CELL_MISMATCH")

    reduced = bundle["reduced_csp"]
    constraints = list(reduced["constraints"])
    cell_set = set(CELL)
    local = [c for c in constraints if cell_set.intersection(map(int, c["scope"]))]
    exterior = [c for c in constraints if not cell_set.intersection(map(int, c["scope"]))]
    boundary = sorted({
        int(v)
        for c in local
        for v in c["scope"]
        if int(v) not in cell_set
    })

    swap_ok = exact_swap_invariant(constraints, CELL[0], CELL[1])
    raw = {bits: canonical_residual(local, bits) for bits in RAW_ASSIGNMENTS}
    mixed_equal = raw[(0, 1)] == raw[(1, 0)]
    any_true_branch = any(
        (not branch["unsat"] and not branch["constraints"])
        for branch in raw.values()
    )

    bdd = ROBDD()
    raw_roots = {bits: bdd.residual_bdd(raw[bits]) for bits in RAW_ASSIGNMENTS}
    interface_root = 0
    retained = []
    for bits in RETAINED:
        root = raw_roots[bits]
        interface_root = bdd.apply("or", interface_root, root)
        retained.append({
            "internal_assignment": list(bits),
            "residual": raw[bits],
            "residual_sha256": csha(raw[bits]),
            "bdd_semantic_sha256": bdd.semantic_hash(root),
        })

    interface_is_true = interface_root == 1
    interface_is_false = interface_root == 0
    interface_is_constant = interface_root in (0, 1)

    unary_projections = {}
    unary_product_root = 1
    for v in boundary:
        allowed0 = bdd.restrict(interface_root, v, 0) != 0
        allowed1 = bdd.restrict(interface_root, v, 1) != 0
        unary_projections[str(v)] = [
            bit for bit, allowed in ((0, allowed0), (1, allowed1)) if allowed
        ]
        if allowed0 and allowed1:
            continue
        if not allowed0 and not allowed1:
            unary_product_root = 0
            break
        lit = bdd.var(v)
        if allowed0 and not allowed1:
            lit = bdd.neg(lit)
        unary_product_root = bdd.apply("and", unary_product_root, lit)

    unary_factorized = interface_root == unary_product_root
    genuine_correlation = bool(not interface_is_constant and not unary_factorized)

    local_symbols = relation_symbol_count(local)
    compressed_orcsp_symbols = sum(branch_symbol_count(raw[b]) for b in RETAINED)
    orcsp_bound = 3 * (local_symbols + 1)
    orcsp_bound_holds = compressed_orcsp_symbols <= orcsp_bound

    base = local_symbols + len(boundary) + 2
    bdd_node_bound = base ** 2
    bdd_operation_bound = base ** 4
    bdd_live_nodes = bdd.live_nodes(interface_root)
    bdd_total_operations = bdd.apply_calls + bdd.mk_calls
    bdd_bounds_hold = (
        bdd_live_nodes <= bdd_node_bound
        and bdd_total_operations <= bdd_operation_bound
    )

    if not swap_ok or not mixed_equal:
        verdict = "FAIL_NONLOCAL_INFORMATION_REQUIRED"
        diagnostic = "FROZEN_SWAP_OR_MIXED_RESIDUAL_IDENTITY_NOT_REPRODUCED"
    elif any_true_branch or interface_is_constant:
        verdict = "FAIL_TRIVIAL_ESCAPE"
        diagnostic = "R_C_TRUE" if interface_is_true else "R_C_FALSE"
    elif not orcsp_bound_holds or not bdd_bounds_hold:
        verdict = "FAIL_CLOSURE_BLOWUP"
        diagnostic = "ORCSP_OR_ROBDD_FROZEN_ENVELOPE_EXCEEDED"
    elif unary_factorized:
        verdict = "FAIL_UNARY_FACTORIZATION"
        diagnostic = "R_C_NONTRIVIAL_BUT_PRODUCT_OF_UNARY_PROJECTIONS"
    else:
        verdict = "PASS_NONTRIVIAL_CORRELATED_BRIDGE"
        diagnostic = "R_C_CORRELATED__FIRST_GENUINE_WALL_SPECIMEN_IF_INDEPENDENTLY_VERIFIED"

    result = {
        "artifact_id": "JANUS-TRUMP-WALL-MANTEQUILLA-FIRST-GENUINE-WALL-UUF100-007-CANDIDATE-v1",
        "date": "2026-09-18",
        "source": "UUF100_007",
        "language": LANGUAGE,
        "verdict": verdict,
        "diagnostic_subclassification": diagnostic,
        "sealed_bundle_payload_sha256": payload_sha,
        "frozen_cell": list(CELL),
        "direct_exact_swap_reproduced": swap_ok,
        "local_constraint_count": len(local),
        "exterior_constraint_count": len(exterior),
        "boundary_variables": boundary,
        "boundary_variable_count": len(boundary),
        "raw_branch_count": 4,
        "retained_branch_count": 3,
        "mixed_branch_residuals_equal": mixed_equal,
        "any_true_raw_branch": any_true_branch,
        "raw_branch_residual_sha256": {
            f"{a}{b}": csha(raw[(a, b)]) for a, b in RAW_ASSIGNMENTS
        },
        "interface": {
            "semantics": "EXISTS_x12_x83_LOCAL_CSP",
            "retained_branches": retained,
            "exactness_method": "STRUCTURAL_SHANNON_TWO_VAR_PLUS_EXACT_SWAP_RESIDUAL_IDENTITY",
            "orcsp_semantic_digest_sha256": csha(retained),
            "robdd_semantic_sha256": bdd.semantic_hash(interface_root),
            "unary_product_robdd_semantic_sha256": bdd.semantic_hash(unary_product_root),
        },
        "semantic_audit": {
            "interface_is_true": interface_is_true,
            "interface_is_false": interface_is_false,
            "interface_is_constant": interface_is_constant,
            "unary_projections": unary_projections,
            "unary_factorized": unary_factorized,
            "genuine_joint_correlation": genuine_correlation,
        },
        "accounting": {
            "local_input_symbol_count": local_symbols,
            "compressed_orcsp_symbol_count": compressed_orcsp_symbols,
            "orcsp_symbol_bound": orcsp_bound,
            "orcsp_bound_holds": orcsp_bound_holds,
            "robdd_live_nonterminal_nodes": bdd_live_nodes,
            "robdd_node_bound": bdd_node_bound,
            "robdd_apply_calls": bdd.apply_calls,
            "robdd_mk_calls": bdd.mk_calls,
            "robdd_total_operations": bdd_total_operations,
            "robdd_operation_bound": bdd_operation_bound,
            "robdd_bounds_hold": bdd_bounds_hold,
            "internal_assignments_constructed": 4,
            "boundary_cube_assignments_enumerated": 0,
            "sat_solver_invocations": 0,
            "full_transposition_searches": 0,
            "frozen_direct_swap_checks": 1,
            "detector_imports": [],
            "wl_imports": [],
            "e3_imports": [],
        },
        "claim_ceiling": "ONE_FRESH_UNSEEN_FROZEN_K2_ACTIVE_EXACT_SYMMETRY_CELL__NONTRIVIAL_BOUNDARY_INTERFACE_ONLY",
        "candidate_runtime_seconds": time.perf_counter() - t0,
    }
    result["candidate_semantic_digest_sha256"] = csha({
        "verdict": result["verdict"],
        "diagnostic_subclassification": diagnostic,
        "sealed_bundle_payload_sha256": payload_sha,
        "frozen_cell": result["frozen_cell"],
        "direct_exact_swap_reproduced": swap_ok,
        "boundary_variables": boundary,
        "mixed_branch_residuals_equal": mixed_equal,
        "any_true_raw_branch": any_true_branch,
        "interface": result["interface"],
        "semantic_audit": result["semantic_audit"],
        "accounting_without_runtime": result["accounting"],
    })

    with open(sys.argv[2], "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps({
        "verdict": verdict,
        "diagnostic_subclassification": diagnostic,
        "boundary_variable_count": len(boundary),
        "local_constraint_count": len(local),
        "any_true_raw_branch": any_true_branch,
        "interface_is_true": interface_is_true,
        "interface_is_false": interface_is_false,
        "unary_factorized": unary_factorized,
        "genuine_joint_correlation": genuine_correlation,
        "compressed_orcsp_symbol_count": compressed_orcsp_symbols,
        "orcsp_symbol_bound": orcsp_bound,
        "robdd_live_nonterminal_nodes": bdd_live_nodes,
        "robdd_node_bound": bdd_node_bound,
        "robdd_total_operations": bdd_total_operations,
        "robdd_operation_bound": bdd_operation_bound,
        "candidate_semantic_digest_sha256": result["candidate_semantic_digest_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
