from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r49i_bipolar_nontauto_cross_union_width5_core_hunt as r49i
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a
import janus_trump_r50g_smallest_first_exact_deadcore_falsifier as r50g
import janus_trump_r50g1_r33_w4_domain_escape_guarded_replay as r50g1

GATE = "JANUS_TRUMP_R50G2_GUARDED_FULL_SMALLEST_FIRST_EXACT_DEADCORE_FALSIFIER"
WIDTH_CAP = 4
MIN_N = 6
MAX_N = 10


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def clv(f):
    return tuple(r33.measure(canon(f)))


def fhash(f):
    return r49i.fhash(canon(f))


def firewall(reachable_found: bool = False, all_w4_found: bool = False):
    return {
        "ARCHITECTURAL_LAW": "PRODUCER_MAY_PROPOSE__INVARIANT_DECIDES_AUTHORITY",
        "GUARDED_U": "REFUTED_BY_EXPLICIT_REACHABLE_SAT_OPEN" if reachable_found else "OPEN",
        "STRONGER_ALL_W4_STEP_COVERAGE": "REFUTED_BY_EXPLICIT_SAT_OPEN" if all_w4_found else "OPEN",
        "NO_DEADCORE_FOUND_IMPLIES_U": False,
        "GENERATED_POOL_SMALLEST_IS_GLOBAL_MINIMUM": False,
        "FINITE_SEARCH_PROVES_P_EQUALS_NP": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_EQ_NP": "NOT_PROVED",
        "P_NE_NP": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "TRUMP_finished": False,
    }


def _r33_authority_status(formula):
    f = canon(formula)
    reduced = r33.simplify(f)
    after = canon(reduced["final_formula"])
    terminal = reduced["terminal"]
    if terminal != "STALLED_STACK_LEAN_CORE":
        return {
            "status": "TERMINAL",
            "terminal": terminal,
            "after": after,
            "reduced": reduced,
        }
    if after != f and max_width(after) <= WIDTH_CAP:
        return {
            "status": "AUTHORIZED_W4_REDUCTION",
            "terminal": terminal,
            "after": after,
            "reduced": reduced,
        }
    if after != f and max_width(after) > WIDTH_CAP:
        return {
            "status": "REJECTED_W4_DOMAIN_ESCAPE",
            "terminal": terminal,
            "after": after,
            "reduced": reduced,
        }
    return {
        "status": "FIXED_POINT",
        "terminal": terminal,
        "after": after,
        "reduced": reduced,
    }


def exact_guarded_open_test(formula):
    """Independent exact audit of a candidate guarded OPEN state.

    R33 may be unavailable either because it is at a fixed point or because its
    exact proposal leaves persisted W4.  The latter is preserved as evidence but
    receives no transition authority.  Every R49H/R47J pivot is then checked.
    """
    f = canon(formula)
    if max_width(f) > WIDTH_CAP:
        return {"applicable": False, "reason": "INPUT_WIDTH_GT_4"}

    r33s = _r33_authority_status(f)
    if r33s["status"] == "TERMINAL":
        return {"applicable": False, "reason": "R33_TERMINAL", "R33_terminal": r33s["terminal"]}
    if r33s["status"] == "AUTHORIZED_W4_REDUCTION":
        return {
            "applicable": False,
            "reason": "R33_AUTHORIZED_W4_REDUCTION_EXISTS",
            "successor_hash": fhash(r33s["after"]),
            "successor_CLV": list(clv(r33s["after"])),
        }

    r33_escape = None
    if r33s["status"] == "REJECTED_W4_DOMAIN_ESCAPE":
        r33_escape = {
            "escaped_hash": fhash(r33s["after"]),
            "escaped_CLV": list(clv(r33s["after"])),
            "escaped_max_width": max_width(r33s["after"]),
            "rule_applications": int(r33s["reduced"]["total_rule_applications"]),
            "history": r33s["reduced"]["history"],
        }

    vars_ = tuple(int(v) for v in r33.variables(f))
    tokens = r50a.expose_exact_tokens(f)
    direct = [t for t in tokens if t["direct_exact_dp_authorized"]]
    if direct:
        return {
            "applicable": True,
            "open": False,
            "reason": "R49H_DIRECT_PIVOT_EXISTS",
            "direct_pivots": [int(t["var"]) for t in direct],
            "R33_status": r33s["status"],
            "R33_domain_escape": r33_escape,
        }

    rows = []
    breaker = None
    for var in sorted(vars_):
        row, candidate = r50a._fallback_candidate(f, int(var))
        replay_pass = True
        if candidate is not None:
            replay = r47j.independent_fixpoint_macro_replay(f, candidate)
            replay_pass = bool(replay["pass"])
            if not replay_pass:
                raise AssertionError(("R50G2_R47J_REPLAY_FAIL", var, replay))
        rr = dict(row)
        rr["independent_replay_pass"] = replay_pass
        rows.append(rr)
        if rr.get("width4_safe", False) and breaker is None:
            breaker = rr

    if breaker is not None:
        return {
            "applicable": True,
            "open": False,
            "reason": "R47J_SAFE_PIVOT_EXISTS",
            "breaker": breaker,
            "rows": rows,
            "R33_status": r33s["status"],
            "R33_domain_escape": r33_escape,
        }

    guarded = r50g1.guarded_exact_step(f)
    if not (
        guarded["kind"] == "OPEN_OBSTRUCTION"
        and guarded.get("all_current_variables_checked") is True
    ):
        raise AssertionError(("R50G2_ALL_DOORS_BLOCKED_BUT_GUARDED_NOT_OPEN", guarded))

    return {
        "applicable": True,
        "open": True,
        "reason": "ALL_GUARDED_DOORS_BLOCKED",
        "rows": rows,
        "R33_status": r33s["status"],
        "R33_domain_escape": r33_escape,
        "all_current_variables_checked": True,
        "guarded_lane": guarded["lane"],
    }


