from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25x_adversarial_stall_search as r50g25x
import janus_trump_r50g25y_minimal_w_policy_counterexample_forensics as r50g25y

GATE = "JANUS_TRUMP_R50G25AA_UNIVERSAL_CONTROLLED_DP_DOOR_EXISTENCE_OR_SYMBOLIC_COUNTEREXAMPLE"
AA_PREREG_COMMIT = "6176a1827a5bdc467007187eb37a6f19fa5513a5"
Z_SEALED_RESULT_COMMIT = "fd66cbc880a2d15617fb3432a31d2d355d281088"
Z_RUN = 34045971286
Z_ARTIFACT = 9993361591
EXPECTED_X_RESIDUALS = 15
EXPECTED_Y_CORE_HASH = "98d929c32c0f838a920888ca10c4a2f2eb9afe5ad58ac471d8854851e5bb7532"


def canonical_hash(formula):
    return r50g25y.canonical_hash(r33.canonical_formula(formula))


def size_sum(formula):
    c, l, _v = r33.measure(formula)
    return c + l


def analytic_dp_upper_bound(formula, var):
    """Sufficient pre-materialization upper bound for exact DP + canonical NF.

    It counts every positive/negative parent pair as if it produced a distinct,
    non-tautological raw resolvent at the maximum pair length. Tautology removal,
    literal deduplication, clause deduplication, and strict-subsumption NF can only
    reduce the exact canonical result from this upper bound.
    """
    formula = r33.canonical_formula(formula)
    C, L, _V = r33.measure(formula)
    pos = [c for c in formula if var in c]
    neg = [c for c in formula if -var in c]
    p, q = len(pos), len(neg)
    if not p or not q:
        return None
    SP = sum(len(c) for c in pos)
    SN = sum(len(c) for c in neg)
    ub_c = C - p - q + p * q
    ub_l = L - SP - SN + q * (SP - p) + p * (SN - q)
    return {
        "var": int(var),
        "p": p,
        "q": q,
        "SP": SP,
        "SN": SN,
        "UB_C": int(ub_c),
        "UB_L": int(ub_l),
        "UB_S": int(ub_c + ub_l),
    }


def terminal_label(w):
    if w["kind"] == "AFFINE":
        return str(w["route"][-1].get("stop", "AFFINE")) if w.get("route") else "AFFINE"
    if w["kind"] == "TERMINAL":
        return str(w["route"][-1].get("R33_terminal")) if w.get("route") else "TERMINAL"
    return None


