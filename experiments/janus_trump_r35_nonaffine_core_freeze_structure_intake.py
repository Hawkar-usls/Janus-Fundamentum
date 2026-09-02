from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34

Clause = Tuple[int, ...]
Formula = Tuple[Clause, ...]


def canonical_json_sha256(obj) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def primal_graph(formula: Formula) -> Dict[int, Set[int]]:
    graph: Dict[int, Set[int]] = {v: set() for v in r33.variables(formula)}
    for clause in formula:
        vs = sorted({abs(l) for l in clause})
        for i, u in enumerate(vs):
            for v in vs[i + 1 :]:
                graph[u].add(v)
                graph[v].add(u)
    return graph


def connected_components(graph: Dict[int, Set[int]]) -> List[List[int]]:
    seen: Set[int] = set()
    out: List[List[int]] = []
    for start in sorted(graph):
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        comp = []
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in sorted(graph[u], reverse=True):
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        out.append(sorted(comp))
    return out


def articulation_points(graph: Dict[int, Set[int]]) -> List[int]:
    timer = 0
    tin: Dict[int, int] = {}
    low: Dict[int, int] = {}
    result: Set[int] = set()

    def dfs(u: int, parent: int | None) -> None:
        nonlocal timer
        timer += 1
        tin[u] = low[u] = timer
        children = 0
        for v in sorted(graph[u]):
            if v == parent:
                continue
            if v in tin:
                low[u] = min(low[u], tin[v])
                continue
            dfs(v, u)
            low[u] = min(low[u], low[v])
            if parent is not None and low[v] >= tin[u]:
                result.add(u)
            children += 1
        if parent is None and children > 1:
            result.add(u)

    for u in sorted(graph):
        if u not in tin:
            dfs(u, None)
    return sorted(result)


def min_fill_width_probe(graph: Dict[int, Set[int]]) -> dict:
    g = {u: set(vs) for u, vs in graph.items()}
    order = []
    width = 0
    fill_edges = 0
    while g:
        candidates = []
        for u in sorted(g):
            nbrs = sorted(g[u])
            missing = 0
            for i, a in enumerate(nbrs):
                for b in nbrs[i + 1 :]:
                    if b not in g[a]:
                        missing += 1
            candidates.append((missing, len(nbrs), u))
        missing, degree, u = min(candidates)
        nbrs = sorted(g[u])
        width = max(width, len(nbrs))
        for i, a in enumerate(nbrs):
            for b in nbrs[i + 1 :]:
                if b not in g[a]:
                    g[a].add(b)
                    g[b].add(a)
                    fill_edges += 1
        for v in nbrs:
            g[v].discard(u)
        del g[u]
        order.append(u)
    return {"heuristic_width": width, "fill_edges_added": fill_edges, "order": order, "authority": "NON_AUTHORITATIVE_UPPER_BOUND_PROBE"}


def affine_bundle_coverage(formula: Formula) -> dict:
    groups: Dict[Tuple[int, ...], List[Clause]] = defaultdict(list)
    for clause in formula:
        groups[tuple(sorted(abs(l) for l in clause))].append(clause)
    complete_groups = []
    covered = 0
    for vs in sorted(groups):
        clauses = groups[vs]
        k = len(vs)
        if not k or len(clauses) != (1 << (k - 1)):
            continue
        falsifying = set()
        parities = set()
        for clause in clauses:
            sign_by_var = {abs(l): l for l in clause}
            if tuple(sorted(sign_by_var)) != vs:
                break
            bits = tuple(1 if sign_by_var[v] < 0 else 0 for v in vs)
            falsifying.add(bits)
            parities.add(sum(bits) & 1)
        else:
            if len(falsifying) == len(clauses) and len(parities) == 1:
                covered += len(clauses)
                complete_groups.append({"vars": list(vs), "clause_count": len(clauses), "equation_rhs": next(iter(parities)) ^ 1})
    return {
        "complete_group_count": len(complete_groups),
        "covered_clauses": covered,
        "total_clauses": len(formula),
        "coverage_fraction": covered / len(formula) if formula else 1.0,
        "groups": complete_groups,
    }