def _direct_sat_witness(formula):
    # Falsifier-only verifier; never transition authority.
    return r33.brute_force_model(canon(formula))


def _open_target(formula, provenance, exact, kind, trace=None):
    f = canon(formula)
    witness = _direct_sat_witness(f)
    if witness is None or not r33.eval_formula(f, witness):
        raise AssertionError(("R50G2_OPEN_STATE_NOT_SAT", provenance))
    return {
        "kind": kind,
        "formula": [list(c) for c in f],
        "hash": fhash(f),
        "CLV": list(clv(f)),
        "max_width": max_width(f),
        "SAT_witness": {str(k): bool(v) for k, v in witness.items()},
        "SAT_witness_directly_verifies": True,
        "exact_guarded_open_test": exact,
        "provenance": provenance,
        "trace": trace,
    }


def trace_reachable_root(root, provenance):
    state = canon(root)
    seen = set()
    trace = []
    escape_events = []
    max_steps = 3 * max(1, len(r33.variables(state))) + 8
    for step_index in range(max_steps):
        h = fhash(state)
        if h in seen:
            raise AssertionError(("R50G2_REACHABLE_TRACE_CYCLE", h))
        seen.add(h)
        if max_width(state) > WIDTH_CAP:
            raise AssertionError(("R50G2_PERSISTED_STATE_LEFT_W4", h, max_width(state)))

        step = r50g1.guarded_exact_step(state)
        if step.get("r33_domain_escape") is not None:
            escape_events.append({
                "step": step_index,
                "state_hash": h,
                "state_CLV": list(clv(state)),
                "guarded_lane": step["lane"],
                "escape": step["r33_domain_escape"],
            })
        trace.append({
            "step": step_index,
            "state_hash": h,
            "state_CLV": list(clv(state)),
            "kind": step["kind"],
            "lane": step["lane"],
            "R33_domain_escape": step.get("r33_domain_escape") is not None,
        })

        if step["kind"] == "TERMINAL":
            return {
                "terminal": step.get("terminal"),
                "open_target": None,
                "trace": trace,
                "escape_events": escape_events,
            }
        if step["kind"] == "OPEN_OBSTRUCTION":
            exact = exact_guarded_open_test(state)
            if not (exact.get("applicable") and exact.get("open")):
                raise AssertionError(("R50G2_GUARDED_OPEN_DISAGREES_WITH_EXACT_AUDIT", exact))
            target = _open_target(
                state,
                provenance,
                exact,
                "REACHABLE_FROM_PLANTED_3CNF_UNDER_GUARDED_CONTROLLER",
                trace=trace,
            )
            return {
                "terminal": None,
                "open_target": target,
                "trace": trace,
                "escape_events": escape_events,
            }
        state = canon(step["successor"])
    raise AssertionError(("R50G2_TRACE_BOUND_EXHAUSTED", provenance, trace[-1] if trace else None))