def controlled_audit(initial, chain):
    initial = r33.canonical_formula(initial)
    c0, l0, v0 = r33.measure(initial)
    budget = (c0 + l0) * (v0 + 1) * (v0 + 1)
    state = initial
    fallback = []
    residual_events = []
    analytic_gap_count = 0
    analytic_certified_event_count = 0
    exact_dp_records_checked = 0
    analytic_bound_checks = 0
    implementation_failures = []

    for outer in range(v0 + 1):
        try:
            w = r50g25y.policy_replay(state, chain)
        except AssertionError as exc:
            return {
                "status": "IMPLEMENTATION_FAILURE",
                "class": "W_POLICY_REPLAY_ASSERTION",
                "error": repr(exc),
                "budget": budget,
                "fallback_DP_count": len(fallback),
                "fallback_trace": fallback,
                "residual_events": residual_events,
                "analytic_gap_count": analytic_gap_count,
                "analytic_certified_event_count": analytic_certified_event_count,
                "exact_dp_records_checked": exact_dp_records_checked,
                "analytic_bound_checks": analytic_bound_checks,
            }

        if w["kind"] in {"TERMINAL", "AFFINE"}:
            return {
                "status": "TERMINAL",
                "terminal_kind": w["kind"],
                "terminal_label": terminal_label(w),
                "budget": budget,
                "fallback_DP_count": len(fallback),
                "fallback_trace": fallback,
                "residual_events": residual_events,
                "residual_event_count": len(residual_events),
                "analytic_gap_count": analytic_gap_count,
                "analytic_certified_event_count": analytic_certified_event_count,
                "exact_dp_records_checked": exact_dp_records_checked,
                "analytic_bound_checks": analytic_bound_checks,
                "max_controlled_state_size": max([c0 + l0] + [x["after_size"] for x in fallback]),
                "implementation_failures": implementation_failures,
            }

        if w["kind"] != "RESIDUAL":
            return {
                "status": "IMPLEMENTATION_FAILURE",
                "class": "UNEXPECTED_W_KIND",
                "kind": w["kind"],
                "budget": budget,
                "fallback_DP_count": len(fallback),
                "fallback_trace": fallback,
                "residual_events": residual_events,
                "analytic_gap_count": analytic_gap_count,
                "analytic_certified_event_count": analytic_certified_event_count,
                "exact_dp_records_checked": exact_dp_records_checked,
                "analytic_bound_checks": analytic_bound_checks,
            }

        core = r33.canonical_formula(w["state"])
        before = r33.measure(core)
        before_size = before[0] + before[1]
        if before_size > budget:
            return {
                "status": "OBSTRUCTION",
                "class": "STATE_BUDGET_VIOLATION",
                "budget": budget,
                "residual_CLV": list(before),
                "residual_hash": canonical_hash(core),
                "residual_formula": [list(c) for c in core],
                "fallback_DP_count": len(fallback),
                "fallback_trace": fallback,
                "residual_events": residual_events,
                "analytic_gap_count": analytic_gap_count,
                "analytic_certified_event_count": analytic_certified_event_count,
                "exact_dp_records_checked": exact_dp_records_checked,
                "analytic_bound_checks": analytic_bound_checks,
            }
        if len(fallback) >= v0:
            return {
                "status": "OBSTRUCTION",
                "class": "RESIDUAL_AFTER_AT_MOST_V0_FALLBACKS",
                "budget": budget,
                "residual_CLV": list(before),
                "residual_hash": canonical_hash(core),
                "residual_formula": [list(c) for c in core],
                "fallback_DP_count": len(fallback),
                "fallback_trace": fallback,
                "residual_events": residual_events,
                "analytic_gap_count": analytic_gap_count,
                "analytic_certified_event_count": analytic_certified_event_count,
                "exact_dp_records_checked": exact_dp_records_checked,
                "analytic_bound_checks": analytic_bound_checks,
            }

        bounds = []
        exact = []
        for var in r33.variables(core):
            ub = analytic_dp_upper_bound(core, var)
            if ub is None:
                continue
            analytic_bound_checks += 1
            try:
                rec = r50g25y.exact_dp_record(core, var)
            except AssertionError as exc:
                implementation_failures.append({"outer": outer, "var": int(var), "class": "EXACT_DP_RECORD_ASSERTION", "error": repr(exc)})
                continue
            if rec is None:
                continue
            exact_dp_records_checked += 1
            if not rec.get("replay_pass"):
                implementation_failures.append({"outer": outer, "var": int(var), "class": "DP_REPLAY_FAILURE"})
                continue
            exact_size = int(rec["CLV_after"][0]) + int(rec["CLV_after"][1])
            if exact_size > ub["UB_S"]:
                implementation_failures.append({
                    "outer": outer,
                    "var": int(var),
                    "class": "ANALYTIC_BOUND_UNSOUND",
                    "exact_size": exact_size,
                    "UB_S": ub["UB_S"],
                })
                continue
            bounds.append({**ub, "exact_size": exact_size, "exact_CLV_after": list(rec["CLV_after"])})
            exact.append(rec)

        if implementation_failures:
            return {
                "status": "IMPLEMENTATION_FAILURE",
                "class": implementation_failures[0]["class"],
                "implementation_failures": implementation_failures,
                "budget": budget,
                "residual_CLV": list(before),
                "residual_hash": canonical_hash(core),
                "fallback_DP_count": len(fallback),
                "fallback_trace": fallback,
                "residual_events": residual_events,
                "analytic_gap_count": analytic_gap_count,
                "analytic_certified_event_count": analytic_certified_event_count,
                "exact_dp_records_checked": exact_dp_records_checked,
                "analytic_bound_checks": analytic_bound_checks,
            }

        if not exact:
            return {
                "status": "OBSTRUCTION",
                "class": "NO_EXACT_DP_PIVOT_AT_RESIDUAL",
                "budget": budget,
                "residual_CLV": list(before),
                "residual_hash": canonical_hash(core),
                "residual_formula": [list(c) for c in core],
                "fallback_DP_count": len(fallback),
                "fallback_trace": fallback,
                "residual_events": residual_events,
                "analytic_gap_count": analytic_gap_count,
                "analytic_certified_event_count": analytic_certified_event_count,
                "exact_dp_records_checked": exact_dp_records_checked,
                "analytic_bound_checks": analytic_bound_checks,
            }

        exact_admissible = []
        for rec in exact:
            after = rec["CLV_after"]
            if int(after[2]) < int(before[2]) and int(after[0]) + int(after[1]) <= budget:
                exact_admissible.append(rec)

        analytic_admissible = [b for b in bounds if b["UB_S"] <= budget and int(b["exact_CLV_after"][2]) < int(before[2])]
        best_bound = min(bounds, key=lambda b: (b["UB_S"], b["var"])) if bounds else None
        event = {
            "outer_round": outer,
            "residual_hash": canonical_hash(core),
            "residual_CLV": list(before),
            "budget": budget,
            "pivot_count": len(exact),
            "exact_admissible_count": len(exact_admissible),
            "analytic_admissible_count": len(analytic_admissible),
            "best_analytic_var": None if best_bound is None else int(best_bound["var"]),
            "best_analytic_UB_S": None if best_bound is None else int(best_bound["UB_S"]),
            "best_analytic_slack": None if best_bound is None else int(budget - best_bound["UB_S"]),
            "min_exact_size": min(int(r["CLV_after"][0]) + int(r["CLV_after"][1]) for r in exact),
        }
        residual_events.append(event)

        if not exact_admissible:
            return {
                "status": "OBSTRUCTION",
                "class": "ALL_EXACT_DP_PIVOTS_EXCEED_ROOT_BUDGET",
                "budget": budget,
                "residual_CLV": list(before),
                "residual_hash": canonical_hash(core),
                "residual_formula": [list(c) for c in core],
                "all_exact_after_CLV": [list(r["CLV_after"]) for r in exact],
                "all_analytic_bounds": bounds,
                "fallback_DP_count": len(fallback),
                "fallback_trace": fallback,
                "residual_events": residual_events,
                "analytic_gap_count": analytic_gap_count,
                "analytic_certified_event_count": analytic_certified_event_count,
                "exact_dp_records_checked": exact_dp_records_checked,
                "analytic_bound_checks": analytic_bound_checks,
            }

        if analytic_admissible:
            analytic_certified_event_count += 1
        else:
            analytic_gap_count += 1

        chosen = min(exact_admissible, key=lambda r: (int(r["CLV_after"][0]), int(r["CLV_after"][1]), int(r["var"])))
        transformed = r33.canonical_formula(chosen["transformed"])
        after = r33.measure(transformed)
        fallback.append({
            "outer_round": outer,
            "var": int(chosen["var"]),
            "before_CLV": list(before),
            "after_CLV": list(after),
            "before_size": before_size,
            "after_size": int(after[0] + after[1]),
            "budget": budget,
            "relation_under_old_CLV": chosen["relation"],
            "pair_checks": int(chosen["pair_checks"]),
            "pool_clause_count": int(chosen["pool_clause_count_before_subsumption"]),
            "replay_pass": bool(chosen["replay_pass"]),
            "analytic_certified_some_pivot": bool(analytic_admissible),
            "chosen_pivot_analytic_UB_S": next((int(b["UB_S"]) for b in bounds if int(b["var"]) == int(chosen["var"])), None),
        })
        state = transformed

    return {
        "status": "OBSTRUCTION",
        "class": "RESIDUAL_AFTER_AT_MOST_V0_FALLBACKS",
        "budget": budget,
        "fallback_DP_count": len(fallback),
        "fallback_trace": fallback,
        "residual_events": residual_events,
        "analytic_gap_count": analytic_gap_count,
        "analytic_certified_event_count": analytic_certified_event_count,
        "exact_dp_records_checked": exact_dp_records_checked,
        "analytic_bound_checks": analytic_bound_checks,
    }


