#!/usr/bin/env python3
"""R42 uniform answer-blind min-product Davis-Putnam controller.

The selector is frozen before the trajectory:
  score(v) = (positive_occurrences(v) * negative_occurrences(v),
              total_occurrences(v),
              variable_id)
and the lexicographic minimum is eliminated.

Selection counts are computed in one literal scan per step. No candidate child
formula is evaluated for selection. Davis-Putnam preserves SAT, not models.
"""
from __future__ import annotations

import json
from pathlib import Path

import janus_trump_r40_pyramidal_obstruction_regeneration as r40

MAX_CLAUSES = 2000
MAX_TOTAL_RESOLVENT_PAIRS = 200000
MAX_ELIMINATIONS = 13


def select_variable(clauses):
    counts = {v: [0, 0] for v in r40.variables_of(clauses)}
    scanned = 0
    for clause in clauses:
        for lit in clause:
            scanned += 1
            if lit > 0:
                counts[lit][0] += 1
            else:
                counts[-lit][1] += 1
    scored = []
    for v, (p, n) in counts.items():
        scored.append((p * n, p + n, v, p, n))
    if not scored:
        return None, scanned
    return min(scored), scanned


def solve_2cnf_scc(clauses):
    """Exact 2-SAT decision via implication-graph SCC."""
    if any(len(c) == 0 for c in clauses):
        return False
    if not all(len(c) <= 2 for c in clauses):
        raise AssertionError("NOT_2CNF")
    variables = r40.variables_of(clauses)
    index = {v: i for i, v in enumerate(variables)}
    graph = [[] for _ in range(2 * len(variables))]
    reverse = [[] for _ in range(2 * len(variables))]

    def node(lit):
        return 2 * index[abs(lit)] + (1 if lit > 0 else 0)

    def edge(a, b):
        graph[a].append(b)
        reverse[b].append(a)

    for clause in clauses:
        if len(clause) == 1:
            a = clause[0]
            edge(node(-a), node(a))
        elif len(clause) == 2:
            a, b = clause
            edge(node(-a), node(b))
            edge(node(-b), node(a))

    seen = [False] * len(graph)
    order = []

    def dfs(u):
        seen[u] = True
        for w in graph[u]:
            if not seen[w]:
                dfs(w)
        order.append(u)

    for u in range(len(graph)):
        if not seen[u]:
            dfs(u)

    component = [-1] * len(graph)

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
        if component[node(v)] == component[node(-v)]:
            return False
    return True


