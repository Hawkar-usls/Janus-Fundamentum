from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations, product
from pathlib import Path

PREREG = "98bfc81908c3887b326fe3f6c560539a7ce2a113"
LADDER = (1, 2, 3, 4, 6, 8)


def clause_ok(clause, assign):
    for lit in clause:
        b = int(assign[abs(int(lit))])
        if (int(lit) > 0 and b == 1) or (int(lit) < 0 and b == 0):
            return True
    return False


def affine_ok(eq, assign):
    x = 0
    for v in eq["vars"]:
        x ^= int(assign[int(v)])
    return x == int(eq["rhs"])


def make_factor(kind, payload, fid):
    if kind == "DEFECT":
        scope = tuple(sorted({abs(int(l)) for l in payload}))
        rows = set()
        for bits in product((0, 1), repeat=len(scope)):
            a = {v: int(b) for v, b in zip(scope, bits)}
            if clause_ok(payload, a):
                rows.add(tuple(bits))
    else:
        scope = tuple(sorted(set(map(int, payload["vars"]))))
        rows = set()
        for bits in product((0, 1), repeat=len(scope)):
            a = {v: int(b) for v, b in zip(scope, bits)}
            if affine_ok(payload, a):
                rows.add(tuple(bits))
    return {"id": int(fid), "scope": scope, "rows": rows, "kind": kind}


def build_graph(variables, scopes):
    graph = {int(v): set() for v in variables}
    for scope in scopes:
        ss = sorted(map(int, scope))
        for a, b in combinations(ss, 2):
            graph[a].add(b); graph[b].add(a)
    return graph


def independent_min_fill(graph0):
    graph = {v: set(ns) for v, ns in graph0.items()}
    order = []
    width = 0
    while graph:
        choices = []
        for v in sorted(graph):
            ns = sorted(graph[v])
            missing = 0
            for a, b in combinations(ns, 2):
                missing += int(b not in graph[a])
            choices.append((missing, len(ns), v))
        _, _, v = min(choices)
        ns = sorted(graph[v])
        width = max(width, len(ns))
        for a, b in combinations(ns, 2):
            graph[a].add(b); graph[b].add(a)
        for u in ns:
            graph[u].discard(v)
        del graph[v]
        order.append(int(v))
    return order, int(width)


def lookup(f, a):
    return tuple(int(a[v]) for v in f["scope"]) in f["rows"]


def replay(payload):
    variables = tuple(map(int, payload["variables"]))
    defects = [tuple(map(int, c)) for c in payload["defects"]]
    equations = [{"vars": list(map(int, e["vars"])), "rhs": int(e["rhs"])} for e in payload["equations"]]
    factors = []
    next_id = 0
    for c in defects:
        factors.append(make_factor("DEFECT", c, next_id)); next_id += 1
    for e in equations:
        factors.append(make_factor("AFFINE", e, next_id)); next_id += 1
    source_rows = sum(len(f["rows"]) for f in factors)
    total_rows = int(source_rows)
    scopes = [f["scope"] for f in factors]
    order, width = independent_min_fill(build_graph(variables, scopes))
    records = []
    max_scope = 0
    max_rows = 0

    for v in order:
        chosen = [f for f in factors if v in f["scope"]]
        factors = [f for f in factors if v not in f["scope"]]
        if not chosen:
            chosen = [{"id": next_id, "scope": (v,), "rows": {(0,), (1,)}, "kind": "NEUTRAL"}]
            next_id += 1
            total_rows += 2
        union = sorted({u for f in chosen for u in f["scope"]})
        new_scope = tuple(u for u in union if u != v)
        rows = set()
        back = {}
        for boundary_bits in product((0, 1), repeat=len(new_scope)):
            boundary = {u: int(b) for u, b in zip(new_scope, boundary_bits)}
            for value in (0, 1):
                local = dict(boundary); local[v] = int(value)
                if all(lookup(f, local) for f in chosen):
                    rows.add(tuple(boundary_bits))
                    back[tuple(boundary_bits)] = int(value)
                    break
        nf = {"id": next_id, "scope": new_scope, "rows": rows, "kind": "GENERATED"}
        factors.append(nf); next_id += 1
        total_rows += len(rows)
        max_scope = max(max_scope, len(new_scope))
        max_rows = max(max_rows, len(rows))
        records.append({"v": int(v), "scope": new_scope, "back": back})

    assert all(not f["scope"] for f in factors), [f["scope"] for f in factors]
    sat = all(() in f["rows"] for f in factors)
    assignment = {}
    if sat:
        for rec in reversed(records):
            key = tuple(int(assignment[u]) for u in rec["scope"])
            if key not in rec["back"]:
                raise AssertionError(("INDEPENDENT_RECONSTRUCTION_MISSING", rec["v"], key))
            assignment[int(rec["v"])] = int(rec["back"][key])
    clause_fail = []
    eq_fail = []
    if sat:
        for i, c in enumerate(defects):
            if not clause_ok(c, assignment): clause_fail.append(i)
        for i, e in enumerate(equations):
            if not affine_ok(e, assignment): eq_fail.append(i)
    return {
        "decision": "SAT" if sat else "UNSAT",
        "order": order,
        "induced_width": width,
        "source_materialized_rows": int(source_rows),
        "total_materialized_rows": int(total_rows),
        "maximum_generated_scope": int(max_scope),
        "maximum_generated_table_rows": int(max_rows),
        "assignment": assignment,
        "reconstruction_pass": (not sat) or (set(assignment) == set(variables)),
        "source_validation_pass": (not sat) or (not clause_fail and not eq_fail),
        "source_clause_failure_indices": clause_fail,
        "source_equation_failure_indices": eq_fail,
    }


