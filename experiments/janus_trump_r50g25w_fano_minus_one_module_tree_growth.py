from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r50g25v_split_tree_growth_random_nae_audit as r50g25v

GATE = "JANUS_TRUMP_R50G25W_STRONGER_TREE_GROWTH_FAMILY"
PARENT_V_CORRECTED_JOURNAL = "9608f1493d3734666161d4a8b95d1e6ef8f83327"
PARENT_V_CORRECTED_RESULT = "cb16fa347bd7bcf4a0b337c9d45d8f218ad2a29e"
PREREG_COMMIT = "0d4279b2ce1263695a4a9f61ae95ee56a56ed5d1"
FANO_HASH = "466163011411ccd10520539fb80f0bec7a9de934400961cfa6a25f1c58c38a00"
DELETED_CLAUSE = (-3, -5, -6)
KNOWN_MODULE_MODEL = {1: False, 2: False, 3: True, 4: False, 5: True, 6: True, 7: False}
SAT_CHAIN_K = (1, 2, 3, 4, 5, 6)
UNSAT_TAIL_K = (0, 1, 2, 3, 4)
SAT_DEPTH_BUDGET = 7
UNSAT_DEPTH_BUDGET = 6
LEDGER_KEYS = r50g25v.LEDGER_KEYS


def empty_ledger():
    return {k: 0 for k in LEDGER_KEYS}


def add_ledger(dst, src):
    for k in LEDGER_KEYS:
        dst[k] += int((src or {}).get(k, 0))


def shift_clause(clause, offset):
    return tuple((abs(int(l)) + offset) if int(l) > 0 else -(abs(int(l)) + offset) for l in clause)


def shift_formula(r33, formula, offset):
    return r33.canonical_formula(shift_clause(c, offset) for c in formula)


def shifted_model(model, offset):
    return {int(v) + offset: bool(value) for v, value in model.items()}


def merge_models(models):
    out = {}
    for model in models:
        overlap = set(out).intersection(model)
        if overlap:
            raise AssertionError(("R50G25W_MODEL_OVERLAP", sorted(overlap)))
        out.update(model)
    return out