def main():
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / "research" / "JANUS_TRUMP_R39_QHORN_SEALED_INPUT_2026-09-03.json").read_text())
    parent_raw = source["clauses"]
    parent_sha = r40.sha256_json(parent_raw)
    if parent_sha != r40.EXPECTED_PARENT_SHA256:
        raise AssertionError(f"PARENT_HASH_MISMATCH:{parent_sha}")

    current = r40.canonical_formula(parent_raw)
    parent_sat, parent_witness_hash = r40.exact_finite_sat_control(current)
    trajectory = []
    cumulative_pairs = 0
    cumulative_selector_scans = 0
    peak_clauses = len(current)
    peak_literals = sum(len(c) for c in current)
    terminal_hits = r40.classify_terminals(current)
    terminal_decision = None
    stop_reason = None

    for step in range(1, MAX_ELIMINATIONS + 1):
        if terminal_hits:
            stop_reason = "POLYNOMIAL_TERMINAL_REACHED"
            break

        score, scanned = select_variable(current)
        cumulative_selector_scans += scanned
        if score is None:
            terminal_hits = ["EMPTY_FORMULA_SAT"]
            stop_reason = "POLYNOMIAL_TERMINAL_REACHED"
            break

        product, occurrences, variable, positive, negative = score
        before_clauses = len(current)
        before_literals = sum(len(c) for c in current)
        child, ledger = r40.davis_putnam_eliminate(current, variable)
        cumulative_pairs += ledger["resolvent_pairs_attempted"]
        after_clauses = len(child)
        after_literals = sum(len(c) for c in child)
        peak_clauses = max(peak_clauses, before_clauses, after_clauses)
        peak_literals = max(peak_literals, before_literals, after_literals)

        child_sat, child_witness_hash = r40.exact_finite_sat_control(child)
        if child_sat != parent_sat:
            raise AssertionError(f"SAT_EQUIVALENCE_CONTROL_MISMATCH_AT_STEP_{step}")

        terminal_hits = r40.classify_terminals(child)
        trajectory.append({
            "step": step,
            "selected_variable": variable,
            "selector_score": {
                "positive_x_negative": product,
                "total_occurrences": occurrences,
                "positive_occurrences": positive,
                "negative_occurrences": negative,
            },
            "selector_literals_scanned": scanned,
            "input_clause_count": before_clauses,
            "input_literal_count": before_literals,
            "output_clause_count": after_clauses,
            "output_literal_count": after_literals,
            "resolvent_pairs_attempted": ledger["resolvent_pairs_attempted"],
            "cumulative_resolvent_pairs_attempted": cumulative_pairs,
            "tautological_resolvents_dropped": ledger["tautological_resolvents_dropped"],
            "unique_resolvents_added": ledger["unique_resolvents_added"],
            "output_formula_sha256": r40.sha256_json(child),
            "finite_semantic_control_sat": child_sat,
            "finite_semantic_control_witness_sha256": child_witness_hash,
            "audited_terminal_hits": terminal_hits,
        })
        current = child

        if len(current) > MAX_CLAUSES or cumulative_pairs > MAX_TOTAL_RESOLVENT_PAIRS:
            stop_reason = "RESOURCE_BOUND_HIT"
            break
        if terminal_hits:
            stop_reason = "POLYNOMIAL_TERMINAL_REACHED"
            break

    if stop_reason is None:
        stop_reason = "MAX_ELIMINATIONS_REACHED"

    if stop_reason == "POLYNOMIAL_TERMINAL_REACHED" and "2CNF" in terminal_hits:
        decision = solve_2cnf_scc(current)
        if decision != parent_sat:
            raise AssertionError("TERMINAL_2SAT_DECISION_MISMATCH_WITH_FINITE_CONTROL")
        terminal_decision = {
            "solver": "EXACT_2SAT_IMPLICATION_SCC",
            "decision": "SAT" if decision else "UNSAT",
            "finite_control_agrees": True,
        }

    result = {
        "schema": "janus.trump.r42.uniform_minproduct_dp_controller.result.v1",
        "date": "2026-09-03",
        "controller_id": "UNIFORM_MINPRODUCT_DP_V1",
        "parent_formula_sha256": parent_sha,
        "status": (
            "UNIFORM_CONTROLLER_REACHED_POLYNOMIAL_TERMINAL"
            if stop_reason == "POLYNOMIAL_TERMINAL_REACHED" and terminal_decision is not None
            else stop_reason
        ),
        "trajectory": trajectory,
        "selected_variable_sequence": [x["selected_variable"] for x in trajectory],
        "terminal_hits": terminal_hits,
        "terminal_formula_sha256": r40.sha256_json(current),
        "terminal_decision": terminal_decision,
        "charged_work": {
            "total_eliminations": len(trajectory),
            "total_selector_literals_scanned": cumulative_selector_scans,
            "total_resolvent_pairs_attempted": cumulative_pairs,
            "peak_clause_count": peak_clauses,
            "peak_literal_count": peak_literals,
        },
        "finite_semantic_control": {
            "parent_sat": parent_sat,
            "parent_witness_sha256": parent_witness_hash,
            "algorithm_authority": False,
        },
        "scientific_interpretation": {
            "fixed_answer_blind_controller_closed_this_sealed_fixpoint": terminal_decision is not None,
            "universal_coverage_proved": False,
            "worst_case_polynomial_bound_proved": False,
            "decision_completeness_proved_for_all_3cnf": False,
            "law": "LOCAL_FIXED_CONTROLLER_SUCCESS != UNIVERSAL_POLYNOMIAL_RESOLVER",
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
