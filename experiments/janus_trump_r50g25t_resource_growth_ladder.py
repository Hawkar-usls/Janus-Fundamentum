from __future__ import annotations

import argparse
import itertools
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import janus_trump_r50g25r_outer_counterexample_search as r50g25r
import janus_trump_r50g25s_max_rup_minimization_structured_escalation as r50g25s
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25h_micro_rup_restart_broader_1212_polynomial_ledger_audit as r50g25h

GATE = "JANUS_TRUMP_R50G25T_RESOURCE_GROWTH_LADDER_AND_HARD_FAMILY_ESCALATION"
S_RUN = 34043229217
S_JOURNAL_COMMIT = "72906aef6cd7983f9c9bc4da2dc245e27908d9ba"
T_PREREG_COMMIT = "170714a1c724b94af83520a1c44af2cb56c14f3c"
FALSIFIER_CLASSES = tuple(r50g25r.FALSIFIER_CLASSES)
RESOURCE_KEYS = (
    "RUP_successful_strengthenings",
    "restart_count",
    "round_count",
    "R33_check_operation_upper_ledger",
    "RUP_checks",
    "RUP_UP_clause_scans",
    "RUP_UP_literal_inspections",
    "R33_certificate_bytes",
    "GF2_estimated_bit_ops",
)


def exact_validation_up_to_14(r33, formula):
    formula = r33.canonical_formula(formula)
    vs = list(r33.variables(formula))
    if len(vs) > 14:
        return {
            "status": "NOT_RUN_SIZE_LIMIT",
            "variable_count": len(vs),
            "sat": None,
            "model_count": None,
        }
    count = 0
    first_model = None
    for bits in itertools.product((False, True), repeat=len(vs)):
        a = dict(zip(vs, bits))
        if r33.eval_formula(formula, a):
            count += 1
            if first_model is None:
                first_model = {str(k): bool(v) for k, v in sorted(a.items())}
    return {
        "status": "CHECKED",
        "variable_count": len(vs),
        "assignment_space_checked": 2 ** len(vs),
        "sat": count > 0,
        "model_count": count,
        "first_model": first_model,
    }


def generate_ladder(r33):
    items = []
    generation = {
        "truth_used_for_generation_or_selection": False,
        "random_and_stall_n": [8, 10, 12, 14, 16, 18],
        "xor_n": [8, 10, 12, 14, 16, 18],
        "tseitin_edge_variables": [9, 12, 15, 18],
    }

    for n in generation["random_and_stall_n"]:
        m = int(round(4.26 * n))
        for seed_i in range(8):
            seed = 25000000 + 100000 * n + seed_i
            items.append({
                "family": "RANDOM_THRESHOLD_LADDER",
                "size": n,
                "formula": r50g25r.random_3cnf(r33, n, m, seed),
                "meta": {"n": n, "m": m, "density": 4.26, "seed": seed},
            })

        selected = 0
        scanned = 0
        for seed_i in range(1000):
            if selected >= 4:
                break
            seed = 28000000 + 100000 * n + seed_i
            f = r50g25r.random_3cnf(r33, n, m, seed)
            scanned += 1
            try:
                baseline = r33.simplify(f)
                stalled = str(baseline.get("terminal")) == "STALLED_STACK_LEAN_CORE"
            except AssertionError:
                stalled = True
            if stalled:
                items.append({
                    "family": "R33_STALL_TARGET_LADDER",
                    "size": n,
                    "formula": f,
                    "meta": {"n": n, "m": m, "seed": seed, "prefilter": "R33_STALL_OR_ASSERTION"},
                })
                selected += 1
        generation.setdefault("stall_prefilter", {})[str(n)] = {"scanned": scanned, "selected": selected}

    for n in generation["xor_n"]:
        for pattern in ("ZERO", "ONE", "ALT"):
            items.append({
                "family": "XOR_CYCLE_LADDER",
                "size": n,
                "formula": r50g25r.xor_cycle_formula(r33, n, pattern),
                "meta": {"n": n, "pattern": pattern},
            })

    # Prism k has 3k edge variables.
    for k in (3, 4, 5, 6):
        for pattern in ("ZERO", "SINGLE", "PAIR", "ALT"):
            f, meta = r50g25s.tseitin_prism_formula(r33, k, pattern)
            items.append({
                "family": "TSEITIN_PRISM_LADDER",
                "size": int(meta["edge_variable_count"]),
                "formula": f,
                "meta": meta,
            })

    generation["candidate_count"] = len(items)
    generation["family_count"] = dict(Counter(i["family"] for i in items))
    return items, generation


