from __future__ import annotations

import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r49i_bipolar_nontauto_cross_union_width5_core_hunt as r49i
import janus_trump_r49k_safe_only_width4_chain_52roots as r49k

GATE = "JANUS_TRUMP_R49L_HYBRID_EASY_R47J_WIDTH4_CHAIN_52ROOTS"
WIDTH_CAP = 4


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def terminal_kind(f):
    f = canon(f)
    if any(len(c) == 0 for c in f):
        return "UNSAT_EMPTY_CLAUSE"
    if len(f) == 0:
        return "SAT_EMPTY_FORMULA"
    return None


def candidate_row(current, candidate, replay_pass=None):
    final = canon(candidate["normalization"]["final_formula"])
    before_vars = set(r33.variables(current))
    after_vars = set(r33.variables(final))
    terminal = candidate["normalization"]["terminal"]
    delta_v = len(before_vars) - len(after_vars)
    no_fresh = after_vars <= before_vars
    w = max_width(final)
    eligible = bool(terminal is not None or (delta_v >= 1 and no_fresh))
    safe = bool(terminal is not None or (eligible and w <= WIDTH_CAP))
    return {
        "var": int(candidate["var"]),
        "input_CLV": list(r49i.clv(current)),
        "forced_DP_CLV": list(candidate["DP"]["measure_after_forced_DP"]),
        "final_CLV": list(r49i.clv(final)),
        "terminal": terminal,
        "semantic_sat": candidate["normalization"]["semantic_sat"],
        "delta_V_eliminated": int(delta_v),
        "no_fresh_variables": bool(no_fresh),
        "eligible": bool(eligible),
        "final_max_width": int(w),
        "width4_safe": bool(safe),
        "R47J_legacy_CLV_accepted_flag": bool(candidate["accepted"]),
        "DP_independent_replay_pass": bool(candidate["DP_independent_replay_pass"]),
        "polynomial_intermediate_envelope_pass": bool(candidate["polynomial_intermediate_envelope_pass"]),
        "R47J_independent_replay_pass": replay_pass,
        "R47J_round_count": int(candidate["normalization"]["round_count"]),
        "R47J_restart_count": int(candidate["normalization"]["restart_count"]),
        "R47J_RUP_checks": int(candidate["normalization"]["ledger"]["RUP_checks"]),
    }


def scan(current, replay_all=False):
    rows = []
    candidates = {}
    for v in r33.variables(current):
        c = r47j.macro_candidate_fixpoint(current, int(v))
        if c is None:
            rows.append({"var": int(v), "candidate": False, "eligible": False, "width4_safe": False})
            continue
        if not c["DP_independent_replay_pass"] or not c["polynomial_intermediate_envelope_pass"]:
            raise AssertionError(("R49L_CANDIDATE_INTEGRITY_FAIL", v))
        replay_pass = None
        if replay_all:
            replay = r47j.independent_fixpoint_macro_replay(current, c)
            if not replay["pass"]:
                raise AssertionError(("R49L_REPLAY_FAIL", v, replay))
            replay_pass = True
        rows.append(candidate_row(current, c, replay_pass))
        candidates[int(v)] = c
    return rows, candidates


