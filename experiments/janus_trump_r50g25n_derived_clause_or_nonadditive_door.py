from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path

import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r50g25m_semantically_admissible_cover_or_no_go as r50g25m
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g

GATE = "JANUS_TRUMP_R50G25N_DERIVED_CLAUSE_OR_NONADDITIVE_DOOR"
TARGET_HASH = "6cf77b7f1acf5a0ca16edf24adb9ec936557a0418a00368ac2b494946c8fdd1e"
EXPECTED_CLV = (9, 25, 6)
EXPECTED_MODELS = 14
EXPECTED_REQUIREMENT = {
    "kind": "BCE",
    "clause": (2, 3, 5),
    "blocking_literal": 5,
    "opposite_parent_count": 1,
}


def find_target():
    _parent, unique = r50g25m.r50g25b.rebuild_unique_states()
    r50g23 = r50g25m.r50g25b.r50g25a.r50g24.r50g23
    for _key, entry in unique.items():
        target = r50g25m.canon(entry["forced_formula"])
        if r50g23.r50g4.fhash(target) == TARGET_HASH:
            return target
    raise AssertionError("R50G25N_TARGET_HASH_NOT_FOUND")


def target_requirement(target):
    reqs, _additions = r50g25m.requirement_system(target)
    for idx, (kind, row) in enumerate(reqs):
        if (
            kind == EXPECTED_REQUIREMENT["kind"]
            and tuple(row["clause"]) == EXPECTED_REQUIREMENT["clause"]
            and int(row["blocking_literal"]) == EXPECTED_REQUIREMENT["blocking_literal"]
            and int(row["opposite_parent_count"]) == EXPECTED_REQUIREMENT["opposite_parent_count"]
        ):
            return idx, kind, row
    raise AssertionError("R50G25N_EXPECTED_BCE_REQUIREMENT_NOT_FOUND")


def requirement_still_present(a, formula):
    for row in a.blocked_candidates(formula):
        if (
            tuple(row["clause"]) == EXPECTED_REQUIREMENT["clause"]
            and int(row["blocking_literal"]) == EXPECTED_REQUIREMENT["blocking_literal"]
        ):
            return True
    return False


def all_non_tautological_clauses(vs, r33):
    # Oracle-only finite forensic universe: each variable is absent/positive/negative.
    for states in itertools.product((0, 1, -1), repeat=len(vs)):
        if all(s == 0 for s in states):
            continue
        clause = []
        for v, state in zip(vs, states):
            if state == 1:
                clause.append(v)
            elif state == -1:
                clause.append(-v)
        yield r33.canonical_clause(clause)


def resolution_candidates(formula, r33):
    seen = set()
    existing = set(formula)
    for x in r33.variables(formula):
        pos = [c for c in formula if x in c]
        neg = [c for c in formula if -x in c]
        for p in pos:
            for n in neg:
                rr_set = (set(p) - {x}) | (set(n) - {-x})
                if any(-lit in rr_set for lit in rr_set):
                    continue
                rr = r33.canonical_clause(rr_set)
                if rr in existing or rr in seen:
                    continue
                seen.add(rr)
                yield {
                    "derived_clause": rr,
                    "pivot": int(x),
                    "positive_parent": p,
                    "negative_parent": n,
                    "certificate_kind": "ONE_STEP_RESOLUTION",
                }


def rup_strengthening_candidates(formula, r33):
    for source in formula:
        for removed in sorted(source, key=r35b.lit_key):
            strengthened = tuple(l for l in source if l != removed)
            assumptions = tuple(-l for l in sorted(strengthened, key=r35b.lit_key))
            if not r35b.independent_up_conflict_checker(formula, assumptions):
                continue
            yield {
                "source_clause": source,
                "removed_literal": int(removed),
                "derived_clause": strengthened,
                "assumptions": assumptions,
                "certificate_kind": "RUP_SINGLE_LITERAL_STRENGTHENING",
            }


def exact_truth(r33, formula):
    _vs, models, truth = r50g25m.exact_models(r33, formula)
    return models, truth


