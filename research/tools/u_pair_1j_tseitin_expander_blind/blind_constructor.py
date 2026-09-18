#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

SCHEMA_IN = "CNF_SKOL_SEARCH_RELATION_V1"
SCHEMA_OUT = "PROOF_CARRYING_CNF_SHANNON_INTERNAL_COVER_V1"
PER_INSTANCE_TIMEOUT_NS = 120 * 1_000_000_000


def canonical_cnf(clauses):
    out = set()
    for clause in clauses:
        lits = set(int(x) for x in clause)
        if any(-lit in lits for lit in lits):
            continue
        out.add(tuple(sorted(lits, key=lambda z: (abs(z), z < 0))))
    return tuple(sorted(out, key=lambda c: (len(c), c)))


def canonical_bytes(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


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


def boundary_tautology_after_internal_assignment(clause, internal_set, alpha):
    remaining = set()
    for lit in clause:
        var = abs(lit)
        if var in internal_set:
            val = alpha[var]
            if (lit > 0 and val == 1) or (lit < 0 and val == 0):
                return True
        else:
            remaining.add(lit)
    return any(-lit in remaining for lit in remaining)


def internal_cover(cnf, internal_vars, alpha):
    internal_set = set(internal_vars)
    inspections = 0
    for clause in cnf:
        inspections += len(clause)
        if not boundary_tautology_after_internal_assignment(
            clause, internal_set, alpha
        ):
            return False, inspections
    return True, inspections


class ObservedBlowup(RuntimeError):
    def __init__(self, kind, observed, cap):
        super().__init__(f"{kind} envelope exceeded: {observed}>{cap}")
        self.kind = kind
        self.observed = observed
        self.cap = cap


class ResourceLimit(RuntimeError):
    pass


class DomainFailure(RuntimeError):
    pass


def synthesize(rel):
    if rel.get("schema") != SCHEMA_IN:
        raise ValueError("unexpected input schema")

    boundary = tuple(int(v) for v in rel["boundary_variables"])
    internal = tuple(int(v) for v in rel["internal_variables"])
    order = tuple(int(v) for v in rel["boundary_order"])
    if set(order) != set(boundary) or len(order) != len(boundary):
        raise ValueError("boundary_order must be a permutation of boundary_variables")
    if set(boundary) & set(internal):
        raise ValueError("boundary/internal overlap")

    cnf = canonical_cnf(rel["clauses"])
    all_vars = {abs(lit) for clause in cnf for lit in clause}
    if not all_vars <= set(boundary) | set(internal):
        raise ValueError("undeclared variable in CNF")

    B = len(boundary)
    state_cap = 8 * B * B
    proof_cap = 8 * B * B * B

    proof_nodes = {}
    proof_hashcons = {}
    states = {}
    memo = {}
    next_proof = 0
    next_state = 0
    memo_hits = 0
    leaf_cover_probes = 0
    leaf_cover_inspections = 0
    start_ns = time.perf_counter_ns()

    def check_time():
        if time.perf_counter_ns() - start_ns > PER_INSTANCE_TIMEOUT_NS:
            raise ResourceLimit("per-instance timeout")

    def intern_const(value):
        nonlocal next_proof
        key = ("CONST", int(value))
        if key in proof_hashcons:
            return proof_hashcons[key]
        if len(proof_nodes) + 1 > proof_cap:
            raise ObservedBlowup("proof_DAG_nodes", len(proof_nodes) + 1, proof_cap)
        pid = f"p{next_proof}"
        next_proof += 1
        proof_nodes[pid] = {"rule": "CONST", "value": int(value)}
        proof_hashcons[key] = pid
        return pid

    def intern_ite(guard, true_child, false_child):
        nonlocal next_proof
        if true_child == false_child:
            return true_child
        key = ("GUARDED_ITE", int(guard), true_child, false_child)
        if key in proof_hashcons:
            return proof_hashcons[key]
        if len(proof_nodes) + 1 > proof_cap:
            raise ObservedBlowup("proof_DAG_nodes", len(proof_nodes) + 1, proof_cap)
        pid = f"p{next_proof}"
        next_proof += 1
        proof_nodes[pid] = {
            "rule": "GUARDED_ITE",
            "guard": int(guard),
            "true_child": true_child,
            "false_child": false_child,
        }
        proof_hashcons[key] = pid
        return pid

    def candidate_alphas():
        zero = {v: 0 for v in internal}
        yield zero
        for chosen in internal:
            alpha = dict(zero)
            alpha[chosen] = 1
            yield alpha

    def normalized_position(pos, residual):
        while pos < len(order) and not var_occurs(residual, order[pos]):
            pos += 1
        return pos

    def build_state(pos, residual):
        nonlocal next_state, memo_hits, leaf_cover_probes, leaf_cover_inspections
        check_time()
        pos = normalized_position(pos, residual)
        key = (pos, residual)
        if key in memo:
            memo_hits += 1
            return memo[key]

        if len(states) + len(memo) + 1 > state_cap * 2:
            # Defensive pre-check before deep recursion; the authoritative state
            # envelope is enforced at actual state creation below.
            check_time()

        for alpha in candidate_alphas():
            leaf_cover_probes += 1
            ok, inspected = internal_cover(residual, internal, alpha)
            leaf_cover_inspections += inspected
            if ok:
                if len(states) + 1 > state_cap:
                    raise ObservedBlowup(
                        "residual_states", len(states) + 1, state_cap
                    )
                sid = f"q{next_state}"
                next_state += 1
                roots = {str(v): intern_const(alpha[v]) for v in internal}
                states[sid] = {
                    "kind": "LEAF",
                    "order_pos": pos,
                    "alpha": {str(v): int(alpha[v]) for v in internal},
                    "justification": "INTERNAL_COVER_WITNESS",
                    "witness_roots": roots,
                }
                memo[key] = sid
                return sid

        if pos >= len(order):
            raise DomainFailure(
                "all boundary variables exhausted without INTERNAL_COVER_WITNESS"
            )

        guard = order[pos]
        false_residual = simplify_boundary(residual, guard, 0)
        true_residual = simplify_boundary(residual, guard, 1)
        false_child = build_state(pos + 1, false_residual)
        true_child = build_state(pos + 1, true_residual)

        if len(states) + 1 > state_cap:
            raise ObservedBlowup("residual_states", len(states) + 1, state_cap)

        sid = f"q{next_state}"
        next_state += 1
        roots = {}
        false_roots = states[false_child]["witness_roots"]
        true_roots = states[true_child]["witness_roots"]
        for v in internal:
            roots[str(v)] = intern_ite(
                guard, true_roots[str(v)], false_roots[str(v)]
            )
        states[sid] = {
            "kind": "BRANCH",
            "order_pos": pos,
            "guard_var": guard,
            "false_child": false_child,
            "true_child": true_child,
            "witness_roots": roots,
        }
        memo[key] = sid
        return sid

    root_state = build_state(0, cnf)
    elapsed = time.perf_counter_ns() - start_ns
    root_witness = dict(states[root_state]["witness_roots"])
    candidate = {
        "schema": SCHEMA_OUT,
        "input_digest_sha256": rel["input_digest_sha256"],
        "root_state": root_state,
        "root_witness": root_witness,
        "states": states,
        "proof_nodes": proof_nodes,
        "derivation": {
            "algorithm": "GENERIC_CLAUSEWISE_SHANNON_INTERNAL_COVER_SYNTHESIS_V1",
            "allowed_rules_used": sorted(
                set(node["rule"] for node in proof_nodes.values())
                | {"INTERNAL_COVER_WITNESS"}
            ),
            "special_function_recognizer_used": False,
            "graph_or_tseitin_recognizer_used": False,
            "source_builder_import_used": False,
            "reference_import_used": False,
            "SAT_solver_calls": 0,
            "generic_validity_calls": 0,
            "generic_tautology_calls": 0,
            "truth_table_enumeration": False,
        },
        "metrics": {
            "B": B,
            "internal_witness_count": len(internal),
            "cnf_clause_count": len(cnf),
            "cnf_literal_occurrences": sum(len(c) for c in cnf),
            "T_synth_ns": elapsed,
            "residual_states": len(states),
            "memo_hits": memo_hits,
            "leaf_cover_probes": leaf_cover_probes,
            "leaf_cover_clause_literal_inspections": leaf_cover_inspections,
            "proof_DAG_nodes": len(proof_nodes),
            "proof_DAG_bytes": len(
                canonical_bytes({"roots": root_witness, "nodes": proof_nodes})
            ),
            "candidate_bytes": len(
                canonical_bytes(
                    {
                        "root_state": root_state,
                        "states": states,
                        "proof_nodes": proof_nodes,
                    }
                )
            ),
            "max_live_shared_nodes": len(proof_nodes),
            "residual_state_envelope": state_cap,
            "proof_DAG_node_envelope": proof_cap,
        },
    }
    return candidate


def main(inp, out):
    rel = json.loads(Path(inp).read_text(encoding="utf-8"))
    try:
        candidate = synthesize(rel)
        Path(out).write_text(
            json.dumps(candidate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({"verdict": "CANDIDATE_FROZEN", "metrics": candidate["metrics"]}, sort_keys=True))
    except ObservedBlowup as exc:
        result = {
            "schema": "PROOF_CARRYING_CNF_SHANNON_OUTCOME_V1",
            "verdict": "FAIL_PROOF_DAG_BLOWUP",
            "kind": exc.kind,
            "observed": exc.observed,
            "cap": exc.cap,
        }
        Path(out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(result, sort_keys=True))
    except ResourceLimit as exc:
        result = {
            "schema": "PROOF_CARRYING_CNF_SHANNON_OUTCOME_V1",
            "verdict": "UNKNOWN_RESOURCE_LIMIT",
            "reason": str(exc),
        }
        Path(out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(result, sort_keys=True))
    except DomainFailure as exc:
        result = {
            "schema": "PROOF_CARRYING_CNF_SHANNON_OUTCOME_V1",
            "verdict": "FAIL_DOMAIN_DROPPED",
            "reason": str(exc),
        }
        Path(out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: blind_constructor.py INPUT.json OUT.json")
    main(sys.argv[1], sys.argv[2])
