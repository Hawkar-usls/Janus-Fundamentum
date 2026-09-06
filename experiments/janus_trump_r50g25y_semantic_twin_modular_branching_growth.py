from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r50g25x_sat_residual_local_neighborhood_search as r50g25x
import janus_trump_r50g25w_fano_minus_one_module_tree_growth as r50g25w

GATE = "JANUS_TRUMP_R50G25Y_SEMANTIC_TWIN_MODULAR_BRANCHING_GROWTH"
PARENT_X_RESULT_COMMIT = "174a98aee942380a00e3c36b211ee15d09874887"
PREREG_COMMIT = "015c8bded478115b5bf997d850f8f546e53c657c"
FANO_HASH = "466163011411ccd10520539fb80f0bec7a9de934400961cfa6a25f1c58c38a00"
BALANCED_HASH = "1eaac3a32b285469a2446be3888f8c48437fa19a220203a854d3ce938dc9ad62"
BALANCED_DELETION_HASH = "e9c1be318387e98bbc136b7586d9cc361dd08c7573997f52304feb268fc8e04e"
SOURCE_CLAUSE = (2, 4, 6)
REPLACEMENT_CLAUSE = (2, -4, 6)
SAT_CHAIN_K = (1, 2, 3, 4, 5, 6)
UNSAT_TAIL_K = (0, 1, 2, 3, 4)
SAT_DEPTH_BUDGET = 7
UNSAT_DEPTH_BUDGET = 6


def model_key(assignment):
    return tuple(bool(assignment[i]) for i in range(1, 8))


def exact_model_set(r33, formula):
    return {model_key(m) for m in r50g25x.all_models(r33, formula)}


def micro_record(formula, r50g23, r35b, r33, r47j):
    micro = r50g25w.r50g25v.r50g25u.r50g25t.r50g25s.r50g25r.r50g25g.micro_normalize(
        formula, r50g23, r35b, r33, r47j
    )
    ledger = micro.get("ledger", {})
    return {
        "terminal": micro.get("terminal") if micro.get("terminal") is not None else "RESIDUAL_FIXPOINT",
        "semantic_sat": micro.get("semantic_sat"),
        "final_CLV": micro.get("final_CLV"),
        "round_count": micro.get("round_count"),
        "restart_count": micro.get("restart_count"),
        "RUP_checks": int(ledger.get("RUP_checks", 0)),
        "RUP_successful_strengthenings": int(ledger.get("RUP_successful_strengthenings", 0)),
        "ledger": ledger,
    }


def semantic_twin_audit(fano, r50g23, r35b, r33, r47j):
    pairs = []
    balanced_candidates = []
    for clause_index, clause in enumerate(fano):
        deletion = r33.canonical_formula(c for j, c in enumerate(fano) if j != clause_index)
        deletion_models = exact_model_set(r33, deletion)
        deletion_micro = micro_record(deletion, r50g23, r35b, r33, r47j)
        if len(deletion_models) != 5 or deletion_micro["terminal"] == "RESIDUAL_FIXPOINT" or deletion_micro["semantic_sat"] is not True:
            raise AssertionError(("R50G25Y_DELETION_TWIN_DRIFT", clause_index, len(deletion_models), deletion_micro))
        deletion_hash = r50g23.r50g4.fhash(deletion)

        for literal_position, lit in enumerate(clause):
            replacement = list(clause)
            replacement[literal_position] = -int(lit)
            replacement = r33.canonical_clause(replacement)
            flip = r33.canonical_formula([c for j, c in enumerate(fano) if j != clause_index] + [replacement])
            flip_models = exact_model_set(r33, flip)
            flip_micro = micro_record(flip, r50g23, r35b, r33, r47j)
            same_models = flip_models == deletion_models
            flip_residual = flip_micro["terminal"] == "RESIDUAL_FIXPOINT"
            if not same_models or len(flip_models) != 5 or not flip_residual:
                raise AssertionError((
                    "R50G25Y_SEMANTIC_TWIN_AUDIT_FAILURE",
                    clause_index,
                    literal_position,
                    same_models,
                    len(flip_models),
                    flip_micro,
                ))
            flip_hash = r50g23.r50g4.fhash(flip)
            x1_values = sorted({bits[0] for bits in flip_models})
            pair = {
                "source_clause_index": clause_index,
                "source_clause": list(clause),
                "literal_position": literal_position,
                "flipped_literal_from": int(lit),
                "replacement_clause": list(replacement),
                "deletion_hash": deletion_hash,
                "flip_hash": flip_hash,
                "model_count": len(flip_models),
                "exact_model_sets_equal": same_models,
                "x1_values": x1_values,
                "deletion_micro": deletion_micro,
                "flip_micro": flip_micro,
            }
            pairs.append(pair)
            if x1_values == [False, True]:
                balanced_candidates.append((flip_hash, flip, deletion, pair, flip_models))

    if len(pairs) != 42:
        raise AssertionError(("R50G25Y_TWIN_PAIR_COUNT_DRIFT", len(pairs)))
    balanced_candidates.sort(key=lambda row: row[0])
    if not balanced_candidates:
        raise AssertionError("R50G25Y_NO_TWO_SIDED_X1_RESIDUAL")
    chosen = balanced_candidates[0]
    if chosen[0] != BALANCED_HASH or chosen[3]["deletion_hash"] != BALANCED_DELETION_HASH:
        raise AssertionError(("R50G25Y_BALANCED_SELECTION_DRIFT", chosen[0], chosen[3]["deletion_hash"]))
    return pairs, balanced_candidates, chosen


