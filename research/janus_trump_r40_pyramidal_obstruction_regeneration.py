#!/usr/bin/env python3
"""R40 bounded single-generation regeneration from the sealed R39 q-Horn obstruction.

This gate is intentionally finite and preregistered:
  - exactly 8 children,
  - exactly one Davis-Putnam variable elimination per child,
  - no recursive generation,
  - exact deterministic resource ledger,
  - polynomial terminal recognizers: 2-CNF, Horn, dual-Horn, renamable-Horn,
  - brute-force SAT only as a finite semantic control, never as algorithm authority.

Davis-Putnam elimination preserves satisfiability, not model identity.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

EXPECTED_PARENT_SHA256 = "3361190b3fe683457061662dd9244cd37ca79283828139666d35b01b11d2fe95"
FROZEN_VARIABLES = [2, 6, 14, 15, 18, 21, 22, 23]


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_json(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def clause_key(clause):
    return (len(clause), tuple((abs(x), 0 if x > 0 else 1) for x in clause))


def canonical_clause(clause):
    return tuple(sorted(set(clause), key=lambda x: (abs(x), 0 if x > 0 else 1)))


def canonical_formula(clauses):
    unique = set()
    for clause in clauses:
        s = set(clause)
        if any(-lit in s for lit in s):
            continue
        unique.add(canonical_clause(clause))
    return [list(c) for c in sorted(unique, key=clause_key)]


def variables_of(clauses):
    return sorted({abs(lit) for clause in clauses for lit in clause})


def davis_putnam_eliminate(clauses, variable):
    positive = [list(c) for c in clauses if variable in c]
    negative = [list(c) for c in clauses if -variable in c]
    rest = canonical_formula([c for c in clauses if variable not in c and -variable not in c])
    rest_set = {tuple(c) for c in rest}

    raw_resolvents = []
    tautological = 0
    for p in positive:
        p_tail = set(p)
        p_tail.remove(variable)
        for n in negative:
            n_tail = set(n)
            n_tail.remove(-variable)
            resolvent = p_tail | n_tail
            if any(-lit in resolvent for lit in resolvent):
                tautological += 1
                continue
            raw_resolvents.append(list(resolvent))

    unique_resolvents = canonical_formula(raw_resolvents)
    added_resolvents = [c for c in unique_resolvents if tuple(c) not in rest_set]
    output = canonical_formula(rest + unique_resolvents)

    ledger = {
        "positive_parent_count": len(positive),
        "negative_parent_count": len(negative),
        "resolvent_pairs_attempted": len(positive) * len(negative),
        "tautological_resolvents_dropped": tautological,
        "unique_resolvents_generated": len(unique_resolvents),
        "unique_resolvents_added": len(added_resolvents),
        "output_clause_count": len(output),
        "output_literal_count": sum(len(c) for c in output),
        "remaining_variable_count": len(variables_of(output)),
    }
    return output, ledger


def is_2cnf(clauses):
    return all(len(c) <= 2 for c in clauses)


def is_horn(clauses):
    return all(sum(lit > 0 for lit in c) <= 1 for c in clauses)


def is_dual_horn(clauses):
    return all(sum(lit < 0 for lit in c) <= 1 for c in clauses)


def renamable_horn_2sat(clauses):
    """Exact polynomial recognizer via the standard flip-variable 2-SAT reduction."""
    variables = variables_of(clauses)
    index = {v: i for i, v in enumerate(variables)}
    n = len(variables)
    graph = [[] for _ in range(2 * n)]
    reverse = [[] for _ in range(2 * n)]

    def node(v, value):
        return 2 * index[v] + int(bool(value))

    def imply(a, b):
        graph[a].append(b)
        reverse[b].append(a)

    for clause in clauses:
        for i in range(len(clause)):
            for j in range(i + 1, len(clause)):
                left, right = clause[i], clause[j]
                lv, lval = abs(left), left > 0
                rv, rval = abs(right), right > 0
                imply(node(lv, not lval), node(rv, rval))
                imply(node(rv, not rval), node(lv, lval))

    seen = [False] * (2 * n)
    order = []

    def dfs(u):
        seen[u] = True
        for w in graph[u]:
            if not seen[w]:
                dfs(w)
        order.append(u)

    for u in range(2 * n):
        if not seen[u]:
            dfs(u)

    component = [-1] * (2 * n)

    def rdfs(u, cid):
        component[u] = cid
        for w in reverse[u]:
            if component[w] == -1:
                rdfs(w, cid)

    cid = 0
    for u in reversed(order):
        if component[u] == -1:
            rdfs(u, cid)
            cid += 1

    for v in variables:
        if component[node(v, False)] == component[node(v, True)]:
            return False
    return True


def exact_finite_sat_control(clauses):
    variables = variables_of(clauses)
    if len(variables) > 13:
        raise AssertionError("FINITE_CONTROL_VARIABLE_BOUND_EXCEEDED")
    for bits in itertools.product((False, True), repeat=len(variables)):
        assignment = dict(zip(variables, bits))
        if all(any(assignment[abs(lit)] if lit > 0 else not assignment[abs(lit)] for lit in c)
               for c in clauses):
            witness = [[v, bool(assignment[v])] for v in variables]
            return True, sha256_json(witness)
    return False, None


def classify_terminals(clauses):
    if any(len(c) == 0 for c in clauses):
        return ["EMPTY_CLAUSE_UNSAT"]
    if len(clauses) == 0:
        return ["EMPTY_FORMULA_SAT"]
    hits = []
    if is_2cnf(clauses):
        hits.append("2CNF")
    if is_horn(clauses):
        hits.append("HORN")
    if is_dual_horn(clauses):
        hits.append("DUAL_HORN")
    if renamable_horn_2sat(clauses):
        hits.append("RENAMABLE_HORN")
    return hits


def main():
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / "research" / "JANUS_TRUMP_R39_QHORN_SEALED_INPUT_2026-09-03.json").read_text())
    parent = source["clauses"]
    parent_sha = sha256_json(parent)
    if parent_sha != EXPECTED_PARENT_SHA256 or parent_sha != source["canonical_formula_sha256"]:
        raise AssertionError(f"PARENT_HASH_MISMATCH:{parent_sha}")

    parent_sat, parent_witness_hash = exact_finite_sat_control(parent)
    children = []
    for variable in FROZEN_VARIABLES:
        child, ledger = davis_putnam_eliminate(parent, variable)
        if variable in variables_of(child):
            raise AssertionError(f"ELIMINATED_VARIABLE_SURVIVED:{variable}")
        child_sat, witness_hash = exact_finite_sat_control(child)
        if child_sat != parent_sat:
            raise AssertionError(f"SAT_EQUIVALENCE_CONTROL_MISMATCH:{variable}")
        terminals = classify_terminals(child)
        children.append({
            "child_id": f"DP_ELIM_{variable}",
            "eliminated_variable": variable,
            "formula_sha256": sha256_json(child),
            "resource_ledger": ledger,
            "audited_terminal_hits": terminals,
            "finite_semantic_control_sat": child_sat,
            "finite_semantic_control_witness_sha256": witness_hash,
            "decisive": bool(terminals),
        })

    decisive = [c["child_id"] for c in children if c["decisive"]]
    total_pairs = sum(c["resource_ledger"]["resolvent_pairs_attempted"] for c in children)
    total_output_literals = sum(c["resource_ledger"]["output_literal_count"] for c in children)
    result = {
        "schema": "janus.trump.r40.pyramidal_obstruction_regeneration.result.v1",
        "date": "2026-09-03",
        "status": "REGENERATED_AND_DECISIVE" if decisive else "REGENERATED_STILL_OPEN",
        "parent_formula_sha256": parent_sha,
        "parent_finite_semantic_control_sat": parent_sat,
        "parent_finite_semantic_control_witness_sha256": parent_witness_hash,
        "generation_depth": 1,
        "frozen_child_count": len(FROZEN_VARIABLES),
        "children": children,
        "decisive_children": decisive,
        "aggregate_charged_work": {
            "resolvent_pairs_attempted": total_pairs,
            "child_output_literals_materialized": total_output_literals,
        },
        "verified_delta": {
            "statement": "No preregistered single-variable Davis-Putnam child reaches 2CNF, Horn, dual-Horn, or renamable-Horn."
            if not decisive else
            "At least one preregistered single-variable Davis-Putnam child reaches an audited polynomial terminal.",
            "verified": True,
            "replay_match_required_for_regeneration": True,
        },
        "proof_authority_delta": 0,
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
