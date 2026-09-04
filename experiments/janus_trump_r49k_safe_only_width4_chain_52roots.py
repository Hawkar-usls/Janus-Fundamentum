from __future__ import annotations

import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r49i_bipolar_nontauto_cross_union_width5_core_hunt as r49i

GATE = "JANUS_TRUMP_R49K_SAFE_ONLY_WIDTH4_CHAIN_52ROOTS"
WIDTH_CAP = 4


def canon(f):
    return r33.canonical_formula(f)


def terminal_kind(f):
    f = canon(f)
    if any(len(c) == 0 for c in f):
        return "UNSAT_EMPTY_CLAUSE"
    if len(f) == 0:
        return "SAT_EMPTY_FORMULA"
    return None


def pure_prune(formula):
    f = canon(formula)
    events = []
    while True:
        tk = terminal_kind(f)
        if tk is not None:
            return f, events, tk
        chosen = None
        chosen_lit = None
        for v in r33.variables(f):
            pos = any(v in c for c in f)
            neg = any(-v in c for c in f)
            if pos and not neg:
                chosen, chosen_lit = int(v), int(v)
                break
            if neg and not pos:
                chosen, chosen_lit = int(v), -int(v)
                break
        if chosen is None:
            return f, events, None
        before = f
        f = canon([c for c in f if chosen_lit not in c])
        events.append({
            "var": chosen,
            "satisfying_literal": chosen_lit,
            "before_CLV": list(r33.measure(before)),
            "after_CLV": list(r33.measure(f)),
        })
        if chosen in set(r33.variables(f)):
            raise AssertionError(("R49K_PURE_VAR_NOT_ELIMINATED", chosen))


def run_root(root, provenance, root_index):
    root = canon(root)
    current = root
    initial_v = len(r33.variables(root))
    steps = []
    total_pair_checks = 0

    for ordinal in range(initial_v + 1):
        current, pure_events, tk = pure_prune(current)
        if max((len(c) for c in current), default=0) > WIDTH_CAP:
            raise AssertionError(("R49K_WIDTH_DRIFT_AFTER_PURE", root_index, ordinal))
        if tk is not None:
            return {
                "covered": True,
                "root_index": int(root_index),
                "root_hash": r49i.fhash(root),
                "root_CLV": list(r49i.clv(root)),
                "provenance": provenance,
                "steps": steps,
                "terminal": tk,
                "final_CLV": list(r49i.clv(current)),
                "total_pair_checks": int(total_pair_checks),
            }

        profiles = [r49i.variable_profile(current, int(v)) for v in r33.variables(current)]
        safe = [p for p in profiles if p["bipolar"] and int(p["chi_star"]) <= WIDTH_CAP]
        if not safe:
            return {
                "covered": False,
                "root_index": int(root_index),
                "root_hash": r49i.fhash(root),
                "root_CLV": list(r49i.clv(root)),
                "provenance": provenance,
                "steps": steps,
                "terminal": None,
                "final_CLV": list(r49i.clv(current)),
                "total_pair_checks": int(total_pair_checks),
                "obstruction": {
                    "state_index": len(steps),
                    "state_hash": r49i.fhash(current),
                    "state_CLV": list(r49i.clv(current)),
                    "state_max_width": r49i.max_width(current),
                    "pure_prune_events_before_obstruction": pure_events,
                    "profiles": profiles,
                    "formula": [list(c) for c in current],
                },
            }

        chosen_profile = min(safe, key=lambda p: int(p["var"]))
        var = int(chosen_profile["var"])
        dp = r45a.exact_dp_record(current, var)
        if dp is None:
            raise AssertionError(("R49K_SAFE_BIPOLAR_WITHOUT_DP", var))
        replay = r45a.independent_dp_replay(current, dp)
        if not replay["pass"]:
            raise AssertionError(("R49K_DP_REPLAY_FAIL", root_index, var, replay))
        transformed = canon(dp["transformed"])
        if var in set(r33.variables(transformed)):
            raise AssertionError(("R49K_PIVOT_NOT_REMOVED", var))
        mw = max((len(c) for c in transformed), default=0)
        if mw > WIDTH_CAP:
            raise AssertionError(("R49K_SAFE_PIVOT_WIDTH_FAIL", root_index, var, chosen_profile, mw))
        total_pair_checks += int(dp["resolution_pair_checks"])
        steps.append({
            "step": len(steps) + 1,
            "before_hash": r49i.fhash(current),
            "before_CLV": list(r49i.clv(current)),
            "pure_prune_events": pure_events,
            "pivot": var,
            "chi_star": int(chosen_profile["chi_star"]),
            "safe_pivot_count": len(safe),
            "after_DP_hash": r49i.fhash(transformed),
            "after_DP_CLV": list(r49i.clv(transformed)),
            "after_DP_max_width": mw,
            "DP_replay_pass": True,
            "resolution_pair_checks": int(dp["resolution_pair_checks"]),
        })
        current = transformed

    raise AssertionError(("R49K_STEP_CAP_EXHAUSTED", root_index, r49i.clv(current)))


