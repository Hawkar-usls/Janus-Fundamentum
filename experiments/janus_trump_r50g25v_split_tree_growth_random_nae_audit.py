from __future__ import annotations

import argparse
import itertools
import json
import random
from collections import Counter
from pathlib import Path

import janus_trump_r50g25u_depth1_certified_split_fano as r50g25u

GATE = "JANUS_TRUMP_R50G25V_SPLIT_DEPTH_AND_TREE_SIZE_AUDIT_BEYOND_FANO"
PARENT_U_RESULT_COMMIT = "3e8d62c17a90af308453e8939f52f9cecc781ea7"
PREREG_COMMIT = "1c74a2978bd2b0e525b04a8dac2217fddf4b0fa1"
MAX_DEPTH = 4

PARAMETERS = (
    (7, (7, 10, 14), (7001, 7002, 7003)),
    (8, (8, 12, 16), (8001, 8002, 8003)),
    (9, (9, 14, 18), (9001, 9002, 9003)),
    (10, (10, 15, 20), (10001, 10002, 10003)),
)

LEDGER_KEYS = (
    "R33_check_operation_upper_ledger",
    "R33_certificate_bytes",
    "RUP_checks",
    "RUP_UP_clause_scans",
    "RUP_UP_literal_inspections",
    "RUP_successful_strengthenings",
    "GF2_estimated_bit_ops",
    "restart_count",
)


def nae_formula(r33, edges):
    clauses = []
    for a, b, c in edges:
        edge = tuple(sorted((int(a), int(b), int(c))))
        clauses.append(edge)
        clauses.append(tuple(-x for x in edge))
    return r33.canonical_formula(clauses)


def random_hypergraph_formula(r33, n, m, seed):
    universe = list(itertools.combinations(range(1, n + 1), 3))
    rng = random.Random(int(seed))
    edges = sorted(rng.sample(universe, int(m)))
    return nae_formula(r33, edges), edges


def exact_root_model_count(r33, formula, n):
    count = 0
    for bits in itertools.product((False, True), repeat=n):
        assignment = {i + 1: bool(bits[i]) for i in range(n)}
        if r33.eval_formula(formula, assignment):
            count += 1
    return count


def empty_ledger():
    return {k: 0 for k in LEDGER_KEYS}


def add_ledger(dst, src):
    for k in LEDGER_KEYS:
        dst[k] += int((src or {}).get(k, 0))


def solve_bounded(formula, root_variables, r50g23, r35b, r33, r47j, depth=0, assumptions=()):
    node_formula = r33.canonical_formula(list(formula) + [(int(l),) for l in assumptions])
    micro = r50g25u.r50g25t.r50g25s.r50g25r.r50g25g.micro_normalize(node_formula, r50g23, r35b, r33, r47j)
    ledger = empty_ledger()
    add_ledger(ledger, micro.get("ledger", {}))

    node = {
        "depth": depth,
        "assumptions": list(assumptions),
        "node_CLV": list(r33.measure(node_formula)),
        "micro_terminal": micro.get("terminal") if micro.get("terminal") is not None else "RESIDUAL_FIXPOINT",
        "micro_semantic_sat": micro.get("semantic_sat"),
        "micro_final_CLV": micro.get("final_CLV"),
        "micro_round_count": micro.get("round_count"),
        "micro_restart_count": micro.get("restart_count"),
        "micro_ledger": micro.get("ledger", {}),
        "children": [],
    }

    if micro.get("terminal") is not None:
        status = "SAT" if micro.get("semantic_sat") is True else "UNSAT"
        node["status"] = status
        return {"status": status, "node": node, "ledger": ledger, "max_depth": depth, "leaf_count": 1, "node_count": 1, "split_count": 0, "budget_residual_leaves": 0}

    if depth >= MAX_DEPTH:
        node["status"] = "UNKNOWN_DEPTH_BUDGET"
        return {"status": "UNKNOWN_DEPTH_BUDGET", "node": node, "ledger": ledger, "max_depth": depth, "leaf_count": 1, "node_count": 1, "split_count": 0, "budget_residual_leaves": 1}

    assigned_vars = {abs(int(l)) for l in assumptions}
    candidates = [v for v in root_variables if v not in assigned_vars]
    if not candidates:
        node["status"] = "UNKNOWN_NO_UNASSIGNED_SPLIT_VAR"
        return {"status": "UNKNOWN_DEPTH_BUDGET", "node": node, "ledger": ledger, "max_depth": depth, "leaf_count": 1, "node_count": 1, "split_count": 0, "budget_residual_leaves": 1}

    pivot = min(candidates)
    node["split_variable"] = pivot
    child_results = []
    for lit in (-pivot, pivot):
        child = solve_bounded(formula, root_variables, r50g23, r35b, r33, r47j, depth + 1, assumptions + (lit,))
        child_results.append(child)
        node["children"].append(child["node"])
        add_ledger(ledger, child["ledger"])
        if child["status"] == "SAT":
            node["status"] = "SAT"
            return {
                "status": "SAT",
                "node": node,
                "ledger": ledger,
                "max_depth": max(depth, *(c["max_depth"] for c in child_results)),
                "leaf_count": sum(c["leaf_count"] for c in child_results),
                "node_count": 1 + sum(c["node_count"] for c in child_results),
                "split_count": 1 + sum(c["split_count"] for c in child_results),
                "budget_residual_leaves": sum(c["budget_residual_leaves"] for c in child_results),
            }

    statuses = [c["status"] for c in child_results]
    if statuses == ["UNSAT", "UNSAT"]:
        status = "UNSAT"
    else:
        status = "UNKNOWN_DEPTH_BUDGET"
    node["status"] = status
    return {
        "status": status,
        "node": node,
        "ledger": ledger,
        "max_depth": max(depth, *(c["max_depth"] for c in child_results)),
        "leaf_count": sum(c["leaf_count"] for c in child_results),
        "node_count": 1 + sum(c["node_count"] for c in child_results),
        "split_count": 1 + sum(c["split_count"] for c in child_results),
        "budget_residual_leaves": sum(c["budget_residual_leaves"] for c in child_results),
    }