def candidate_key(target):
    C, L, V = target["CLV"]
    return (V, C, L, target["hash"])


def run_worker(worker: int, roots_per_worker: int, w4_candidates_per_worker: int):
    n = MIN_N + int(worker)
    if not (MIN_N <= n <= MAX_N):
        raise ValueError("R50G2_WORKER_OUTSIDE_FROZEN_N_RANGE")

    reachable_targets = []
    trace_rows = []
    all_escape_events = []
    for i in range(roots_per_worker):
        m = 3 * n + (i % (3 * n + 1))
        seed = 50_700_000 + worker * 100_000 + i
        root, _planted = r50g.make_planted(seed, n, m, "3CNF")
        if len(r33.variables(root)) != n:
            continue
        provenance = {
            "source": "PLANTED_3CNF",
            "worker": worker,
            "seed": seed,
            "n": n,
            "m": m,
            "root_hash": fhash(root),
        }
        result = trace_reachable_root(root, provenance)
        all_escape_events.extend(result["escape_events"])
        if result["open_target"] is not None:
            reachable_targets.append(result["open_target"])
        trace_rows.append({
            "seed": seed,
            "root_hash": fhash(root),
            "root_CLV": list(clv(root)),
            "trace_length": len(result["trace"]),
            "terminal": result["terminal"],
            "guarded_open_found": result["open_target"] is not None,
            "domain_escape_events": len(result["escape_events"]),
        })

    # Stronger all-W4 falsifier lane.  Unlike R49O this lane is mixed-width,
    # has no min-side cutoff, and sorts only by exact structural size after
    # checking that R33 itself has no authorized W4 move and R49H is absent.
    structural_pool = []
    profiles = ("W34", "W234", "W4_CONTROL")
    for i in range(w4_candidates_per_worker):
        profile = profiles[i % len(profiles)]
        m = 3 * n + (i % (4 * n + 1))
        seed = 50_800_000 + worker * 100_000 + i
        formula, _planted = r50g.make_planted(seed, n, m, profile)
        if len(r33.variables(formula)) != n or max_width(formula) > WIDTH_CAP:
            continue

        r33s = _r33_authority_status(formula)
        if r33s["status"] in ("TERMINAL", "AUTHORIZED_W4_REDUCTION"):
            continue
        tokens = r50a.expose_exact_tokens(formula)
        if any(t["direct_exact_dp_authorized"] for t in tokens):
            continue
        structural_pool.append((
            candidate_key({"CLV": list(clv(formula)), "hash": fhash(formula)}),
            formula,
            {
                "source": "PLANTED_W4_GENERATED_POOL",
                "profile": profile,
                "worker": worker,
                "seed": seed,
                "n": n,
                "m": m,
                "R33_status": r33s["status"],
            },
        ))

    structural_pool.sort(key=lambda row: row[0])
    all_w4_targets = []
    exact_finalists_tested = 0
    for _, formula, provenance in structural_pool[:8]:
        exact_finalists_tested += 1
        exact = exact_guarded_open_test(formula)
        if exact.get("applicable") and exact.get("open"):
            all_w4_targets.append(_open_target(
                formula,
                provenance,
                exact,
                "GENERATED_ALL_W4__REACHABILITY_NOT_ESTABLISHED",
                trace=None,
            ))

    reachable_targets.sort(key=candidate_key)
    all_w4_targets.sort(key=candidate_key)
    reachable_found = bool(reachable_targets)
    all_w4_found = bool(all_w4_targets)
    if reachable_found:
        verdict = "EXPLICIT_REACHABLE_SAT_GUARDED_DEADCORE_FOUND__GUARDED_U_REFUTED_FOR_FROZEN_MACHINE"
    elif all_w4_found:
        verdict = "EXPLICIT_SAT_ALL_W4_GUARDED_DEADCORE_FOUND__REACHABILITY_OPEN"
    else:
        verdict = "NO_GUARDED_DEADCORE_FOUND_IN_GENERATED_WORKER_BUDGET"

    return {
        "gate": GATE,
        "mode": "WORKER",
        "worker": worker,
        "n": n,
        "verdict": verdict,
        "reachable_lane": {
            "requested_roots": roots_per_worker,
            "executed_roots": len(trace_rows),
            "terminal_roots": sum(1 for r in trace_rows if r["terminal"] is not None),
            "guarded_open_count": len(reachable_targets),
            "domain_escape_events": len(all_escape_events),
            "first_target": reachable_targets[0] if reachable_targets else None,
            "rows": trace_rows,
        },
        "all_W4_lane": {
            "generated_candidates_requested": w4_candidates_per_worker,
            "structural_pool_count": len(structural_pool),
            "exact_finalists_tested": exact_finalists_tested,
            "guarded_open_count_reachability_open": len(all_w4_targets),
            "first_target": all_w4_targets[0] if all_w4_targets else None,
        },
        "firewall": firewall(reachable_found, all_w4_found),
    }


