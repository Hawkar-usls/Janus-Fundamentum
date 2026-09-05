from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r49i_bipolar_nontauto_cross_union_width5_core_hunt as r49i
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a
import janus_trump_r50g_smallest_first_exact_deadcore_falsifier as r50g
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g5_immediate_bve_exact_descent_algebraic_reduction as r50g5
import janus_trump_r50g9_explicit_wide_fixpoint_ancestry_counterexample as r50g9

GATE = "JANUS_TRUMP_R50G10_WIDE_FIXPOINT_FORCES_ALTERNATE_CERTIFIED_DOOR"
WIDTH_CAP = 4


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def fhash(f):
    return r50g4.fhash(canon(f))


def exact_pre_bve_clean(formula):
    f = canon(formula)
    return bool(
        not any(r33.is_tautology(c) for c in f)
        and not any(len(c) == 1 for c in f)
        and not r33.pure_literals(f)
        and r33.first_subsumed_clause(f) is None
        and r33.first_blocked_clause(f) is None
    )


def build_r50g9_source():
    _sealed, core = r47j.load_counterexample()
    core = canon(core)
    source = canon(list(core) + [r50g9.POS_PARENT, r50g9.NEG_PARENT])
    return source


def exact_door_row(formula, y: int):
    f = canon(formula)
    token = r50a.operational_token(f, int(y))
    if not token["bipolar"]:
        raise AssertionError(("R50G10_PRE_BVE_VARIABLE_NOT_BIPOLAR", y, token))

    r49h = bool(token["direct_exact_dp_authorized"])
    if r49h != (int(token["chi_star"]) <= WIDTH_CAP):
        raise AssertionError(("R50G10_R49H_CHARACTERIZATION_FAIL", y, token))

    row, cand = r50a._fallback_candidate(f, int(y))
    if cand is None:
        raise AssertionError(("R50G10_BIPOLAR_R47J_CANDIDATE_MISSING", y))
    replay = r47j.independent_fixpoint_macro_replay(f, cand)
    if not replay["pass"]:
        raise AssertionError(("R50G10_R47J_REPLAY_FAIL", y, replay))
    if not row["no_fresh_variables"] or not row["strict_variable_descent"]:
        raise AssertionError(("R50G10_R47J_STRUCTURAL_SAFETY_PREDICATE_FAIL", y, row))

    terminal = row["terminal"]
    final_w = int(row["final_max_width"])
    expected_safe = bool(terminal is not None or final_w <= WIDTH_CAP)
    if bool(row["width4_safe"]) != expected_safe:
        raise AssertionError(("R50G10_R47J_SAFE_IFF_FAIL", y, row, expected_safe))

    r47j_safe = bool(row["width4_safe"])
    any_door = bool(r49h or r47j_safe)
    closed = not any_door
    if closed:
        if int(token["chi_star"]) < 5:
            raise AssertionError(("R50G10_CLOSED_R49H_WITH_CHI_LT5", y, token))
        if terminal is not None or final_w <= WIDTH_CAP:
            raise AssertionError(("R50G10_CLOSED_R47J_NOT_WIDE_NONTERMINAL", y, row))

    return {
        "pivot": int(y),
        "chi_star": int(token["chi_star"]),
        "r49h_authorized": r49h,
        "r49h_max_width_witness": r49i.variable_profile(f, int(y))["max_width_witness"],
        "r47j_safe": r47j_safe,
        "r47j_terminal": terminal,
        "r47j_final_width": final_w,
        "r47j_final_CLV": row["final_CLV"],
        "independent_replay_pass": True,
        "alternate_certified_door": any_door,
        "closed_door_certificate": closed,
    }