def extract_resources(micro):
    ledger = micro.get("ledger", {})
    return {
        "RUP_successful_strengthenings": int(ledger.get("RUP_successful_strengthenings", 0)),
        "restart_count": int(micro.get("restart_count", 0)),
        "round_count": int(micro.get("round_count", 0)),
        "R33_check_operation_upper_ledger": int(ledger.get("R33_check_operation_upper_ledger", 0)),
        "RUP_checks": int(ledger.get("RUP_checks", 0)),
        "RUP_UP_clause_scans": int(ledger.get("RUP_UP_clause_scans", 0)),
        "RUP_UP_literal_inspections": int(ledger.get("RUP_UP_literal_inspections", 0)),
        "R33_certificate_bytes": int(ledger.get("R33_certificate_bytes", 0)),
        "GF2_estimated_bit_ops": int(ledger.get("GF2_estimated_bit_ops", 0)),
    }


def audit_item(item, r50g23, r35b, r33, r47j):
    formula = r33.canonical_formula(item["formula"])
    measure = tuple(r33.measure(formula))
    envelope = r50g25h.polynomial_meter_envelope(measure)
    classes = []
    detail = []
    micro = None
    assertion = None
    try:
        micro = r50g25g.micro_normalize(formula, r50g23, r35b, r33, r47j)
    except AssertionError as exc:
        assertion = repr(exc)
        cls = r50g25r.classify_assertion(exc)
        if cls is None:
            detail.append({"class": "UNCLASSIFIED_ASSERTION", "detail": assertion[:1000]})
        else:
            classes.append(cls)
            detail.append({"class": cls, "detail": assertion[:1000]})

    exact = exact_validation_up_to_14(r33, formula)
    resources = None
    meter_violations = []
    terminal = None
    semantic_sat = None

    if micro is not None:
        resources = extract_resources(micro)
        terminal = str(micro.get("terminal")) if micro.get("terminal") is not None else "RESIDUAL_FIXPOINT"
        semantic_sat = micro.get("semantic_sat")
        if semantic_sat is None:
            classes.append("RESIDUAL_FIXPOINT")
        if exact["status"] == "CHECKED" and semantic_sat is not None and bool(semantic_sat) != bool(exact["sat"]):
            classes.append("SEMANTIC_MISMATCH")
        if semantic_sat is True and not micro.get("SAT_reconstruction", {}).get("pass", False):
            classes.append("RECONSTRUCTION_FAILURE")
        meter_violations = r50g25r.meter_violations(micro, envelope)
        if meter_violations:
            classes.append("POLYNOMIAL_LEDGER_FAILURE")

    return {
        "family": item["family"],
        "size": int(item["size"]),
        "meta": item["meta"],
        "state_hash": r50g23.r50g4.fhash(formula),
        "CLV": list(measure),
        "terminal": terminal,
        "semantic_sat": semantic_sat,
        "exact_validation": exact,
        "resources": resources,
        "meter_violations": meter_violations,
        "falsifier_classes": sorted(set(classes), key=lambda x: FALSIFIER_CLASSES.index(x)),
        "unclassified_assertion": assertion is not None and r50g25r.classify_assertion(AssertionError(assertion)) is None,
        "assertion_detail": assertion,
    }


def median_resource_table(rows):
    grouped = defaultdict(lambda: defaultdict(list))
    for row in rows:
        if row["resources"] is None:
            continue
        for key in RESOURCE_KEYS:
            grouped[(row["family"], row["size"])][key].append(int(row["resources"][key]))
    out = {}
    for (family, size), metrics in sorted(grouped.items()):
        out.setdefault(family, {})[str(size)] = {
            key: float(statistics.median(vals)) for key, vals in metrics.items()
        }
    return out


def finite_growth_diagnostic(medians):
    diagnostics = {}
    global_candidates = []
    for family, by_size in sorted(medians.items()):
        sizes = sorted(int(n) for n in by_size)
        if len(sizes) < 4:
            continue
        family_diag = {}
        for resource in RESOURCE_KEYS:
            degree_failures = []
            degree_rows = {}
            for d in range(1, 9):
                vals = []
                for n in sizes:
                    raw = float(by_size[str(n)][resource])
                    vals.append(raw / max(1.0, float(n ** d)))
                monotone = all(vals[i + 1] >= vals[i] for i in range(len(vals) - 1))
                endpoint_ratio = (vals[-1] / vals[0]) if vals[0] > 0 else (float("inf") if vals[-1] > 0 else 1.0)
                fails_degree = bool(monotone and endpoint_ratio >= 4.0)
                degree_rows[str(d)] = {
                    "normalized_sequence": vals,
                    "monotone_non_decreasing": monotone,
                    "endpoint_ratio": endpoint_ratio,
                    "degree_not_supported_by_finite_ladder": fails_degree,
                }
                if fails_degree:
                    degree_failures.append(d)
            all_1_to_8 = degree_failures == list(range(1, 9))
            family_diag[resource] = {
                "degrees_not_supported": degree_failures,
                "all_degrees_1_to_8_not_supported": all_1_to_8,
                "degree_diagnostics": degree_rows,
            }
            if all_1_to_8:
                global_candidates.append({"family": family, "resource": resource})
        diagnostics[family] = family_diag
    return diagnostics, global_candidates