def collect_leaf_terminals(node, out):
    children = node.get("children", [])
    if not children:
        out[node.get("micro_terminal", "UNKNOWN")] += 1
        return
    for child in children:
        collect_leaf_terminals(child, out)


def run_case(spec, formula, n, r50g23, r35b, r33, r47j):
    formula = r33.canonical_formula(formula)
    root_variables = list(r33.variables(formula))
    formula_hash = r50g23.r50g4.fhash(formula)
    exact_models = exact_root_model_count(r33, formula, n)
    exact_status = "SAT" if exact_models > 0 else "UNSAT"
    root_micro = r50g25u.r50g25t.r50g25s.r50g25r.r50g25g.micro_normalize(formula, r50g23, r35b, r33, r47j)
    result = solve_bounded(formula, root_variables, r50g23, r35b, r33, r47j)
    decisive = result["status"] in {"SAT", "UNSAT"}
    semantic_agreement = (not decisive) or result["status"] == exact_status
    if not semantic_agreement:
        raise AssertionError(("R50G25V_SEMANTIC_MISMATCH", spec, result["status"], exact_status))
    leaf_hist = Counter()
    collect_leaf_terminals(result["node"], leaf_hist)
    return {
        "spec": spec,
        "formula_hash": formula_hash,
        "CLV": list(r33.measure(formula)),
        "present_root_variables": root_variables,
        "root_micro_terminal": root_micro.get("terminal") if root_micro.get("terminal") is not None else "RESIDUAL_FIXPOINT",
        "root_micro_semantic_sat": root_micro.get("semantic_sat"),
        "exact_truth_validation": {
            "assignment_space_checked": 2 ** n,
            "model_count": exact_models,
            "status": exact_status,
            "validation_only_not_algorithmic_authority": True,
        },
        "tree_solver": {
            "status": result["status"],
            "max_split_depth_used": result["max_depth"],
            "tree_node_count": result["node_count"],
            "leaf_count": result["leaf_count"],
            "split_count": result["split_count"],
            "residual_budget_leaf_count": result["budget_residual_leaves"],
            "terminal_leaf_partition": dict(sorted(leaf_hist.items())),
            "sum_micro_ledgers": result["ledger"],
            "tree": result["node"],
        },
        "semantic_agreement": semantic_agreement,
    }