def new_random_roots():
    out = []
    for n in (64, 72, 80):
        for density in (4.20, 4.26, 4.32):
            m = int(round(density * n))
            for rep in range(2):
                seed = 61000000 + n * 10000 + int(round(density * 100)) * 10 + rep
                f = r50g25x.r50g25r.random_3cnf(r33, n, m, seed)
                out.append({"name": f"AA_RANDOM_{n}_{int(round(density*100))}_{rep}", "family": "NEW_RANDOM_THRESHOLD", "formula": f, "meta": {"n": n, "m": m, "density": density, "seed": seed}})
    return out


def new_stall_targets():
    out = []
    failures = []
    for n in (64, 72, 80):
        m = int(round(4.26 * n))
        selected = None
        for i in range(800):
            seed = 62000000 + n * 10000 + i
            f = r50g25x.r50g25r.random_3cnf(r33, n, m, seed)
            try:
                base = r33.simplify(f)
            except AssertionError as exc:
                failures.append({"n": n, "seed": seed, "error": repr(exc)})
                continue
            if str(base.get("terminal")) == "STALLED_STACK_LEAN_CORE":
                selected = {"name": f"AA_R33_STALL_{n}", "family": "NEW_R33_STALL_TARGET", "formula": f, "meta": {"n": n, "m": m, "seed": seed, "scanned": i + 1}}
                break
        if selected is not None:
            out.append(selected)
    return out, failures