def compact(record):
    out = {
        "covered": bool(record["covered"]),
        "root_index": int(record["root_index"]),
        "root_hash": record["root_hash"],
        "root_CLV": record["root_CLV"],
        "provenance": record["provenance"],
        "selected_pivots": [int(s["pivot"]) for s in record["steps"]],
        "step_count": len(record["steps"]),
        "terminal": record["terminal"],
        "final_CLV": record["final_CLV"],
        "total_pair_checks": int(record["total_pair_checks"]),
    }
    if not record["covered"]:
        o = record["obstruction"]
        out["obstruction"] = {
            "state_index": int(o["state_index"]),
            "state_hash": o["state_hash"],
            "state_CLV": o["state_CLV"],
            "state_max_width": int(o["state_max_width"]),
        }
    return out


def run():
    roots = r49i.collect_roots()
    records = []
    first_obstruction = None
    for idx, (root, provenance) in enumerate(roots, 1):
        rec = run_root(root, provenance, idx)
        records.append(rec)
        if not rec["covered"]:
            first_obstruction = rec
            break

    compact_records = [compact(r) for r in records]
    covered = [r for r in records if r["covered"]]
    verdict = (
        "EXPLICIT_REACHABLE_SAFE_ONLY_CHAIN_OBSTRUCTION_FOUND"
        if first_obstruction is not None
        else "ALL_52_FROZEN_ROOTS_REACH_TERMINAL_BY_PURE_OR_CHI_STAR_SAFE_EXACT_DP__FINITE_ONLY"
    )
    return {
        "gate": GATE,
        "verdict": verdict,
        "controller": {
            "pre_step": "REPEATED_PURE_LITERAL_EXISTENTIAL_PRUNE",
            "pivot_policy": "MINIMUM_VARIABLE_AMONG_BIPOLAR_PIVOTS_WITH_chi_star_LE_4",
            "successor": "CANONICAL_EXACT_DP_WITH_INDEPENDENT_REPLAY",
            "persisted_width_cap": WIDTH_CAP,
            "fresh_variables": False,
        },
        "metrics": {
            "roots_attempted": len(records),
            "roots_covered": len(covered),
            "obstructions": 0 if first_obstruction is None else 1,
            "total_selected_steps": sum(len(r["steps"]) for r in records),
            "max_selected_steps": max((len(r["steps"]) for r in records), default=0),
            "total_resolution_pair_checks": sum(int(r["total_pair_checks"]) for r in records),
        },
        "first_obstruction": None if first_obstruction is None else first_obstruction,
        "roots": compact_records,
        "interpretation": {
            "one_obstruction_refutes_this_deterministic_safe_only_policy": first_obstruction is not None,
            "all_52_green_proves_universal_W4_coverage": False,
            "finite_green_is_evidence_for_easy_lane_chain_only": first_obstruction is None,
        },
        "firewall": {
            "R49H_LOCAL_SAFE_PIVOT_LEMMA": "PROVED_IN_SCOPE",
            "SAFE_ONLY_52ROOT_CHAIN": "REFUTED" if first_obstruction is not None else "FINITE_GREEN_ONLY",
            "DIRECT_W4_STEP_COVERAGE": "OPEN",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    out = run()
    path = Path("artifacts/JANUS_TRUMP_R49K_SAFE_ONLY_WIDTH4_CHAIN_52ROOTS_RESULT.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": out["gate"],
        "verdict": out["verdict"],
        "metrics": out["metrics"],
        "first_obstruction": None if out["first_obstruction"] is None else compact(out["first_obstruction"]),
        "firewall": out["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