def variable_component_count(formula):
    variables = sorted({abs(l) for c in formula for l in c})
    if not variables:
        return 0
    adj = {v: set() for v in variables}
    for clause in formula:
        cvs = sorted({abs(l) for l in clause})
        for i, u in enumerate(cvs):
            for v in cvs[i + 1:]:
                adj[u].add(v)
                adj[v].add(u)
    seen = set()
    count = 0
    for start in variables:
        if start in seen:
            continue
        count += 1
        stack = [start]
        seen.add(start)
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
    return count


def componentwise_tree_summary(components, r50g23, r35b, r33, r47j, depth_limit):
    records = []
    total_nodes = total_leaves = total_splits = 0
    max_depth = 0
    total_ledger = r50g25w.empty_ledger()
    statuses = []
    for index, component in enumerate(components):
        tree = r50g25w.solve_bounded(
            component,
            list(r33.variables(component)),
            r50g23,
            r35b,
            r33,
            r47j,
            depth_limit,
        )
        statuses.append(tree["status"])
        total_nodes += tree["node_count"]
        total_leaves += tree["leaf_count"]
        total_splits += tree["split_count"]
        max_depth = max(max_depth, tree["max_depth"])
        r50g25w.add_ledger(total_ledger, tree["ledger"])
        records.append({
            "component_index": index,
            "CLV": list(r33.measure(component)),
            "status": tree["status"],
            "depth": tree["max_depth"],
            "nodes": tree["node_count"],
            "leaves": tree["leaf_count"],
            "splits": tree["split_count"],
        })
    if "UNSAT" in statuses:
        conjunction_status = "UNSAT"
    elif all(s == "SAT" for s in statuses):
        conjunction_status = "SAT"
    else:
        conjunction_status = "UNKNOWN_DEPTH_BUDGET"
    return {
        "component_count": len(components),
        "component_statuses": statuses,
        "conjunction_status": conjunction_status,
        "sum_nodes": total_nodes,
        "sum_leaves": total_leaves,
        "sum_splits": total_splits,
        "max_component_depth": max_depth,
        "sum_ledgers": total_ledger,
        "components": records,
    }