def structured_controls():
    out = []
    for n in (36, 48, 60):
        for pattern in ("ZERO", "ALT"):
            f = r50g25x.r50g25r.xor_cycle_formula(r33, n, pattern)
            out.append({"name": f"AA_XOR_{n}_{pattern}", "family": "STRUCTURED_XOR_CONTROL", "formula": f, "meta": {"n": n, "pattern": pattern}})
    for k in (12, 16, 20):
        for pattern in ("ZERO", "SINGLE"):
            f, meta = r50g25x.r50g25s.tseitin_prism_formula(r33, k, pattern)
            out.append({"name": f"AA_TSEITIN_{k}_{pattern}", "family": "STRUCTURED_TSEITIN_CONTROL", "formula": f, "meta": meta})
    return out


def z_replay_cases(chain):
    x = r50g25x.run()
    if x["residual_fixpoint_count"] != EXPECTED_X_RESIDUALS:
        raise AssertionError(("AA_X_RESIDUAL_COUNT_DRIFT", x["residual_fixpoint_count"]))
    out = []
    for i, res in enumerate(x["residuals"]):
        f = r33.canonical_formula(res["residual_formula"])
        out.append({"name": f"Z_X_RESIDUAL_{i:02d}", "family": "Z_X_RESIDUAL", "formula": f, "meta": {"source_family": res["family"], "source_hash": res["residual_hash"]}})

    _sealed, target = r47j.load_counterexample()
    minimized, ledger = r50g25y.truth_blind_minimize(target, chain)
    yrep = r50g25y.policy_replay(minimized, chain)
    if yrep["kind"] != "RESIDUAL":
        raise AssertionError(("AA_Y_RESIDUAL_REPRO_FAIL", yrep["kind"]))
    core = r33.canonical_formula(yrep["state"])
    if canonical_hash(core) != EXPECTED_Y_CORE_HASH:
        raise AssertionError(("AA_Y_CORE_HASH_DRIFT", canonical_hash(core)))
    out.append({"name": "Z_Y_MINIMIZED_CORE", "family": "Z_Y_MINIMIZED_CORE", "formula": core, "meta": {"accepted_edits": ledger["accepted_count"]}})
    return out


