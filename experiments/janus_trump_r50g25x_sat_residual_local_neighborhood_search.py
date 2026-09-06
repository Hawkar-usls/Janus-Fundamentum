from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path

import janus_trump_r50g25w_fano_minus_one_module_tree_growth as r50g25w

GATE = "JANUS_TRUMP_R50G25X_SEARCH_FOR_SAT_RESIDUAL_MODULE_OR_COMPONENT_DECOMPOSITION_GAP"
PARENT_W_RESULT_COMMIT = "bb20fa204cc63c3544cbfd795e854be531cfb822"
PREREG_COMMIT = "22d07ee1a193024e144de79a2c72d7930f58062a"
FANO_HASH = "466163011411ccd10520539fb80f0bec7a9de934400961cfa6a25f1c58c38a00"
MODULE_HASH = "06c6be429b38d5dcfc8939ff0324c73679b37b143a56a27bed77ca070498c302"
DELETED_CLAUSE = (-3, -5, -6)


def all_models(r33, formula, universe=range(1, 8)):
    formula = r33.canonical_formula(formula)
    vs = list(universe)
    out = []
    for bits in itertools.product((False, True), repeat=len(vs)):
        assignment = dict(zip(vs, bits))
        if r33.eval_formula(formula, assignment):
            out.append(assignment)
    return out


def incidence_connected(formula):
    clauses = list(formula)
    variables = sorted({abs(l) for c in clauses for l in c})
    if not variables:
        return True, 0
    adj = {v: set() for v in variables}
    for clause in clauses:
        cvs = sorted({abs(l) for l in clause})
        for i, u in enumerate(cvs):
            for v in cvs[i + 1:]:
                adj[u].add(v)
                adj[v].add(u)
    seen = set()
    components = 0
    for start in variables:
        if start in seen:
            continue
        components += 1
        stack = [start]
        seen.add(start)
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
    return components == 1, components


def candidate_record(family, parameter, parameter_index, formula, r50g23, r35b, r33, r47j):
    formula = r33.canonical_formula(formula)
    formula_hash = r50g23.r50g4.fhash(formula)
    models = all_models(r33, formula)
    exact_sat = bool(models)
    connected, component_count = incidence_connected(formula)
    micro = r50g25w.r50g25v.r50g25u.r50g25t.r50g25s.r50g25r.r50g25g.micro_normalize(
        formula, r50g23, r35b, r33, r47j
    )
    micro_terminal_raw = micro.get("terminal")
    micro_terminal = micro_terminal_raw if micro_terminal_raw is not None else "RESIDUAL_FIXPOINT"
    micro_semantic_sat = micro.get("semantic_sat")
    if micro_terminal_raw is not None and micro_semantic_sat is not None:
        if bool(micro_semantic_sat) != exact_sat:
            raise AssertionError((
                "R50G25X_SEMANTIC_MISMATCH",
                family,
                parameter,
                formula_hash,
                exact_sat,
                micro_semantic_sat,
                micro_terminal,
            ))
    sat_residual = exact_sat and micro_terminal_raw is None
    ledger = micro.get("ledger", {})
    return {
        "family": family,
        "parameter": parameter,
        "parameter_index": parameter_index,
        "formula_hash": formula_hash,
        "CLV": list(r33.measure(formula)),
        "connected": connected,
        "incidence_variable_component_count": component_count,
        "exact_truth_validation": {
            "assignment_space_checked": 128,
            "model_count": len(models),
            "sat": exact_sat,
            "validation_only_not_algorithmic_authority": True,
        },
        "micro_terminal": micro_terminal,
        "micro_semantic_sat": micro_semantic_sat,
        "micro_final_CLV": micro.get("final_CLV"),
        "micro_round_count": micro.get("round_count"),
        "micro_restart_count": micro.get("restart_count"),
        "micro_RUP_successful_strengthenings": int(ledger.get("RUP_successful_strengthenings", 0)),
        "micro_RUP_checks": int(ledger.get("RUP_checks", 0)),
        "micro_ledger": ledger,
        "SAT_residual": sat_residual,
        "formula": [list(c) for c in formula],
    }


