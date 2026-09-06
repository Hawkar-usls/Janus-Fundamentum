from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path

import janus_trump_r50g25v_split_tree_growth_random_nae_audit as r50g25v

GATE = "JANUS_TRUMP_R50G25W_MINIMIZE_TREE_GROWTH_WITNESS_AND_SCALE_NAE_FAMILY"
PARENT_V_JOURNAL_COMMIT = "2060aab00eb6366c29c387945b87ac5a8b7facb4"
PARENT_V_RESULT_COMMIT = "d99383cbdff399eb812429d77f414054d645b81d"
PREREG_COMMIT = "12948756b00715f64cab69e3c1f477810c73e187"
EXPECTED_TARGET_HASH = "b26a37dd5b43f5d5293726f42130ebe6b01a78a637ecc0ee279624808bf89fa8"
TARGET_EDGES = (
    (1,3,4),(1,3,5),(1,4,5),(2,4,7),(2,5,9),
    (2,5,10),(3,5,10),(3,8,9),(5,7,9),(6,7,9),
)
MIN_DEPTH_LIMIT = 6
SCALE_DEPTH_LIMIT = 6
SCALE_PARAMETERS = (
    (11, (11,16,22), (11001,11002)),
    (12, (12,18,24), (12001,12002)),
)
LEDGER_KEYS = r50g25v.LEDGER_KEYS


def empty_ledger():
    return {k: 0 for k in LEDGER_KEYS}


def add_ledger(dst, src):
    for k in LEDGER_KEYS:
        dst[k] += int((src or {}).get(k, 0))


def solve_bounded(formula, root_variables, r50g23, r35b, r33, r47j, depth_limit, depth=0, assumptions=(), forced_first_pivot=None):
    node_formula = r33.canonical_formula(list(formula) + [(int(l),) for l in assumptions])
    micro = r50g25v.r50g25u.r50g25t.r50g25s.r50g25r.r50g25g.micro_normalize(node_formula, r50g23, r35b, r33, r47j)
    ledger = empty_ledger()
    add_ledger(ledger, micro.get("ledger", {}))
    node = {
        "depth": depth,
        "assumptions": list(assumptions),
        "micro_terminal": micro.get("terminal") if micro.get("terminal") is not None else "RESIDUAL_FIXPOINT",
        "micro_semantic_sat": micro.get("semantic_sat"),
        "micro_final_CLV": micro.get("final_CLV"),
        "micro_ledger": micro.get("ledger", {}),
        "children": [],
    }
    if micro.get("terminal") is not None:
        status = "SAT" if micro.get("semantic_sat") is True else "UNSAT"
        node["status"] = status
        return {"status": status, "node": node, "ledger": ledger, "max_depth": depth, "leaf_count": 1, "node_count": 1, "split_count": 0, "budget_residual_leaves": 0}
    if depth >= depth_limit:
        node["status"] = "UNKNOWN_DEPTH_BUDGET"
        return {"status": "UNKNOWN_DEPTH_BUDGET", "node": node, "ledger": ledger, "max_depth": depth, "leaf_count": 1, "node_count": 1, "split_count": 0, "budget_residual_leaves": 1}
    assigned = {abs(int(l)) for l in assumptions}
    candidates = [v for v in root_variables if v not in assigned]
    if not candidates:
        node["status"] = "UNKNOWN_NO_UNASSIGNED_SPLIT_VAR"
        return {"status": "UNKNOWN_DEPTH_BUDGET", "node": node, "ledger": ledger, "max_depth": depth, "leaf_count": 1, "node_count": 1, "split_count": 0, "budget_residual_leaves": 1}
    if depth == 0 and forced_first_pivot is not None:
        if forced_first_pivot not in candidates:
            raise AssertionError(("R50G25W_FORCED_FIRST_PIVOT_ABSENT", forced_first_pivot, candidates))
        pivot = int(forced_first_pivot)
    else:
        pivot = min(candidates)
    node["split_variable"] = pivot
    children = []
    for lit in (-pivot, pivot):
        child = solve_bounded(formula, root_variables, r50g23, r35b, r33, r47j, depth_limit, depth + 1, assumptions + (lit,), forced_first_pivot=None)
        children.append(child)
        node["children"].append(child["node"])
        add_ledger(ledger, child["ledger"])
        if child["status"] == "SAT":
            node["status"] = "SAT"
            return {
                "status": "SAT", "node": node, "ledger": ledger,
                "max_depth": max(depth, *(c["max_depth"] for c in children)),
                "leaf_count": sum(c["leaf_count"] for c in children),
                "node_count": 1 + sum(c["node_count"] for c in children),
                "split_count": 1 + sum(c["split_count"] for c in children),
                "budget_residual_leaves": sum(c["budget_residual_leaves"] for c in children),
            }
    statuses = [c["status"] for c in children]
    status = "UNSAT" if statuses == ["UNSAT", "UNSAT"] else "UNKNOWN_DEPTH_BUDGET"
    node["status"] = status
    return {
        "status": status, "node": node, "ledger": ledger,
        "max_depth": max(depth, *(c["max_depth"] for c in children)),
        "leaf_count": sum(c["leaf_count"] for c in children),
        "node_count": 1 + sum(c["node_count"] for c in children),
        "split_count": 1 + sum(c["split_count"] for c in children),
        "budget_residual_leaves": sum(c["budget_residual_leaves"] for c in children),
    }