def profile_all_alternate_doors(formula, x: int):
    f = canon(formula)
    if not exact_pre_bve_clean(f):
        raise AssertionError("R50G10_SOURCE_NOT_PRE_BVE_CLEAN")
    rows = [exact_door_row(f, int(y)) for y in r33.variables(f) if int(y) != int(x)]
    open_rows = [r for r in rows if r["alternate_certified_door"]]
    closed_rows = [r for r in rows if r["closed_door_certificate"]]
    return {
        "alternate_variable_count": len(rows),
        "open_door_count": len(open_rows),
        "closed_door_count": len(closed_rows),
        "r49h_door_count": sum(int(r["r49h_authorized"]) for r in rows),
        "r47j_safe_door_count": sum(int(r["r47j_safe"]) for r in rows),
        "all_alternate_doors_closed": len(rows) > 0 and not open_rows,
        "first_open_door": open_rows[0] if open_rows else None,
        "first_closed_door": closed_rows[0] if closed_rows else None,
        "rows": rows,
    }


def support_frontier_from_r50g9_result(r9):
    wide = r9["source"]["predicted_wide_resolvent"]
    vars_ = {abs(int(l)) for l in wide}
    for row in r9["final"]["support_certificate"]:
        for lit in row["external_escape_literals"]:
            vars_.add(abs(int(lit)))
    return sorted(vars_)


def profile_r50g9_witness():
    r9 = r50g9.run()
    if not r9["final"]["local_wide_fixpoint_witness"]:
        raise AssertionError("R50G10_R50G9_WITNESS_DRIFT")
    source = build_r50g9_source()
    micro = r50g4.micro_r33_status(source)
    if micro["status"] != "IMMEDIATE_BVE_W4_ESCAPE":
        raise AssertionError(("R50G10_R50G9_SOURCE_STATUS_DRIFT", micro))
    x = int(r9["source"]["pivot"])
    all_doors = profile_all_alternate_doors(source, x)
    frontier = support_frontier_from_r50g9_result(r9)
    by_var = {r["pivot"]: r for r in all_doors["rows"]}
    frontier_rows = [by_var[y] for y in frontier if y != x and y in by_var]
    frontier_open = [r for r in frontier_rows if r["alternate_certified_door"]]
    return {
        "source_hash": fhash(source),
        "source_CLV": list(r33.measure(source)),
        "same_pivot": x,
        "same_pivot_final_width": int(r9["same_pivot"]["final_width"]),
        "same_pivot_terminal": r9["same_pivot"]["terminal"],
        "support_frontier_variables": frontier,
        "support_frontier_size": len(frontier),
        "support_frontier_open_door_count": len(frontier_open),
        "support_frontier_all_have_door": bool(frontier_rows and len(frontier_open) == len(frontier_rows)),
        "support_frontier_first_open": frontier_open[0] if frontier_open else None,
        "all_alternate_doors": all_doors,
    }


def replay_frozen_reachable_roots():
    immediate = 0
    same_wide = 0
    wide_with_alt = 0
    wide_without_alt = []
    for worker, n in enumerate(range(6, 11)):
        for i in range(80):
            m = 3 * n + (i % (3 * n + 1))
            seed = 50_700_000 + worker * 100_000 + i
            root, _ = r50g.make_planted(seed, n, m, "3CNF")
            if len(r33.variables(root)) != n:
                continue
            result = r50g5.trace_root(root, {"worker": worker, "seed": seed, "n": n, "m": m})
            for row in result["escape_rows"]:
                immediate += 1
                if not row["same_pivot_wide_survivor"]:
                    continue
                same_wide += 1
                if row["existing_certified_door_exists"]:
                    wide_with_alt += 1
                else:
                    wide_without_alt.append({"worker": worker, "n": n, "seed": seed, **row})
    return {
        "frozen_roots": 400,
        "immediate_BVE_states": immediate,
        "same_pivot_wide_survivor_states": same_wide,
        "wide_survivors_with_existing_alternate_door": wide_with_alt,
        "wide_survivors_without_existing_alternate_door": len(wide_without_alt),
        "first_reachable_all_doors_closed": wide_without_alt[0] if wide_without_alt else None,
    }


