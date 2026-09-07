from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50g25as_universal_envelope_admissible_pivot as asmod
import janus_trump_r50g25at_tautology_hardened_runner as ath
import janus_trump_r50g25y_minimal_w_policy_counterexample_forensics as y

GATE = "JANUS_TRUMP_R50G25AV_REACHABLE_MULTI_DEFECT_RESIDUAL_OR_GROWTH_WITNESS"
PREREG_COMMIT = "ab413eb9c5300934e6e4b4feaee008cd3a366339"
PARENT_AU_SEALED_HEAD = "e68a5034434ef36d6130685dd92ce12c456cdbf3"
PARENT_AU_RECEIPT = "0d33f95c348fd5d2209692d5f4cc467b80ef3699"
PARENT_AU_META = "f94312fdb4957f2c1b71ce924e090da8b24c42c6"
Y_TARGET_HASH = "c379fb11374c4259a736545f6652a417b6d98d016e9dcaed62d44d3740b71adb"
Y_PREREG_COMMIT = "92b93a34cd582800fc925e961196607ff8d27ee0"
TAUTOLOGY_POLICY = "DETECT_AND_DROP_AS_ALWAYS_TRUE_BEFORE_AFFINE_GROUPING"

OBSTRUCTION = "REACHABLE_DEFECT_BRANCH_PRODUCT_EXCEEDS_L4"
MULTI_SURVIVAL = "REACHABLE_D_GT_4_WITHIN_L4_ON_FROZEN_ATTACKS__UNIVERSAL_GROWTH_OPEN"
NO_MULTI = "NO_D_GT_4_ON_FROZEN_ATTACKS__UNIVERSAL_GROWTH_OPEN"
FAILURE = "IMPLEMENTATION_OR_CONTRACT_FAILURE"
UNKNOWN = "UNKNOWN_RESOURCE_LIMIT"

LOCAL_K = (2, 5, 8, 16, 24, 32)
Y_COPIES = (1, 2, 3)


def canonical(formula):
    return r33.canonical_formula(formula)


def clv(formula):
    return tuple(map(int, r33.measure(canonical(formula))))


def formula_hash(formula):
    return y.canonical_hash(canonical(formula))


def is_tautology(clause):
    s = set(int(lit) for lit in clause)
    return any(-lit in s for lit in s)


def effective_canonical(formula):
    source = canonical(formula)
    tautologies = [tuple(c) for c in source if is_tautology(c)]
    effective = canonical([tuple(c) for c in source if not is_tautology(c)])
    return effective, tautologies


def independent_ledger(residual, extraction):
    effective, tautologies = effective_canonical(residual)
    L = sum(len(c) for c in effective)
    defects = [tuple(map(int, c)) for c in extraction["defects"]]
    widths = [len(c) for c in defects]
    product_a = math.prod(widths) if widths else 1
    product_b = 1
    for w in widths:
        product_b *= int(w)
    budget = int(L) ** 4
    return {
        "effective_clause_count": len(effective),
        "L": int(L),
        "tautology_count": len(tautologies),
        "defect_count": len(defects),
        "defect_widths": widths,
        "B_defect": int(product_a),
        "B_defect_recomputed": int(product_b),
        "L4_budget": int(budget),
        "budget_slack": int(budget - product_a),
        "product_recompute_match": product_a == product_b,
        "L_matches_effective_CLV": int(L) == int(clv(effective)[1]),
    }


def compact_route(replay):
    route = replay.get("route", [])
    return {
        "route_length": len(route),
        "route_head": route[:3],
        "route_tail": route[-5:] if len(route) > 5 else route,
    }


def base_hamming16():
    base, base_meta = asmod.hamming_xor_formula(16, punctured=True)
    return canonical(base), base_meta