def case_eval(r33, r50g23, r35b, r47j, formula, n, depth_limit, forced_first_pivot=None):
    formula = r33.canonical_formula(formula)
    root_variables = list(r33.variables(formula))
    exact_models = r50g25v.exact_root_model_count(r33, formula, n)
    exact_status = "SAT" if exact_models > 0 else "UNSAT"
    root_micro = r50g25v.r50g25u.r50g25t.r50g25s.r50g25r.r50g25g.micro_normalize(formula, r50g23, r35b, r33, r47j)
    tree = solve_bounded(formula, root_variables, r50g23, r35b, r33, r47j, depth_limit, forced_first_pivot=forced_first_pivot)
    decisive = tree["status"] in {"SAT", "UNSAT"}
    semantic_agreement = (not decisive) or tree["status"] == exact_status
    if not semantic_agreement:
        raise AssertionError(("R50G25W_SEMANTIC_MISMATCH", r50g23.r50g4.fhash(formula), tree["status"], exact_status))
    return {
        "formula_hash": r50g23.r50g4.fhash(formula),
        "CLV": list(r33.measure(formula)),
        "present_root_variables": root_variables,
        "root_micro_terminal": root_micro.get("terminal") if root_micro.get("terminal") is not None else "RESIDUAL_FIXPOINT",
        "exact_truth_validation": {
            "assignment_space_checked": 2 ** n,
            "model_count": exact_models,
            "status": exact_status,
            "validation_only_not_algorithmic_authority": True,
        },
        "tree_solver": {
            "status": tree["status"],
            "max_split_depth_used": tree["max_depth"],
            "tree_node_count": tree["node_count"],
            "leaf_count": tree["leaf_count"],
            "split_count": tree["split_count"],
            "residual_budget_leaf_count": tree["budget_residual_leaves"],
            "sum_micro_ledgers": tree["ledger"],
            "tree": tree["node"],
        },
        "semantic_agreement": semantic_agreement,
    }


