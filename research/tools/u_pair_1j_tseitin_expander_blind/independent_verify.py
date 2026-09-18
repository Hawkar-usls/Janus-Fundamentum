#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

SCHEMA_IN = "CNF_SKOL_SEARCH_RELATION_V1"
SCHEMA_CAND = "PROOF_CARRYING_CNF_SHANNON_INTERNAL_COVER_V1"


def canonical_bytes(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def canonical_cnf(clauses):
    out = set()
    for clause in clauses:
        lits = set(int(x) for x in clause)
        if any(-lit in lits for lit in lits):
            continue
        out.add(tuple(sorted(lits, key=lambda z: (abs(z), z < 0))))
    return tuple(sorted(out, key=lambda c: (len(c), c)))


def simplify_boundary(cnf, var, value):
    true_lit = var if value else -var
    false_lit = -true_lit
    residual = []
    for clause in cnf:
        if true_lit in clause:
            continue
        residual.append(tuple(lit for lit in clause if lit != false_lit))
    return canonical_cnf(residual)


def var_occurs(cnf, var):
    return any(var in clause or -var in clause for clause in cnf)


def normalized_position(order, pos, residual):
    while pos < len(order) and not var_occurs(residual, order[pos]):
        pos += 1
    return pos


def internal_cover(cnf, internal_vars, alpha):
    internal_set = set(internal_vars)
    inspections = 0
    for clause in cnf:
        inspections += len(clause)
        satisfied = False
        remaining = set()
        for lit in clause:
            var = abs(lit)
            if var in internal_set:
                val = alpha[var]
                if (lit > 0 and val == 1) or (lit < 0 and val == 0):
                    satisfied = True
                    break
            else:
                remaining.add(lit)
        if satisfied:
            continue
        if not any(-lit in remaining for lit in remaining):
            return False, inspections
    return True, inspections


def input_digest(rel):
    payload = {
        "schema": rel["schema"],
        "boundary_variables": [int(v) for v in rel["boundary_variables"]],
        "internal_variables": [int(v) for v in rel["internal_variables"]],
        "boundary_order": [int(v) for v in rel["boundary_order"]],
        "clauses": [list(map(int, c)) for c in canonical_cnf(rel["clauses"])],
    }
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def proof_key(node):
    rule = node.get("rule")
    if rule == "CONST":
        value = int(node["value"])
        assert value in (0, 1)
        return ("CONST", value)
    if rule == "GUARDED_ITE":
        return (
            "GUARDED_ITE",
            int(node["guard"]),
            str(node["true_child"]),
            str(node["false_child"]),
        )
    raise AssertionError(f"unsupported proof rule: {rule}")


def verify(rel, cand):
    assert rel.get("schema") == SCHEMA_IN
    assert cand.get("schema") == SCHEMA_CAND

    digest = input_digest(rel)
    assert rel["input_digest_sha256"] == digest
    assert cand["input_digest_sha256"] == digest

    boundary = tuple(int(v) for v in rel["boundary_variables"])
    internal = tuple(int(v) for v in rel["internal_variables"])
    order = tuple(int(v) for v in rel["boundary_order"])
    assert set(order) == set(boundary)
    assert len(order) == len(boundary)
    assert not (set(boundary) & set(internal))

    cnf = canonical_cnf(rel["clauses"])
    states = cand["states"]
    nodes = cand["proof_nodes"]
    assert cand["root_state"] in states

    deriv = cand["derivation"]
    assert deriv["special_function_recognizer_used"] is False
    assert deriv["graph_or_tseitin_recognizer_used"] is False
    assert deriv["source_builder_import_used"] is False
    assert deriv["reference_import_used"] is False
    assert deriv["SAT_solver_calls"] == 0
    assert deriv["generic_validity_calls"] == 0
    assert deriv["generic_tautology_calls"] == 0
    assert deriv["truth_table_enumeration"] is False

    key_to_pid = {}
    for pid, node in nodes.items():
        key = proof_key(node)
        assert key not in key_to_pid, "duplicate non-hash-consed proof node"
        key_to_pid[key] = pid
        if node["rule"] == "GUARDED_ITE":
            assert int(node["guard"]) in set(boundary)
            assert node["true_child"] in nodes
            assert node["false_child"] in nodes
            assert node["true_child"] != node["false_child"]

    visited_states = set()
    signature_to_sid = {}
    sid_signature = {}
    cover_inspections = 0
    verifier_state_visits = 0

    def expected_const(value):
        return key_to_pid[("CONST", int(value))]

    def visit(sid, pos, residual):
        nonlocal cover_inspections, verifier_state_visits
        pos = normalized_position(order, pos, residual)
        signature = (pos, residual)

        if sid in sid_signature:
            assert sid_signature[sid] == signature, "state reused for unequal residuals"
            return states[sid]["witness_roots"]
        if signature in signature_to_sid:
            assert signature_to_sid[signature] == sid, "duplicate residual state not shared"

        sid_signature[sid] = signature
        signature_to_sid[signature] = sid
        visited_states.add(sid)
        verifier_state_visits += 1

        state = states[sid]
        roots = state["witness_roots"]
        assert set(roots) == {str(v) for v in internal}
        for pid in roots.values():
            assert pid in nodes

        if state["kind"] == "LEAF":
            assert int(state["order_pos"]) == pos
            assert state["justification"] == "INTERNAL_COVER_WITNESS"
            alpha = {int(k): int(v) for k, v in state["alpha"].items()}
            assert set(alpha) == set(internal)
            assert all(v in (0, 1) for v in alpha.values())
            assert sum(alpha.values()) in (0, 1), "leaf alpha outside frozen probe set"
            ok, inspected = internal_cover(residual, internal, alpha)
            cover_inspections += inspected
            assert ok, "leaf INTERNAL_COVER_WITNESS failed"
            for v in internal:
                assert roots[str(v)] == expected_const(alpha[v])
            return roots

        assert state["kind"] == "BRANCH"
        assert int(state["order_pos"]) == pos
        assert pos < len(order), "branch after boundary exhaustion"
        guard = int(state["guard_var"])
        assert guard == order[pos], "non-frozen or non-next guard"
        false_child = state["false_child"]
        true_child = state["true_child"]
        assert false_child in states and true_child in states

        false_residual = simplify_boundary(residual, guard, 0)
        true_residual = simplify_boundary(residual, guard, 1)
        false_roots = visit(false_child, pos + 1, false_residual)
        true_roots = visit(true_child, pos + 1, true_residual)

        for v in internal:
            t = true_roots[str(v)]
            f = false_roots[str(v)]
            if t == f:
                expected = t
            else:
                expected = key_to_pid[("GUARDED_ITE", guard, t, f)]
            assert roots[str(v)] == expected
        return roots

    start = time.perf_counter_ns()
    root_roots = visit(cand["root_state"], 0, cnf)
    assert root_roots == cand["root_witness"]
    assert visited_states == set(states), "unreachable candidate states present"

    reachable_proof = set()
    stack = list(cand["root_witness"].values())
    while stack:
        pid = stack.pop()
        if pid in reachable_proof:
            continue
        reachable_proof.add(pid)
        node = nodes[pid]
        if node["rule"] == "GUARDED_ITE":
            stack.extend([node["true_child"], node["false_child"]])
    assert reachable_proof == set(nodes), "unreachable proof nodes present"

    B = len(boundary)
    state_envelope = 8 * B * B
    proof_envelope = 8 * B * B * B
    assert len(states) <= state_envelope
    assert len(nodes) <= proof_envelope

    elapsed = time.perf_counter_ns() - start
    return {
        "verdict": "PASS_INDEPENDENT_TSEITIN_EXPANDER_PROOF_CARRYING_WITNESS",
        "T_verify_ns": elapsed,
        "verifier_state_visits": verifier_state_visits,
        "verifier_proof_node_visits": len(reachable_proof),
        "leaf_cover_clause_literal_inspections": cover_inspections,
        "domain_verified": "EXACT_COMPLEMENTARY_BOUNDARY_BRANCH_COVER_TO_INTERNAL_COVER_LEAVES",
        "reference_DAG_read": False,
        "source_builder_read": False,
        "candidate_constructor_imported": False,
        "semantic_truth_table_used": False,
        "generic_validity_used": False,
        "generic_tautology_used": False,
    }


def main(relpath, candpath, outpath):
    rel = json.loads(Path(relpath).read_text(encoding="utf-8"))
    cand = json.loads(Path(candpath).read_text(encoding="utf-8"))
    result = verify(rel, cand)
    Path(outpath).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("usage: independent_verify.py INPUT.json CANDIDATE.json OUT.json")
    main(sys.argv[1], sys.argv[2], sys.argv[3])
