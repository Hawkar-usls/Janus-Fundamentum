from __future__ import annotations

import hashlib
import json
import sys
import time
from collections import Counter
from itertools import product

CELL = (61, 91, 237)
GENERATORS = ((61, 91), (61, 237), (91, 237))
RAW_ASSIGNMENTS = tuple(product((0, 1), repeat=3))
REPS = {
    0: (0, 0, 0),
    1: (0, 0, 1),
    2: (0, 1, 1),
    3: (1, 1, 1),
}
LANGUAGE = "OR_OF_CANONICAL_RESIDUAL_CSP_ORBIT_BRANCHES_PLUS_CANONICAL_ROBDD"


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
    original = formula_counter(constraints)
    swapped = Counter(renamed_key(c, left, right) for c in constraints)
    return original == swapped


def canonical_residual(local_constraints, bits):
    fixed = {CELL[i]: int(bits[i]) for i in range(3)}
    residual = {}
    for c in local_constraints:
        scope = [int(v) for v in c["scope"]]
        remaining = [v for v in scope if v not in fixed]
        surviving = []
        for row in c["allowed"]:
            amap = {v: int(bit) for v, bit in zip(scope, row, strict=True)}
            if all(amap[v] == value for v, value in fixed.items() if v in amap):
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
    total = 0
    for c in constraints:
        total += 1 + len(c["scope"])
        total += sum(len(row) for row in c["allowed"])
    return total


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

    def neg(self, u):
        return self.apply("xor", u, 1)

    def _term(self, op, a, b):
        if op == "and":
            return int(bool(a) and bool(b))
        if op == "or":
            return int(bool(a) or bool(b))
        if op == "xor":
            return int(bool(a) ^ bool(b))
        raise ValueError(op)

    def apply(self, op, u, v):
        self.apply_calls += 1
        if op in {"and", "or", "xor"} and u > v:
            u, v = v, u
        key = (op, int(u), int(v))
        if key in self.apply_cache:
            return self.apply_cache[key]
        if u < 2 and v < 2:
            out = self._term(op, u, v)
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

    def restrict(self, u, var, bit):
        key = (int(u), int(var), int(bit))
        if key in self.restrict_cache:
            return self.restrict_cache[key]
        if u < 2:
            self.restrict_cache[key] = u
            return u
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
            v, low, high = self.nodes[u]
            h = csha({"var": v, "low": rec(low), "high": rec(high)})
            memo[u] = h
            return h
        return rec(root)