def synthesize(directory: Path):
    paths = sorted(directory.glob("JANUS_TRUMP_R50G2_WORKER_*.json"))
    if len(paths) != 5:
        raise AssertionError(("R50G2_EXPECTED_FIVE_WORKERS", len(paths), [p.name for p in paths]))
    workers = [json.loads(p.read_text(encoding="utf-8")) for p in paths]
    n_values = sorted(int(w["n"]) for w in workers)
    if n_values != [6, 7, 8, 9, 10]:
        raise AssertionError(("R50G2_N_RANGE_DRIFT", n_values))

    reachable_targets = [
        w["reachable_lane"]["first_target"]
        for w in workers
        if w["reachable_lane"]["first_target"] is not None
    ]
    all_w4_targets = [
        w["all_W4_lane"]["first_target"]
        for w in workers
        if w["all_W4_lane"]["first_target"] is not None
    ]
    reachable_targets.sort(key=candidate_key)
    all_w4_targets.sort(key=candidate_key)
    reachable_found = bool(reachable_targets)
    all_w4_found = bool(all_w4_targets)

    if reachable_found:
        verdict = "EXPLICIT_REACHABLE_SAT_GUARDED_DEADCORE_FOUND__GUARDED_U_REFUTED_FOR_FROZEN_MACHINE"
    elif all_w4_found:
        verdict = "EXPLICIT_SAT_ALL_W4_GUARDED_DEADCORE_FOUND__REACHABILITY_OPEN"
    else:
        verdict = "NO_GUARDED_DEADCORE_FOUND_IN_FROZEN_R50G2_BUDGET__U_REMAINS_OPEN"

    return {
        "gate": GATE,
        "mode": "SYNTHESIS",
        "verdict": verdict,
        "workers": len(workers),
        "n_values": n_values,
        "reachable_roots_executed": sum(int(w["reachable_lane"]["executed_roots"]) for w in workers),
        "terminal_roots": sum(int(w["reachable_lane"]["terminal_roots"]) for w in workers),
        "R33_domain_escape_events": sum(int(w["reachable_lane"]["domain_escape_events"]) for w in workers),
        "reachable_deadcore_count": sum(int(w["reachable_lane"]["guarded_open_count"]) for w in workers),
        "all_w4_deadcore_count_reachability_open": sum(int(w["all_W4_lane"]["guarded_open_count_reachability_open"]) for w in workers),
        "all_W4_structural_pool_count": sum(int(w["all_W4_lane"]["structural_pool_count"]) for w in workers),
        "all_W4_exact_finalists_tested": sum(int(w["all_W4_lane"]["exact_finalists_tested"]) for w in workers),
        "first_reachable_target": reachable_targets[0] if reachable_targets else None,
        "first_all_W4_target": all_w4_targets[0] if all_w4_targets else None,
        "worker_summaries": [
            {
                "worker": w["worker"],
                "n": w["n"],
                "verdict": w["verdict"],
                "terminal_roots": w["reachable_lane"]["terminal_roots"],
                "domain_escape_events": w["reachable_lane"]["domain_escape_events"],
                "reachable_open": w["reachable_lane"]["guarded_open_count"],
                "all_W4_open": w["all_W4_lane"]["guarded_open_count_reachability_open"],
            }
            for w in workers
        ],
        "firewall": firewall(reachable_found, all_w4_found),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", type=int)
    ap.add_argument("--roots-per-worker", type=int, default=80)
    ap.add_argument("--w4-candidates-per-worker", type=int, default=240)
    ap.add_argument("--synthesize-dir", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()

    if a.synthesize_dir is not None:
        out = synthesize(a.synthesize_dir)
    else:
        if a.worker is None:
            raise SystemExit("--worker required outside synthesis mode")
        out = run_worker(a.worker, a.roots_per_worker, a.w4_candidates_per_worker)

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": out["gate"],
        "mode": out["mode"],
        "verdict": out["verdict"],
        "firewall": out["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
