from __future__ import annotations

import argparse
import hashlib
import inspect
import json
from collections import Counter, defaultdict
from pathlib import Path

import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25h_micro_rup_restart_broader_1212_polynomial_ledger_audit as r50g25h
import janus_trump_r50g25r_outer_counterexample_search as r50g25r
import janus_trump_r50g25s_max_rup_minimization_structured_escalation as r50g25s

GATE = "JANUS_TRUMP_R50G25U_SCALE_LADDER_AND_CERTIFICATE_SIZE_THEOREM_GATE"
T_RUN = 34043535597
T_JOURNAL_COMMIT = "c89d0712bd959943a22603b4ba7d1eca9d9b48c0"
U_PREREG_COMMIT = "fa75b44eec3f3c4c987c4ba5c8cd3f2282de34e2"
FALSIFIER_CLASSES = tuple(r50g25r.FALSIFIER_CLASSES)
KNOWN_R33_RULES = {
    "TAUTOLOGY_DELETION",
    "UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE",
    "PURE_LITERAL_AUTARKY",
    "SUBSUMPTION",
    "BLOCKED_CLAUSE_ELIMINATION",
    "BOUNDED_VARIABLE_ELIMINATION",
}
ALLOWED_KEYS = {
    "TAUTOLOGY_DELETION": {"rule", "clause", "measure_before", "measure_after", "certificate_bytes"},
    "UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE": {"rule", "literal", "touched_clauses", "measure_before", "measure_after", "certificate_bytes"},
    "PURE_LITERAL_AUTARKY": {"rule", "literal", "removed_clauses", "measure_before", "measure_after", "certificate_bytes"},
    "SUBSUMPTION": {"rule", "deleted", "witness_subclause", "measure_before", "measure_after", "certificate_bytes"},
    "BLOCKED_CLAUSE_ELIMINATION": {"rule", "clause", "blocking_literal", "measure_before", "measure_after", "certificate_bytes"},
    "BOUNDED_VARIABLE_ELIMINATION": {"rule", "var", "positive", "negative", "resolvents", "measure_before", "measure_after", "certificate_bytes"},
}


def source_schema_audit(r33):
    simplify_src = inspect.getsource(r33.simplify)
    bve_src = inspect.getsource(r33.bve_candidate)
    required_fragments = [
        '"TAUTOLOGY_DELETION"',
        '"UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE"',
        '"PURE_LITERAL_AUTARKY"',
        '"SUBSUMPTION"',
        '"BLOCKED_CLAUSE_ELIMINATION"',
        '"BOUNDED_VARIABLE_ELIMINATION"',
        'record["certificate_bytes"] = certificate_bytes(record)',
    ]
    missing = [x for x in required_fragments if x not in simplify_src]
    bve_condition_present = "len(resolvents) <= len(removed)" in bve_src
    return {
        "pass": not missing and bve_condition_present,
        "missing_required_fragments": missing,
        "bve_resolvent_count_condition_present": bve_condition_present,
        "simplify_source_sha256": hashlib.sha256(simplify_src.encode()).hexdigest(),
        "bve_candidate_source_sha256": hashlib.sha256(bve_src.encode()).hexdigest(),
    }


def symbolic_bounds(measure):
    c, _l, v = (int(x) for x in measure)
    cv = c * v
    state_bound = (c + 1) * (cv + 1) * (v + 1)
    digits = len(str(max(1, cv))) + 2
    max_integer_leaves_per_record = 2 * cv + 64
    per_record = 2048 + max_integer_leaves_per_record * (digits + 8)
    total = state_bound * per_record
    # Stronger diagnostic that also allows the stored certificate_bytes self-field.
    per_record_full = per_record + 128
    total_full = state_bound * per_record_full
    return {
        "C0": c,
        "V0": v,
        "CV": cv,
        "state_triplet_bound": state_bound,
        "integer_digit_bound": digits,
        "max_integer_leaves_per_record": max_integer_leaves_per_record,
        "per_R33_record_reported_bytes_bound": per_record,
        "total_R33_reported_certificate_bytes_bound": total,
        "per_R33_record_full_serialized_bytes_bound": per_record_full,
        "total_R33_full_serialized_history_bytes_bound": total_full,
    }