def run():
    _b, r50g23, r35b, r33, r47j = r50g25g._chain()
    items, generation = generate_ladder(r33)
    rows = [audit_item(item, r50g23, r35b, r33, r47j) for item in items]

    falsifier_hist = Counter()
    unclassified = 0
    terminals = Counter()
    exact_hist = Counter()
    exact_not_run = 0
    top_cost = []
    for row in rows:
        for cls in row["falsifier_classes"]:
            falsifier_hist[cls] += 1
        if row["unclassified_assertion"]:
            unclassified += 1
        terminals[str(row["terminal"])] += 1
        ev = row["exact_validation"]
        if ev["status"] == "CHECKED":
            exact_hist["SAT" if ev["sat"] else "UNSAT"] += 1
        else:
            exact_not_run += 1
        if row["resources"] is not None:
            r = row["resources"]
            top_cost.append((
                int(r["RUP_successful_strengthenings"]),
                int(r["restart_count"]),
                int(r["round_count"]),
                int(r["R33_check_operation_upper_ledger"]),
                row["state_hash"], row["family"], row["size"], row["CLV"],
            ))

    medians = median_resource_table(rows)
    growth_diag, growth_candidates = finite_growth_diagnostic(medians)
    hard_obstruction = any(falsifier_hist[c] for c in FALSIFIER_CLASSES) or unclassified > 0

    if hard_obstruction:
        verdict = "RESOURCE_OBSTRUCTION_FOUND"
        next_gate = "R50G25U_MINIMAL_RESOURCE_OR_Q_FALSIFIER_FORENSICS"
    elif growth_candidates:
        verdict = "SUPERPOLYNOMIAL_GROWTH_CANDIDATE"
        next_gate = "R50G25U_GROWTH_CANDIDATE_EXTENSION_AND_FALSIFICATION"
    else:
        verdict = "PASS_NO_RESOURCE_OBSTRUCTION"
        next_gate = "R50G25U_SCALE_LADDER_AND_CERTIFICATE_SIZE_THEOREM_GATE"

    top_cost.sort(reverse=True)
    return {
        "gate": GATE,
        "parent_S_run": S_RUN,
        "parent_S_journal_commit": S_JOURNAL_COMMIT,
        "T_preregistration_commit": T_PREREG_COMMIT,
        "generation_contract": generation,
        "evaluated_candidate_count": len(rows),
        "terminal_partition": dict(sorted(terminals.items())),
        "exact_validation_partition": dict(sorted(exact_hist.items())),
        "exact_validation_not_run_size_limit": exact_not_run,
        "frozen_Q_falsifier_classes": list(FALSIFIER_CLASSES),
        "falsifier_partition": {c: int(falsifier_hist[c]) for c in FALSIFIER_CLASSES},
        "unclassified_assertion_count": unclassified,
        "family_size_resource_medians": medians,
        "finite_growth_diagnostic": growth_diag,
        "superpolynomial_growth_candidates": growth_candidates,
        "top_12_route_costs": [
            {
                "RUP": a, "restart": b, "rounds": c, "R33_checks": d,
                "state_hash": h, "family": fam, "size": n, "CLV": clv,
            }
            for a, b, c, d, h, fam, n, clv in top_cost[:12]
        ],
        "verdict": verdict,
        "next_gate": next_gate,
        "interpretation_contract": {
            "finite_growth_diagnostic_is_not_asymptotic_lower_bound": True,
            "exact_truth_is_post_selection_validation_only": True,
            "no_exact_truth_used_above_14_variables": True,
            "termination_does_not_imply_polynomial_runtime": True,
            "finite_success_is_not_universal_coverage": True,
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
        "evaluated_candidate_count": out["evaluated_candidate_count"],
        "terminal_partition": out["terminal_partition"],
        "exact_validation_partition": out["exact_validation_partition"],
        "exact_validation_not_run_size_limit": out["exact_validation_not_run_size_limit"],
        "falsifier_partition": out["falsifier_partition"],
        "unclassified_assertion_count": out["unclassified_assertion_count"],
        "superpolynomial_growth_candidates": out["superpolynomial_growth_candidates"],
        "top_12_route_costs": out["top_12_route_costs"],
        "next_gate": out["next_gate"],
        "firewall": out["firewall"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