def run_root(root, provenance, root_index):
    root = canon(root)
    current = root
    V0 = len(r33.variables(root))
    selected = []
    total_candidate_probes = 0
    total_r47j_rup_checks = 0
    easy_steps = 0
    r47j_steps = 0

    for state_index in range(V0 + 1):
        current, pure_events, tk = r49k.pure_prune(current)
        if max_width(current) > WIDTH_CAP:
            raise AssertionError(("R49L_WIDTH_DRIFT_AFTER_PURE", root_index, state_index))
        if tk is not None:
            return {
                "covered": True,
                "root_index": int(root_index),
                "root_hash": r49i.fhash(root),
                "root_CLV": list(r49i.clv(root)),
                "provenance": provenance,
                "selected": selected,
                "terminal": tk,
                "final_CLV": list(r49i.clv(current)),
                "easy_steps": easy_steps,
                "r47j_steps": r47j_steps,
                "total_candidate_probes": total_candidate_probes,
                "total_r47j_rup_checks": total_r47j_rup_checks,
                "obstruction": None,
            }

        profiles = [r49i.variable_profile(current, int(v)) for v in r33.variables(current)]
        easy = [p for p in profiles if p["bipolar"] and int(p["chi_star"]) <= WIDTH_CAP]
        if easy:
            p = min(easy, key=lambda x: int(x["var"]))
            var = int(p["var"])
            dp = r45a.exact_dp_record(current, var)
            if dp is None:
                raise AssertionError(("R49L_EASY_WITHOUT_DP", root_index, var))
            replay = r45a.independent_dp_replay(current, dp)
            if not replay["pass"]:
                raise AssertionError(("R49L_DP_REPLAY_FAIL", root_index, var, replay))
            final = canon(dp["transformed"])
            if max_width(final) > WIDTH_CAP or var in set(r33.variables(final)):
                raise AssertionError(("R49L_EASY_PERSIST_FAIL", root_index, var, max_width(final)))
            selected.append({
                "step": len(selected) + 1,
                "lane": "CHI_STAR_SAFE_EXACT_DP",
                "before_hash": r49i.fhash(current),
                "before_CLV": list(r49i.clv(current)),
                "pure_prune_events": pure_events,
                "var": var,
                "chi_star": int(p["chi_star"]),
                "after_hash": r49i.fhash(final),
                "after_CLV": list(r49i.clv(final)),
                "after_max_width": max_width(final),
                "DP_replay_pass": True,
                "resolution_pair_checks": int(dp["resolution_pair_checks"]),
            })
            easy_steps += 1
            current = final
            continue

        rows, candidates = scan(current, replay_all=False)
        total_candidate_probes += len(rows)
        safe = [x for x in rows if x.get("width4_safe", False)]
        if not safe:
            replay_rows, _ = scan(current, replay_all=True)
            replay_safe = [x for x in replay_rows if x.get("width4_safe", False)]
            total_candidate_probes += len(replay_rows)
            if replay_safe:
                raise AssertionError(("R49L_REPLAY_DISCOVERY_DRIFT", root_index, replay_safe))
            return {
                "covered": False,
                "root_index": int(root_index),
                "root_hash": r49i.fhash(root),
                "root_CLV": list(r49i.clv(root)),
                "provenance": provenance,
                "selected": selected,
                "terminal": None,
                "final_CLV": list(r49i.clv(current)),
                "easy_steps": easy_steps,
                "r47j_steps": r47j_steps,
                "total_candidate_probes": total_candidate_probes,
                "total_r47j_rup_checks": total_r47j_rup_checks,
                "obstruction": {
                    "kind": "NO_EASY_OR_PARTIAL_R47J_WIDTH4_SAFE_SUCCESSOR",
                    "state_index": int(state_index),
                    "state_hash": r49i.fhash(current),
                    "state_CLV": list(r49i.clv(current)),
                    "state_max_width": max_width(current),
                    "profiles": profiles,
                    "candidate_rows": replay_rows,
                    "formula": [list(c) for c in current],
                },
            }

        chosen_row = min(safe, key=lambda x: int(x["var"]))
        var = int(chosen_row["var"])
        chosen = candidates[var]
        replay = r47j.independent_fixpoint_macro_replay(current, chosen)
        if not replay["pass"]:
            raise AssertionError(("R49L_R47J_REPLAY_FAIL", root_index, var, replay))
        row = candidate_row(current, chosen, True)
        final = canon(chosen["normalization"]["final_formula"])
        if row["terminal"] is None:
            if int(row["final_max_width"]) > WIDTH_CAP or int(row["delta_V_eliminated"]) < 1 or not row["no_fresh_variables"]:
                raise AssertionError(("R49L_R47J_PERSIST_FAIL", root_index, row))
        total_r47j_rup_checks += int(row["R47J_RUP_checks"])
        selected.append({
            "step": len(selected) + 1,
            "lane": "PARTIAL_R47J_WIDTH4_DISCHARGE",
            "before_hash": r49i.fhash(current),
            "before_CLV": list(r49i.clv(current)),
            "pure_prune_events": pure_events,
            "var": var,
            "after_hash": r49i.fhash(final),
            "after_CLV": list(r49i.clv(final)),
            "after_max_width": int(row["final_max_width"]),
            "terminal": row["terminal"],
            "semantic_sat": row["semantic_sat"],
            "R47J_RUP_checks": int(row["R47J_RUP_checks"]),
            "R47J_independent_replay_pass": True,
        })
        r47j_steps += 1
        if row["terminal"] is not None:
            return {
                "covered": True,
                "root_index": int(root_index),
                "root_hash": r49i.fhash(root),
                "root_CLV": list(r49i.clv(root)),
                "provenance": provenance,
                "selected": selected,
                "terminal": row["terminal"],
                "semantic_sat": row["semantic_sat"],
                "final_CLV": list(r49i.clv(final)),
                "easy_steps": easy_steps,
                "r47j_steps": r47j_steps,
                "total_candidate_probes": total_candidate_probes,
                "total_r47j_rup_checks": total_r47j_rup_checks,
                "obstruction": None,
            }
        current = final

    raise AssertionError(("R49L_STEP_CAP_EXHAUSTED", root_index, r49i.clv(current)))