def local_injection_candidates():
    base, base_meta = base_hamming16()
    pool = [tuple(c) for c in itertools.combinations(range(1, 17), 5)]
    assert len(pool) >= max(LOCAL_K)
    assert all(len(c) == 5 and all(lit > 0 for lit in c) for c in pool[: max(LOCAL_K)])
    for k in LOCAL_K:
        injected = tuple(pool[:k])
        root = canonical(list(base) + list(injected))
        meta = {
            "family": "HAMMING16_LEX_POSITIVE_WIDTH5_DEFECT_INJECTION",
            "n": 16,
            "k": int(k),
            "injected_width": 5,
            "base_family": base_meta["family"],
            "base_hash": formula_hash(base),
            "injection_pool_rule": "LEXICOGRAPHIC_ALL_POSITIVE_WIDTH5_OVER_1_TO_16",
            "injected_clauses": [list(c) for c in injected],
        }
        yield root, meta


def load_sealed_y_target():
    _sealed, target = r47j.load_counterexample()
    target = canonical(target)
    observed = formula_hash(target)
    if observed != Y_TARGET_HASH:
        raise AssertionError(("Y_TARGET_HASH_DRIFT", observed, Y_TARGET_HASH))
    replay = asmod.y.policy_replay(target, asmod.r50g25g._chain())
    if replay.get("kind") != "RESIDUAL":
        raise AssertionError(("Y_TARGET_POLICY_DRIFT", replay.get("kind")))
    return target


def shift_formula(formula, offset):
    out = []
    for clause in canonical(formula):
        shifted = []
        for lit in clause:
            sign = 1 if lit > 0 else -1
            shifted.append(sign * (abs(int(lit)) + int(offset)))
        out.append(tuple(shifted))
    return canonical(out)


def y_composition_candidates():
    base, base_meta = base_hamming16()
    target = load_sealed_y_target()
    target_vars = sorted(r33.variables(target))
    if not target_vars:
        raise AssertionError("Y_TARGET_EMPTY_VARIABLE_SET")
    m = max(map(abs, target_vars))
    for g in Y_COPIES:
        copies = []
        copy_hashes = []
        copy_var_sets = []
        for j in range(g):
            offset = 16 + j * m
            cp = shift_formula(target, offset)
            copies.extend(cp)
            copy_hashes.append(formula_hash(cp))
            copy_var_sets.append(sorted(map(int, r33.variables(cp))))
        root = canonical(list(base) + copies)
        all_sets = [set(range(1, 17))] + [set(vs) for vs in copy_var_sets]
        disjoint = all(all_sets[i].isdisjoint(all_sets[j]) for i in range(len(all_sets)) for j in range(i + 1, len(all_sets)))
        if not disjoint:
            raise AssertionError(("ROOT_GENERATOR_DRIFT", "non-disjoint shifted copies", g))
        meta = {
            "family": "HAMMING16_PLUS_SHIFTED_SEALED_Y_RESIDUAL_COPIES",
            "n": 16,
            "copy_count": int(g),
            "base_family": base_meta["family"],
            "base_hash": formula_hash(base),
            "Y_target_hash": Y_TARGET_HASH,
            "Y_target_CLV": list(clv(target)),
            "Y_target_max_var": int(m),
            "copy_hashes": copy_hashes,
            "copy_var_ranges": [[min(vs), max(vs)] for vs in copy_var_sets],
            "disjoint_variable_blocks": True,
        }
        yield root, meta


def frozen_candidates():
    yield from local_injection_candidates()
    yield from y_composition_candidates()


def audit_residual(root, meta, replay):
    residual = canonical(replay["state"])
    extraction = ath.hardened_extract(residual)
    failures = []
    if extraction.get("explicit_tautology_policy") != TAUTOLOGY_POLICY or not extraction.get("tautology_check_pass"):
        failures.append({"kind": "TAUTOLOGY_POLICY_DRIFT"})
    if not extraction.get("partition_pass") or extraction.get("replay_failures"):
        failures.append({
            "kind": "AFFINE_EXTRACTION_OR_REPLAY_FAILURE",
            "partition_pass": bool(extraction.get("partition_pass")),
            "replay_failures": extraction.get("replay_failures", []),
        })
    ledger = independent_ledger(residual, extraction)
    if not ledger["product_recompute_match"] or not ledger["L_matches_effective_CLV"]:
        failures.append({"kind": "INDEPENDENT_LEDGER_MISMATCH", "ledger": ledger})
    row = {
        "meta": meta,
        "root_hash": formula_hash(root),
        "root_CLV": list(clv(root)),
        "policy_kind": "RESIDUAL",
        "residual_hash": formula_hash(residual),
        "residual_CLV_before_tautology_drop": list(clv(residual)),
        **compact_route(replay),
        "extraction": {
            "affine_clause_count": int(extraction["affine_clause_count"]),
            "recognized_equation_count": int(extraction["recognized_equation_count"]),
            "defect_clause_count": int(extraction["defect_clause_count"]),
            "partition_pass": bool(extraction["partition_pass"]),
            "replay_failure_count": len(extraction.get("replay_failures", [])),
            "tautology_count": int(extraction.get("tautology_count", -1)),
            "explicit_tautology_policy": extraction.get("explicit_tautology_policy"),
        },
        "ledger": ledger,
        "failure_count": len(failures),
        "failures": failures,
    }
    return row, failures


