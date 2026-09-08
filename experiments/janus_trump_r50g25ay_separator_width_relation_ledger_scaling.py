from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations, product
from pathlib import Path

import janus_trump_r50g25av_reachable_multi_defect_growth_witness as av
import janus_trump_r50g25at_tautology_hardened_runner as ath
import janus_trump_r50g25aw_defect_component_decomposition as aw

GATE = "R50G25AY_SEPARATOR_WIDTH_SCALING_OR_RELATION_LEDGER_BLOWUP_COUNTEREXAMPLE"
PREREG = "98bfc81908c3887b326fe3f6c560539a7ce2a113"
PARENT_AX = "79d976215037655740bf999db3908d6e80025046"
AX2_META = "69ffdf46d4d8ec3cc704831900526dbaa37be78b"
AR_AS_BACKFILL = "a12a77d591a83f3ee8fe53cde261409f79f3fae4"
Y_TARGET_HASH = av.Y_TARGET_HASH
LADDER = (1, 2, 3, 4, 6, 8)
TAUTOLOGY_POLICY = av.TAUTOLOGY_POLICY

WIDTH_AND_LEDGER = "WIDTH_AND_RELATION_LEDGER_WITHIN_L4"
SPARSE_ONLY = "SPARSE_RELATION_LEDGER_ONLY_WITHIN_L4"
LEDGER_OBSTRUCTION = "RELATION_LEDGER_EXCEEDS_L4"
CONTRACT_FAILURE = "RELATION_CONTRACT_FAILURE"
ABSORBED = "NON_FALSIFYING_CHEAP_POLICY_ABSORPTION"
UNKNOWN = "UNKNOWN_RESOURCE_LIMIT"


def canonical(formula):
    return av.canonical(formula)


def clv(formula):
    return av.clv(formula)


def formula_hash(formula):
    return av.formula_hash(formula)


def build_root(g: int):
    if int(g) not in LADDER:
        raise AssertionError(("G_NOT_IN_FROZEN_LADDER", g, LADDER))
    unit = canonical(av.load_sealed_y_target())
    if formula_hash(unit) != Y_TARGET_HASH:
        raise AssertionError(("Y_UNIT_HASH_DRIFT", formula_hash(unit), Y_TARGET_HASH))
    unit_vars = sorted(map(int, av.r33.variables(unit)))
    if not unit_vars:
        raise AssertionError("EMPTY_Y_UNIT")
    m = max(unit_vars)
    copies = []
    var_sets = []
    copy_hashes = []
    for j in range(int(g)):
        cp = av.shift_formula(unit, j * m)
        vs = sorted(map(int, av.r33.variables(cp)))
        copies.extend(cp)
        var_sets.append(vs)
        copy_hashes.append(formula_hash(cp))
    if any(set(var_sets[i]).intersection(var_sets[j]) for i in range(len(var_sets)) for j in range(i + 1, len(var_sets))):
        raise AssertionError("SHIFTED_COPY_VARIABLE_OVERLAP")
    bridges = []
    for j in range(int(g) - 1):
        bridges.append((max(var_sets[j]), min(var_sets[j + 1])))
    root = canonical(list(copies) + bridges)
    meta = {
        "family": "CHAIN_CONNECTED_SHIFTED_SEALED_Y_RESIDUAL_COPIES",
        "g": int(g),
        "Y_target_hash": Y_TARGET_HASH,
        "Y_unit_CLV": list(clv(unit)),
        "Y_unit_max_var": int(m),
        "copy_hashes": copy_hashes,
        "copy_var_ranges": [[min(vs), max(vs)] for vs in var_sets],
        "bridge_rule": "ALL_POSITIVE_BINARY_MAX_OF_COPY_J_TO_MIN_OF_COPY_J_PLUS_1",
        "bridges": [list(map(int, c)) for c in bridges],
        "bridge_endpoints": sorted({abs(int(l)) for c in bridges for l in c}),
    }
    return root, meta