def compact(r):
    return {
        "covered": bool(r["covered"]),
        "root_index": int(r["root_index"]),
        "root_hash": r["root_hash"],
        "root_CLV": r["root_CLV"],
        "selected_pivots": [int(x["var"]) for x in r["selected"]],
        "selected_lanes": [x["lane"] for x in r["selected"]],
        "step_count": len(r["selected"]),
        "easy_steps": int(r["easy_steps"]),
        "r47j_steps": int(r["r47j_steps"]),
        "total_candidate_probes": int(r["total_candidate_probes"]),
        "total_r47j_rup_checks": int(r["total_r47j_rup_checks"]),
        "terminal": r.get("terminal"),
        "final_CLV": r["final_CLV"],
        "obstruction": None if r["obstruction"] is None else {
            "kind": r["obstruction"]["kind"],
            "state_index": int(r["obstruction"]["state_index"]),
            "state_hash": r["obstruction"]["state_hash"],
            "state_CLV": r["obstruction"]["state_CLV"],
            "state_max_width": int(r["obstruction"]["state_max_width"]),
        },
    }


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
    verdict = (
        "EXPLICIT_REACHABLE_HYBRID_EASY_R47J_WIDTH4_OBSTRUCTION_FOUND"
        if first_obstruction is not None
        else "ALL_52_FROZEN_ROOTS_REACH_TERMINAL_BY_HYBRID_EASY_R47J_WIDTH4__FINITE_ONLY"
    )
    return {
        "gate": GATE,
        "verdict": verdict,
        "metrics": {
            "roots_attempted": len(records),
            "roots_covered": sum(1 for r in records if r["covered"]),
            "obstructions": 0 if first_obstruction is None else 1,
            "total_steps": sum(len(r["selected"]) for r in records),
            "total_easy_steps": sum(int(r["easy_steps"]) for r in records),
            "total_r47j_steps": sum(int(r["r47j_steps"]) for r in records),
            "max_steps": max((len(r["selected"]) for r in records), default=0),
            "total_candidate_probes": sum(int(r["total_candidate_probes"]) for r in records),
            "total_r47j_rup_checks": sum(int(r["total_r47j_rup_checks"]) for r in records),
        },
        "first_obstruction": first_obstruction,
        "roots": [compact(r) for r in records],
        "interpretation": {
            "R49K_safe_only_obstruction_is_explicitly_targeted_by_R47J_fallback": True,
            "one_obstruction_refutes_this_hybrid_policy": first_obstruction is not None,
            "all_52_green_proves_universal_W4_coverage": False,
        },
        "firewall": {
            "R49H_LOCAL_SAFE_PIVOT_LEMMA": "PROVED_IN_SCOPE",
            "R49F_PARTIAL_R47J_RESOURCE_POLYNOMIALITY": "PROVED_IN_SCOPE",
            "HYBRID_52ROOT_CHAIN": "REFUTED" if first_obstruction is not None else "FINITE_GREEN_ONLY",
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
    path = Path("artifacts/JANUS_TRUMP_R49L_HYBRID_EASY_R47J_WIDTH4_CHAIN_52ROOTS_RESULT.json")
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