def count_integer_leaves(obj):
    if isinstance(obj, bool):
        return 0
    if isinstance(obj, int):
        return 1
    if isinstance(obj, dict):
        return sum(count_integer_leaves(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return sum(count_integer_leaves(v) for v in obj)
    return 0


def record_without_self_size(record):
    return {k: v for k, v in record.items() if k != "certificate_bytes"}


def audit_r33_result(r33, result, initial_measure):
    bounds = symbolic_bounds(initial_measure)
    violations = []
    reported_sum = 0
    full_sum = 0
    max_record_reported = 0
    max_record_full = 0
    for index, record in enumerate(result.get("history", [])):
        rule = str(record.get("rule"))
        if rule not in KNOWN_R33_RULES:
            violations.append({"type": "UNKNOWN_RULE", "index": index, "rule": rule})
            continue
        extra_keys = sorted(set(record) - ALLOWED_KEYS[rule])
        missing_keys = sorted(ALLOWED_KEYS[rule] - set(record))
        if extra_keys or missing_keys:
            violations.append({"type": "SCHEMA_KEY_DRIFT", "index": index, "rule": rule, "extra": extra_keys, "missing": missing_keys})

        recomputed_reported = r33.certificate_bytes(record_without_self_size(record))
        stored_reported = int(record.get("certificate_bytes", -1))
        if recomputed_reported != stored_reported:
            violations.append({"type": "REPORTED_BYTE_RECOMPUTE_MISMATCH", "index": index, "rule": rule, "stored": stored_reported, "recomputed": recomputed_reported})
        full_bytes = len(json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        integer_leaves = count_integer_leaves(record_without_self_size(record))
        if integer_leaves > bounds["max_integer_leaves_per_record"]:
            violations.append({"type": "INTEGER_LEAF_BOUND", "index": index, "rule": rule, "observed": integer_leaves, "bound": bounds["max_integer_leaves_per_record"]})
        if stored_reported > bounds["per_R33_record_reported_bytes_bound"]:
            violations.append({"type": "PER_RECORD_REPORTED_BYTE_BOUND", "index": index, "rule": rule, "observed": stored_reported, "bound": bounds["per_R33_record_reported_bytes_bound"]})
        if full_bytes > bounds["per_R33_record_full_serialized_bytes_bound"]:
            violations.append({"type": "PER_RECORD_FULL_BYTE_BOUND", "index": index, "rule": rule, "observed": full_bytes, "bound": bounds["per_R33_record_full_serialized_bytes_bound"]})
        reported_sum += stored_reported
        full_sum += full_bytes
        max_record_reported = max(max_record_reported, stored_reported)
        max_record_full = max(max_record_full, full_bytes)

    if reported_sum != int(result.get("total_certificate_bytes", -1)):
        violations.append({"type": "TOTAL_REPORTED_SUM_MISMATCH", "observed_sum": reported_sum, "result_total": result.get("total_certificate_bytes")})
    return {
        "record_count": len(result.get("history", [])),
        "reported_certificate_bytes": reported_sum,
        "full_serialized_history_bytes": full_sum,
        "max_record_reported_bytes": max_record_reported,
        "max_record_full_bytes": max_record_full,
        "bounds": bounds,
        "violations": violations,
    }


def audit_micro_certificate_path(initial, r50g23, r35b, r33, r47j):
    state = r33.canonical_formula(initial)
    initial_measure = tuple(r33.measure(state))
    global_bounds = symbolic_bounds(initial_measure)
    height_bound = r47j.restart_height_bound(state)
    total_reported = 0
    total_full = 0
    total_records = 0
    all_violations = []
    rounds = 0
    rup_count = 0
    terminal = None

    for round_index in range(height_bound + 1):
        rounds += 1
        before = state
        reduced = r33.simplify(before)
        local = audit_r33_result(r33, reduced, initial_measure)
        total_reported += int(local["reported_certificate_bytes"])
        total_full += int(local["full_serialized_history_bytes"])
        total_records += int(local["record_count"])
        if local["violations"]:
            all_violations.extend({"round": round_index, **v} for v in local["violations"])

        after_r33 = r33.canonical_formula(reduced["final_formula"])
        if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
            terminal = str(reduced["terminal"])
            state = after_r33
            break
        affine = r50g23.r34.recognize_complete_affine_cnf(after_r33)
        if affine["recognized"]:
            terminal = "AFFINE_RECOGNIZED"
            state = after_r33
            break
        proposal, _proposal_ledger = r35b.first_rup_strengthening(after_r33)
        if proposal is None:
            terminal = "MICRO_RUP_FIXPOINT"
            state = after_r33
            break
        assumptions = tuple(int(x) for x in proposal["assumptions"])
        if not r35b.independent_up_conflict_checker(after_r33, assumptions):
            all_violations.append({"round": round_index, "type": "RUP_CERT_FAILURE"})
            terminal = "RUP_CERT_FAILURE"
            state = after_r33
            break
        source = tuple(int(x) for x in proposal["source_clause"])
        strengthened = tuple(int(x) for x in proposal["strengthened_clause"])
        state = r35b.replace_clause_with_subclause(after_r33, source, strengthened)
        rup_count += 1
    else:
        all_violations.append({"type": "HEIGHT_BOUND_EXHAUSTED"})
        terminal = "HEIGHT_BOUND_EXHAUSTED"

    if total_records > global_bounds["state_triplet_bound"]:
        all_violations.append({"type": "TOTAL_RECORD_COUNT_BOUND", "observed": total_records, "bound": global_bounds["state_triplet_bound"]})
    if total_reported > global_bounds["total_R33_reported_certificate_bytes_bound"]:
        all_violations.append({"type": "TOTAL_REPORTED_CERTIFICATE_BOUND", "observed": total_reported, "bound": global_bounds["total_R33_reported_certificate_bytes_bound"]})
    if total_full > global_bounds["total_R33_full_serialized_history_bytes_bound"]:
        all_violations.append({"type": "TOTAL_FULL_HISTORY_BOUND", "observed": total_full, "bound": global_bounds["total_R33_full_serialized_history_bytes_bound"]})

    return {
        "initial_CLV": list(initial_measure),
        "rounds": rounds,
        "RUP_strengthenings": rup_count,
        "terminal_kind": terminal,
        "R33_record_count": total_records,
        "R33_reported_certificate_bytes": total_reported,
        "R33_full_serialized_history_bytes": total_full,
        "global_bounds": global_bounds,
        "violations": all_violations,
    }


def generate_scale_ladder(r33):
    items = []
    sizes = [12, 16, 20, 24, 28, 32]
    stall_meta = {}
    for n in sizes:
        m = int(round(4.26 * n))
        for seed_i in range(2):
            seed = 35000000 + 100000 * n + seed_i
            items.append({"family": "RANDOM_THRESHOLD", "size": n, "formula": r50g25r.random_3cnf(r33, n, m, seed), "meta": {"n": n, "m": m, "seed": seed}})

        selected = 0
        scanned = 0
        for seed_i in range(1200):
            if selected >= 1:
                break
            seed = 38000000 + 100000 * n + seed_i
            f = r50g25r.random_3cnf(r33, n, m, seed)
            scanned += 1
            try:
                baseline = r33.simplify(f)
                stalled = str(baseline.get("terminal")) == "STALLED_STACK_LEAN_CORE"
            except AssertionError:
                stalled = True
            if stalled:
                items.append({"family": "R33_STALL_TARGET", "size": n, "formula": f, "meta": {"n": n, "m": m, "seed": seed}})
                selected += 1
        stall_meta[str(n)] = {"scanned": scanned, "selected": selected}

        for pattern in ("ZERO", "ALT"):
            items.append({"family": "XOR_CYCLE", "size": n, "formula": r50g25r.xor_cycle_formula(r33, n, pattern), "meta": {"n": n, "pattern": pattern}})

    for k in (4, 6, 8, 10):
        for pattern in ("ZERO", "SINGLE"):
            f, meta = r50g25s.tseitin_prism_formula(r33, k, pattern)
            items.append({"family": "TSEITIN_PRISM", "size": int(meta["edge_variable_count"]), "formula": f, "meta": meta})

    return items, {
        "truth_used_for_generation_or_selection": False,
        "exact_truth_authority": False,
        "nominal_n_ladder": sizes,
        "stall_prefilter": stall_meta,
        "candidate_count": len(items),
        "family_partition": dict(Counter(i["family"] for i in items)),
    }


def run():
    _b, r50g23, r35b, r33, r47j = r50g25g._chain()
    schema = source_schema_audit(r33)
    items, generation = generate_scale_ladder(r33)
    rows = []
    q_hist = Counter()
    unclassified = 0
    cert_bound_violation_count = 0
    terminal_hist = Counter()
    max_reported = None
    max_full = None

    for item in items:
        formula = r33.canonical_formula(item["formula"])
        cert = audit_micro_certificate_path(formula, r50g23, r35b, r33, r47j)
        if cert["violations"]:
            cert_bound_violation_count += 1

        micro = None
        assertion = None
        try:
            micro = r50g25g.micro_normalize(formula, r50g23, r35b, r33, r47j)
        except AssertionError as exc:
            assertion = repr(exc)
            cls = r50g25r.classify_assertion(exc)
            if cls is None:
                unclassified += 1
            else:
                q_hist[cls] += 1

        if micro is not None:
            terminal = str(micro.get("terminal")) if micro.get("terminal") is not None else "RESIDUAL_FIXPOINT"
            terminal_hist[terminal] += 1
            if micro.get("semantic_sat") is None:
                q_hist["RESIDUAL_FIXPOINT"] += 1
            if micro.get("semantic_sat") is True and not micro.get("SAT_reconstruction", {}).get("pass", False):
                q_hist["RECONSTRUCTION_FAILURE"] += 1
            envelope = r50g25h.polynomial_meter_envelope(r33.measure(formula))
            if r50g25r.meter_violations(micro, envelope):
                q_hist["POLYNOMIAL_LEDGER_FAILURE"] += 1
            if int(micro.get("ledger", {}).get("R33_certificate_bytes", 0)) != int(cert["R33_reported_certificate_bytes"]):
                cert["violations"].append({
                    "type": "CANONICAL_MICRO_CERTIFICATE_LEDGER_DISAGREEMENT",
                    "canonical": int(micro.get("ledger", {}).get("R33_certificate_bytes", 0)),
                    "independent_audit": int(cert["R33_reported_certificate_bytes"]),
                })
                cert_bound_violation_count += 1
        else:
            terminal = "ASSERTION"
            terminal_hist[terminal] += 1

        row = {
            "family": item["family"],
            "size": int(item["size"]),
            "meta": item["meta"],
            "state_hash": r50g23.r50g4.fhash(formula),
            "CLV": list(r33.measure(formula)),
            "canonical_micro_terminal": None if micro is None else terminal,
            "canonical_micro_RUP": None if micro is None else int(micro.get("ledger", {}).get("RUP_successful_strengthenings", 0)),
            "canonical_micro_rounds": None if micro is None else int(micro.get("round_count", 0)),
            "certificate_audit": cert,
            "assertion": assertion,
        }
        rows.append(row)
        if max_reported is None or cert["R33_reported_certificate_bytes"] > max_reported[0]:
            max_reported = (cert["R33_reported_certificate_bytes"], row)
        if max_full is None or cert["R33_full_serialized_history_bytes"] > max_full[0]:
            max_full = (cert["R33_full_serialized_history_bytes"], row)

    hard_fail = (not schema["pass"]) or cert_bound_violation_count > 0 or unclassified > 0 or any(q_hist[c] for c in FALSIFIER_CLASSES)
    if hard_fail:
        verdict = "CERTIFICATE_SIZE_OR_Q_OBSTRUCTION_FOUND"
        next_gate = "R50G25V_MINIMAL_CERTIFICATE_OR_Q_OBSTRUCTION_FORENSICS"
    else:
        verdict = "IMPLEMENTATION_LEVEL_CERTIFICATE_SIZE_BOUND_ESTABLISHED_AND_SCALE_LADDER_CLEAN"
        next_gate = "R50G25V_UNIVERSAL_STEP_COUNT_LEMMA_OR_EXPLICIT_RESIDUAL_CORE"

    def compact_max(pair):
        if pair is None:
            return None
        value, row = pair
        cert = row["certificate_audit"]
        return {
            "bytes": int(value),
            "state_hash": row["state_hash"],
            "family": row["family"],
            "size": row["size"],
            "CLV": row["CLV"],
            "RUP": row["canonical_micro_RUP"],
            "rounds": row["canonical_micro_rounds"],
            "reported_bound": cert["global_bounds"]["total_R33_reported_certificate_bytes_bound"],
            "full_bound": cert["global_bounds"]["total_R33_full_serialized_history_bytes_bound"],
        }

    return {
        "gate": GATE,
        "parent_T_run": T_RUN,
        "parent_T_journal_commit": T_JOURNAL_COMMIT,
        "U_preregistration_commit": U_PREREG_COMMIT,
        "schema_source_audit": schema,
        "symbolic_certificate_size_lemma": {
            "per_record_integer_leaf_bound": "<=2*C*V+64",
            "per_record_reported_bytes_bound": "2048+(2*C*V+64)*(len(str(max(1,C*V)))+10)",
            "record_count_bound": "<=(C+1)*(C*V+1)*(V+1)",
            "total_reported_certificate_bytes_bound": "state_triplet_bound * per_record_reported_bytes_bound",
            "full_serialized_history_has_same_polynomial_order": True,
            "scope": "CURRENT_IMPLEMENTED_R33_RECORD_SCHEMA_AND_MICRO_SCHEDULER_ONLY",
        },
        "generation_contract": generation,
        "evaluated_candidate_count": len(rows),
        "terminal_partition": dict(sorted(terminal_hist.items())),
        "frozen_Q_falsifier_classes": list(FALSIFIER_CLASSES),
        "Q_falsifier_partition_without_exact_truth_authority": {c: int(q_hist[c]) for c in FALSIFIER_CLASSES},
        "semantic_mismatch_exact_oracle_not_run": True,
        "unclassified_assertion_count": unclassified,
        "certificate_bound_violation_count": cert_bound_violation_count,
        "max_reported_certificate_case": compact_max(max_reported),
        "max_full_serialized_history_case": compact_max(max_full),
        "verdict": verdict,
        "next_gate": next_gate,
        "interpretation_contract": {
            "reported_certificate_bytes_excludes_its_own_certificate_bytes_field_per_R33_implementation": True,
            "U_also_audits_full_serialized_history_bytes_as_stronger_diagnostic": True,
            "implementation_level_certificate_size_bound_is_not_universal_SAT_runtime_proof": True,
            "finite_scale_success_is_not_asymptotic_runtime_proof": True,
            "no_exact_truth_used_as_authority": True,
        },
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
        },
        "rows": rows,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = run()
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "verdict": out["verdict"],
        "schema_source_audit": out["schema_source_audit"],
        "evaluated_candidate_count": out["evaluated_candidate_count"],
        "terminal_partition": out["terminal_partition"],
        "Q_falsifier_partition_without_exact_truth_authority": out["Q_falsifier_partition_without_exact_truth_authority"],
        "unclassified_assertion_count": out["unclassified_assertion_count"],
        "certificate_bound_violation_count": out["certificate_bound_violation_count"],
        "max_reported_certificate_case": out["max_reported_certificate_case"],
        "max_full_serialized_history_case": out["max_full_serialized_history_case"],
        "next_gate": out["next_gate"],
        "firewall": out["firewall"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