def factor_table_clause(fid: int, clause):
    scope = tuple(sorted({abs(int(l)) for l in clause}))
    table = {}
    for bits in product((0, 1), repeat=len(scope)):
        assign = {v: int(b) for v, b in zip(scope, bits)}
        ok = False
        for lit in clause:
            bit = assign[abs(int(lit))]
            if (int(lit) > 0 and bit == 1) or (int(lit) < 0 and bit == 0):
                ok = True
                break
        if ok:
            table[tuple(bits)] = True
    return {"id": int(fid), "kind": "DEFECT", "scope": scope, "table": table}


def factor_table_affine(fid: int, eq):
    scope = tuple(sorted(set(map(int, eq["vars"]))))
    rhs = int(eq["rhs"])
    if rhs not in (0, 1):
        raise AssertionError(("AFFINE_RHS_NOT_BIT", rhs))
    table = {}
    for bits in product((0, 1), repeat=len(scope)):
        lhs = 0
        for b in bits:
            lhs ^= int(b)
        if lhs == rhs:
            table[tuple(bits)] = True
    return {"id": int(fid), "kind": "AFFINE", "scope": scope, "table": table}


def primal_graph(variables, scopes):
    adj = {int(v): set() for v in variables}
    for scope in scopes:
        for a, b in combinations(sorted(map(int, scope)), 2):
            adj[a].add(b)
            adj[b].add(a)
    return adj


def min_fill_order(adj0):
    adj = {int(v): set(map(int, ns)) for v, ns in adj0.items()}
    order = []
    width = 0
    fill_edges = []
    bags = []
    while adj:
        scored = []
        for v in sorted(adj):
            ns = sorted(adj[v])
            missing = sum(1 for a, b in combinations(ns, 2) if b not in adj[a])
            scored.append((missing, len(ns), v))
        _, _, v = min(scored)
        ns = sorted(adj[v])
        width = max(width, len(ns))
        new_fill = []
        for a, b in combinations(ns, 2):
            if b not in adj[a]:
                adj[a].add(b)
                adj[b].add(a)
                e = (min(a, b), max(a, b))
                fill_edges.append(e)
                new_fill.append(e)
        bags.append({"eliminate": int(v), "later_neighbors": ns, "new_fill_edges": [list(e) for e in new_fill]})
        for u in ns:
            adj[u].discard(v)
        del adj[v]
        order.append(int(v))
    return {"order": order, "induced_width": int(width), "fill_edges": fill_edges, "bags": bags}


def factor_lookup(factor, assignment):
    key = tuple(int(assignment[v]) for v in factor["scope"])
    return bool(factor["table"].get(key, False))


