from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path

import janus_trump_r50g25b_source_realizability_minimum_joint_debt as r50g25b
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g

GATE = "JANUS_TRUMP_R50G25M_SEMANTICALLY_ADMISSIBLE_BINARY_COVER_OR_EXPLICIT_NO_GO"
EXPECTED_UNIQUE = 1212
PIVOT = 1


def canon(formula):
    return r50g25b.canon(formula)


def exact_models(r33, formula):
    formula = r33.canonical_formula(formula)
    vs = list(r33.variables(formula))
    if len(vs) > 6:
        raise AssertionError(("R50G25M_EXACT_ORACLE_DOMAIN_DRIFT", len(vs)))
    models = []
    truth = []
    for values in itertools.product((False, True), repeat=len(vs)):
        assignment = dict(zip(vs, values))
        sat = bool(r33.eval_formula(formula, assignment))
        truth.append("1" if sat else "0")
        if sat:
            models.append(assignment)
    return vs, models, "".join(truth)


def clause_entailed_by_models(r33, models, clause):
    return all(r33.eval_clause(tuple(clause), assignment) for assignment in models)


def requirement_system(formula):
    a = r50g25b.r50g25a
    formula = canon(formula)
    bces = a.blocked_candidates(formula)
    bves = a.all_bve_candidates(formula)
    reqs = [("BCE", row) for row in bces] + [("BVE", row) for row in bves]
    additions = sorted(a.all_binary_additions(formula))
    return reqs, additions


def hit_requirement(a, kind, row, clause):
    if kind == "BCE":
        return a.bce_requirement_hit(row, clause)
    x = int(row["pivot"])
    return x in clause or -x in clause