def structure_intake(formula: Formula) -> dict:
    graph = primal_graph(formula)
    degrees = Counter(len(nbrs) for nbrs in graph.values())
    occurrence = {}
    for v in r33.variables(formula):
        pos = sum(1 for clause in formula if v in clause)
        neg = sum(1 for clause in formula if -v in clause)
        occurrence[str(v)] = {"positive": pos, "negative": neg, "total": pos + neg}

    overlap = Counter()
    for i, a in enumerate(formula):
        av = {abs(l) for l in a}
        for b in formula[i + 1 :]:
            overlap[len(av & {abs(l) for l in b})] += 1

    horn = sum(1 for c in formula if sum(1 for l in c if l > 0) <= 1)
    two = sum(1 for c in formula if len(c) <= 2)
    components = connected_components(graph)
    return {
        "variable_occurrences": occurrence,
        "primal_graph_degree_histogram": {str(k): v for k, v in sorted(degrees.items())},
        "primal_graph_edge_count": sum(len(n) for n in graph.values()) // 2,
        "connected_components": components,
        "connected_component_sizes": [len(c) for c in components],
        "articulation_points": articulation_points(graph),
        "clause_pair_variable_overlap_histogram": {str(k): v for k, v in sorted(overlap.items())},
        "Horn_clause_count": horn,
        "Horn_clause_fraction": horn / len(formula) if formula else 1.0,
        "2CNF_clause_count": two,
        "2CNF_clause_fraction": two / len(formula) if formula else 1.0,
        "affine_bundle_coverage": affine_bundle_coverage(formula),
        "min_fill_probe": min_fill_width_probe(graph),
    }


def run_audit() -> dict:
    source = r33.deterministic_random_3cnf(33004, n=24, ratio=4.2)
    reduced = r33.simplify(source)
    core = r33.canonical_formula(reduced["final_formula"])
    routed = r34.apply_extended_policy(source)

    expected = (
        list(r33.measure(source)) == [101, 303, 24]
        and reduced["final_measure"] == [98, 300, 23]
        and reduced["total_rule_applications"] == 3
        and routed["terminal"] == "STALLED_NONAFFINE_CORE"
        and routed.get("recognition", {}).get("reason") == "INCOMPLETE_PARITY_BUNDLE"
    )
    verdict = "R35_NONAFFINE_CORE_FROZEN__STRUCTURE_INTAKE_ONLY" if expected else "R35_FAIL_INTEGRITY"

    core_list = [list(c) for c in core]
    source_list = [list(c) for c in source]
    return {
        "schema": "JANUS_TRUMP_R35_NONAFFINE_CORE_FREEZE_STRUCTURE_INTAKE_RESULT",
        "version": "1.0",
        "date": "2026-09-02",
        "verdict": verdict,
        "frozen_selector": {"seed": 33004, "n": 24, "ratio": 4.2},
        "source": {
            "measure": list(r33.measure(source)),
            "canonical_clause_list_sha256": canonical_json_sha256(source_list),
            "clauses": source_list,
        },
        "R33_reduction": {
            "final_measure": reduced["final_measure"],
            "total_rule_applications": reduced["total_rule_applications"],
            "rule_counts": reduced["rule_counts"],
            "total_certificate_bytes": reduced["total_certificate_bytes"],
            "total_check_operation_count_upper_ledger": reduced["total_check_operation_count_upper_ledger"],
        },
        "R34_route": {
            "terminal": routed["terminal"],
            "recognition_reason": routed.get("recognition", {}).get("reason"),
            "failed_vars": routed.get("recognition", {}).get("failed_vars"),
        },
        "frozen_nonaffine_core": {
            "measure": list(r33.measure(core)),
            "canonical_clause_list_sha256": canonical_json_sha256(core_list),
            "clauses": core_list,
        },
        "structure_intake": structure_intake(core),
        "candidate_firewall": {
            "new_reduction_rule_added": False,
            "new_terminal_solver_added": False,
            "external_SAT_solver_used": False,
            "assignment_enumeration_used": False,
            "semantic_redundancy_oracle_used": False,
        },
        "captain_verdict": {
            "answer": "CORE_FROZEN_BEFORE_EXPLANATION",
            "instruction": "TOPA/Captain may now choose at most one R35B mechanism from the exact residual. Any structural parameter must carry its total complexity dependence; FPT alone is not P.",
        },
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }


def self_test() -> None:
    d = run_audit()
    assert d["verdict"] == "R35_NONAFFINE_CORE_FROZEN__STRUCTURE_INTAKE_ONLY"
    assert d["source"]["measure"] == [101, 303, 24]
    assert d["frozen_nonaffine_core"]["measure"] == [98, 300, 23]
    assert d["R33_reduction"]["total_rule_applications"] == 3
    assert d["R34_route"]["terminal"] == "STALLED_NONAFFINE_CORE"
    assert len(d["frozen_nonaffine_core"]["clauses"]) == 98
    print("R35_CORE_FREEZE_SELF_TEST_PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    text = json.dumps(run_audit(), indent=2, sort_keys=True) + "\n"
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