def table_sha(scope, table):
    payload = {"scope": list(map(int, scope)), "rows": [list(map(int, k)) for k in sorted(table)]}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def bucket_relation(variables, defects, equations, order, induced_width: int):
    factors = []
    nodes = {}
    next_id = 0
    source_factor_count = 0
    for clause in defects:
        f = factor_table_clause(next_id, clause)
        factors.append(f); nodes[next_id] = f; next_id += 1; source_factor_count += 1
    for eq in equations:
        f = factor_table_affine(next_id, eq)
        factors.append(f); nodes[next_id] = f; next_id += 1; source_factor_count += 1

    total_rows = sum(len(f["table"]) for f in factors)
    source_rows = int(total_rows)
    max_generated_scope = 0
    max_generated_rows = 0
    generated_count = 0
    evaluation_attempts = 0
    trace = []

    for step, v0 in enumerate(order):
        v = int(v0)
        gathered = [f for f in factors if v in f["scope"]]
        factors = [f for f in factors if v not in f["scope"]]
        if not gathered:
            neutral = {"id": next_id, "kind": "NEUTRAL", "scope": (v,), "table": {(0,): True, (1,): True}}
            nodes[next_id] = neutral; next_id += 1
            gathered = [neutral]
            total_rows += 2
        union_scope = sorted({u for f in gathered for u in f["scope"]})
        if v not in union_scope:
            raise AssertionError(("BUCKET_VARIABLE_MISSING", step, v, union_scope))
        new_scope = tuple(u for u in union_scope if u != v)
        if len(new_scope) > int(induced_width):
            raise AssertionError(("GENERATED_SCOPE_EXCEEDS_REPLAYED_WIDTH", step, v, len(new_scope), induced_width))
        table = {}
        choices = {}
        for boundary_bits in product((0, 1), repeat=len(new_scope)):
            boundary = {u: int(b) for u, b in zip(new_scope, boundary_bits)}
            for value in (0, 1):
                evaluation_attempts += 1
                local = dict(boundary); local[v] = int(value)
                if all(factor_lookup(f, local) for f in gathered):
                    key = tuple(boundary_bits)
                    table[key] = True
                    choices[key] = {"value": int(value), "child_factor_ids": [int(f["id"]) for f in gathered]}
                    break
        generated = {
            "id": next_id,
            "kind": "GENERATED",
            "scope": new_scope,
            "table": table,
            "eliminated": v,
            "children": tuple(int(f["id"]) for f in gathered),
            "choices": choices,
        }
        nodes[next_id] = generated
        factors.append(generated)
        generated_count += 1
        total_rows += len(table)
        max_generated_scope = max(max_generated_scope, len(new_scope))
        max_generated_rows = max(max_generated_rows, len(table))
        trace.append({
            "step": int(step),
            "eliminated": v,
            "input_factor_count": len(gathered),
            "output_scope": list(map(int, new_scope)),
            "output_rows": len(table),
            "output_table_sha256": table_sha(new_scope, table),
        })
        next_id += 1

    if any(f["scope"] for f in factors):
        raise AssertionError(("NONEMPTY_ROOT_SCOPE", [f["scope"] for f in factors]))
    sat = all(bool(f["table"].get((), False)) for f in factors)
    assignment = {}
    reconstruction_failures = []

    def reconstruct(fid: int, available):
        f = nodes[int(fid)]
        if f["kind"] in {"DEFECT", "AFFINE", "NEUTRAL"}:
            return
        key = tuple(int(available[u]) for u in f["scope"])
        choice = f["choices"].get(key)
        if choice is None:
            reconstruction_failures.append(f"MISSING_CHOICE:{fid}")
            return
        v = int(f["eliminated"]); value = int(choice["value"])
        if v in assignment and assignment[v] != value:
            reconstruction_failures.append(f"ASSIGNMENT_CONFLICT:{v}")
            return
        assignment[v] = value
        local = dict(available); local[v] = value
        for child_id in choice["child_factor_ids"]:
            child = nodes[int(child_id)]
            child_available = {u: int(local[u]) for u in child["scope"]}
            reconstruct(int(child_id), child_available)

    if sat:
        for f in factors:
            reconstruct(int(f["id"]), {})

    return {
        "decision": "SAT" if sat else "UNSAT",
        "source_factor_count": int(source_factor_count),
        "generated_factor_count": int(generated_count),
        "source_materialized_rows": int(source_rows),
        "total_materialized_rows": int(total_rows),
        "maximum_generated_scope": int(max_generated_scope),
        "maximum_generated_table_rows": int(max_generated_rows),
        "evaluation_attempts": int(evaluation_attempts),
        "trace": trace,
        "assignment": {int(k): int(v) for k, v in assignment.items()},
        "reconstruction_failures": reconstruction_failures,
    }


def validate_source(assignment, defects, equations):
    clause_fail = []
    for i, clause in enumerate(defects):
        ok = False
        for lit in clause:
            bit = int(assignment[abs(int(lit))])
            if (int(lit) > 0 and bit == 1) or (int(lit) < 0 and bit == 0):
                ok = True; break
        if not ok:
            clause_fail.append(i)
    eq_fail = []
    for i, eq in enumerate(equations):
        lhs = 0
        for v in eq["vars"]:
            lhs ^= int(assignment[int(v)])
        if lhs != int(eq["rhs"]):
            eq_fail.append(i)
    return clause_fail, eq_fail