def frozen_r49h_hard_controls():
    roots = r49i.collect_roots()
    hard = []
    for idx, (root, provenance) in enumerate(roots, 1):
        profiles = [r49i.variable_profile(root, int(v)) for v in r33.variables(root)]
        if profiles and all(p["bipolar"] and int(p["chi_star"]) >= 5 for p in profiles):
            hard.append({
                "root_index": idx,
                "hash": fhash(root),
                "CLV": list(r33.measure(root)),
                "provenance": provenance,
                "minimum_chi_star": min(int(p["chi_star"]) for p in profiles),
            })
    return {
        "frozen_roots": len(roots),
        "all_r49h_closed_roots": len(hard),
        "first_all_r49h_closed_root": hard[0] if hard else None,
        "interpretation": "R49H_ALONE_CANNOT_BE_THE_UNIVERSAL_ALTERNATE_DOOR_THEOREM" if hard else "FINITE_NO_HARD_R49H_CONTROL",
    }


def run():
    witness = profile_r50g9_witness()
    reachable = replay_frozen_reachable_roots()
    r49h_controls = frozen_r49h_hard_controls()

    local_all_closed = bool(witness["all_alternate_doors"]["all_alternate_doors_closed"])
    reachable_all_closed = bool(reachable["wide_survivors_without_existing_alternate_door"])

    if reachable_all_closed:
        verdict = "EXPLICIT_REACHABLE_COUNTEREXAMPLE_TO_WIDE_FIXPOINT_FORCES_ALTERNATE_DOOR_FOUND"
    elif local_all_closed:
        verdict = "STRONG_LOCAL_ALTERNATE_DOOR_THEOREM_REFUTED__REACHABLE_THEOREM_REMAINS_OPEN"
    else:
        verdict = "ALL_DOORS_CLOSED_CERTIFICATE_REDUCTION_CLOSED__R50G9_WIDE_SUPPORT_FRONTIER_HIT_BY_CERTIFIED_DOORS__REACHABLE_THEOREM_OPEN"

    return {
        "gate": GATE,
        "mode": "SYMBOLIC_CLOSED_DOOR_REDUCTION_PLUS_FROZEN_EXACT_REPLAY",
        "proved_from_frozen_source_definitions": [
            "PRE_BVE_CLEANLINESS_IMPLIES_ALL_PRESENT_VARIABLES_BIPOLAR",
            "BIPOLAR_R49H_CLOSED_IFF_CHI_STAR_GE_5",
            "BIPOLAR_R47J_REMOVES_PIVOT_AND_INTRODUCES_NO_FRESH_VARIABLES",
            "BIPOLAR_R47J_SAFE_IFF_TERMINAL_OR_FINAL_WIDTH_LE_4",
            "ALL_ALTERNATE_DOORS_CLOSED_HAS_EXPLICIT_PER_VARIABLE_CHI_STAR_GE_5_AND_NONTERMINAL_WIDE_R47J_LEDGER",
        ],
        "r50g9_witness": witness,
        "reachable_replay": reachable,
        "r49h_hard_controls": r49h_controls,
        "critical_next_obligation": "SUPPORT_FRONTIER_HITTING_THEOREM_OR_EXPLICIT_ALL_DOORS_CLOSED_COUNTEREXAMPLE__WITH_REACHABILITY_CERTIFICATE_FOR_REACHABLE_REFUTATION",
        "verdict": verdict,
        "firewall": {
            "FINITE_SUCCESS_IMPLIES_SUPPORT_FRONTIER_THEOREM": False,
            "HEURISTIC_AUTHORITY": False,
            "LEARNED_SELECTOR": False,
            "PROBABILISTIC_AUTHORITY": False,
            "NEW_SEMANTIC_INFERENCE_RULE": False,
            "LOCAL_ALTERNATE_DOOR_THEOREM": "REFUTED" if local_all_closed else "OPEN",
            "REACHABLE_ALTERNATE_DOOR_THEOREM": "REFUTED" if reachable_all_closed else "OPEN",
            "IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "U_MU": "OPEN",
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
    args = ap.parse_args()
    out = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
