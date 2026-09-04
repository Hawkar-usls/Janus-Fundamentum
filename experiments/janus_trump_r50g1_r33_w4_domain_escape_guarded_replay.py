from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a
import janus_trump_r50g_smallest_first_exact_deadcore_falsifier as r50g

GATE = "JANUS_TRUMP_R50G1_R33_W4_DOMAIN_ESCAPE_GUARDED_REPLAY"
WIDTH_CAP = 4
N = 10
ROOTS = 80
WORKER = 4


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def fhash(f):
    return r50g.fhash(canon(f))


def clv(f):
    return tuple(r33.measure(canon(f)))


def guarded_exact_step(formula):
    """R50A with one frozen authority guard: an R33 result may not leave W4.

    No new inference rule is introduced.  If full R33 simplification would leave
    persisted W4, its exact result is recorded but not committed; the unchanged
    state proceeds to the already-existing R49H and exhaustive R47J lanes.
    """
    f = canon(formula)
    if max_width(f) > WIDTH_CAP:
        raise ValueError("R50G1_DOMAIN_REQUIRES_W4")

    reduced = r33.simplify(f)
    after = canon(reduced["final_formula"])
    terminal = reduced["terminal"]
    escape = None

    if terminal != "STALLED_STACK_LEAN_CORE":
        solved = r42.solve_declared_terminal(after, terminal)
        if not solved["verification_pass"]:
            raise AssertionError(("R50G1_R33_TERMINAL_VERIFY_FAIL", solved))
        return {
            "kind": "TERMINAL",
            "lane": "R33_CERTIFIED_TERMINAL",
            "terminal": solved["kind"],
            "semantic_sat": bool(solved["sat"]),
            "r33_domain_escape": None,
        }

    if after != f and max_width(after) <= WIDTH_CAP:
        return {
            "kind": "NONTERMINAL",
            "lane": "R33_CERTIFIED_REDUCTION",
            "successor": [list(c) for c in after],
            "successor_hash": fhash(after),
            "successor_CLV": list(clv(after)),
            "r33_domain_escape": None,
        }

    if after != f and max_width(after) > WIDTH_CAP:
        escape = {
            "input_hash": fhash(f),
            "input_CLV": list(clv(f)),
            "input_max_width": max_width(f),
            "escaped_hash": fhash(after),
            "escaped_CLV": list(clv(after)),
            "escaped_max_width": max_width(after),
            "R33_terminal": terminal,
            "R33_rule_applications": int(reduced["total_rule_applications"]),
            "R33_history": reduced["history"],
            "escaped_formula": [list(c) for c in after],
        }

    tokens = r50a.expose_exact_tokens(f)
    for token in tokens:
        if token["direct_exact_dp_authorized"]:
            step = r50a._direct_dp_transition(f, token)
            step["r33_domain_escape"] = escape
            step["guarded_R33_skipped"] = escape is not None
            return step

    attempts = []
    for var in sorted(r33.variables(f)):
        row, candidate = r50a._fallback_candidate(f, int(var))
        attempts.append(row)
        if not row["width4_safe"]:
            continue
        replay = r47j.independent_fixpoint_macro_replay(f, candidate)
        if not replay["pass"]:
            raise AssertionError(("R50G1_R47J_REPLAY_FAIL", var, replay))
        final = canon(candidate["normalization"]["final_formula"])
        term = candidate["normalization"]["terminal"]
        return {
            "kind": "TERMINAL" if term is not None else "NONTERMINAL",
            "lane": "EXHAUSTIVE_R47J_FIRST_CERTIFIED_WIDTH4_DESCENT",
            "selected_pivot": int(var),
            "terminal": term,
            "semantic_sat": candidate["normalization"]["semantic_sat"],
            "successor": [list(c) for c in final],
            "successor_hash": fhash(final),
            "successor_CLV": list(clv(final)),
            "fallback_attempts_before_accept": attempts,
            "independent_replay_pass": True,
            "r33_domain_escape": escape,
            "guarded_R33_skipped": escape is not None,
        }

    return {
        "kind": "OPEN_OBSTRUCTION",
        "lane": "GUARDED_R33_THEN_EXHAUSTIVE_NO_WIDTH4_SUCCESSOR",
        "input_hash": fhash(f),
        "input_CLV": list(clv(f)),
        "all_current_variables_checked": True,
        "fallback_attempts": attempts,
        "r33_domain_escape": escape,
        "guarded_R33_skipped": escape is not None,
    }


def direct_sat_witness(formula):
    # Falsifier-only verifier.  Never used as algorithmic authority.
    return r33.brute_force_model(canon(formula))