def minimize_target(r33, r50g23, r35b, r47j):
    current = list(sorted(TARGET_EDGES))
    initial_formula = r50g25v.nae_formula(r33, current)
    initial_hash = r50g23.r50g4.fhash(initial_formula)
    if initial_hash != EXPECTED_TARGET_HASH:
        raise AssertionError(("R50G25W_TARGET_HASH_DRIFT", initial_hash))
    initial = case_eval(r33, r50g23, r35b, r47j, initial_formula, 10, MIN_DEPTH_LIMIT)
    if initial["exact_truth_validation"]["status"] != "SAT" or initial["tree_solver"]["max_split_depth_used"] != 4:
        raise AssertionError(("R50G25W_TARGET_BEHAVIOR_DRIFT", initial))

    deletion_history = []
    while True:
        removed = False
        for edge in list(sorted(current)):
            candidate_edges = [e for e in current if e != edge]
            formula = r50g25v.nae_formula(r33, candidate_edges)
            result = case_eval(r33, r50g23, r35b, r47j, formula, 10, MIN_DEPTH_LIMIT)
            preserves = result["exact_truth_validation"]["status"] == "SAT" and result["tree_solver"]["max_split_depth_used"] >= 4
            deletion_history.append({
                "current_edge_count_before": len(current),
                "tested_edge": list(edge),
                "candidate_formula_hash": result["formula_hash"],
                "candidate_exact_status": result["exact_truth_validation"]["status"],
                "candidate_depth": result["tree_solver"]["max_split_depth_used"],
                "candidate_tree_status": result["tree_solver"]["status"],
                "preserves_depth_ge_4_and_SAT": preserves,
            })
            if preserves:
                current = candidate_edges
                removed = True
                break
        if not removed:
            break

    final_formula = r50g25v.nae_formula(r33, current)
    final = case_eval(r33, r50g23, r35b, r47j, final_formula, 10, MIN_DEPTH_LIMIT)
    post = []
    irreducible = True
    for edge in sorted(current):
        candidate_edges = [e for e in current if e != edge]
        result = case_eval(r33, r50g23, r35b, r47j, r50g25v.nae_formula(r33, candidate_edges), 10, MIN_DEPTH_LIMIT)
        preserves = result["exact_truth_validation"]["status"] == "SAT" and result["tree_solver"]["max_split_depth_used"] >= 4
        irreducible = irreducible and not preserves
        post.append({
            "removed_edge": list(edge),
            "candidate_hash": result["formula_hash"],
            "exact_status": result["exact_truth_validation"]["status"],
            "depth": result["tree_solver"]["max_split_depth_used"],
            "tree_status": result["tree_solver"]["status"],
            "preserves_depth_ge_4_and_SAT": preserves,
        })
    if not irreducible:
        raise AssertionError(("R50G25W_MINIMIZATION_FIXPOINT_FAIL", post))

    pivot_rows = []
    baseline_depth = final["tree_solver"]["max_split_depth_used"]
    for pivot in final["present_root_variables"]:
        result = case_eval(r33, r50g23, r35b, r47j, final_formula, 10, MIN_DEPTH_LIMIT, forced_first_pivot=pivot)
        pivot_rows.append({
            "forced_first_pivot": pivot,
            "status": result["tree_solver"]["status"],
            "depth": result["tree_solver"]["max_split_depth_used"],
            "nodes": result["tree_solver"]["tree_node_count"],
            "leaves": result["tree_solver"]["leaf_count"],
        })
    heuristic_sensitive = any(row["depth"] <= baseline_depth - 2 for row in pivot_rows)

    return {
        "initial": initial,
        "algorithm": "DETERMINISTIC_LEX_FIRST_SINGLE_EDGE_DELETION_FIXPOINT",
        "deletion_history": deletion_history,
        "final_edges": [list(e) for e in sorted(current)],
        "final_edge_count": len(current),
        "removed_edge_count": len(TARGET_EDGES) - len(current),
        "final": final,
        "post_fixpoint_single_edge_tests": post,
        "single_edge_deletion_irreducible_for_depth_ge_4_and_SAT": irreducible,
        "claim_scope": "SINGLE_EDGE_DELETION_IRREDUCIBLE_FOR_DEPTH_GE_4_UNDER_FROZEN_SOLVER",
        "global_minimum_edge_count_claimed": False,
        "first_pivot_sensitivity": {
            "baseline_smallest_pivot_depth": baseline_depth,
            "rows": pivot_rows,
            "heuristic_sensitivity_depth_drop_ge_2": heuristic_sensitive,
        },
    }