def verify(result):
    failures = []
    if result.get("preregistration_commit") != PREREG:
        failures.append("PREREG_DRIFT")
    g = int(result.get("g", -1))
    if g not in LADDER:
        failures.append("G_NOT_IN_FROZEN_LADDER")
    if not result.get("relevant"):
        if result.get("classification") not in {"NON_FALSIFYING_CHEAP_POLICY_ABSORPTION", "RELATION_CONTRACT_FAILURE"}:
            failures.append("INVALID_NONRELEVANT_CLASSIFICATION")
        return {"status": "PASS" if not failures else "FAIL", "g": g, "failures": failures, "classification": result.get("classification")}

    payload = result["source_payload"]
    payload_sha = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if payload_sha != result.get("source_payload_sha256"):
        failures.append("SOURCE_PAYLOAD_SHA_MISMATCH")
    if int(payload.get("g", -1)) != g:
        failures.append("SOURCE_PAYLOAD_G_MISMATCH")

    independent = replay(payload)
    sci = result.get("relation") or {}
    sep = result.get("separator") or {}
    if independent["order"] != list(map(int, payload["order"])):
        failures.append("MIN_FILL_ORDER_REPLAY_MISMATCH")
    if independent["induced_width"] != int(payload["induced_width"]):
        failures.append("MIN_FILL_WIDTH_REPLAY_MISMATCH")
    if independent["induced_width"] != int(sep.get("induced_width", -1)):
        failures.append("SEPARATOR_RESULT_WIDTH_MISMATCH")
    for key in ("decision", "source_materialized_rows", "total_materialized_rows", "maximum_generated_scope", "maximum_generated_table_rows"):
        if independent[key] != sci.get(key):
            failures.append("RELATION_REPLAY_MISMATCH:" + key)
    if independent["reconstruction_pass"] != bool(result.get("reconstruction_pass")):
        failures.append("RECONSTRUCTION_STATUS_MISMATCH")
    if independent["source_validation_pass"] != bool(result.get("source_validation_pass")):
        failures.append("SOURCE_VALIDATION_STATUS_MISMATCH")
    if independent["source_clause_failure_indices"]:
        failures.append("INDEPENDENT_SOURCE_CLAUSE_FAILURE")
    if independent["source_equation_failure_indices"]:
        failures.append("INDEPENDENT_SOURCE_EQUATION_FAILURE")

    L = int(payload["L"]); budget = int(payload["L4_budget"])
    if budget != L ** 4:
        failures.append("L4_BUDGET_MISMATCH")
    state_bound = 1 << independent["induced_width"]
    if independent["total_materialized_rows"] > budget:
        klass = "RELATION_LEDGER_EXCEEDS_L4"
    elif state_bound > budget:
        klass = "SPARSE_RELATION_LEDGER_ONLY_WITHIN_L4"
    else:
        klass = "WIDTH_AND_RELATION_LEDGER_WITHIN_L4"
    if not bool(result.get("semantic_relation_contract_pass")):
        klass = "RELATION_CONTRACT_FAILURE"
    if klass != result.get("classification"):
        failures.append("CLASSIFICATION_REPLAY_MISMATCH")

    return {
        "status": "PASS" if not failures else "FAIL",
        "g": g,
        "classification": result.get("classification"),
        "failures": failures,
        "independent": independent,
        "source_payload_sha256": payload_sha,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--result", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    result = json.loads(args.result.read_text())
    receipt = verify(result)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": receipt["status"], "g": receipt["g"], "classification": receipt.get("classification"), "failure_count": len(receipt["failures"])}, sort_keys=True))
    if receipt["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