def witness_from_row(row, klass):
    l = row["ledger"]
    return {
        "class": klass,
        "meta": row["meta"],
        "root_hash": row["root_hash"],
        "root_CLV": row["root_CLV"],
        "residual_hash": row["residual_hash"],
        "residual_CLV": row["residual_CLV_before_tautology_drop"],
        "route_length": row["route_length"],
        "defect_count": int(l["defect_count"]),
        "defect_widths": list(l["defect_widths"]),
        "L": int(l["L"]),
        "B_defect": int(l["B_defect"]),
        "L4_budget": int(l["L4_budget"]),
        "budget_slack": int(l["budget_slack"]),
    }


def run():
    chain = asmod.r50g25g._chain()
    rows = []
    failures = []
    first_multi = None
    obstruction = None
    max_d = -1
    max_product = -1
    min_slack = None
    residual_count = 0
    absorbed_terminal = 0
    absorbed_affine = 0

    try:
        candidates = list(frozen_candidates())
    except Exception as exc:
        return {
            "gate": GATE,
            "status": "SCIENTIFIC_RESULT",
            "preregistration_commit": PREREG_COMMIT,
            "verdict": FAILURE,
            "failure_count": 1,
            "failures": [{"kind": "ROOT_GENERATOR_DRIFT", "detail": repr(exc)}],
            "rows": [],
            "firewall": {"P_VS_NP": "OPEN", "SAT_IN_P": "NOT_PROVED", "TRUMP_finished": False},
        }

    if len(candidates) != len(LOCAL_K) + len(Y_COPIES):
        failures.append({"kind": "ROOT_GENERATOR_DRIFT", "detail": "candidate count mismatch", "observed": len(candidates)})

    for root, meta in candidates:
        root = canonical(root)
        replay = asmod.y.policy_replay(root, chain)
        kind = str(replay.get("kind"))
        if kind in {"TERMINAL", "AFFINE"}:
            if kind == "TERMINAL":
                absorbed_terminal += 1
            else:
                absorbed_affine += 1
            rows.append({
                "meta": meta,
                "root_hash": formula_hash(root),
                "root_CLV": list(clv(root)),
                "policy_kind": kind,
                "classification": "NON_FALSIFYING_CHEAP_POLICY_ABSORPTION",
                **compact_route(replay),
                "failure_count": 0,
                "failures": [],
            })
            continue
        if kind != "RESIDUAL":
            failure = {"kind": "POLICY_CONTRACT_DRIFT", "meta": meta, "observed_kind": kind}
            failures.append(failure)
            rows.append({"meta": meta, "policy_kind": kind, "classification": FAILURE, "failure_count": 1, "failures": [failure]})
            break

        residual_count += 1
        row, row_failures = audit_residual(root, meta, replay)
        if row_failures:
            failures.extend(row_failures)
            row["classification"] = FAILURE
            rows.append(row)
            break

        l = row["ledger"]
        d = int(l["defect_count"])
        max_d = max(max_d, d)
        max_product = max(max_product, int(l["B_defect"]))
        min_slack = int(l["budget_slack"]) if min_slack is None else min(min_slack, int(l["budget_slack"]))

        if d > 4 and first_multi is None:
            first_multi = witness_from_row(row, "FIRST_REACHABLE_D_GT_4")

        if int(l["B_defect"]) > int(l["L4_budget"]):
            row["classification"] = "DEFECT_BRANCH_PRODUCT_EXCEEDS_L4"
            obstruction = witness_from_row(row, "DEFECT_BRANCH_PRODUCT_EXCEEDS_L4")
            obstruction["residual_formula"] = [list(c) for c in canonical(replay["state"])]
        elif d > 4:
            row["classification"] = "REACHABLE_D_GT_4_WITHIN_L4"
        else:
            row["classification"] = "D_LE_4_WITHIN_L4"
        rows.append(row)

        if obstruction is not None:
            break

    if failures:
        verdict = FAILURE
    elif obstruction is not None:
        verdict = OBSTRUCTION
    elif first_multi is not None:
        verdict = MULTI_SURVIVAL
    else:
        verdict = NO_MULTI

    return {
        "gate": GATE,
        "status": "SCIENTIFIC_RESULT",
        "preregistration_commit": PREREG_COMMIT,
        "parent_AU_sealed_head": PARENT_AU_SEALED_HEAD,
        "parent_AU_receipt": PARENT_AU_RECEIPT,
        "parent_AU_meta": PARENT_AU_META,
        "Y_target_hash": Y_TARGET_HASH,
        "Y_preregistration_commit": Y_PREREG_COMMIT,
        "verdict": verdict,
        "candidate_count_frozen": len(LOCAL_K) + len(Y_COPIES),
        "candidate_count_audited": len(rows),
        "residual_count_audited": residual_count,
        "cheap_policy_absorption": {"TERMINAL": absorbed_terminal, "AFFINE": absorbed_affine},
        "first_reachable_d_gt_4": first_multi,
        "first_L4_obstruction": obstruction,
        "max_defect_count_observed": None if max_d < 0 else max_d,
        "max_B_defect_observed": None if max_product < 0 else max_product,
        "minimum_budget_slack_observed": min_slack,
        "failure_count": len(failures),
        "failures": failures,
        "rows": rows,
        "frozen_bound": {
            "B_defect": "product_i |D_i|",
            "L": "literal count of current canonical residual after explicit tautology removal",
            "budget": "L^4",
            "exponent": 4,
            "posthoc_tuning_forbidden": True,
        },
        "frozen_attack_contract": {
            "local_k": list(LOCAL_K),
            "Y_copy_counts": list(Y_COPIES),
            "candidate_order": "LOCAL_INJECTION_THEN_Y_COMPOSITION",
            "stop_on_first_L4_obstruction": True,
        },
        "scientific_scope": {
            "finite_frozen_attack_families_only": True,
            "universal_defect_growth_bound": "OPEN",
            "arbitrary_CNF_coverage": "OPEN",
            "simple_defect_enumeration_if_obstruction": "FALSIFIED_ON_REACHABLE_WITNESS" if obstruction is not None else "NOT_FALSIFIED_ON_FROZEN_ATTACKS",
            "second_structural_door_if_obstruction": "MUST_BE_SEPARATELY_PREREGISTERED",
        },
        "truth_oracle": {
            "used_for_generation": False,
            "used_for_selection": False,
            "used_for_verdict": False,
        },
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "AR_AS_meta_backfill_pending": True,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("JANUS_TRUMP_R50G25AV_RESULT.json"))
    args = ap.parse_args()
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": result["gate"],
        "verdict": result["verdict"],
        "candidate_count_audited": result.get("candidate_count_audited"),
        "residual_count_audited": result.get("residual_count_audited"),
        "max_defect_count_observed": result.get("max_defect_count_observed"),
        "max_B_defect_observed": result.get("max_B_defect_observed"),
        "minimum_budget_slack_observed": result.get("minimum_budget_slack_observed"),
        "failure_count": result.get("failure_count"),
        "first_multi_family": None if result.get("first_reachable_d_gt_4") is None else result["first_reachable_d_gt_4"]["meta"]["family"],
        "obstruction_family": None if result.get("first_L4_obstruction") is None else result["first_L4_obstruction"]["meta"]["family"],
    }, sort_keys=True))
    good = result["verdict"] in {OBSTRUCTION, MULTI_SURVIVAL, NO_MULTI} and result.get("failure_count") == 0
    raise SystemExit(0 if good else 1)


if __name__ == "__main__":
    main()