def scale_suite(r33, r50g23, r35b, r47j):
    cases = []
    for n, edge_counts, seeds in SCALE_PARAMETERS:
        for m in edge_counts:
            for seed in seeds:
                formula, edges = r50g25v.random_hypergraph_formula(r33, n, m, seed)
                result = case_eval(r33, r50g23, r35b, r47j, formula, n, SCALE_DEPTH_LIMIT)
                result["spec"] = {"n": n, "edge_count": m, "seed": seed, "edges": [list(e) for e in edges]}
                cases.append(result)
    if len(cases) != 12:
        raise AssertionError(("R50G25W_SCALE_CASE_COUNT_DRIFT", len(cases)))
    status_hist = Counter(c["tree_solver"]["status"] for c in cases)
    depth_hist = Counter(str(c["tree_solver"]["max_split_depth_used"]) for c in cases)
    max_depth = max(c["tree_solver"]["max_split_depth_used"] for c in cases)
    max_nodes = max(c["tree_solver"]["tree_node_count"] for c in cases)
    max_leaves = max(c["tree_solver"]["leaf_count"] for c in cases)
    residuals = [c for c in cases if c["tree_solver"]["status"] == "UNKNOWN_DEPTH_BUDGET"]
    depth5 = [c for c in cases if c["tree_solver"]["max_split_depth_used"] >= 5]
    tree_size_growth = [c for c in cases if c["tree_solver"]["tree_node_count"] > 5 or c["tree_solver"]["leaf_count"] > 2]
    hardest = sorted(cases, key=lambda c: (-c["tree_solver"]["max_split_depth_used"], -c["tree_solver"]["tree_node_count"], -c["tree_solver"]["leaf_count"], c["formula_hash"]))[:6]
    return {
        "case_count": 12,
        "status_partition": dict(sorted(status_hist.items())),
        "depth_histogram": dict(sorted(depth_hist.items(), key=lambda kv: int(kv[0]))),
        "max_observed_depth": max_depth,
        "max_observed_nodes": max_nodes,
        "max_observed_leaves": max_leaves,
        "depth_ge_5_count": len(depth5),
        "depth6_residual_count": len(residuals),
        "tree_size_growth_count_over_V_maxima": len(tree_size_growth),
        "hardest_cases": hardest,
        "all_cases": cases,
    }


def run():
    _b, r50g23, r35b, r33, r47j = r50g25v.r50g25u.r50g25t.r50g25s.r50g25r.r50g25g._chain()
    minimized = minimize_target(r33, r50g23, r35b, r47j)
    scaled = scale_suite(r33, r50g23, r35b, r47j)

    if scaled["depth6_residual_count"] > 0:
        scale_finding = "DEPTH6_RESIDUAL"
        next_gate = "R50G25X_MINIMIZE_DEPTH6_RESIDUAL_AND_AUDIT_BRANCH_TREE_SIZE"
    elif scaled["depth_ge_5_count"] > 0:
        scale_finding = "DEPTH_GROWTH_CONTINUES"
        next_gate = "R50G25X_MINIMIZE_DEEPER_SCALE_WITNESS_AND_TEST_N13_N14"
    else:
        scale_finding = "NO_FURTHER_DEPTH_GROWTH_FINITE"
        next_gate = "R50G25X_TARGET_UNSAT_BRANCHING_TREE_SIZE_GROWTH"

    if scaled["tree_size_growth_count_over_V_maxima"] > 0:
        tree_size_finding = "TREE_SIZE_GROWTH_WITNESS"
    else:
        tree_size_finding = "NO_TREE_SIZE_GROWTH_OVER_V_MAXIMA_IN_FINITE_SCALE_SUITE"

    return {
        "gate": GATE,
        "parent_V_journal_commit": PARENT_V_JOURNAL_COMMIT,
        "parent_V_result_commit": PARENT_V_RESULT_COMMIT,
        "preregistration_commit": PREREG_COMMIT,
        "minimization": minimized,
        "scale_suite": scaled,
        "scale_finding": scale_finding,
        "tree_size_finding": tree_size_finding,
        "verdict": f"MINIMIZATION_COMPLETE__{scale_finding}__{tree_size_finding}",
        "next_gate": next_gate,
        "interpretation_contract": {
            "single_edge_irreducible_is_not_global_minimum": True,
            "finite_n11_n12_success_is_not_polynomial_bound": True,
            "observed_depth_growth_is_not_asymptotic_lower_bound": True,
            "branching_can_be_exponential": True,
            "truth_table_validation_is_not_algorithmic_authority": True,
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