def run():
    parent = r50g25m.run()
    if parent["verdict"] != "EXPLICIT_NO_GO_FOR_SEMANTICS_PRESERVING_EXISTING_VARIABLE_BINARY_COVER":
        raise AssertionError(("R50G25N_PARENT_M_VERDICT_DRIFT", parent["verdict"]))
    if parent["smallest_no_go_witness"]["state_hash"] != TARGET_HASH:
        raise AssertionError("R50G25N_PARENT_SMALLEST_WITNESS_DRIFT")

    target = find_target()
    _b, r50g23, r35b_chain, r33, r47j = r50g25g._chain()
    r42 = r50g23.r42
    a = r50g25m.r50g25b.r50g25a

    if tuple(r33.measure(target)) != EXPECTED_CLV:
        raise AssertionError(("R50G25N_TARGET_CLV_DRIFT", r33.measure(target)))
    models, target_truth = exact_truth(r33, target)
    if len(models) != EXPECTED_MODELS:
        raise AssertionError(("R50G25N_TARGET_MODEL_COUNT_DRIFT", len(models)))

    req_index, req_kind, req_row = target_requirement(target)
    if req_kind != "BCE":
        raise AssertionError("R50G25N_EXPECTED_BCE_KIND_DRIFT")

    # Baseline is recorded only as context. N's success criterion is removal of
    # the specific unsupported BCE debt by a certified semantics-preserving step.
    baseline_r33 = r33.simplify(target)
    baseline_first_rule = baseline_r33["history"][0]["rule"] if baseline_r33.get("history") else None

    # Oracle-only existence audit across every clause over the existing variables.
    # This is explicitly NOT algorithmic authority.
    oracle_supports = []
    oracle_width_hist = Counter()
    vs = list(r33.variables(target))
    for clause in all_non_tautological_clauses(vs, r33):
        if not r50g25m.clause_entailed_by_models(r33, models, clause):
            continue
        if not a.bce_requirement_hit(req_row, clause):
            continue
        oracle_supports.append(clause)
        oracle_width_hist[len(clause)] += 1
    oracle_supports = sorted(set(oracle_supports), key=lambda c: (len(c), c))

    proof_candidates = []

    # One-step resolution additions are logical consequences by resolution.
    for cand in resolution_candidates(target, r33):
        clause = tuple(cand["derived_clause"])
        if not a.bce_requirement_hit(req_row, clause):
            continue
        if not r50g25m.clause_entailed_by_models(r33, models, clause):
            raise AssertionError(("R50G25N_RESOLUTION_SOUNDNESS_OR_ORACLE_DRIFT", cand))
        transformed = r50g25m.canon(r42.subsumption_minimize(list(target) + [clause]))
        _m2, truth2 = exact_truth(r33, transformed)
        if truth2 != target_truth:
            raise AssertionError(("R50G25N_RESOLUTION_SEMANTIC_DRIFT", cand))
        gone = not requirement_still_present(a, transformed)
        micro = r50g25g.micro_normalize(transformed, r50g23, r35b_chain, r33, r47j)
        proof_candidates.append({
            "certificate_kind": cand["certificate_kind"],
            "derived_clause": list(clause),
            "derived_width": len(clause),
            "pivot": cand["pivot"],
            "positive_parent": list(cand["positive_parent"]),
            "negative_parent": list(cand["negative_parent"]),
            "target_BCE_requirement_removed": gone,
            "transformed_CLV": list(r33.measure(transformed)),
            "micro_terminal": micro.get("terminal"),
            "micro_semantic_sat": micro.get("semantic_sat"),
            "micro_restarts": int(micro.get("restart_count", 0)),
            "micro_RUP_strengthenings": int(micro.get("ledger", {}).get("RUP_successful_strengthenings", 0)),
        })

    # RUP clause strengthening is equivalence preserving when the strengthened
    # clause is RUP; independent UP replay is the certificate checker.
    for cand in rup_strengthening_candidates(target, r33):
        clause = tuple(cand["derived_clause"])
        if not a.bce_requirement_hit(req_row, clause):
            continue
        transformed = r35b.replace_clause_with_subclause(target, tuple(cand["source_clause"]), clause)
        _m2, truth2 = exact_truth(r33, transformed)
        if truth2 != target_truth:
            raise AssertionError(("R50G25N_RUP_SEMANTIC_DRIFT", cand))
        gone = not requirement_still_present(a, transformed)
        micro = r50g25g.micro_normalize(transformed, r50g23, r35b_chain, r33, r47j)
        proof_candidates.append({
            "certificate_kind": cand["certificate_kind"],
            "source_clause": list(cand["source_clause"]),
            "removed_literal": cand["removed_literal"],
            "derived_clause": list(clause),
            "derived_width": len(clause),
            "assumptions": list(cand["assumptions"]),
            "independent_RUP_replay_pass": True,
            "target_BCE_requirement_removed": gone,
            "transformed_CLV": list(r33.measure(transformed)),
            "micro_terminal": micro.get("terminal"),
            "micro_semantic_sat": micro.get("semantic_sat"),
            "micro_restarts": int(micro.get("restart_count", 0)),
            "micro_RUP_strengthenings": int(micro.get("ledger", {}).get("RUP_successful_strengthenings", 0)),
        })

    proof_candidates.sort(key=lambda x: (
        not bool(x["target_BCE_requirement_removed"]),
        int(x["derived_width"]),
        str(x["certificate_kind"]),
        tuple(x["derived_clause"]),
    ))
    neutralizers = [x for x in proof_candidates if x["target_BCE_requirement_removed"]]

    if neutralizers:
        verdict = "ONE_STEP_CERTIFIED_DERIVED_CLAUSE_NEUTRALIZES_MINIMAL_BCE_NO_GO"
        next_gate = "R50G25O_DERIVED_DOOR_REPLAY_ACROSS_696_BINARY_NO_GO_TARGETS"
    elif oracle_supports:
        verdict = "ENTAILED_EXISTING_VARIABLE_SUPPORT_EXISTS_BUT_NOT_ONE_STEP_RUP_OR_RESOLUTION_DERIVED"
        next_gate = "R50G25O_PROOF_DERIVATION_CHAIN_FOR_MINIMUM_WIDTH_ENTAILED_SUPPORT"
    else:
        verdict = "EXACT_NO_GO_FOR_ANY_ADDITIVE_EXISTING_VARIABLE_ENTAILED_CLAUSE_ON_MINIMAL_WITNESS"
        next_gate = "R50G25O_NONADDITIVE_EQUIVALENCE_REWRITE_ON_MINIMAL_WITNESS"

    return {
        "gate": GATE,
        "parent_gate": parent["gate"],
        "parent_M_run": 34036862384,
        "target": {
            "state_hash": TARGET_HASH,
            "CLV": list(r33.measure(target)),
            "variable_count": len(vs),
            "exact_model_count": len(models),
            "baseline_first_R33_rule": baseline_first_rule,
            "unsupported_requirement_index": req_index,
            "unsupported_requirement": {
                "kind": req_kind,
                "clause": list(req_row["clause"]),
                "blocking_literal": int(req_row["blocking_literal"]),
                "opposite_parent_count": int(req_row["opposite_parent_count"]),
            },
        },
        "oracle_only_existing_variable_clause_support": {
            "enumerated_non_tautological_clause_count": (3 ** len(vs)) - 1,
            "support_count": len(oracle_supports),
            "minimum_support_width": min((len(c) for c in oracle_supports), default=None),
            "support_width_histogram": {str(k): int(v) for k, v in sorted(oracle_width_hist.items())},
            "first_supports": [list(c) for c in oracle_supports[:20]],
            "exact_model_enumeration_is_validation_or_existence_oracle_only": True,
        },
        "one_step_certified_candidate_count": len(proof_candidates),
        "one_step_certified_neutralizer_count": len(neutralizers),
        "best_one_step_certified_neutralizer": neutralizers[0] if neutralizers else None,
        "certified_candidates": proof_candidates[:40],
        "verdict": verdict,
        "next_gate": next_gate,
        "interpretation_contract": {
            "one_step_resolution_enumeration_is_polynomial_in_current_formula_size": True,
            "one_literal_RUP_candidate_enumeration_with_UP_checks_is_polynomial_in_current_formula_size": True,
            "oracle_all_clause_enumeration_is_not_algorithmic_authority": True,
            "oracle_all_clause_enumeration_is_exponential_in_variable_count": True,
            "derived_clause_success_on_one_witness_is_not_outer_coverage": True,
            "no_family_expansion": True,
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