def dedupe_cases(cases):
    seen = set()
    out = []
    for case in cases:
        f = r33.canonical_formula(case["formula"])
        if f in seen:
            continue
        seen.add(f)
        out.append({**case, "formula": f, "hash": canonical_hash(f), "CLV": list(r33.measure(f))})
    return out


def audit_case(case, chain):
    out = controlled_audit(case["formula"], chain)
    residual_events = out.get("residual_events", [])
    slacks = [e["best_analytic_slack"] for e in residual_events if e.get("best_analytic_slack") is not None]
    return {
        "name": case["name"],
        "family": case["family"],
        "hash": case["hash"],
        "initial_CLV": case["CLV"],
        "meta": case.get("meta", {}),
        "min_best_analytic_slack": min(slacks) if slacks else None,
        **out,
    }


def mutation_cases(base_cases, base_rows):
    row_by_hash = {r["hash"]: r for r in base_rows}
    candidates = []
    for c in base_cases:
        r = row_by_hash[c["hash"]]
        if c["family"] not in {"NEW_RANDOM_THRESHOLD", "NEW_R33_STALL_TARGET"}:
            continue
        if int(r.get("residual_event_count", len(r.get("residual_events", [])))) <= 0:
            continue
        if r.get("min_best_analytic_slack") is None:
            continue
        candidates.append((int(r["min_best_analytic_slack"]), c["hash"], c))
    candidates.sort(key=lambda x: (x[0], x[1]))
    parents = candidates[:4]
    out = []
    for pi, (slack, _h, parent) in enumerate(parents):
        n = int(parent.get("meta", {}).get("n") or r33.measure(parent["formula"])[2])
        for j in range(5):
            seed = 64000000 + 1000 * pi + j
            mutated = r50g25x.mutate_clause_truth_blind(parent["formula"], n, seed)
            out.append({
                "name": f"AA_BEHAVIOR_MUT_{pi}_{j}",
                "family": "BEHAVIOR_GUIDED_MUTATION",
                "formula": mutated,
                "meta": {"parent_hash": parent["hash"], "parent_min_best_analytic_slack": slack, "n": n, "seed": seed},
            })
    return out, [{"hash": c[2]["hash"], "name": c[2]["name"], "min_best_analytic_slack": c[0]} for c in parents]


