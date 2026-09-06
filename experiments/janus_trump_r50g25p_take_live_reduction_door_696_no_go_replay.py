from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r50g25m_semantically_admissible_cover_or_no_go as r50g25m
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g

GATE = "JANUS_TRUMP_R50G25P_TAKE_LIVE_REDUCTION_DOOR_REPLAY_ACROSS_696_ADDITIVE_NO_GO_TARGETS"
EXPECTED_TARGETS = 1212
EXPECTED_NO_GO = 696


def semantic_binary_no_go(target, r33):
    _vs, models, _truth = r50g25m.exact_models(r33, target)
    reqs, additions = r50g25m.requirement_system(target)
    entailed = [c for c in additions if r50g25m.clause_entailed_by_models(r33, models, c)]
    a = r50g25m.r50g25b.r50g25a
    support = [0] * len(reqs)
    for clause in entailed:
        for i, (kind, row) in enumerate(reqs):
            if r50g25m.hit_requirement(a, kind, row, clause):
                support[i] += 1
    unsupported = [i for i, n in enumerate(support) if n == 0]
    return bool(unsupported), unsupported[0] if unsupported else None


def bce_step_certificate(r33, formula, record):
    clause = tuple(int(x) for x in record["clause"])
    lit = int(record["blocking_literal"])
    if clause not in formula or lit not in clause:
        return {"pass": False, "reason": "SOURCE_CLAUSE_OR_LITERAL_MISSING"}, None
    cset = set(clause)
    parents = []
    ok = True
    for other in formula:
        if -lit not in other:
            continue
        rr = (cset - {lit}) | (set(other) - {-lit})
        taut = any(-x in rr for x in rr)
        witnesses = sorted({abs(x) for x in rr if -x in rr})
        parents.append({
            "opposite_parent": list(other),
            "resolvent": list(r33.canonical_clause(rr)),
            "tautological": taut,
            "tautology_witness_variables": witnesses,
        })
        ok = ok and taut
    transformed = r33.canonical_formula(c for c in formula if c != clause)
    return {
        "pass": ok,
        "clause": list(clause),
        "blocking_literal": lit,
        "opposite_parent_count": len(parents),
        "opposite_parents": parents,
    }, transformed


def bve_step_certificate(r33, formula, record):
    cand = r33.bve_candidate(formula)
    if cand is None:
        return {"pass": False, "reason": "NO_BVE_CANDIDATE"}, None
    x, pos, neg, resolvents, transformed = cand
    expected = {
        "var": int(x),
        "positive": [list(c) for c in pos],
        "negative": [list(c) for c in neg],
        "resolvents": [list(c) for c in resolvents],
    }
    observed = {
        "var": int(record["var"]),
        "positive": record["positive"],
        "negative": record["negative"],
        "resolvents": record["resolvents"],
    }
    return {
        "pass": expected == observed,
        "pivot": int(x),
        "positive_parent_count": len(pos),
        "negative_parent_count": len(neg),
        "resolvent_count": len(resolvents),
        "expected_record_core": expected,
    }, transformed


def one_step_semantic_reconstruction_audit(r33, target, first_record, transformed):
    before_vs, before_models, _before_truth = r50g25m.exact_models(r33, target)
    after_vs, after_models, _after_truth = r50g25m.exact_models(r33, transformed)

    original_to_reduced_failures = sum(1 for a in before_models if not r33.eval_formula(transformed, a))
    fake = {"history": [first_record]}
    reconstruction_failures = 0
    for a in after_models:
        rec = r33.reconstruct_model(fake, dict(a))
        if not r33.eval_formula(target, rec):
            reconstruction_failures += 1

    return {
        "before_variable_count": len(before_vs),
        "after_variable_count": len(after_vs),
        "before_model_count": len(before_models),
        "after_model_count": len(after_models),
        "SAT_status_equal": bool(before_models) == bool(after_models),
        "original_to_reduced_failure_count": original_to_reduced_failures,
        "reduced_model_reconstruction_failure_count": reconstruction_failures,
        "pass": (
            bool(before_models) == bool(after_models)
            and original_to_reduced_failures == 0
            and reconstruction_failures == 0
        ),
    }