def run():
    _b, r50g23, r35b, r33, r47j = r50g25u.r50g25t.r50g25s.r50g25r.r50g25g._chain()
    cases = []
    hashes = Counter()

    fano = r50g25u.r50g25t.r50g25s.nae_formula(r33, r50g25u.r50g25t.r50g25s.fano_edges())
    fano_case = run_case({"family": "FANO_NAE_CONTROL", "n": 7}, fano, 7, r50g23, r35b, r33, r47j)
    if fano_case["tree_solver"]["status"] != "UNSAT" or fano_case["tree_solver"]["max_split_depth_used"] != 1:
        raise AssertionError(("R50G25V_FANO_CONTROL_DRIFT", fano_case["tree_solver"]))

    for n, edge_counts, seeds in PARAMETERS:
        for m in edge_counts:
            for seed in seeds:
                formula, edges = random_hypergraph_formula(r33, n, m, seed)
                spec = {"family": "DETERMINISTIC_RANDOM_3UNIFORM_NAE", "n": n, "edge_count": m, "seed": seed, "edges": [list(e) for e in edges]}
                case = run_case(spec, formula, n, r50g23, r35b, r33, r47j)
                cases.append(case)
                hashes[case["formula_hash"]] += 1

    if len(cases) != 36:
        raise AssertionError(("R50G25V_CASE_COUNT_DRIFT", len(cases)))

    status_hist = Counter(c["tree_solver"]["status"] for c in cases)
    root_hist = Counter(c["root_micro_terminal"] for c in cases)
    depth_hist = Counter(str(c["tree_solver"]["max_split_depth_used"]) for c in cases)
    growth = [c for c in cases if c["tree_solver"]["max_split_depth_used"] >= 2]
    residual4 = [c for c in cases if c["tree_solver"]["status"] == "UNKNOWN_DEPTH_BUDGET"]
    max_depth = max(c["tree_solver"]["max_split_depth_used"] for c in cases)
    max_nodes = max(c["tree_solver"]["tree_node_count"] for c in cases)
    max_leaves = max(c["tree_solver"]["leaf_count"] for c in cases)
    hardest = sorted(cases, key=lambda c: (-c["tree_solver"]["max_split_depth_used"], -c["tree_solver"]["tree_node_count"], -c["tree_solver"]["leaf_count"], c["formula_hash"]))[:10]

    if residual4:
        verdict = "DEPTH4_RESIDUAL_FOUND_IN_RANDOM_NAE_OUTER_SUITE"
        next_gate = "R50G25W_MINIMIZE_DEPTH4_RESIDUAL_OR_TREE_GROWTH_WITNESS"
    elif growth:
        verdict = "TREE_GROWTH_WITNESS_FOUND__ALL_CASES_DECIDED_WITHIN_DEPTH4"
        next_gate = "R50G25W_MINIMIZE_TREE_GROWTH_WITNESS_AND_SCALE_NAE_FAMILY"
    else:
        verdict = "FINITE_DEPTH4_ALL_DECIDED_WITHOUT_DEPTH2_GROWTH_WITNESS"
        next_gate = "R50G25W_STRONGER_TREE_GROWTH_FAMILY"

    return {
        "gate": GATE,
        "parent_U_result_commit": PARENT_U_RESULT_COMMIT,
        "preregistration_commit": PREREG_COMMIT,
        "depth_budget": MAX_DEPTH,
        "outer_case_count": 36,
        "Fano_control": fano_case,
        "hash_collision_case_count": sum(v - 1 for v in hashes.values() if v > 1),
        "root_micro_terminal_partition": dict(sorted(root_hist.items())),
        "tree_solver_status_partition": dict(sorted(status_hist.items())),
        "max_depth_histogram": dict(sorted(depth_hist.items(), key=lambda kv: int(kv[0]))),
        "tree_growth_witness_count_depth_ge_2": len(growth),
        "depth4_residual_count": len(residual4),
        "max_observed_split_depth": max_depth,
        "max_observed_tree_node_count": max_nodes,
        "max_observed_leaf_count": max_leaves,
        "hardest_cases": hardest,
        "all_cases": cases,
        "verdict": verdict,
        "next_gate": next_gate,
        "interpretation_contract": {
            "finite_depth4_success_is_not_polynomial_bound": True,
            "observed_small_tree_is_not_asymptotic_small_tree": True,
            "generic_branching_can_be_exponential": True,
            "truth_table_is_validation_only_not_algorithmic_authority": True,
            "tree_growth_witness_is_about_candidate_solver_cost_not_P_vs_NP_resolution": True,
        },
        "firewall": {"P_VS_NP": "OPEN", "SAT_IN_P": "NOT_PROVED", "TRUMP_finished": False},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    out = run()
    text = json.dumps(out, sort_keys=True, indent=2)
    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