def solve_bounded(formula, root_variables, r50g23, r35b, r33, r47j, depth_limit, depth=0, assumptions=()):
    node_formula = r33.canonical_formula(list(formula) + [(int(l),) for l in assumptions])
    micro = r50g25v.r50g25u.r50g25t.r50g25s.r50g25r.r50g25g.micro_normalize(node_formula, r50g23, r35b, r33, r47j)
    ledger = empty_ledger()
    add_ledger(ledger, micro.get("ledger", {}))
    node = {
        "depth": depth,
        "assumptions": list(assumptions),
        "node_CLV": list(r33.measure(node_formula)),
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
    pivot = min(candidates)
    node["split_variable"] = pivot
    children = []
    for lit in (-pivot, pivot):
        child = solve_bounded(formula, root_variables, r50g23, r35b, r33, r47j, depth_limit, depth + 1, assumptions + (lit,))
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


def summarize_tree(tree):
    return {
        "status": tree["status"],
        "max_split_depth_used": tree["max_depth"],
        "tree_node_count": tree["node_count"],
        "leaf_count": tree["leaf_count"],
        "split_count": tree["split_count"],
        "residual_budget_leaf_count": tree["budget_residual_leaves"],
        "sum_micro_ledgers": tree["ledger"],
        "tree": tree["node"],
    }


def build_fano_and_module(r33, r50g23):
    fano = r50g25v.r50g25u.r50g25t.r50g25s.nae_formula(r33, r50g25v.r50g25u.r50g25t.r50g25s.fano_edges())
    if r50g23.r50g4.fhash(fano) != FANO_HASH or tuple(r33.measure(fano)) != (14, 42, 7):
        raise AssertionError(("R50G25W_FANO_SOURCE_DRIFT", r50g23.r50g4.fhash(fano), r33.measure(fano)))
    if DELETED_CLAUSE not in fano:
        raise AssertionError(("R50G25W_DELETED_CLAUSE_MISSING", DELETED_CLAUSE))
    module = r33.canonical_formula(c for c in fano if c != DELETED_CLAUSE)
    if tuple(r33.measure(module)) != (13, 39, 7):
        raise AssertionError(("R50G25W_MODULE_CLV_DRIFT", r33.measure(module)))
    exact_count = r50g25v.exact_root_model_count(r33, module, 7)
    if exact_count != 5:
        raise AssertionError(("R50G25W_MODULE_MODEL_COUNT_DRIFT", exact_count))
    if not r33.eval_formula(module, KNOWN_MODULE_MODEL):
        raise AssertionError("R50G25W_KNOWN_MODULE_MODEL_FAIL")
    return fano, module


def build_sat_chain(r33, module, k):
    formulas = [shift_formula(r33, module, 7 * i) for i in range(k)]
    formula = r33.canonical_formula(c for f in formulas for c in f)
    witness = merge_models([shifted_model(KNOWN_MODULE_MODEL, 7 * i) for i in range(k)])
    return formula, witness


def build_unsat_tail(r33, module, fano, k):
    sat_parts = [shift_formula(r33, module, 7 * i) for i in range(k)]
    tail_offset = 7 * k
    tail = shift_formula(r33, fano, tail_offset)
    formula = r33.canonical_formula(c for f in sat_parts + [tail] for c in f)
    mapped_tail = r33.canonical_formula(shift_clause(c, -tail_offset) for c in tail)
    return formula, tail, mapped_tail


def run():
    _b, r50g23, r35b, r33, r47j = r50g25v.r50g25u.r50g25t.r50g25s.r50g25r.r50g25g._chain()
    fano, module = build_fano_and_module(r33, r50g23)
    module_micro = r50g25v.r50g25u.r50g25t.r50g25s.r50g25r.r50g25g.micro_normalize(module, r50g23, r35b, r33, r47j)
    module_receipt = {
        "formula_hash": r50g23.r50g4.fhash(module),
        "CLV": list(r33.measure(module)),
        "exact_model_count_validation_only": 5,
        "known_model_pass": r33.eval_formula(module, KNOWN_MODULE_MODEL),
        "micro_terminal": module_micro.get("terminal") if module_micro.get("terminal") is not None else "RESIDUAL_FIXPOINT",
        "micro_semantic_sat": module_micro.get("semantic_sat"),
        "micro_final_CLV": module_micro.get("final_CLV"),
        "micro_ledger": module_micro.get("ledger", {}),
    }
    if module_micro.get("terminal") is not None:
        return {
            "gate": GATE,
            "parent_V_corrected_journal_commit": PARENT_V_CORRECTED_JOURNAL,
            "parent_V_corrected_result_commit": PARENT_V_CORRECTED_RESULT,
            "preregistration_commit": PREREG_COMMIT,
            "module": module_receipt,
            "sat_chain_cases": [],
            "unsat_tail_cases": [],
            "findings": ["MODULE_NOT_RESIDUAL"],
            "verdict": "MODULE_NOT_RESIDUAL__FANO_MINUS_ONE_CLAUSE_NOT_A_TREE_GROWTH_BUILDING_BLOCK",
            "next_gate": "R50G25X_SEARCH_FOR_SAT_RESIDUAL_MODULE_OR_COMPONENT_DECOMPOSITION_GAP",
            "interpretation_contract": {
                "module_failure_is_a_valid_negative_result": True,
                "no_tree_growth_claim_from_unexecuted_modular_families": True,
                "constructed_heuristic_tree_growth_is_not_general_SAT_lower_bound": True,
            },
            "firewall": {"P_VS_NP": "OPEN", "SAT_IN_P": "NOT_PROVED", "TRUMP_finished": False},
        }

    sat_cases = []
    for k in SAT_CHAIN_K:
        formula, witness = build_sat_chain(r33, module, k)
        if not r33.eval_formula(formula, witness):
            raise AssertionError(("R50G25W_SAT_CHAIN_WITNESS_FAIL", k))
        tree = solve_bounded(formula, list(r33.variables(formula)), r50g23, r35b, r33, r47j, SAT_DEPTH_BUDGET)
        if tree["status"] == "UNSAT":
            raise AssertionError(("R50G25W_SAT_CHAIN_FALSE_UNSAT", k))
        sat_cases.append({
            "k": k,
            "formula_hash": r50g23.r50g4.fhash(formula),
            "CLV": list(r33.measure(formula)),
            "known_parent_semantics": "SAT_BY_CONCATENATED_T_MODEL",
            "known_model_pass": True,
            "tree_solver": summarize_tree(tree),
        })

    unsat_cases = []
    for k in UNSAT_TAIL_K:
        formula, tail, mapped_tail = build_unsat_tail(r33, module, fano, k)
        mapped_hash = r50g23.r50g4.fhash(mapped_tail)
        if mapped_hash != FANO_HASH or mapped_tail != fano:
            raise AssertionError(("R50G25W_UNSAT_TAIL_CERTIFICATE_FAIL", k, mapped_hash))
        tree = solve_bounded(formula, list(r33.variables(formula)), r50g23, r35b, r33, r47j, UNSAT_DEPTH_BUDGET)
        if tree["status"] == "SAT":
            raise AssertionError(("R50G25W_UNSAT_TAIL_FALSE_SAT", k))
        expected_depth = k + 1
        expected_leaves = 2 ** (k + 1)
        expected_nodes = 2 ** (k + 2) - 1
        unsat_cases.append({
            "k": k,
            "formula_hash": r50g23.r50g4.fhash(formula),
            "CLV": list(r33.measure(formula)),
            "known_parent_semantics": "UNSAT_BY_EMBEDDED_INTACT_FANO_SUBFORMULA",
            "tail_offset": 7 * k,
            "tail_mapped_hash": mapped_hash,
            "tree_solver": summarize_tree(tree),
            "full_binary_reference": {
                "expected_depth": expected_depth,
                "expected_leaves": expected_leaves,
                "expected_nodes": expected_nodes,
                "exact_match": tree["max_depth"] == expected_depth and tree["leaf_count"] == expected_leaves and tree["node_count"] == expected_nodes,
            },
        })

    findings = []
    sat_depths = [c["tree_solver"]["max_split_depth_used"] for c in sat_cases]
    if max(sat_depths) >= 2:
        findings.append("SAT_CHAIN_DEPTH_GROWTH")
    if any(c["tree_solver"]["status"] == "UNKNOWN_DEPTH_BUDGET" for c in sat_cases + unsat_cases):
        findings.append("DEPTH_BUDGET_RESIDUAL")

    unsat_nodes = [c["tree_solver"]["tree_node_count"] for c in unsat_cases]
    strict_nodes = all(a < b for a, b in zip(unsat_nodes, unsat_nodes[1:]))
    if strict_nodes and unsat_cases[-1]["tree_solver"]["tree_node_count"] >= 31:
        findings.append("UNSAT_TAIL_TREE_SIZE_GROWTH")
    exact_full_binary = all(c["full_binary_reference"]["exact_match"] for c in unsat_cases)
    if exact_full_binary:
        findings.append("EXACT_FULL_BINARY_PATTERN")
    if not findings:
        findings.append("NO_GROWTH_IN_CONSTRUCTED_FAMILIES")

    if "DEPTH_BUDGET_RESIDUAL" in findings:
        next_gate = "R50G25X_MINIMIZE_MODULAR_DEPTH_BUDGET_RESIDUAL"
    elif "UNSAT_TAIL_TREE_SIZE_GROWTH" in findings:
        next_gate = "R50G25X_PROVE_OR_BREAK_COMPONENTWISE_TREE_RECURRENCE_AND_ADD_COMPONENT_DECOMPOSITION_CONTROL"
    elif "SAT_CHAIN_DEPTH_GROWTH" in findings:
        next_gate = "R50G25X_SCALE_MODULAR_DEPTH_AND_TEST_COMPONENT_DECOMPOSITION_DOOR"
    else:
        next_gate = "R50G25X_SEARCH_FOR_STRONGER_CONNECTED_TREE_GROWTH_FAMILY"

    return {
        "gate": GATE,
        "parent_V_corrected_journal_commit": PARENT_V_CORRECTED_JOURNAL,
        "parent_V_corrected_result_commit": PARENT_V_CORRECTED_RESULT,
        "preregistration_commit": PREREG_COMMIT,
        "module": module_receipt,
        "sat_chain_cases": sat_cases,
        "unsat_tail_cases": unsat_cases,
        "sat_chain_depth_vector": sat_depths,
        "unsat_tail_node_vector": unsat_nodes,
        "unsat_tail_leaf_vector": [c["tree_solver"]["leaf_count"] for c in unsat_cases],
        "unsat_tail_depth_vector": [c["tree_solver"]["max_split_depth_used"] for c in unsat_cases],
        "findings": findings,
        "verdict": "__".join(findings),
        "next_gate": next_gate,
        "interpretation_contract": {
            "constructed_heuristic_tree_growth_is_not_general_SAT_lower_bound": True,
            "finite_k_0_to_6_is_not_asymptotic_proof": True,
            "even_exact_full_binary_pattern_on_finite_k_is_not_P_vs_NP_resolution": True,
            "disconnected_component_construction_may_expose_missing_component_decomposition_rule": True,
            "adding_component_decomposition_later_requires_new_certificate_and_cost_audit": True,
            "no_truth_table_used_for_parent_semantics_beyond_single_module_validation": True,
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
