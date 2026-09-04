from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a
import janus_trump_r50g_smallest_first_exact_deadcore_falsifier as r50g
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4

GATE = "JANUS_TRUMP_R50G5_IMMEDIATE_BVE_EXACT_DESCENT_ALGEBRAIC_REDUCTION"
WIDTH_CAP = 4
MIN_N = 6
MAX_N = 10


def canon(f):
    return r33.canonical_formula(f)


def clv(f):
    return tuple(r33.measure(canon(f)))


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def vars_set(f):
    return set(r33.variables(canon(f)))


def firewall():
    return {
        "HEURISTIC_AUTHORITY": False,
        "LEARNED_SELECTOR": False,
        "PROBABILISTIC_AUTHORITY": False,
        "FINITE_REPLAY_IMPLIES_UNIVERSAL_THEOREM": False,
        "IMMEDIATE_BVE_CASE_ELIMINATED": False,
        "U_MU": "OPEN",
        "SAT_IN_P": "NOT_PROVED",
        "P_EQ_NP": "NOT_PROVED",
        "P_NE_NP": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "TRUMP_finished": False,
    }


def prove_immediate_bve_same_pivot(formula):
    """Mechanically check the source-level corollaries for one immediate escape.

    Finite calls to this routine are regression/falsifier only.  The proof authority
    is the source-definition argument frozen in the R50G5 proof note.
    """
    f = canon(formula)
    status = r50g4.micro_r33_status(f)
    if status["status"] != "IMMEDIATE_BVE_W4_ESCAPE":
        return {"applicable": False}

    direct = r50g4.first_r33_micro_candidate(f)
    if direct["kind"] != "PROPOSAL" or direct["rule"] != "BOUNDED_VARIABLE_ELIMINATION":
        raise AssertionError(("R50G5_ESCAPE_NOT_DIRECT_BVE", direct))
    x = int(direct["var"])
    if not direct["positive"] or not direct["negative"]:
        raise AssertionError(("R50G5_BVE_PIVOT_NOT_BIPOLAR", x))

    g = canon(direct["after"])
    if max_width(g) <= WIDTH_CAP:
        raise AssertionError(("R50G5_ESCAPE_AFTER_NOT_WIDE", x, max_width(g)))
    if not (clv(g) < clv(f)):
        raise AssertionError(("R50G5_R33_BVE_NOT_STRICT_CLV_DESCENT", x, clv(f), clv(g)))

    candidate = r47j.macro_candidate_fixpoint(f, x)
    if candidate is None:
        raise AssertionError(("R50G5_SAME_PIVOT_R47J_MISSING", x))
    replay = r47j.independent_fixpoint_macro_replay(f, candidate)
    if not replay["pass"]:
        raise AssertionError(("R50G5_SAME_PIVOT_REPLAY_FAIL", x, replay))
    if not candidate["DP_independent_replay_pass"]:
        raise AssertionError(("R50G5_DP_REPLAY_FLAG_FAIL", x))
    if not candidate["polynomial_intermediate_envelope_pass"]:
        raise AssertionError(("R50G5_POLY_ENVELOPE_FAIL", x))

    dp = candidate["DP"]
    dp_pos = {tuple(c) for c in dp["positive"]}
    dp_neg = {tuple(c) for c in dp["negative"]}
    direct_pos = {tuple(c) for c in direct["positive"]}
    direct_neg = {tuple(c) for c in direct["negative"]}
    if dp_pos != direct_pos or dp_neg != direct_neg:
        raise AssertionError(("R50G5_DP_PARENT_SET_MISMATCH", x))
    if {tuple(c) for c in dp["full_non_tautological_resolvents"]} != {tuple(c) for c in direct["resolvents"]}:
        raise AssertionError(("R50G5_DP_RESOLVENT_SET_MISMATCH", x))

    forced = canon(dp["transformed"])
    if not set(forced).issubset(set(g)):
        raise AssertionError(("R50G5_SUBSUMPTION_RESULT_NOT_SUBSET_OF_R33_POOL", x))
    if not (clv(forced) < clv(f)):
        raise AssertionError(("R50G5_FORCED_DP_NOT_STRICT_CLV_DESCENT", x, clv(f), clv(forced)))

    if not candidate["accepted"]:
        raise AssertionError(("R50G5_IMMEDIATE_BVE_NOT_R47J_LEGACY_ACCEPTED", x, candidate["final_CLV"]))

    final = canon(candidate["normalization"]["final_formula"])
    if not (clv(final) < clv(f)):
        raise AssertionError(("R50G5_NORMALIZATION_LOST_STRICT_CLV_DESCENT", x, clv(f), clv(final)))
    before_vars = vars_set(f)
    final_vars = vars_set(final)
    if not final_vars <= before_vars:
        raise AssertionError(("R50G5_NORMALIZATION_INTRODUCED_FRESH_VAR", x, sorted(final_vars - before_vars)))
    if x in final_vars:
        raise AssertionError(("R50G5_ELIMINATED_PIVOT_REINTRODUCED", x))
    if len(final_vars) >= len(before_vars):
        raise AssertionError(("R50G5_NO_STRICT_VARIABLE_DESCENT", x, len(before_vars), len(final_vars)))

    row, fallback_candidate = r50a._fallback_candidate(f, x)
    if fallback_candidate is None:
        raise AssertionError(("R50G5_R50A_FALLBACK_MISSING_FOR_SAME_PIVOT", x))
    terminal = candidate["normalization"]["terminal"]
    expected_safe = bool(terminal is not None or max_width(final) <= WIDTH_CAP)
    if bool(row["width4_safe"]) != expected_safe:
        raise AssertionError(("R50G5_SAFE_IFF_CHARACTERIZATION_FAIL", x, row, expected_safe))
    if not row["no_fresh_variables"] or not row["strict_variable_descent"]:
        raise AssertionError(("R50G5_MACHINE_SAFE_STRUCTURAL_PREDICATE_FAIL", x, row))

    direct_r49h = [
        int(t["pivot"])
        for t in r50a.expose_exact_tokens(f)
        if t["direct_exact_dp_authorized"]
    ]
    other_safe = []
    for v in sorted(r33.variables(f)):
        rr, cc = r50a._fallback_candidate(f, int(v))
        if cc is not None and rr["width4_safe"]:
            rep = r47j.independent_fixpoint_macro_replay(f, cc)
            if not rep["pass"]:
                raise AssertionError(("R50G5_ALT_R47J_REPLAY_FAIL", v, rep))
            other_safe.append(int(v))

    same_safe = bool(row["width4_safe"])
    implication_rescued = bool(direct_r49h or other_safe)
    return {
        "applicable": True,
        "pivot": x,
        "input_CLV": list(clv(f)),
        "R33_escape_CLV": list(clv(g)),
        "R33_escape_width": max_width(g),
        "forced_DP_CLV": list(clv(forced)),
        "forced_DP_width": max_width(forced),
        "final_CLV": list(clv(final)),
        "final_width": max_width(final),
        "terminal": terminal,
        "same_pivot_R47J_legacy_accepted": bool(candidate["accepted"]),
        "same_pivot_R47J_machine_safe": same_safe,
        "same_pivot_W4_reentry": bool(terminal is None and max_width(final) <= WIDTH_CAP),
        "same_pivot_terminal": terminal is not None,
        "same_pivot_wide_survivor": bool(terminal is None and max_width(final) > WIDTH_CAP),
        "R49H_authorized_pivots": direct_r49h,
        "R47J_safe_pivots": other_safe,
        "existing_certified_door_exists": implication_rescued,
        "strict_CLV_descent_proved": True,
        "no_fresh_variables_proved": True,
        "strict_variable_descent_proved": True,
        "independent_replay_pass": True,
        "polynomial_per_transition_envelope_pass": True,
    }