def trace_root(root, provenance):
    state = canon(root)
    seen = set()
    trace = []
    escapes = []
    max_steps = 3 * max(1, len(r33.variables(state))) + 8
    for i in range(max_steps):
        h = fhash(state)
        if h in seen:
            raise AssertionError(("R50G1_CYCLE", h))
        seen.add(h)
        if max_width(state) > WIDTH_CAP:
            raise AssertionError(("R50G1_PERSISTED_STATE_LEFT_W4", h, max_width(state)))

        current_machine_failure = None
        try:
            r50a.exact_step(state)
        except AssertionError as e:
            if str(e) == "R50A_R33_WIDTH4_PERSISTENCE_FAIL":
                current_machine_failure = str(e)
            else:
                raise

        step = guarded_exact_step(state)
        if step.get("r33_domain_escape") is not None:
            escapes.append({
                "step": i,
                "state_formula": [list(c) for c in state],
                "state_hash": h,
                "state_CLV": list(clv(state)),
                "current_R50A_failure": current_machine_failure,
                "guarded_lane": step["lane"],
                "escape": step["r33_domain_escape"],
            })
        trace.append({
            "step": i,
            "state_hash": h,
            "state_CLV": list(clv(state)),
            "current_R50A_failure": current_machine_failure,
            "guarded_kind": step["kind"],
            "guarded_lane": step["lane"],
        })

        if step["kind"] == "TERMINAL":
            return {"trace": trace, "escapes": escapes, "terminal": step.get("terminal"), "open": None}
        if step["kind"] == "OPEN_OBSTRUCTION":
            sat = direct_sat_witness(state)
            open_row = {
                "formula": [list(c) for c in state],
                "hash": h,
                "CLV": list(clv(state)),
                "SAT": sat is not None,
                "SAT_witness": None if sat is None else {str(k): bool(v) for k, v in sat.items()},
                "all_current_variables_checked": bool(step["all_current_variables_checked"]),
                "fallback_attempts": step["fallback_attempts"],
                "r33_domain_escape": step["r33_domain_escape"],
                "provenance": provenance,
            }
            return {"trace": trace, "escapes": escapes, "terminal": None, "open": open_row}
        state = canon(step["successor"])
    raise AssertionError(("R50G1_TRACE_BOUND", provenance))


def run():
    rows = []
    all_escapes = []
    open_states = []
    for i in range(ROOTS):
        m = 3 * N + (i % (3 * N + 1))
        seed = 50_700_000 + WORKER * 100_000 + i
        root, witness = r50g.make_planted(seed, N, m, "3CNF")
        if len(r33.variables(root)) != N:
            continue
        provenance = {"worker": WORKER, "seed": seed, "n": N, "m": m, "root_hash": fhash(root)}
        result = trace_root(root, provenance)
        for e in result["escapes"]:
            e["provenance"] = provenance
            all_escapes.append(e)
        if result["open"] is not None:
            open_states.append(result["open"])
        rows.append({
            **provenance,
            "trace_length": len(result["trace"]),
            "domain_escape_count": len(result["escapes"]),
            "terminal": result["terminal"],
            "guarded_open": result["open"] is not None,
        })

    reproduced = len(all_escapes) > 0
    reachable_sat_open = [x for x in open_states if x["SAT"]]
    if not reproduced:
        verdict = "R50G_DOMAIN_ESCAPE_NOT_REPRODUCED__INSTRUMENTATION_REVIEW_REQUIRED"
    elif reachable_sat_open:
        verdict = "EXPLICIT_REACHABLE_SAT_OPEN_STATE_AFTER_R33_W4_GUARD__GUARDED_U_FALSIFIED_FOR_FROZEN_RULESET"
    else:
        verdict = "R33_W4_DOMAIN_ESCAPE_REPRODUCED__ALL_OBSERVED_ESCAPES_RESCUED_BY_EXISTING_R49H_OR_R47J_OR_TERMINAL__FINITE_ONLY"

    return {
        "gate": GATE,
        "verdict": verdict,
        "corpus": {"n": N, "requested_roots": ROOTS, "executed_roots": len(rows)},
        "metrics": {
            "domain_escape_events": len(all_escapes),
            "roots_with_domain_escape": sum(1 for r in rows if r["domain_escape_count"] > 0),
            "guarded_open_states": len(open_states),
            "guarded_reachable_sat_open_states": len(reachable_sat_open),
            "terminal_roots": sum(1 for r in rows if r["terminal"] is not None),
        },
        "first_domain_escape": all_escapes[0] if all_escapes else None,
        "first_reachable_sat_open": reachable_sat_open[0] if reachable_sat_open else None,
        "rows": rows,
        "firewall": {
            "CURRENT_R50A_TOTALITY": "REFUTED_BY_REPRODUCED_DOMAIN_ESCAPE" if reproduced else "OBSERVED_PREVIOUSLY_NOT_REPRODUCED_HERE",
            "GUARDED_U": "REFUTED_BY_EXPLICIT_REACHABLE_SAT_OPEN" if reachable_sat_open else "OPEN",
            "FINITE_REPAIR_SUCCESS_PROVES_U": False,
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    out = run()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"gate": out["gate"], "verdict": out["verdict"], "metrics": out["metrics"], "firewall": out["firewall"]}, sort_keys=True))


if __name__ == "__main__":
    main()