def run_rung(g: int):
    root, meta = build_root(int(g))
    replay = av.asmod.y.policy_replay(root, av.asmod.r50g25g._chain())
    kind = str(replay.get("kind"))
    base = {
        "gate": GATE,
        "preregistration_commit": PREREG,
        "parent_AX_head": PARENT_AX,
        "AX2_meta": AX2_META,
        "AR_AS_backfill": AR_AS_BACKFILL,
        "g": int(g),
        "meta": meta,
        "root_hash": formula_hash(root),
        "root_CLV": list(clv(root)),
        "policy_kind": kind,
        "truth_oracle": {"generation": False, "selection": False, "verdict": False},
        "firewall": {"P_VS_NP": "OPEN", "SAT_IN_P": "NOT_PROVED", "TRUMP_finished": False},
    }
    if kind in {"TERMINAL", "AFFINE"}:
        base.update({"classification": ABSORBED, "relevant": False, "route_length": len(replay.get("route", [])), "failures": []})
        return base
    if kind != "RESIDUAL":
        base.update({"classification": CONTRACT_FAILURE, "relevant": False, "failures": [{"kind": "POLICY_CONTRACT_DRIFT", "observed": kind}]})
        return base

    residual = canonical(replay["state"])
    effective, tautologies = av.effective_canonical(residual)
    extraction = ath.hardened_extract(residual)
    failures = []
    if extraction.get("explicit_tautology_policy") != TAUTOLOGY_POLICY or not extraction.get("tautology_check_pass"):
        failures.append("TAUTOLOGY_POLICY_DRIFT")
    if not extraction.get("partition_pass") or extraction.get("replay_failures"):
        failures.append("AFFINE_EXTRACTION_OR_REPLAY_FAILURE")
    factor = aw.factor_components(extraction)
    if not factor.get("factorization_partition_pass") or not factor.get("semantic_independence_pass"):
        failures.append("FACTOR_COMPONENT_CONTRACT_FAILURE")
    defect_components = [c for c in factor["components"] if c["defect_count"] > 0]
    bridge_endpoints = set(map(int, meta["bridge_endpoints"]))
    if int(g) == 1:
        targets = defect_components if len(defect_components) == 1 else []
    else:
        targets = [c for c in defect_components if bridge_endpoints <= set(map(int, c["variables"]))]
    if len(targets) != 1:
        failures.append("TARGET_CONNECTED_COMPONENT_SELECTION_FAILURE")
        target = max(defect_components, key=lambda c: c["defect_count"], default={"variables": [], "defect_indices": [], "affine_equation_indices": [], "defect_count": 0, "affine_equation_count": 0})
    else:
        target = targets[0]
    if len(defect_components) != 1:
        failures.append("FROZEN_CHAIN_DID_NOT_FORM_ONE_DEFECT_COMPONENT")

    defects = [tuple(map(int, extraction["defects"][i])) for i in target.get("defect_indices", [])]
    equations = [
        {"vars": list(map(int, extraction["equations"][i]["vars"])), "rhs": int(extraction["equations"][i]["rhs"])}
        for i in target.get("affine_equation_indices", [])
    ]
    variables = tuple(sorted(map(int, target.get("variables", []))))
    L = int(sum(len(c) for c in effective))
    budget = int(L) ** 4

    source_scopes = [tuple(sorted({abs(int(l)) for l in c})) for c in defects] + [tuple(sorted(set(map(int, e["vars"])))) for e in equations]
    adj = primal_graph(variables, source_scopes)
    sep = min_fill_order(adj)
    w = int(sep["induced_width"])
    state_bound = 1 << w

    relation = None
    if not failures:
        try:
            relation = bucket_relation(variables, defects, equations, sep["order"], w)
        except MemoryError:
            return {**base, "relevant": True, "classification": UNKNOWN, "residual_hash": formula_hash(residual), "L": L, "L4_budget": budget, "failures": ["MEMORY_ERROR"]}
        except Exception as exc:
            failures.append("RELATION_EXECUTION_FAILURE:" + repr(exc))

    reconstruction_pass = False
    source_validation_pass = False
    clause_fail = []
    eq_fail = []
    if relation is not None:
        if relation["decision"] == "SAT":
            reconstruction_pass = not relation["reconstruction_failures"] and set(map(int, relation["assignment"])) == set(variables)
            if reconstruction_pass:
                clause_fail, eq_fail = validate_source(relation["assignment"], defects, equations)
                source_validation_pass = not clause_fail and not eq_fail
            if not reconstruction_pass:
                failures.append("SAT_RECONSTRUCTION_FAILURE")
            if reconstruction_pass and not source_validation_pass:
                failures.append("RECONSTRUCTED_ASSIGNMENT_SOURCE_VALIDATION_FAILURE")
        else:
            reconstruction_pass = True
            source_validation_pass = True

    semantic_contract_pass = relation is not None and not failures
    rows = int(relation["total_materialized_rows"]) if relation else 0
    width_within = state_bound <= budget
    ledger_within = relation is not None and rows <= budget

    if not semantic_contract_pass:
        classification = CONTRACT_FAILURE
    elif not ledger_within:
        classification = LEDGER_OBSTRUCTION
    elif not width_within:
        classification = SPARSE_ONLY
    else:
        classification = WIDTH_AND_LEDGER

    source_payload = {
        "g": int(g),
        "variables": list(variables),
        "defects": [list(map(int, c)) for c in defects],
        "equations": equations,
        "order": list(map(int, sep["order"])),
        "induced_width": w,
        "L": L,
        "L4_budget": budget,
        "residual_hash": formula_hash(residual),
    }
    source_payload_sha = hashlib.sha256(json.dumps(source_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    base.update({
        "relevant": True,
        "classification": classification,
        "residual_hash": formula_hash(residual),
        "residual_CLV": list(clv(residual)),
        "route_length": len(replay.get("route", [])),
        "tautology_count": len(tautologies),
        "extraction": {
            "affine_clause_count": int(extraction.get("affine_clause_count", 0)),
            "recognized_equation_count": int(extraction.get("recognized_equation_count", 0)),
            "defect_clause_count": int(extraction.get("defect_clause_count", 0)),
            "partition_pass": bool(extraction.get("partition_pass")),
            "replay_failure_count": len(extraction.get("replay_failures", [])),
        },
        "target_component": {
            "variable_count": len(variables),
            "defect_count": len(defects),
            "affine_equation_count": len(equations),
            "component_count_with_defects": len(defect_components),
        },
        "L": L,
        "L4_budget": budget,
        "separator": {
            "algorithm": "DETERMINISTIC_MIN_FILL_MISSING_THEN_DEGREE_THEN_VAR",
            "induced_width": w,
            "state_bound_2_pow_w": int(state_bound),
            "width_state_within_L4": bool(width_within),
            "fill_edge_count": len(sep["fill_edges"]),
            "order": sep["order"],
        },
        "relation": relation,
        "semantic_relation_contract_pass": bool(semantic_contract_pass),
        "full_RIPC_size_obligation_pass": bool(semantic_contract_pass and ledger_within),
        "reconstruction_pass": bool(reconstruction_pass),
        "source_validation_pass": bool(source_validation_pass),
        "source_clause_failure_indices": clause_fail,
        "source_equation_failure_indices": eq_fail,
        "relation_ledger_within_L4": bool(ledger_within),
        "source_payload": source_payload,
        "source_payload_sha256": source_payload_sha,
        "failures": failures,
    })
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    result = run_rung(args.g)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    summary = {k: result.get(k) for k in ("g", "policy_kind", "relevant", "classification", "L", "L4_budget", "reconstruction_pass", "source_validation_pass")}
    if result.get("relation"):
        summary["total_materialized_rows"] = result["relation"]["total_materialized_rows"]
        summary["w"] = result["separator"]["induced_width"]
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