def trace_root(root, provenance):
    state = canon(root)
    seen = set()
    rows = []
    bound = 8 * max(1, len(r33.variables(state))) + 4 * max(1, len(state)) + 32
    for step_index in range(bound):
        h = r50g4.fhash(state)
        if h in seen:
            raise AssertionError(("R50G5_TRACE_CYCLE", provenance, h))
        seen.add(h)
        proof = prove_immediate_bve_same_pivot(state)
        if proof["applicable"]:
            rows.append({"step": step_index, "hash": h, **proof})
        step = r50g4.refined_exact_step(state)
        if step["kind"] in ("TERMINAL", "OPEN_OBSTRUCTION"):
            return {"escape_rows": rows, "final_kind": step["kind"], "final_lane": step["lane"]}
        state = canon(step["successor"])
    raise AssertionError(("R50G5_TRACE_BOUND", provenance))


def run_worker(worker: int, roots_per_worker: int):
    n = MIN_N + int(worker)
    if not (MIN_N <= n <= MAX_N):
        raise ValueError("R50G5_WORKER_OUTSIDE_FROZEN_RANGE")

    escape_rows = []
    final_open = 0
    for i in range(roots_per_worker):
        m = 3 * n + (i % (3 * n + 1))
        seed = 50_700_000 + worker * 100_000 + i
        root, _ = r50g.make_planted(seed, n, m, "3CNF")
        if len(r33.variables(root)) != n:
            continue
        result = trace_root(root, {"worker": worker, "seed": seed, "n": n, "m": m})
        escape_rows.extend(result["escape_rows"])
        if result["final_kind"] == "OPEN_OBSTRUCTION":
            final_open += 1

    same_safe = sum(int(r["same_pivot_R47J_machine_safe"]) for r in escape_rows)
    same_wide = sum(int(r["same_pivot_wide_survivor"]) for r in escape_rows)
    alt_r49h_rescue = sum(int(r["same_pivot_wide_survivor"] and bool(r["R49H_authorized_pivots"])) for r in escape_rows)
    alt_r47j_rescue = sum(int(r["same_pivot_wide_survivor"] and not r["R49H_authorized_pivots"] and bool(r["R47J_safe_pivots"])) for r in escape_rows)
    implication_failures = [r for r in escape_rows if not r["existing_certified_door_exists"]]

    return {
        "gate": GATE,
        "worker": worker,
        "n": n,
        "reachable_immediate_BVE_states": len(escape_rows),
        "same_pivot_R47J_safe": same_safe,
        "same_pivot_wide_survivor": same_wide,
        "same_pivot_terminal": sum(int(r["same_pivot_terminal"]) for r in escape_rows),
        "same_pivot_W4_reentry": sum(int(r["same_pivot_W4_reentry"]) for r in escape_rows),
        "wide_survivor_rescued_by_R49H": alt_r49h_rescue,
        "wide_survivor_rescued_by_other_R47J": alt_r47j_rescue,
        "exact_implication_failure_count": len(implication_failures),
        "first_exact_implication_failure": implication_failures[0] if implication_failures else None,
        "refined_open_roots": final_open,
        "rows": escape_rows,
        "firewall": firewall(),
    }