def run():
    _parent, unique = r50g25b.rebuild_unique_states()
    if len(unique) != EXPECTED_UNIQUE:
        raise AssertionError(("R50G25M_UNIQUE_TARGET_DRIFT", len(unique)))

    _b, r50g23, r35b, r33, r47j = r50g25g._chain()
    r42 = r50g23.r42
    a = r50g25b.r50g25a

    no_go_count = 0
    admissible_cover_count = 0
    semantic_cover_terminal_count = 0
    semantic_cover_residual_count = 0
    semantic_equivalence_failure_count = 0
    sat_target_count = 0
    unsat_target_count = 0
    admissible_cover_size_hist = Counter()
    uncovered_req_kind_hist = Counter()
    entailed_binary_count_hist = Counter()
    terminal_hist = Counter()
    smallest_no_go = None
    no_go_examples = []

    for _key, entry in sorted(unique.items(), key=lambda kv: (kv[1]["forced_CLV"], kv[0])):
        target = canon(entry["forced_formula"])
        state_hash = r50g23.r50g4.fhash(target)
        vs, models, target_truth = exact_models(r33, target)
        if models:
            sat_target_count += 1
        else:
            unsat_target_count += 1

        reqs, additions = requirement_system(target)
        entailed = [c for c in additions if clause_entailed_by_models(r33, models, c)]
        entailed_binary_count_hist[len(entailed)] += 1

        masks = []
        support_counts = [0] * len(reqs)
        for clause in entailed:
            mask = 0
            for i, (kind, row) in enumerate(reqs):
                if hit_requirement(a, kind, row, clause):
                    mask |= 1 << i
                    support_counts[i] += 1
            masks.append((tuple(clause), mask))

        unsupported = [i for i, count in enumerate(support_counts) if count == 0]
        if unsupported:
            no_go_count += 1
            i = unsupported[0]
            kind, row = reqs[i]
            uncovered_req_kind_hist[kind] += 1
            witness = {
                "state_hash": state_hash,
                "target_CLV": list(r33.measure(target)),
                "target_sat": bool(models),
                "target_model_count": len(models),
                "requirement_count": len(reqs),
                "entailed_binary_clause_count": len(entailed),
                "first_unsupported_requirement_index": i,
                "first_unsupported_requirement_kind": kind,
                "first_unsupported_requirement": row,
                "all_admissible_binary_supports_checked": len(entailed),
                "claim": "No conjunction of semantics-preserving existing-variable binary clauses can cover this requirement, because every conjunct of an equivalent strengthening must itself be entailed by T.",
            }
            if smallest_no_go is None:
                smallest_no_go = witness
            if len(no_go_examples) < 20:
                no_go_examples.append(witness)
            continue

        full = (1 << len(reqs)) - 1
        covered = 0
        chosen = []
        while covered != full:
            missing = next(i for i in range(len(reqs)) if not (covered >> i) & 1)
            selected = next((x for x in masks if (x[1] >> missing) & 1), None)
            if selected is None:
                raise AssertionError(("R50G25M_INTERNAL_SUPPORT_DRIFT", state_hash, missing))
            chosen.append(selected[0])
            covered |= selected[1]

        admissible_cover_count += 1
        admissible_cover_size_hist[len(chosen)] += 1
        augmented = canon(r42.subsumption_minimize(list(target) + chosen))
        _vs2, _models2, augmented_truth = exact_models(r33, augmented)
        if target_truth != augmented_truth:
            semantic_equivalence_failure_count += 1
            continue

        micro = r50g25g.micro_normalize(augmented, r50g23, r35b, r33, r47j)
        term = str(micro.get("terminal")) if micro.get("terminal") is not None else "RESIDUAL_FIXPOINT"
        terminal_hist[term] += 1
        if micro.get("semantic_sat") is None:
            semantic_cover_residual_count += 1
        else:
            semantic_cover_terminal_count += 1

    if semantic_equivalence_failure_count:
        verdict = "IMPLEMENTATION_OR_ORACLE_FAILURE"
        next_gate = "R50G25N_SEMANTIC_EQUIVALENCE_REPLAY_FAILURE_FORENSICS"
    elif no_go_count:
        verdict = "EXPLICIT_NO_GO_FOR_SEMANTICS_PRESERVING_EXISTING_VARIABLE_BINARY_COVER"
        next_gate = "R50G25N_ALTERNATE_NONADDITIVE_OR_DERIVED_CLAUSE_COLLAPSE_DOOR"
    elif semantic_cover_residual_count:
        verdict = "SEMANTIC_BINARY_COVER_EXISTS_BUT_SCHEDULER_RESIDUAL"
        next_gate = "R50G25N_SEMANTIC_COVER_SCHEDULER_RESIDUAL_FORENSICS"
    else:
        verdict = "SEMANTICALLY_ADMISSIBLE_BINARY_COVER_1212_TERMINAL"
        next_gate = "R50G25N_POLYNOMIAL_CERTIFICATE_FOR_SEMANTIC_BINARY_COVER"

    return {
        "gate": GATE,
        "parent_L_run": 34036738431,
        "coverage_contract": {
            "frozen_target_count": EXPECTED_UNIQUE,
            "new_source_skeletons_added": 0,
            "exact_model_enumeration_is_existence_oracle_only": True,
            "claim_scope": "existing-variable binary clause conjunctions only",
        },
        "verdict": verdict,
        "SAT_target_count": sat_target_count,
        "UNSAT_target_count": unsat_target_count,
        "semantics_preserving_binary_cover_exists_count": admissible_cover_count,
        "explicit_binary_cover_no_go_target_count": no_go_count,
        "semantic_equivalence_failure_count": semantic_equivalence_failure_count,
        "semantic_cover_terminal_count": semantic_cover_terminal_count,
        "semantic_cover_residual_count": semantic_cover_residual_count,
        "admissible_cover_size_histogram": {str(k): int(v) for k, v in sorted(admissible_cover_size_hist.items())},
        "entailed_binary_clause_count_histogram": {str(k): int(v) for k, v in sorted(entailed_binary_count_hist.items())},
        "first_unsupported_requirement_kind_histogram": dict(sorted(uncovered_req_kind_hist.items())),
        "semantic_cover_terminal_partition": dict(sorted(terminal_hist.items())),
        "smallest_no_go_witness": smallest_no_go,
        "no_go_examples": no_go_examples,
        "next_gate": next_gate,
        "interpretation_contract": {
            "no_go_is_exact_for_existing_variable_binary_conjunctive_covers_on_the_witness": True,
            "no_go_does_not_exclude_extension_variables": True,
            "no_go_does_not_exclude_nonadditive_transformations": True,
            "no_go_does_not_exclude_other_derived_clause_families": True,
            "frozen_no_go_is_not_universal_3CNF_no_go": True,
        },
        "firewall": {
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
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
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