def run():
    chain = r50g25g._chain()
    generation_failures = []
    try:
        cases = z_replay_cases(chain)
    except AssertionError as exc:
        return {
            "gate": GATE,
            "AA_preregistration_commit": AA_PREREG_COMMIT,
            "parent_Z_sealed_result_commit": Z_SEALED_RESULT_COMMIT,
            "verdict": "IMPLEMENTATION_OR_REPLAY_FAILURE",
            "generation_failures": [{"class": "Z_REPLAY_GENERATION_FAILURE", "error": repr(exc)}],
            "firewall": {"P_VS_NP": "OPEN", "SAT_IN_P": "NOT_PROVED", "TRUMP_finished": False, "finite_success_is_not_universal_coverage": True},
        }

    cases.extend(new_random_roots())
    stalls, stall_failures = new_stall_targets()
    generation_failures.extend(stall_failures)
    cases.extend(stalls)
    cases.extend(structured_controls())
    base_cases = dedupe_cases(cases)
    base_rows = [audit_case(c, chain) for c in base_cases]

    mutations, mutation_parents = mutation_cases(base_cases, base_rows)
    all_cases = dedupe_cases(base_cases + mutations)
    audited_hashes = {r["hash"] for r in base_rows}
    rows = list(base_rows)
    for c in all_cases:
        if c["hash"] not in audited_hashes:
            rows.append(audit_case(c, chain))
            audited_hashes.add(c["hash"])

    family_hist = Counter(r["family"] for r in rows)
    status_hist = Counter(r["status"] for r in rows)
    terminal_hist = Counter(str(r.get("terminal_label") or r.get("terminal_kind")) for r in rows if r["status"] == "TERMINAL")
    obstruction_hist = Counter(r.get("class", "UNKNOWN") for r in rows if r["status"] == "OBSTRUCTION")
    implementation_hist = Counter(r.get("class", "UNKNOWN") for r in rows if r["status"] == "IMPLEMENTATION_FAILURE")
    residual_event_count = sum(len(r.get("residual_events", [])) for r in rows)
    analytic_gap_event_count = sum(int(r.get("analytic_gap_count", 0)) for r in rows)
    analytic_certified_event_count = sum(int(r.get("analytic_certified_event_count", 0)) for r in rows)
    exact_records_checked = sum(int(r.get("exact_dp_records_checked", 0)) for r in rows)
    analytic_bound_checks = sum(int(r.get("analytic_bound_checks", 0)) for r in rows)

    obstruction_rows = [r for r in rows if r["status"] == "OBSTRUCTION"]
    implementation_rows = [r for r in rows if r["status"] == "IMPLEMENTATION_FAILURE"]
    exact_obstruction_rows = [r for r in obstruction_rows if r.get("class") in {"NO_EXACT_DP_PIVOT_AT_RESIDUAL", "ALL_EXACT_DP_PIVOTS_EXCEED_ROOT_BUDGET", "RESIDUAL_AFTER_AT_MOST_V0_FALLBACKS", "STATE_BUDGET_VIOLATION"}]

    if generation_failures or implementation_rows:
        verdict = "IMPLEMENTATION_OR_REPLAY_FAILURE"
    elif exact_obstruction_rows:
        verdict = "EXACT_CONTROLLED_DP_DOOR_OBSTRUCTION_FOUND"
    elif analytic_gap_event_count:
        verdict = "ANALYTIC_CERTIFICATE_GAP_BUT_EXACT_DOOR_EXISTS"
    elif residual_event_count and analytic_certified_event_count == residual_event_count:
        verdict = "ANALYTIC_DOOR_CERTIFICATE_COVERS_ALL_AA_RESIDUALS"
    else:
        verdict = "NO_EXACT_OBSTRUCTION_IN_AA_DOMAIN_BUT_UNIVERSAL_DOOR_EXISTENCE_REMAINS_OPEN"

    hardest = None
    for r in rows:
        if r.get("min_best_analytic_slack") is None:
            continue
        key = (int(r["min_best_analytic_slack"]), r["hash"])
        if hardest is None or key < (int(hardest["min_best_analytic_slack"]), hardest["hash"]):
            hardest = r
    max_fallback = None
    for r in rows:
        n = int(r.get("fallback_DP_count", 0))
        if max_fallback is None or (n, r["hash"]) > (int(max_fallback.get("fallback_DP_count", 0)), max_fallback["hash"]):
            max_fallback = r

    def compact_row(r):
        if r is None:
            return None
        keep = {k: r.get(k) for k in ["name", "family", "hash", "initial_CLV", "status", "class", "terminal_label", "budget", "fallback_DP_count", "max_controlled_state_size", "min_best_analytic_slack", "analytic_gap_count", "analytic_certified_event_count"] if k in r}
        if r.get("status") == "OBSTRUCTION":
            keep["residual_CLV"] = r.get("residual_CLV")
            keep["residual_hash"] = r.get("residual_hash")
            keep["residual_formula"] = r.get("residual_formula")
        return keep

    next_gate = "R50G25AB_MINIMIZE_CONTROLLED_DP_BUDGET_OBSTRUCTION_AND_CLASSIFY_FILL_IN_CAUSE" if exact_obstruction_rows else "R50G25AB_HYBRID_EXCLUSION_INVARIANT_VS_GALIL_STYLE_DP_LOWER_BOUND"

    return {
        "gate": GATE,
        "AA_preregistration_commit": AA_PREREG_COMMIT,
        "parent_Z_sealed_result_commit": Z_SEALED_RESULT_COMMIT,
        "parent_Z_run_id": Z_RUN,
        "parent_Z_artifact_id": Z_ARTIFACT,
        "known_theory_guard": {
            "Galil_1977_pure_DP_exponential_clause_lower_bound_any_elimination_order": True,
            "DOI": "10.1016/0304-3975(77)90054-8",
            "pure_DP_variable_descent_alone_cannot_prove_universal_polynomiality": True,
        },
        "analytic_bound_contract": {
            "UB_C": "C-p-q+p*q",
            "UB_L": "L-SP-SN+q*(SP-p)+p*(SN-q)",
            "UB_S": "UB_C+UB_L",
            "exact_size_must_be_le_UB_S": True,
            "UB_S_le_B_is_sufficient_not_necessary": True,
        },
        "generation_contract": {
            "truth_used_for_generation_ranking_or_pivot_selection": False,
            "exact_truth_authority": False,
            "base_case_count": len(base_cases),
            "mutation_count": len(all_cases) - len(base_cases),
            "total_unique_case_count": len(rows),
            "mutation_parents": mutation_parents,
            "generation_failure_count": len(generation_failures),
        },
        "family_partition": dict(sorted(family_hist.items())),
        "status_partition": dict(sorted(status_hist.items())),
        "terminal_partition": dict(sorted(terminal_hist.items())),
        "obstruction_partition": dict(sorted(obstruction_hist.items())),
        "implementation_failure_partition": dict(sorted(implementation_hist.items())),
        "residual_event_count": residual_event_count,
        "analytic_certified_event_count": analytic_certified_event_count,
        "analytic_gap_event_count": analytic_gap_event_count,
        "exact_dp_records_checked": exact_records_checked,
        "analytic_bound_checks": analytic_bound_checks,
        "exact_controlled_door_obstruction_count": len(exact_obstruction_rows),
        "generation_failures": generation_failures,
        "hardest_analytic_slack_case": compact_row(hardest),
        "max_fallback_case": compact_row(max_fallback),
        "obstructions": [compact_row(r) for r in exact_obstruction_rows[:10]],
        "verdict": verdict,
        "next_gate": next_gate,
        "interpretation": {
            "analytic_certificate_success_if_any_is_only_a_finite_domain_result": True,
            "absence_of_exact_obstruction_in_AA_does_not_override_Galil_pure_DP_lower_bound": True,
            "a_universal_hybrid_theorem_must_show_extra_doors_prevent_the_hard_fill_in_regime": True,
        },
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "finite_success_is_not_universal_coverage": True,
            "polynomial_state_budget_is_not_polynomial_runtime_without_universal_door_and_operation_bounds": True,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    result = run()
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result.get(k) for k in ["gate", "verdict", "family_partition", "status_partition", "residual_event_count", "analytic_certified_event_count", "analytic_gap_event_count", "exact_controlled_door_obstruction_count", "next_gate"]}, indent=2, sort_keys=True))
    print("HARDEST", json.dumps(result.get("hardest_analytic_slack_case"), sort_keys=True))
    print("MAX_FALLBACK", json.dumps(result.get("max_fallback_case"), sort_keys=True))
    print("OBSTRUCTIONS", json.dumps(result.get("obstructions"), sort_keys=True))


if __name__ == "__main__":
    main()