def branch_key(branch):
    return json.dumps(branch, sort_keys=True, separators=(",", ":"))


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: candidate.py SEALED_BUNDLE.json OUTPUT.json")
    t0 = time.perf_counter()
    bundle = json.load(open(sys.argv[1], "r", encoding="utf-8"))
    payload_hash = bundle.get("payload_sha256")
    payload = dict(bundle)
    payload.pop("payload_sha256", None)
    if csha(payload) != payload_hash:
        raise RuntimeError("SEALED_BUNDLE_PAYLOAD_SHA_MISMATCH")
    if tuple(bundle["frozen_witness"]["cell"]) != CELL:
        raise RuntimeError("FROZEN_CELL_MISMATCH")

    reduced = bundle["reduced_csp"]
    constraints = list(reduced["constraints"])
    cell_set = set(CELL)
    local = [c for c in constraints if cell_set.intersection(map(int, c["scope"]))]
    exterior = [c for c in constraints if not cell_set.intersection(map(int, c["scope"]))]
    boundary = sorted({
        int(v) for c in local for v in c["scope"] if int(v) not in cell_set
    })

    generator_checks = {
        f"{a}_{b}": exact_swap_invariant(constraints, a, b)
        for a, b in GENERATORS
    }
    full_s3_ok = all(generator_checks.values())

    raw = {bits: canonical_residual(local, bits) for bits in RAW_ASSIGNMENTS}
    orbit_identity = {}
    orbit_members = {}
    for weight in range(4):
        members = [bits for bits in RAW_ASSIGNMENTS if sum(bits) == weight]
        keys = [branch_key(raw[bits]) for bits in members]
        orbit_members[str(weight)] = [list(bits) for bits in members]
        orbit_identity[str(weight)] = len(set(keys)) == 1

    bdd = ROBDD()
    raw_roots = {bits: bdd.residual_bdd(raw[bits]) for bits in RAW_ASSIGNMENTS}
    any_true_branch = any(root == 1 for root in raw_roots.values())

    retained = []
    interface_root = 0
    for weight in range(4):
        bits = REPS[weight]
        root = raw_roots[bits]
        interface_root = bdd.apply("or", interface_root, root)
        retained.append({
            "hamming_weight": weight,
            "representative": list(bits),
            "residual": raw[bits],
            "residual_sha256": csha(raw[bits]),
            "bdd_semantic_sha256": bdd.semantic_hash(root),
        })

    interface_is_constant = interface_root in (0, 1)

    unary_projection = {}
    unary_product_root = 1
    for v in boundary:
        allowed0 = bdd.restrict(interface_root, v, 0) != 0
        allowed1 = bdd.restrict(interface_root, v, 1) != 0
        unary_projection[str(v)] = [b for b, ok in ((0, allowed0), (1, allowed1)) if ok]
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
    correlated = not unary_factorized

    local_symbols = relation_symbol_count(local)
    base = local_symbols + len(boundary) + 2
    node_bound = base ** 2
    operation_bound = base ** 4
    live_nodes = bdd.live_nodes(interface_root)
    operations = bdd.apply_calls + bdd.mk_calls
    bounds_hold = live_nodes <= node_bound and operations <= operation_bound

    if not full_s3_ok or not all(orbit_identity.values()):
        verdict = "FAIL_NONLOCAL_INFORMATION_REQUIRED"
        reason = "FROZEN_S3_OR_ORBIT_RESIDUAL_IDENTITY_NOT_REPRODUCED"
    elif any_true_branch or len(boundary) < 2 or interface_is_constant:
        verdict = "FAIL_TRIVIAL_ESCAPE"
        reason = "TRUE_INTERNAL_BRANCH_OR_CONSTANT_INTERFACE_OR_BOUNDARY_TOO_SMALL"
    elif not bounds_hold:
        verdict = "FAIL_CLOSURE_BLOWUP"
        reason = "ROBDD_POLYNOMIAL_ENVELOPE_EXCEEDED"
    elif unary_factorized:
        verdict = "FAIL_UNARY_FACTORIZATION"
        reason = "EXACT_BOUNDARY_RELATION_EQUALS_PRODUCT_OF_UNARY_PROJECTIONS"
    else:
        verdict = "PASS_NONTRIVIAL_CORRELATED_BRIDGE"
        reason = None

    result = {
        "artifact_id": "JANUS-TRUMP-WALL-MANTEQUILLA-NONTRIVIAL-CORRELATED-BOUNDARY-UF250-016-CANDIDATE-v1",
        "source": "UF250_016",
        "language": LANGUAGE,
        "verdict": verdict,
        "failure_reason": reason,
        "sealed_bundle_payload_sha256": payload_hash,
        "frozen_cell": list(CELL),
        "generator_checks": generator_checks,
        "full_s3_generator_invariance": full_s3_ok,
        "local_constraint_count": len(local),
        "exterior_constraint_count": len(exterior),
        "boundary_variables": boundary,
        "boundary_variable_count": len(boundary),
        "raw_branch_count": 8,
        "orbit_representative_count": 4,
        "orbit_members": orbit_members,
        "equal_weight_residual_identity": orbit_identity,
        "any_true_raw_branch": any_true_branch,
        "raw_branch_residual_sha256": {
            "".join(map(str, bits)): csha(raw[bits]) for bits in RAW_ASSIGNMENTS
        },
        "interface": {
            "semantics": "EXISTS_x61_x91_x237_LOCAL_CSP",
            "retained_orbit_branches": retained,
            "exactness_method": "STRUCTURAL_SHANNON_THREE_VAR_PLUS_EXACT_S3_WEIGHT_ORBIT_IDENTITY",
            "robdd_semantic_sha256": bdd.semantic_hash(interface_root),
            "unary_product_robdd_semantic_sha256": bdd.semantic_hash(unary_product_root),
        },
        "semantic_audit": {
            "interface_is_constant": interface_is_constant,
            "unary_projections": unary_projection,
            "unary_factorized": unary_factorized,
            "genuine_joint_correlation": correlated and not interface_is_constant,
        },
        "accounting": {
            "local_input_symbol_count": local_symbols,
            "robdd_live_nonterminal_nodes": live_nodes,
            "robdd_node_bound": node_bound,
            "robdd_apply_calls": bdd.apply_calls,
            "robdd_mk_calls": bdd.mk_calls,
            "robdd_total_operations": operations,
            "robdd_operation_bound": operation_bound,
            "robdd_bounds_hold": bounds_hold,
            "internal_assignments_constructed": 8,
            "boundary_cube_assignments_enumerated": 0,
            "sat_solver_invocations": 0,
            "full_transposition_searches": 0,
            "frozen_generator_checks": 3,
            "detector_imports": [],
            "wl_imports": [],
            "e3_imports": [],
        },
        "claim_ceiling": "ONE_FROZEN_K3_EXACT_SYMMETRY_CELL__NONTRIVIAL_BOUNDARY_INTERFACE_ONLY",
        "candidate_runtime_seconds": time.perf_counter() - t0,
    }
    result["candidate_semantic_digest_sha256"] = csha({
        "verdict": result["verdict"],
        "sealed_bundle_payload_sha256": payload_hash,
        "frozen_cell": result["frozen_cell"],
        "generator_checks": generator_checks,
        "boundary_variables": boundary,
        "equal_weight_residual_identity": orbit_identity,
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
        "failure_reason": reason,
        "boundary_variable_count": len(boundary),
        "local_constraint_count": len(local),
        "any_true_raw_branch": any_true_branch,
        "interface_is_constant": interface_is_constant,
        "unary_factorized": unary_factorized,
        "genuine_joint_correlation": result["semantic_audit"]["genuine_joint_correlation"],
        "robdd_live_nonterminal_nodes": live_nodes,
        "robdd_node_bound": node_bound,
        "robdd_total_operations": operations,
        "robdd_operation_bound": operation_bound,
        "candidate_semantic_digest_sha256": result["candidate_semantic_digest_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