def all_non_tautological_clauses_width1_to3(r33):
    clauses = []
    for width in (1, 2, 3):
        for vs in itertools.combinations(range(1, 8), width):
            for signs in itertools.product((False, True), repeat=width):
                clause = r33.canonical_clause(v if sign else -v for v, sign in zip(vs, signs))
                clauses.append(clause)
    if len(clauses) != 378 or len(set(clauses)) != 378:
        raise AssertionError(("R50G25X_RAW_CLAUSE_UNIVERSE_DRIFT", len(clauses), len(set(clauses))))
    return clauses


def clause_satisfied(clause, assignment):
    return any(bool(assignment[abs(l)]) == (l > 0) for l in clause)


def run():
    _b, r50g23, r35b, r33, r47j = (
        r50g25w.r50g25v.r50g25u.r50g25t.r50g25s.r50g25r.r50g25g._chain()
    )
    fano, module = r50g25w.build_fano_and_module(r33, r50g23)
    if r50g23.r50g4.fhash(fano) != FANO_HASH:
        raise AssertionError("R50G25X_FANO_HASH_DRIFT")
    if r50g23.r50g4.fhash(module) != MODULE_HASH or DELETED_CLAUSE in module:
        raise AssertionError(("R50G25X_MODULE_DRIFT", r50g23.r50g4.fhash(module)))

    module_models = all_models(r33, module)
    if len(module_models) != 5:
        raise AssertionError(("R50G25X_MODULE_MODEL_COUNT_DRIFT", len(module_models)))

    cases = []
    family_parameter_counts = Counter()

    # Family A: all 14 single-clause deletions of Fano.
    for idx, clause in enumerate(fano):
        formula = r33.canonical_formula(c for j, c in enumerate(fano) if j != idx)
        rec = candidate_record(
            "A_SINGLE_CLAUSE_DELETION",
            {"removed_clause_index": idx, "removed_clause": list(clause)},
            idx,
            formula,
            r50g23,
            r35b,
            r33,
            r47j,
        )
        if rec["exact_truth_validation"]["model_count"] != 5:
            raise AssertionError(("R50G25X_T_DELETION_MODEL_COUNT_DRIFT", idx, rec["exact_truth_validation"]))
        cases.append(rec)
        family_parameter_counts[rec["family"]] += 1

    # Family B: replace each Fano clause by its one-literal sign-flipped variant.
    flip_index = 0
    for clause_index, clause in enumerate(fano):
        for literal_position, lit in enumerate(clause):
            replacement = list(clause)
            replacement[literal_position] = -int(lit)
            replacement = r33.canonical_clause(replacement)
            formula = r33.canonical_formula(
                [c for j, c in enumerate(fano) if j != clause_index] + [replacement]
            )
            rec = candidate_record(
                "B_SINGLE_LITERAL_FLIP_REPLACEMENT",
                {
                    "source_clause_index": clause_index,
                    "source_clause": list(clause),
                    "literal_position": literal_position,
                    "flipped_literal_from": int(lit),
                    "replacement_clause": list(replacement),
                },
                flip_index,
                formula,
                r50g23,
                r35b,
                r33,
                r47j,
            )
            cases.append(rec)
            family_parameter_counts[rec["family"]] += 1
            flip_index += 1
    if flip_index != 42:
        raise AssertionError(("R50G25X_FLIP_COUNT_DRIFT", flip_index))

    # Family C: all width 1..3 clauses entailed by the canonical SAT module.
    raw_clauses = all_non_tautological_clauses_width1_to3(r33)
    module_set = set(module)
    entailed = []
    for clause in raw_clauses:
        if clause in module_set:
            continue
        if all(clause_satisfied(clause, m) for m in module_models):
            entailed.append(clause)
    entailed = sorted(set(entailed))
    for idx, clause in enumerate(entailed):
        formula = r33.canonical_formula(list(module) + [clause])
        rec = candidate_record(
            "C_ENTAILED_WIDTH1_TO3_ADDITION",
            {"added_clause": list(clause), "entailed_by_all_5_module_models": True},
            idx,
            formula,
            r50g23,
            r35b,
            r33,
            r47j,
        )
        if rec["exact_truth_validation"]["model_count"] != 5:
            raise AssertionError(("R50G25X_ENTAILED_ADDITION_MODEL_SET_DRIFT", clause, rec["exact_truth_validation"]))
        cases.append(rec)
        family_parameter_counts[rec["family"]] += 1

    if family_parameter_counts["A_SINGLE_CLAUSE_DELETION"] != 14:
        raise AssertionError(family_parameter_counts)
    if family_parameter_counts["B_SINGLE_LITERAL_FLIP_REPLACEMENT"] != 42:
        raise AssertionError(family_parameter_counts)

    hashes = Counter(c["formula_hash"] for c in cases)
    terminal_hist = Counter(c["micro_terminal"] for c in cases)
    exact_status_hist = Counter("SAT" if c["exact_truth_validation"]["sat"] else "UNSAT" for c in cases)
    residuals = [c for c in cases if c["SAT_residual"]]
    residual_family_hist = Counter(c["family"] for c in residuals)
    connected_residual_count = sum(1 for c in residuals if c["connected"])

    residuals.sort(key=lambda c: (
        0 if c["connected"] else 1,
        c["CLV"][0],
        c["CLV"][1],
        c["formula_hash"],
        c["family"],
        c["parameter_index"],
    ))
    primary = residuals[0] if residuals else None

    if primary is None:
        verdict = "NO_SAT_RESIDUAL_IN_FROZEN_LOCAL_NEIGHBORHOOD"
        next_gate = "R50G25Y_PAIR_ADDITIONS_EXTENSION_GADGET_OR_CONNECTED_SAT_RESIDUAL_SEARCH"
    elif primary["family"] == "A_SINGLE_CLAUSE_DELETION":
        verdict = "SAT_RESIDUAL_FOUND_SINGLE_DELETION"
        next_gate = "R50G25Y_BUILD_MODULAR_BRANCHING_GROWTH_FROM_VERIFIED_SAT_RESIDUAL"
    elif primary["family"] == "B_SINGLE_LITERAL_FLIP_REPLACEMENT":
        verdict = "SAT_RESIDUAL_FOUND_SINGLE_LITERAL_FLIP"
        next_gate = "R50G25Y_BUILD_MODULAR_BRANCHING_GROWTH_FROM_VERIFIED_SAT_RESIDUAL"
    else:
        verdict = "SAT_RESIDUAL_FOUND_ENTAILED_ADDITION"
        next_gate = "R50G25Y_BUILD_MODULAR_BRANCHING_GROWTH_FROM_VERIFIED_SAT_RESIDUAL"

    return {
        "gate": GATE,
        "parent_W_result_commit": PARENT_W_RESULT_COMMIT,
        "preregistration_commit": PREREG_COMMIT,
        "source": {
            "Fano_hash": FANO_HASH,
            "canonical_module_hash": MODULE_HASH,
            "canonical_module_model_count": len(module_models),
        },
        "candidate_contract": {
            "A_parameter_cases": 14,
            "B_parameter_cases": 42,
            "C_raw_clause_universe": 378,
            "C_entailed_addition_candidate_count": len(entailed),
            "C_entailed_clauses": [list(c) for c in entailed],
            "total_executed_parameter_cases": len(cases),
            "unique_formula_hash_count": len(hashes),
            "hash_collision_case_count": sum(v - 1 for v in hashes.values() if v > 1),
            "entailment_candidate_generation_fixed_n7_oracle_only": True,
        },
        "exact_status_partition": dict(sorted(exact_status_hist.items())),
        "micro_terminal_partition": dict(sorted(terminal_hist.items())),
        "SAT_residual_count": len(residuals),
        "connected_SAT_residual_count": connected_residual_count,
        "SAT_residual_family_partition": dict(sorted(residual_family_hist.items())),
        "primary_SAT_residual": primary,
        "all_SAT_residuals": residuals,
        "all_cases": cases,
        "verdict": verdict,
        "next_gate": next_gate,
        "interpretation_contract": {
            "exact_n7_enumeration_is_validation_only": True,
            "oracle_assisted_entailed_candidate_generation_is_not_general_algorithm": True,
            "SAT_residual_is_not_hard_for_all_solvers": True,
            "no_local_residual_is_not_no_residual_exists": True,
            "finite_local_neighborhood_is_not_universal_coverage": True,
        },
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    out = run()
    text = json.dumps(out, sort_keys=True, indent=2)
    if args.out:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