def synthesize(directory: Path):
    files = sorted(directory.glob("JANUS_TRUMP_R50G5_WORKER_*.json"))
    rows = [json.loads(p.read_text()) for p in files]
    if len(rows) != 5:
        raise AssertionError(("R50G5_EXPECTED_5_WORKERS", len(rows)))
    if sorted(r["n"] for r in rows) != [6, 7, 8, 9, 10]:
        raise AssertionError(("R50G5_N_RANGE_DRIFT", [r["n"] for r in rows]))

    metrics = {
        "reachable_immediate_BVE_states": sum(r["reachable_immediate_BVE_states"] for r in rows),
        "same_pivot_R47J_safe": sum(r["same_pivot_R47J_safe"] for r in rows),
        "same_pivot_wide_survivor": sum(r["same_pivot_wide_survivor"] for r in rows),
        "same_pivot_terminal": sum(r["same_pivot_terminal"] for r in rows),
        "same_pivot_W4_reentry": sum(r["same_pivot_W4_reentry"] for r in rows),
        "wide_survivor_rescued_by_R49H": sum(r["wide_survivor_rescued_by_R49H"] for r in rows),
        "wide_survivor_rescued_by_other_R47J": sum(r["wide_survivor_rescued_by_other_R47J"] for r in rows),
        "exact_implication_failure_count": sum(r["exact_implication_failure_count"] for r in rows),
        "refined_open_roots": sum(r["refined_open_roots"] for r in rows),
    }
    first_failure = next((r["first_exact_implication_failure"] for r in rows if r["first_exact_implication_failure"] is not None), None)
    verdict = (
        "EXPLICIT_REACHABLE_COUNTEREXAMPLE_TO_IMMEDIATE_BVE_IMPLIES_EXISTING_CERTIFIED_DOOR_FOUND"
        if metrics["exact_implication_failure_count"]
        else "SAME_PIVOT_EXACT_DESCENT_THEOREM_CLOSED__NO_COUNTEREXAMPLE_TO_EXISTING_DOOR_IMPLICATION_IN_FROZEN_REPLAY__UNIVERSAL_WIDE_CLEARANCE_OR_ALTERNATE_DOOR_OPEN"
    )
    return {
        "gate": GATE,
        "mode": "SYNTHESIS",
        "workers": len(rows),
        "n_values": sorted(r["n"] for r in rows),
        "proved_from_frozen_source_definitions": [
            "IMMEDIATE_BVE_PIVOT_IS_BIPOLAR",
            "SAME_PIVOT_EXACT_DP_EXISTS",
            "SAME_PIVOT_DP_REPLAY_AND_POLYNOMIAL_PER_TRANSITION_ENVELOPE",
            "SAME_PIVOT_STRICT_CLV_DESCENT_BEFORE_NORMALIZATION",
            "NORMALIZATION_PRESERVES_NET_STRICT_CLV_DESCENT",
            "SAME_PIVOT_NO_FRESH_VARIABLES",
            "SAME_PIVOT_STRICT_VARIABLE_DESCENT",
            "SAME_PIVOT_R47J_LEGACY_ACCEPTED",
            "SAME_PIVOT_R47J_SAFE_IFF_TERMINAL_OR_FINAL_WIDTH_LE_4",
        ],
        "critical_remaining_obligation": "UNIVERSAL_WIDE_SURVIVOR_IMPOSSIBILITY_OR_ALTERNATE_CERTIFIED_DOOR_FOR_REACHABLE_IMMEDIATE_BVE_STATES",
        "metrics": metrics,
        "first_exact_implication_failure": first_failure,
        "verdict": verdict,
        "firewall": firewall(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", type=int)
    ap.add_argument("--roots-per-worker", type=int, default=80)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--synthesize-dir", type=Path)
    args = ap.parse_args()

    if args.synthesize_dir is not None:
        out = synthesize(args.synthesize_dir)
    else:
        if args.worker is None:
            raise ValueError("--worker is required outside synthesis mode")
        out = run_worker(args.worker, args.roots_per_worker)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in out if k not in {"rows"}}, sort_keys=True))


if __name__ == "__main__":
    main()