def run():
    parent = r50g25m.run()
    if parent["verdict"] != "EXPLICIT_NO_GO_FOR_SEMANTICS_PRESERVING_EXISTING_VARIABLE_BINARY_COVER":
        raise AssertionError(("R50G25P_PARENT_M_VERDICT_DRIFT", parent["verdict"]))
    if parent["explicit_binary_cover_no_go_target_count"] != EXPECTED_NO_GO:
        raise AssertionError(("R50G25P_PARENT_NO_GO_COUNT_DRIFT", parent["explicit_binary_cover_no_go_target_count"]))

    _parent_states, unique = r50g25m.r50g25b.rebuild_unique_states()
    if len(unique) != EXPECTED_TARGETS:
        raise AssertionError(("R50G25P_UNIQUE_TARGET_DRIFT", len(unique)))

    _b, r50g23, r35b, r33, r47j = r50g25g._chain()

    no_go_count = 0
    first_door_hist = Counter()
    full_r33_terminal_hist = Counter()
    micro_terminal_hist = Counter()
    micro_rup_hist = Counter()
    micro_restart_hist = Counter()
    certificate_failure_count = 0
    semantic_reconstruction_failure_count = 0
    strict_descent_failure_count = 0
    full_terminal_failure_count = 0
    examples = []
    failures = []

    for _key, entry in sorted(unique.items(), key=lambda kv: (kv[1]["forced_CLV"], kv[0])):
        target = r50g25m.canon(entry["forced_formula"])
        is_no_go, first_unsupported = semantic_binary_no_go(target, r33)
        if not is_no_go:
            continue
        no_go_count += 1
        state_hash = r50g23.r50g4.fhash(target)

        baseline = r33.simplify(target)
        history = baseline.get("history", [])
        if not history:
            certificate_failure_count += 1
            failures.append({"state_hash": state_hash, "reason": "NO_LIVE_R33_HISTORY"})
            continue
        first = history[0]
        rule = str(first["rule"])
        first_door_hist[rule] += 1

        if rule == "BLOCKED_CLAUSE_ELIMINATION":
            cert, transformed = bce_step_certificate(r33, target, first)
        elif rule == "BOUNDED_VARIABLE_ELIMINATION":
            cert, transformed = bve_step_certificate(r33, target, first)
        else:
            cert, transformed = {"pass": False, "reason": "FIRST_RULE_NOT_BCE_OR_BVE", "rule": rule}, None

        if transformed is None or not cert.get("pass"):
            certificate_failure_count += 1
            if len(failures) < 30:
                failures.append({"state_hash": state_hash, "reason": "FIRST_DOOR_CERTIFICATE_FAIL", "rule": rule, "certificate": cert})
            continue

        before_measure = tuple(r33.measure(target))
        after_measure = tuple(r33.measure(transformed))
        strict_descent = after_measure < before_measure
        if not strict_descent:
            strict_descent_failure_count += 1

        sem = one_step_semantic_reconstruction_audit(r33, target, first, transformed)
        if not sem["pass"]:
            semantic_reconstruction_failure_count += 1
            if len(failures) < 30:
                failures.append({"state_hash": state_hash, "reason": "ONE_STEP_SEMANTIC_RECONSTRUCTION_FAIL", "rule": rule, "semantic": sem})

        terminal = str(baseline.get("terminal"))
        full_r33_terminal_hist[terminal] += 1
        micro = r50g25g.micro_normalize(target, r50g23, r35b, r33, r47j)
        micro_term = str(micro.get("terminal")) if micro.get("terminal") is not None else "RESIDUAL_FIXPOINT"
        micro_terminal_hist[micro_term] += 1
        micro_rup_hist[int(micro.get("ledger", {}).get("RUP_successful_strengthenings", 0))] += 1
        micro_restart_hist[int(micro.get("restart_count", 0))] += 1
        if micro.get("semantic_sat") is None:
            full_terminal_failure_count += 1

        if len(examples) < 20:
            examples.append({
                "state_hash": state_hash,
                "first_unsupported_requirement_index": first_unsupported,
                "first_live_rule": rule,
                "CLV_before": list(before_measure),
                "CLV_after_first_live_rule": list(after_measure),
                "certificate": cert,
                "one_step_semantic_reconstruction": sem,
                "full_R33_terminal": terminal,
                "full_R33_rule_applications": int(baseline.get("total_rule_applications", 0)),
                "micro_terminal": micro_term,
                "micro_RUP_strengthenings": int(micro.get("ledger", {}).get("RUP_successful_strengthenings", 0)),
                "micro_restart_count": int(micro.get("restart_count", 0)),
            })

    if no_go_count != EXPECTED_NO_GO:
        raise AssertionError(("R50G25P_REBUILT_NO_GO_COUNT_DRIFT", no_go_count))

    all_first_live_certified = certificate_failure_count == 0
    all_one_step_semantics_clean = semantic_reconstruction_failure_count == 0
    all_strict_descent = strict_descent_failure_count == 0
    all_micro_terminal = full_terminal_failure_count == 0

    if not all_first_live_certified:
        verdict = "LIVE_REDUCTION_DOOR_CERTIFICATE_FAILURE"
        next_gate = "R50G25Q_FIRST_DOOR_CERTIFICATE_FAILURE_FORENSICS"
    elif not all_one_step_semantics_clean:
        verdict = "LIVE_REDUCTION_DOOR_RECONSTRUCTION_FAILURE"
        next_gate = "R50G25Q_RECONSTRUCTION_FAILURE_FORENSICS"
    elif not all_strict_descent:
        verdict = "LIVE_REDUCTION_DOOR_PROGRESS_FAILURE"
        next_gate = "R50G25Q_PROGRESS_MEASURE_FAILURE_FORENSICS"
    elif not all_micro_terminal:
        verdict = "LIVE_REDUCTION_DOOR_696_HAS_RESIDUAL"
        next_gate = "R50G25Q_696_RESIDUAL_FIXPOINT_FORENSICS"
    else:
        verdict = "ALL_696_ADDITIVE_NO_GO_TARGETS_HAVE_CERTIFIED_LIVE_BCE_OR_BVE_REDUCTION_DOOR_AND_TERMINATE"
        next_gate = "R50G25Q_HARDENING_VS_SOLVER_ROLE_SEPARATION_AND_OUTER_COUNTEREXAMPLE_GATE"

    return {
        "gate": GATE,
        "parent_M_run": 34036862384,
        "parent_O_run": 34037730521,
        "coverage_contract": {
            "frozen_target_count": EXPECTED_TARGETS,
            "exact_additive_no_go_subset_count": EXPECTED_NO_GO,
            "new_source_skeletons_added": 0,
            "no_cover_clauses_added": True,
            "no_family_expansion": True,
        },
        "evaluated_additive_no_go_target_count": no_go_count,
        "first_live_reduction_door_partition": dict(sorted(first_door_hist.items())),
        "first_door_certificate_failure_count": certificate_failure_count,
        "one_step_semantic_reconstruction_failure_count": semantic_reconstruction_failure_count,
        "strict_measure_descent_failure_count": strict_descent_failure_count,
        "full_micro_terminal_failure_count": full_terminal_failure_count,
        "full_R33_terminal_partition": dict(sorted(full_r33_terminal_hist.items())),
        "micro_terminal_partition": dict(sorted(micro_terminal_hist.items())),
        "micro_RUP_strengthening_histogram": {str(k): int(v) for k, v in sorted(micro_rup_hist.items())},
        "micro_restart_histogram": {str(k): int(v) for k, v in sorted(micro_restart_hist.items())},
        "examples": examples,
        "failures": failures[:30],
        "verdict": verdict,
        "next_gate": next_gate,
        "interpretation_contract": {
            "additive_cover_no_go_does_not_mean_solver_no_go": True,
            "BCE_and_BVE_are_nonadditive_SAT_preserving_reduction_doors_with_reconstruction": True,
            "hardening_experiments_must_not_be_confused_with_required_solver_steps": True,
            "696_frozen_targets_are_not_outer_or_universal_coverage": True,
            "full_micro_terminal_on_696_does_not_prove_arbitrary_3CNF_termination": True,
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
