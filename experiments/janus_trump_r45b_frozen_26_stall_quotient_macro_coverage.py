from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r43_frozen_r42_counterexample_hunt as r43
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a

Formula = Tuple[Tuple[int, ...], ...]

R45A_SEAL_COMMIT = "d07b28eafe99fb3df9ab025a274ac88fa76ce955"
R45A_MACRO_BLOB = "a88ea0b9bbeab3e62a21b1351d5887a00c79416a"
EXPECTED_STALL_CLASS_COUNT = 25
FROZEN_STALL_SEEDS = (
    43004,
    43101, 43102, 43103, 43104, 43105, 43106, 43107, 43108, 43109, 43110, 43111, 43112, 43113, 43115,
    43201, 43203, 43204, 43205, 43206, 43207, 43209, 43210, 43212, 43213, 43216,
)


def canonical_sha256(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def clv(formula: Formula) -> Tuple[int, int, int]:
    return r33.measure(r33.canonical_formula(formula))


def frozen_case_map() -> Dict[int, Tuple[str, Formula]]:
    out: Dict[int, Tuple[str, Formula]] = {}
    for label, seed, formula in r43.frozen_search_cases():
        if seed is None:
            continue
        out[int(seed)] = (str(label), r33.canonical_formula(formula))
    return out


def replay_r42_terminal_formula(initial_formula: Formula, label: str) -> Tuple[dict, Formula]:
    original = r33.canonical_formula(initial_formula)
    result = r42.run_fixed_successor(original, label)
    if result["semantic_decided"] or result["terminal_status"] != "STALLED_FIXED_SUCCESSOR":
        raise AssertionError(("R45B_FROZEN_SEED_NO_LONGER_STALLS", label, result["terminal_status"], result["semantic_decided"]))

    state = original
    for _ in range(int(result["cycle_count"]) + 2):
        before = state
        reduced = r33.simplify(before)
        after_r33 = r33.canonical_formula(reduced["final_formula"])
        if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
            raise AssertionError(("R45B_REPLAY_UNEXPECTED_R33_TERMINAL", label, reduced["terminal"]))
        affine = r34.recognize_complete_affine_cnf(after_r33)
        if affine["recognized"]:
            raise AssertionError(("R45B_REPLAY_UNEXPECTED_AFFINE_TERMINAL", label))
        rup = r35b.run_candidate(after_r33)
        rup_replay = r35b.independent_certificate_replay(after_r33, rup)
        if not rup_replay["pass"]:
            raise AssertionError(("R45B_REPLAY_RUP_CERT_FAIL", label))
        if rup["status"] == "UNSAT_BY_UNIT_PROPAGATION":
            raise AssertionError(("R45B_REPLAY_UNEXPECTED_RUP_TERMINAL", label))
        after_rup = r33.canonical_formula(rup["final_formula"])
        bve, _ = r42.best_sa_bve_candidate(after_rup)
        after_bve = r33.canonical_formula(bve["transformed"]) if bve is not None else after_rup
        if after_bve == before:
            state = after_bve
            break
        state = after_bve
    else:
        raise AssertionError(("R45B_REPLAY_FAILED_TO_REACH_FIXPOINT", label))

    if r42.formula_hash(state) != result["terminal_formula_hash"]:
        raise AssertionError((
            "R45B_TERMINAL_HASH_REPLAY_DRIFT",
            label,
            r42.formula_hash(state),
            result["terminal_formula_hash"],
        ))
    if list(clv(state)) != result["terminal_measure_CLV"]:
        raise AssertionError(("R45B_TERMINAL_CLV_REPLAY_DRIFT", label, list(clv(state)), result["terminal_measure_CLV"]))
    return result, state


def structural_signature(row: dict) -> Tuple[object, ...]:
    return (
        tuple(row["input_measure_CLV"]),
        tuple(row["delta_measure_CLV"]),
        int(row["cycle_count"]),
        int(row["SA_BVE_applications"]),
    )


def analyze_stall_seed(seed: int) -> dict:
    cases = frozen_case_map()
    if seed not in cases:
        raise AssertionError(("R45B_FROZEN_SEED_MISSING_FROM_R43", seed))
    label, formula = cases[seed]
    inherited, stall = replay_r42_terminal_formula(formula, label)
    input_clv = tuple(int(x) for x in inherited["initial_measure_CLV"])
    stall_clv = tuple(int(x) for x in inherited["terminal_measure_CLV"])
    delta_clv = tuple(a - b for a, b in zip(input_clv, stall_clv))

    scan = r45a.select_macro(stall)
    selected = scan["selected"]
    selected_replay = scan["selected_independent_replay"]
    q_macro = bool(
        selected is not None
        and selected_replay is not None
        and selected_replay["pass"]
        and scan["global_polynomial_scan_bounds"]["pass"]
        and selected["DP_independent_replay"]["pass"]
        and selected["polynomial_intermediate_envelope"]["pass"]
        and selected["accepted"]
    )
    selected_terminal = selected["normalization"]["terminal"] if selected else None
    row = {
        "seed": int(seed),
        "label": label,
        "input_formula_sha256": inherited["initial_formula_hash"],
        "input_measure_CLV": list(input_clv),
        "stall_formula_sha256": inherited["terminal_formula_hash"],
        "stall_measure_CLV": list(stall_clv),
        "delta_measure_CLV": list(delta_clv),
        "cycle_count": int(inherited["cycle_count"]),
        "SA_BVE_applications": int(inherited["SA_BVE_applications"]),
        "Q_macro": q_macro,
        "candidate_count": int(scan["candidate_count"]),
        "acceptable_candidate_count": int(scan["acceptable_candidate_count"]),
        "selected_var": int(selected["var"]) if selected else None,
        "selected_terminal": selected_terminal,
        "selected_semantic_sat": selected["normalization"]["semantic_sat"] if selected else None,
        "selected_final_CLV": selected["final_CLV"] if selected else None,
        "selected_net_CLV_descent": bool(selected["net_CLV_descent"]) if selected else False,
        "selected_temporary_internal_ascent": bool(selected["temporary_internal_ascent"]) if selected else False,
        "selected_independent_replay_pass": bool(selected_replay and selected_replay["pass"]),
        "selected_macro_certificate_sha256": canonical_sha256(selected) if selected else None,
        "selected_macro_certificate": selected,
        "candidate_digest_sha256": scan["candidate_digest_sha256"],
        "global_polynomial_scan_bounds": scan["global_polynomial_scan_bounds"],
        "resource_ledger": scan["resource_ledger"],
    }
    return row


def build_quotient(rows: Sequence[dict]) -> dict:
    groups: Dict[Tuple[object, ...], List[dict]] = defaultdict(list)
    membership = defaultdict(int)
    for row in rows:
        groups[structural_signature(row)].append(row)

    F = 0
    mixed = 0
    class_rows = []
    first_failure = None
    for sig in sorted(groups, key=repr):
        members = sorted(groups[sig], key=lambda r: int(r["seed"]))
        representative = members[0]
        rep_q = bool(representative["Q_macro"])
        q_values = set()
        failures = 0
        transport_records = []
        for member in members:
            membership[int(member["seed"])] += 1
            mq = bool(member["Q_macro"])
            q_values.add(mq)
            ok = mq == rep_q
            transport_records.append({"seed": member["seed"], "Q_macro": mq, "matches_representative": ok})
            if not ok:
                F += 1
                failures += 1
                if first_failure is None:
                    first_failure = {
                        "representative_seed": representative["seed"],
                        "representative_Q_macro": rep_q,
                        "member_seed": member["seed"],
                        "member_Q_macro": mq,
                    }
        if len(q_values) > 1:
            mixed += 1
        class_rows.append({
            "signature": {
                "input_measure_CLV": list(sig[0]),
                "delta_measure_CLV": list(sig[1]),
                "cycle_count": sig[2],
                "SA_BVE_applications": sig[3],
            },
            "signature_sha256": canonical_sha256(list(sig)),
            "representative_seed": representative["seed"],
            "representative_Q_macro": rep_q,
            "member_seeds": [m["seed"] for m in members],
            "member_count": len(members),
            "Q_values_present": sorted(q_values),
            "transport_failures": failures,
            "transport_certificate_sha256": canonical_sha256(transport_records),
        })

    expected = set(FROZEN_STALL_SEEDS)
    R = sum(1 for seed in expected if membership[int(seed)] != 1)
    return {
        "N_raw_stalls": len(rows),
        "K_quotient_classes": len(groups),
        "R_uncovered_or_nonexact_membership": R,
        "F_Q_macro_transport_failures": F,
        "mixed_Q_macro_class_count": mixed,
        "first_transport_failure": first_failure,
        "classes": class_rows,
        "class_ledger_sha256": canonical_sha256(class_rows),
        "AUDIT_TRANSPORT_ONLY": True,
        "RUNTIME_QUOTIENT_COMPRESSION_PROVEN": False,
    }


def aggregate_resources(rows: Sequence[dict]) -> dict:
    sums: Dict[str, int] = defaultdict(int)
    peaks: Dict[str, int] = defaultdict(int)
    peak_keys = {"peak_intermediate_clauses", "peak_intermediate_literals"}
    for row in rows:
        for key, value in row["resource_ledger"].items():
            if not isinstance(value, (int, float)):
                continue
            iv = int(value)
            if key in peak_keys:
                peaks[key] = max(peaks[key], iv)
            else:
                sums[key] += iv
    return {"sum": dict(sorted(sums.items())), "peak": dict(sorted(peaks.items()))}


def run_r45b(max_workers: Optional[int] = None) -> dict:
    if len(FROZEN_STALL_SEEDS) != 26 or len(set(FROZEN_STALL_SEEDS)) != 26:
        raise AssertionError("R45B_FROZEN_SEED_LEDGER_INVALID")
    cases = frozen_case_map()
    missing = [s for s in FROZEN_STALL_SEEDS if s not in cases]
    if missing:
        raise AssertionError(("R45B_FROZEN_SEEDS_MISSING", missing))

    workers = max_workers or min(4, max(1, os.cpu_count() or 1), len(FROZEN_STALL_SEEDS))
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        rows = list(executor.map(analyze_stall_seed, FROZEN_STALL_SEEDS))
    rows.sort(key=lambda r: int(r["seed"]))

    if [r["seed"] for r in rows] != sorted(FROZEN_STALL_SEEDS):
        raise AssertionError("R45B_RESULT_SEED_ORDER_DRIFT")
    quotient = build_quotient(rows)
    if quotient["K_quotient_classes"] != EXPECTED_STALL_CLASS_COUNT:
        raise AssertionError(("R45B_R44_QUOTIENT_CLASS_REGRESSION_DRIFT", quotient["K_quotient_classes"], EXPECTED_STALL_CLASS_COUNT))

    q_false = [r["seed"] for r in rows if not r["Q_macro"]]
    terminal_rows = [r for r in rows if r["Q_macro"] and r["selected_terminal"] is not None]
    descent_only = [r for r in rows if r["Q_macro"] and r["selected_terminal"] is None and r["selected_net_CLV_descent"]]
    all_replays = all(r["Q_macro"] and r["selected_independent_replay_pass"] for r in rows)
    all_bounds = all(r["global_polynomial_scan_bounds"]["pass"] for r in rows)
    finite_pass = (
        len(rows) == 26
        and quotient["R_uncovered_or_nonexact_membership"] == 0
        and quotient["F_Q_macro_transport_failures"] == 0
        and not q_false
        and all_replays
        and all_bounds
    )
    verdict = (
        "R45B_FINITE_26_STALL_MACRO_APPLICABILITY_CERTIFIED__UNIVERSAL_COVERAGE_OPEN"
        if finite_pass
        else "R45B_UNCOVERED_FROZEN_STALL_OR_TRANSPORT_FAILURE"
    )

    compact_rows = [{k: v for k, v in row.items() if k != "selected_macro_certificate"} for row in rows]
    certificate_bank = {
        str(row["seed"]): row["selected_macro_certificate"]
        for row in rows
        if row["selected_macro_certificate"] is not None
    }

    return {
        "schema": "JANUS_TRUMP_R45B_FROZEN_26_STALL_QUOTIENT_MACRO_COVERAGE_RESULT",
        "version": "1.0",
        "date": "2026-09-02",
        "source_git_commit": os.environ.get("GITHUB_SHA", "LOCAL_UNCOMMITTED"),
        "lineage": {
            "R45A_seal_commit": R45A_SEAL_COMMIT,
            "R45A_macro_blob_sha": R45A_MACRO_BLOB,
            "R44_quotient_regression_expected_K": EXPECTED_STALL_CLASS_COUNT,
        },
        "parallel_execution": {"workers": workers, "proof_authority": False},
        "frozen_stall_seeds": list(FROZEN_STALL_SEEDS),
        "rows": compact_rows,
        "rows_sha256": canonical_sha256(compact_rows),
        "selected_macro_certificate_bank": certificate_bank,
        "selected_macro_certificate_bank_sha256": canonical_sha256(certificate_bank),
        "quotient": quotient,
        "metrics": {
            "N": len(rows),
            "K": quotient["K_quotient_classes"],
            "R": quotient["R_uncovered_or_nonexact_membership"],
            "F": quotient["F_Q_macro_transport_failures"],
            "Q_macro_false": len(q_false),
            "uncovered_seeds": q_false,
            "terminal_macro_count": len(terminal_rows),
            "descent_only_macro_count": len(descent_only),
            "temporary_ascent_selected_count": sum(1 for r in rows if r["Q_macro"] and r["selected_temporary_internal_ascent"]),
        },
        "resource_ledger": aggregate_resources(rows),
        "status": {
            "FINITE_26_STALL_MACRO_APPLICABILITY_CERTIFIED": finite_pass,
            "FINITE_26_STALL_ONE_MACRO_SEMANTIC_DECISION_COVERAGE_CERTIFIED": finite_pass and len(terminal_rows) == 26,
            "QUOTIENT_Q_MACRO_TRANSPORT_SOUND": quotient["F_Q_macro_transport_failures"] == 0,
            "AUDIT_TRANSPORT_ONLY": True,
            "RUNTIME_QUOTIENT_COMPRESSION_PROVEN": False,
            "UNIVERSAL_REACHABLE_STALL_COVERAGE_PROVEN": False,
            "FULL_ALGORITHM_POLYNOMIALITY_PROVEN": False,
        },
        "scientific_interpretation": {
            "if_pass": "The byte-pinned macro exists and independently replays on every one of the 26 previously sealed R42 stalls. This is finite applicability coverage only.",
            "if_uncovered": "At least one previously sealed stall has no acceptable macro under the frozen selector; the R45 successor candidate is refuted on the finite R44 stall set.",
            "if_transport_F_gt_0": "The preregistered truth-blind quotient is too coarse for transporting Q_macro and must not be used as a representative shortcut.",
            "one_macro_escape_not_full_decision": True,
        },
        "next_gate": (
            "R46_INTEGRATED_R42_PLUS_R45_RESTART_CONTROLLER_PROSPECTIVE_STALL_HUNT"
            if finite_pass
            else "RETURN_TO_CAPTAIN_WITH_R45B_UNCOVERED_STALL_OR_QUOTIENT_FAILURE"
        ),
        "verdict": verdict,
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }


def self_test() -> None:
    assert len(FROZEN_STALL_SEEDS) == 26
    assert len(set(FROZEN_STALL_SEEDS)) == 26
    assert FROZEN_STALL_SEEDS[0] == 43004
    rows = [
        {
            "seed": 1,
            "input_measure_CLV": [10, 30, 8],
            "delta_measure_CLV": [1, 3, 0],
            "cycle_count": 2,
            "SA_BVE_applications": 0,
            "Q_macro": True,
        },
        {
            "seed": 2,
            "input_measure_CLV": [10, 30, 8],
            "delta_measure_CLV": [1, 3, 0],
            "cycle_count": 2,
            "SA_BVE_applications": 0,
            "Q_macro": False,
        },
    ]
    original = globals()["FROZEN_STALL_SEEDS"]
    try:
        globals()["FROZEN_STALL_SEEDS"] = (1, 2)
        q = build_quotient(rows)
        assert q["K_quotient_classes"] == 1
        assert q["R_uncovered_or_nonexact_membership"] == 0
        assert q["F_Q_macro_transport_failures"] == 1
        assert q["mixed_Q_macro_class_count"] == 1
    finally:
        globals()["FROZEN_STALL_SEEDS"] = original
    print("R45B_SELF_TEST_PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    result = run_r45b(args.workers)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict": result["verdict"],
        "metrics": result["metrics"],
        "status": result["status"],
        "workers": result["parallel_execution"]["workers"],
        "next_gate": result["next_gate"],
        "P_VS_NP": result["P_VS_NP"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
