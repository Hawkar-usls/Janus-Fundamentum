from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r43_frozen_r42_counterexample_hunt as r43

R43_SEALED_COMMIT = "48fd0dd9b846d42ef0654eed6bfb2e041b013e16"
R43_EXECUTION_HEAD = "46c326e72ad525725617b0a69302df1401915a50"
R42_CONTROLLER_BLOB_SHA = "d71d7edb284a37bc7d7039c0d585d64cf2844de9"
SEALED_COUNTEREXAMPLE_SEED = 43004
SEALED_COUNTEREXAMPLE_INPUT_SHA256 = "eab8907cd5e97c244548797f226a91dfd0d43c196fb4461fb8880234c7de43a6"
EXPECTED_CASE_COUNT = 83


def canonical_sha256(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def outcome_row(ordinal: int, label: str, seed, formula, result: dict) -> dict:
    input_clv = tuple(int(x) for x in r33.measure(formula))
    terminal_clv = tuple(int(x) for x in result["terminal_measure_CLV"])
    delta_clv = tuple(a - b for a, b in zip(input_clv, terminal_clv))
    semantic_decided = bool(result["semantic_decided"])
    semantic_sat = result["semantic_sat"]

    if semantic_decided:
        if semantic_sat not in (True, False):
            raise AssertionError(("R44_DECIDED_WITHOUT_BOOLEAN_SEMANTICS", label, semantic_sat))
        if semantic_sat is True:
            replay = result.get("final_original_model_replay")
            if not replay or replay.get("pass") is not True:
                raise AssertionError(("R44_SAT_MODEL_REPLAY_MISSING_OR_FAILED", label))
    else:
        if semantic_sat is not None or result["terminal_status"] != "STALLED_FIXED_SUCCESSOR":
            raise AssertionError(("R44_NONSEMANTIC_STATUS_DRIFT", label, result["terminal_status"], semantic_sat))

    return {
        "ordinal": ordinal,
        "label": label,
        "seed": seed,
        "input_formula_sha256": r42.formula_hash(formula),
        "input_measure_CLV": list(input_clv),
        "terminal_formula_sha256": result["terminal_formula_hash"],
        "terminal_measure_CLV": list(terminal_clv),
        "delta_measure_CLV": list(delta_clv),
        "cycle_count": int(result["cycle_count"]),
        "SA_BVE_applications": int(result["SA_BVE_applications"]),
        "terminal_status": result["terminal_status"],
        "semantic_decided": semantic_decided,
        "semantic_sat": semantic_sat,
        "SAT_model_replay_pass": (
            result.get("final_original_model_replay", {}).get("pass") if semantic_sat is True else None
        ),
        "controller_execution_integrity": True,
    }


def truth_blind_signature(row: dict) -> Tuple[object, ...]:
    return (
        tuple(row["input_measure_CLV"]),
        tuple(row["delta_measure_CLV"]),
        int(row["cycle_count"]),
        int(row["SA_BVE_applications"]),
    )


def build_candidate_quotient(rows: Sequence[dict]) -> dict:
    groups: Dict[Tuple[object, ...], List[dict]] = defaultdict(list)
    membership_count: Dict[str, int] = defaultdict(int)
    for row in rows:
        groups[truth_blind_signature(row)].append(row)

    classes = []
    F = 0
    first_mixed_transport_failure = None
    stall_class_count = 0
    mixed_class_count = 0
    compressed_class_count = 0

    for signature in sorted(groups, key=repr):
        members = sorted(groups[signature], key=lambda r: int(r["ordinal"]))
        representative = members[0]
        rep_q = bool(representative["semantic_decided"])
        transport_records = []
        class_failures = 0
        q_values = set()
        for member in members:
            membership_count[member["label"]] += 1
            member_q = bool(member["semantic_decided"])
            q_values.add(member_q)
            ok = member_q == rep_q
            transport_records.append({
                "ordinal": member["ordinal"],
                "label": member["label"],
                "seed": member["seed"],
                "Q_semantic_decided": member_q,
                "transport_Q_matches_representative": ok,
            })
            if not ok:
                F += 1
                class_failures += 1
                if first_mixed_transport_failure is None:
                    first_mixed_transport_failure = {
                        "representative": {
                            "ordinal": representative["ordinal"],
                            "label": representative["label"],
                            "seed": representative["seed"],
                            "Q_semantic_decided": rep_q,
                        },
                        "member": {
                            "ordinal": member["ordinal"],
                            "label": member["label"],
                            "seed": member["seed"],
                            "Q_semantic_decided": member_q,
                        },
                        "signature": {
                            "input_measure_CLV": list(signature[0]),
                            "delta_measure_CLV": list(signature[1]),
                            "cycle_count": signature[2],
                            "SA_BVE_applications": signature[3],
                        },
                    }
        if not rep_q:
            stall_class_count += 1
        if len(q_values) > 1:
            mixed_class_count += 1
        if len(members) > 1:
            compressed_class_count += 1
        classes.append({
            "signature": {
                "input_measure_CLV": list(signature[0]),
                "delta_measure_CLV": list(signature[1]),
                "cycle_count": signature[2],
                "SA_BVE_applications": signature[3],
            },
            "signature_sha256": canonical_sha256(list(signature)),
            "representative": {
                "ordinal": representative["ordinal"],
                "label": representative["label"],
                "seed": representative["seed"],
                "Q_semantic_decided": rep_q,
            },
            "member_count": len(members),
            "member_ordinals": [m["ordinal"] for m in members],
            "member_seeds": [m["seed"] for m in members],
            "Q_values_present": sorted(q_values),
            "transport_checks": len(members),
            "transport_failures": class_failures,
            "transport_certificate_sha256": canonical_sha256(transport_records),
        })

    labels = [r["label"] for r in rows]
    R = sum(1 for label in labels if membership_count[label] != 1)
    return {
        "N_raw_states": len(rows),
        "K_quotient_classes": len(groups),
        "R_uncovered_or_nonexact_membership": R,
        "F_transport_failures": F,
        "compression_ratio_N_over_K": (len(rows) / len(groups)) if groups else None,
        "QUOTIENT_COMPRESSION_OBSERVED": len(groups) < len(rows),
        "CANDIDATE_QUOTIENT_TRANSPORT_SOUND": F == 0,
        "stall_representative_class_count": stall_class_count,
        "mixed_Q_class_count": mixed_class_count,
        "compressed_class_count": compressed_class_count,
        "first_mixed_transport_failure": first_mixed_transport_failure,
        "classes": classes,
        "class_ledger_sha256": canonical_sha256(classes),
    }


def pyramid_controls(depths: Iterable[int] = (1, 2, 3, 4, 5, 6)) -> dict:
    results = []
    for depth in depths:
        N = 4 ** int(depth)
        symmetric = [{"level": depth, "property": True, "boundary": "shared"} for _ in range(N)]
        broken = [dict(x) for x in symmetric]
        broken[-1]["property"] = False
        boundary = [{"level": depth, "property": True, "boundary": f"path:{i}"} for i in range(N)]

        def safe_key(x):
            return (x["level"], x["property"], x["boundary"])

        def unsafe_key(x):
            return (x["level"],)

        def evaluate(states, key_fn):
            groups = defaultdict(list)
            for state in states:
                groups[key_fn(state)].append(state)
            F = 0
            for members in groups.values():
                rep = members[0]
                for member in members:
                    if (
                        member["level"] != rep["level"]
                        or member["property"] != rep["property"]
                        or member["boundary"] != rep["boundary"]
                    ):
                        F += 1
            return {"N": len(states), "K": len(groups), "R": 0, "F": F}

        sym = evaluate(symmetric, safe_key)
        broken_unsafe = evaluate(broken, unsafe_key)
        bound = evaluate(boundary, safe_key)
        expectations = {
            "symmetric_N": sym["N"] == N,
            "symmetric_K1_R0_F0": sym["K"] == 1 and sym["R"] == 0 and sym["F"] == 0,
            "broken_unsafe_detected": broken_unsafe["K"] == 1 and broken_unsafe["F"] > 0,
            "boundary_K_equals_N": bound["K"] == N and bound["F"] == 0,
        }
        results.append({
            "depth": depth,
            "symmetric": sym,
            "broken_unsafe": broken_unsafe,
            "boundary_dependency": bound,
            "expectations": expectations,
            "pass": all(expectations.values()),
        })
    return {
        "source_design_reference": "Lvl6_pyr_1_6_trimmer.3mf",
        "role": "ADVERSARIAL_DESIGN_REFERENCE_NOT_PROOF",
        "depth_results": results,
        "pass": all(r["pass"] for r in results),
    }


def run_r44() -> dict:
    cases = list(r43.frozen_search_cases())
    if len(cases) != EXPECTED_CASE_COUNT:
        raise AssertionError(("R44_FROZEN_UNIVERSE_SIZE_DRIFT", len(cases), EXPECTED_CASE_COUNT))

    rows = []
    for ordinal, (label, seed, formula) in enumerate(cases, 1):
        r43.validate_exact_3cnf(formula)
        result = r42.run_fixed_successor(formula, label)
        rows.append(outcome_row(ordinal, label, seed, formula, result))

    sealed = next((r for r in rows if r["seed"] == SEALED_COUNTEREXAMPLE_SEED), None)
    if sealed is None:
        raise AssertionError("R44_SEALED_COUNTEREXAMPLE_MISSING")
    if sealed["input_formula_sha256"] != SEALED_COUNTEREXAMPLE_INPUT_SHA256:
        raise AssertionError(("R44_43004_INPUT_HASH_DRIFT", sealed["input_formula_sha256"]))
    if sealed["semantic_decided"] is not False or sealed["terminal_status"] != "STALLED_FIXED_SUCCESSOR":
        raise AssertionError(("R44_43004_NO_LONGER_REPLAYS_AS_SEALED_STALL", sealed))

    quotient = build_candidate_quotient(rows)
    q_false_rows = [r for r in rows if not r["semantic_decided"]]
    q_false_labels = [r["label"] for r in q_false_rows]
    q_false_seeds = [r["seed"] for r in q_false_rows]
    seed43004_class = next(
        c for c in quotient["classes"] if sealed["ordinal"] in c["member_ordinals"]
    )
    controls = pyramid_controls()

    all_execution_integrity = all(r["controller_execution_integrity"] for r in rows)
    R = quotient["R_uncovered_or_nonexact_membership"]
    F = quotient["F_transport_failures"]
    Q_false = len(q_false_rows)
    finite_universal_decision_coverage = (
        all_execution_integrity and R == 0 and F == 0 and Q_false == 0
    )
    if finite_universal_decision_coverage:
        raise AssertionError("R44_CONTRADICTS_SEALED_R43_COUNTEREXAMPLE")

    verdict = (
        "R44_STALL_CLASS_EXTRACTED__R42_L2_REMAINS_REFUTED"
        if Q_false > 1
        else "R44_NO_ADDITIONAL_STALL_BUT_43004_CONFIRMED__R42_L2_REMAINS_REFUTED"
    )

    return {
        "schema": "JANUS_TRUMP_R44_43004_QUOTIENT_TRANSPORT_STALL_CLASS_RESULT",
        "version": "1.0",
        "date": "2026-09-02",
        "source_git_commit": os.environ.get("GITHUB_SHA", "LOCAL_UNCOMMITTED"),
        "lineage": {
            "sealed_R43_commit": R43_SEALED_COMMIT,
            "R43_execution_head": R43_EXECUTION_HEAD,
            "frozen_R42_controller_blob_sha": R42_CONTROLLER_BLOB_SHA,
            "R42_modified_during_R44": False,
            "new_operator_or_terminal_added_during_R44": False,
        },
        "formal_property_Q": "frozen_R42_controller_reaches_verified_semantic_decision",
        "frozen_universe": {
            "expected_case_count": EXPECTED_CASE_COUNT,
            "executed_case_count": len(rows),
            "all_83_executed_even_after_seed_43004": True,
            "rows_sha256": canonical_sha256(rows),
        },
        "outcome_counts": {
            "Q_true_semantic_decisions": len(rows) - Q_false,
            "Q_false_stalls": Q_false,
            "stall_labels": q_false_labels,
            "stall_seeds": q_false_seeds,
        },
        "sealed_43004_replay": sealed,
        "candidate_truth_blind_quotient": quotient,
        "sealed_43004_candidate_class": seed43004_class,
        "pyramid_adversarial_control": controls,
        "metrics": {
            "N": len(rows),
            "K": quotient["K_quotient_classes"],
            "R": R,
            "F": F,
            "Q_false": Q_false,
            "K_stall_representatives": quotient["stall_representative_class_count"],
            "seed_43004_class_size": seed43004_class["member_count"],
        },
        "status": {
            "QUOTIENT_COMPRESSION_OBSERVED": quotient["QUOTIENT_COMPRESSION_OBSERVED"],
            "FINITE_TRANSPORT_AUDIT_CERTIFIED": all_execution_integrity and R == 0,
            "CANDIDATE_QUOTIENT_TRANSPORT_SOUND": F == 0,
            "FINITE_UNIVERSAL_DECISION_COVERAGE_CERTIFIED": finite_universal_decision_coverage,
            "SEALED_43004_STALL_REPRODUCED": True,
            "PYRAMID_ADVERSARIAL_CONTROLS_PASS": controls["pass"],
            "POLYNOMIALITY_PROVEN": False,
        },
        "scientific_interpretation": {
            "if_F_gt_0": "The preregistered truth-blind structural quotient is too coarse: at least one class mixes Q=true and Q=false, so representative-to-class transport is rejected.",
            "if_F_eq_0": "Within this finite 83-case universe the preregistered structural signature preserves Q, but Q=false classes remain and therefore universal decision coverage still fails.",
            "R42_L2_effect": "R42 remains refuted for L2 because seed 43004 is replayed as a nonsemantic halt; quotienting cannot turn a Q=false representative into Q=true.",
            "next_use": "The Q=false rows and their predecision structural signatures are the frozen target family for a genuinely new successor, not a post-hoc patch to R42."
        },
        "proof_ladder": {
            "highest_verified_level": "R44_FINITE_CLASS_LEVEL_FAILURE_FORENSICS",
            "R42_L2_restored": False,
            "L2_UNIVERSAL_3CNF_COVERAGE": False,
            "L3_ONE_UNIFORM_TOTAL_TRUMP_RESOLVER": False,
            "L4_WORST_CASE_POLYNOMIAL_UNIFORM_TRUMP_RESOLVER": False,
        },
        "complexity_firewall": {
            "finite_quotient_growth_is_asymptotic_proof": False,
            "symbolic_all_n_K_bound_proved": False,
            "polynomial_construction_cost_proved": False,
            "polynomial_transport_verification_cost_proved": False,
            "POLYNOMIALITY_PROVEN": False,
        },
        "captain_verdict": {
            "verdict": verdict,
            "next_gate": "R45_NEW_SUCCESSOR_TARGETING_CERTIFIED_STALL_CLASS_WITH_PREDECISION_INVARIANTS",
            "law": "REPRESENTATIVE MAY SPEAK FOR A CLASS ONLY AFTER TRANSPORT; A STALLED REPRESENTATIVE MAY NOT BE PROMOTED INTO A DECISION.",
        },
        "verdict": verdict,
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }


def self_test() -> None:
    cases = list(r43.frozen_search_cases())
    assert len(cases) == 83
    label, seed, formula = cases[6]
    assert seed == SEALED_COUNTEREXAMPLE_SEED
    assert r42.formula_hash(formula) == SEALED_COUNTEREXAMPLE_INPUT_SHA256
    controls = pyramid_controls((1, 2, 3, 4))
    assert controls["pass"] is True
    print("R44_SELF_TEST_PASS", {"cases": len(cases), "ordinal7_seed": seed, "pyramid_controls": True})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    result = run_r44()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict": result["verdict"],
        "metrics": result["metrics"],
        "status": result["status"],
        "stall_seeds": result["outcome_counts"]["stall_seeds"],
        "P_VS_NP": result["P_VS_NP"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