def run():
    _b, r50g23, r35b, r33, r47j = (
        r50g25w.r50g25v.r50g25u.r50g25t.r50g25s.r50g25r.r50g25g._chain()
    )
    fano, _ = r50g25w.build_fano_and_module(r33, r50g23)
    if r50g23.r50g4.fhash(fano) != FANO_HASH:
        raise AssertionError("R50G25Y_FANO_DRIFT")

    twin_pairs, balanced_candidates, chosen = semantic_twin_audit(fano, r50g23, r35b, r33, r47j)
    balanced_hash, module, deletion_twin, balanced_pair, balanced_models = chosen
    if tuple(r33.measure(module)) != (14, 42, 7):
        raise AssertionError(("R50G25Y_BALANCED_CLV_DRIFT", r33.measure(module)))

    model_rows = [dict(zip(range(1, 8), bits)) for bits in sorted(balanced_models)]
    x1_partition = {
        "false": sum(1 for bits in balanced_models if bits[0] is False),
        "true": sum(1 for bits in balanced_models if bits[0] is True),
    }
    if x1_partition != {"false": 1, "true": 4}:
        raise AssertionError(("R50G25Y_X1_PARTITION_DRIFT", x1_partition))
    lex_first_model = model_rows[0]

    child_profiles = []
    for lit in (-1, 1):
        child = r33.canonical_formula(list(module) + [(lit,)])
        rec = micro_record(child, r50g23, r35b, r33, r47j)
        child_profiles.append({"assumption": lit, **rec})
    balanced_children_decisive = all(c["terminal"] != "RESIDUAL_FIXPOINT" and c["semantic_sat"] is True for c in child_profiles)

    sat_cases = []
    for k in SAT_CHAIN_K:
        components = [r50g25w.shift_formula(r33, module, 7 * i) for i in range(k)]
        formula = r33.canonical_formula(c for comp in components for c in comp)
        witness = r50g25w.merge_models([r50g25w.shifted_model(lex_first_model, 7 * i) for i in range(k)])
        if not r33.eval_formula(formula, witness):
            raise AssertionError(("R50G25Y_SAT_CHAIN_WITNESS_FAIL", k))
        tree = r50g25w.solve_bounded(
            formula, list(r33.variables(formula)), r50g23, r35b, r33, r47j, SAT_DEPTH_BUDGET
        )
        if tree["status"] == "UNSAT":
            raise AssertionError(("R50G25Y_FALSE_UNSAT_SAT_CHAIN", k))
        componentwise = componentwise_tree_summary(components, r50g23, r35b, r33, r47j, 2)
        if variable_component_count(formula) != k:
            raise AssertionError(("R50G25Y_SAT_COMPONENT_COUNT_DRIFT", k, variable_component_count(formula)))
        sat_cases.append({
            "k": k,
            "formula_hash": r50g23.r50g4.fhash(formula),
            "CLV": list(r33.measure(formula)),
            "known_semantics": "SAT_BY_CONCATENATED_MODULE_MODEL",
            "tree_solver": r50g25w.summarize_tree(tree),
            "componentwise": componentwise,
            "linear_path_reference": {
                "depth": k,
                "nodes": k + 1,
                "leaves": 1,
                "exact_match": tree["max_depth"] == k and tree["node_count"] == k + 1 and tree["leaf_count"] == 1,
            },
        })

    unsat_cases = []
    for k in UNSAT_TAIL_K:
        sat_components = [r50g25w.shift_formula(r33, module, 7 * i) for i in range(k)]
        tail = r50g25w.shift_formula(r33, fano, 7 * k)
        mapped_tail = r33.canonical_formula(r50g25w.shift_clause(c, -7 * k) for c in tail)
        if mapped_tail != fano or r50g23.r50g4.fhash(mapped_tail) != FANO_HASH:
            raise AssertionError(("R50G25Y_TAIL_CERT_FAIL", k))
        components = sat_components + [tail]
        formula = r33.canonical_formula(c for comp in components for c in comp)
        tree = r50g25w.solve_bounded(
            formula, list(r33.variables(formula)), r50g23, r35b, r33, r47j, UNSAT_DEPTH_BUDGET
        )
        if tree["status"] == "SAT":
            raise AssertionError(("R50G25Y_FALSE_SAT_UNSAT_TAIL", k))
        componentwise = componentwise_tree_summary(components, r50g23, r35b, r33, r47j, 2)
        if variable_component_count(formula) != k + 1:
            raise AssertionError(("R50G25Y_UNSAT_COMPONENT_COUNT_DRIFT", k, variable_component_count(formula)))
        expected_depth = k + 1
        expected_leaves = 2 ** (k + 1)
        expected_nodes = 2 ** (k + 2) - 1
        unsat_cases.append({
            "k": k,
            "formula_hash": r50g23.r50g4.fhash(formula),
            "CLV": list(r33.measure(formula)),
            "known_semantics": "UNSAT_BY_EMBEDDED_FANO_TAIL",
            "tree_solver": r50g25w.summarize_tree(tree),
            "componentwise": componentwise,
            "full_binary_reference": {
                "depth": expected_depth,
                "leaves": expected_leaves,
                "nodes": expected_nodes,
                "exact_match": tree["max_depth"] == expected_depth and tree["leaf_count"] == expected_leaves and tree["node_count"] == expected_nodes,
            },
        })

    findings = ["SEMANTIC_TWIN_42_OF_42_CONFIRMED"]
    if balanced_children_decisive:
        findings.append("BALANCED_MODULE_CHILDREN_DECISIVE")
    if any(c["tree_solver"]["max_split_depth_used"] >= 2 for c in sat_cases if c["k"] >= 2):
        findings.append("SAT_CHAIN_DEPTH_GROWTH")
    unsat_nodes = [c["tree_solver"]["tree_node_count"] for c in unsat_cases]
    strict_node_growth = all(a < b for a, b in zip(unsat_nodes, unsat_nodes[1:]))
    if strict_node_growth and unsat_cases[-1]["tree_solver"]["tree_node_count"] >= 31:
        findings.append("UNSAT_TAIL_TREE_SIZE_GROWTH")
    if all(c["full_binary_reference"]["exact_match"] for c in unsat_cases):
        findings.append("EXACT_FULL_BINARY_PATTERN")
    if any(c["tree_solver"]["status"] == "UNKNOWN_DEPTH_BUDGET" for c in sat_cases + unsat_cases):
        findings.append("DEPTH_BUDGET_RESIDUAL")

    global_nodes = [c["tree_solver"]["tree_node_count"] for c in unsat_cases]
    component_nodes = [c["componentwise"]["sum_nodes"] for c in unsat_cases]
    decomposition_gap = any(g > comp for g, comp in zip(global_nodes, component_nodes))
    if decomposition_gap:
        findings.append("COMPONENT_DECOMPOSITION_GAP_CANDIDATE")
    growth_findings = {"SAT_CHAIN_DEPTH_GROWTH", "UNSAT_TAIL_TREE_SIZE_GROWTH", "EXACT_FULL_BINARY_PATTERN"}
    if not any(x in findings for x in growth_findings):
        findings.append("NO_MODULAR_GROWTH_OBSERVED")

    if "DEPTH_BUDGET_RESIDUAL" in findings:
        next_gate = "R50G25Z_MINIMIZE_MODULAR_DEPTH_BUDGET_RESIDUAL"
    elif "COMPONENT_DECOMPOSITION_GAP_CANDIDATE" in findings:
        next_gate = "R50G25Z_ADD_CERTIFIED_COMPONENT_DECOMPOSITION_DOOR_AND_REPLAY_MODULAR_FAMILIES"
    elif any(x in findings for x in growth_findings):
        next_gate = "R50G25Z_SCALE_CONNECTED_BRANCHING_GROWTH_BEYOND_DISCONNECTED_MODULES"
    else:
        next_gate = "R50G25Z_SEARCH_CONNECTED_SAT_RESIDUAL_COMPOSITION"

    return {
        "gate": GATE,
        "parent_X_result_commit": PARENT_X_RESULT_COMMIT,
        "preregistration_commit": PREREG_COMMIT,
        "semantic_twin_audit": {
            "pair_count": len(twin_pairs),
            "all_42_exact_model_sets_equal": all(p["exact_model_sets_equal"] for p in twin_pairs),
            "all_42_deletion_twins_decisive_SAT": all(p["deletion_micro"]["terminal"] != "RESIDUAL_FIXPOINT" and p["deletion_micro"]["semantic_sat"] is True for p in twin_pairs),
            "all_42_flip_twins_residual": all(p["flip_micro"]["terminal"] == "RESIDUAL_FIXPOINT" for p in twin_pairs),
            "two_sided_x1_residual_count": len(balanced_candidates),
            "pairs": twin_pairs,
        },
        "balanced_module": {
            "formula_hash": balanced_hash,
            "deletion_twin_hash": balanced_pair["deletion_hash"],
            "source_clause": balanced_pair["source_clause"],
            "replacement_clause": balanced_pair["replacement_clause"],
            "CLV": list(r33.measure(module)),
            "model_count": len(balanced_models),
            "x1_model_partition": x1_partition,
            "lex_first_model_validation_only": {str(k): bool(v) for k, v in sorted(lex_first_model.items())},
            "conditioned_child_profiles": child_profiles,
            "both_x1_children_decisive_SAT": balanced_children_decisive,
        },
        "SAT_chain_cases": sat_cases,
        "UNSAT_tail_cases": unsat_cases,
        "SAT_chain_depth_vector": [c["tree_solver"]["max_split_depth_used"] for c in sat_cases],
        "SAT_chain_node_vector": [c["tree_solver"]["tree_node_count"] for c in sat_cases],
        "UNSAT_tail_depth_vector": [c["tree_solver"]["max_split_depth_used"] for c in unsat_cases],
        "UNSAT_tail_node_vector": global_nodes,
        "UNSAT_tail_leaf_vector": [c["tree_solver"]["leaf_count"] for c in unsat_cases],
        "UNSAT_tail_componentwise_node_vector": component_nodes,
        "findings": findings,
        "verdict": "__".join(findings),
        "next_gate": next_gate,
        "interpretation_contract": {
            "same_Boolean_function_different_micro_behavior_is_syntax_sensitivity_not_complexity_lower_bound": True,
            "disconnected_component_tree_growth_is_not_general_SAT_lower_bound": True,
            "finite_k_is_not_asymptotic_proof": True,
            "full_binary_pattern_on_finite_k_is_not_P_vs_NP_resolution": True,
            "component_decomposition_if_added_requires_certificate_and_cost_audit": True,
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
