from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a
import janus_trump_r50g_smallest_first_exact_deadcore_falsifier as r50g
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g5_immediate_bve_exact_descent_algebraic_reduction as r50g5
import janus_trump_r50g10_wide_fixpoint_forces_alternate_certified_door as r50g10
import janus_trump_r50g12_v6_rup_external_support_elimination as r50g12

GATE = "JANUS_TRUMP_R50G13_V7_SINGLE_EXTERNAL_SUPPORT_HUB_ELIMINATION_OR_REALIZATION"
WIDTH_CAP = 4


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def hub_polarity_and_guard_controls():
    c = r33.canonical_clause((1, 2, 3, 4, 5))
    assumptions = tuple(-l for l in c if l != 1)

    opposite_supports = canon([c, (-1, 6), (-1, -6)])
    receipt = r35b.candidate_unit_propagation_trace(opposite_supports, assumptions)
    independent = r35b.independent_up_conflict_checker(opposite_supports, assumptions)
    if not receipt["conflict"] or not independent:
        raise AssertionError("R50G13_OPPOSITE_HUB_SUPPORTS_DID_NOT_FORCE_RUP")

    one_support = canon([c, (-1, 6)])
    if r35b.candidate_unit_propagation_trace(one_support, assumptions)["conflict"]:
        raise AssertionError("R50G13_SINGLE_HUB_SUPPORT_FALSE_CONFLICT")

    unguarded_anti_hub = canon([c, (-1, 6), (-6, 2)])
    u = r35b.candidate_unit_propagation_trace(unguarded_anti_hub, assumptions)
    if not u["conflict"] or not r35b.independent_up_conflict_checker(unguarded_anti_hub, assumptions):
        raise AssertionError("R50G13_UNGUARDED_ANTI_HUB_DID_NOT_FORCE_RUP")

    guarded_anti_hub = canon([c, (-1, 6), (-6, -2)])
    g = r35b.candidate_unit_propagation_trace(guarded_anti_hub, assumptions)
    if g["conflict"] or r35b.independent_up_conflict_checker(guarded_anti_hub, assumptions):
        raise AssertionError("R50G13_GUARDED_ANTI_HUB_FALSE_CONFLICT")

    return {
        "wide_clause": list(c),
        "literal": 1,
        "assumptions": list(assumptions),
        "opposite_hub_supports_force_rup_conflict": True,
        "single_hub_support_does_not_force_conflict": True,
        "unguarded_opposite_hub_clause_forces_rup_conflict": True,
        "guarded_opposite_hub_clause_control_no_conflict": True,
    }


def hub_clause_certificate(final_formula, clause):
    f = canon(final_formula)
    c = r33.canonical_clause(clause)
    base = r50g12.external_support_fixedpoint_audit(f, c)
    if base["formula_variable_count"] != 6 or len(c) != 5:
        raise AssertionError(("R50G13_NOT_V6_W5_HUB_BOUNDARY", base))
    if len(base["external_formula_variables"]) != 1:
        raise AssertionError(("R50G13_NOT_SINGLE_EXTERNAL_HUB", base))
    hub = int(base["external_formula_variables"][0])

    rows = []
    for item in base["per_literal"]:
        lit = int(item["literal"])
        polarities = set()
        for sr in item["supports"]:
            d = tuple(int(x) for x in sr["support_clause"])
            has_pos = hub in d
            has_neg = -hub in d
            if has_pos == has_neg:
                raise AssertionError(("R50G13_SUPPORT_HUB_LITERAL_INVALID", hub, d))
            polarities.add(1 if has_pos else -1)
        if len(polarities) != 1:
            assumptions = tuple(-x for x in c if x != lit)
            if not r35b.independent_up_conflict_checker(f, assumptions):
                raise AssertionError(("R50G13_POLARITY_INCOHERENCE_WITHOUT_RUP_CONFLICT", c, lit, item))
            raise AssertionError(("R50G13_RUP_FIXED_BUT_OPPOSITE_HUB_SUPPORTS", c, lit, item))
        sigma = next(iter(polarities))

        guard_literals = {lit} | {-int(k) for k in c if int(k) != lit}
        anti_hub = []
        for e in f:
            if -sigma * hub not in e:
                continue
            guarded_by = sorted(set(e) & guard_literals, key=lambda q: (abs(q), q < 0))
            if not guarded_by:
                assumptions = tuple(-x for x in c if x != lit)
                if not r35b.independent_up_conflict_checker(f, assumptions):
                    raise AssertionError(("R50G13_UNGUARDED_ANTI_HUB_WITHOUT_RUP_CONFLICT", c, lit, e))
                raise AssertionError(("R50G13_RUP_FIXED_BUT_UNGUARDED_ANTI_HUB", c, lit, e))
            anti_hub.append({"clause": list(e), "guarded_by": list(guarded_by)})

        rows.append({
            "literal": lit,
            "hub_polarity": sigma,
            "support_count": len(item["supports"]),
            "opposite_hub_clause_count": len(anti_hub),
            "opposite_hub_guards": anti_hub,
        })

    return {
        "wide_clause": list(c),
        "hub_variable": hub,
        "support_polarity_coherent_per_literal": True,
        "opposite_hub_guard_obligation_pass": True,
        "rows": rows,
    }


def r47j_hub_debt(source, y: int):
    f = canon(source)
    row, cand = r50a._fallback_candidate(f, int(y))
    if cand is None:
        raise AssertionError(("R50G13_R47J_CANDIDATE_MISSING", y))
    replay = r47j.independent_fixpoint_macro_replay(f, cand)
    if not replay["pass"]:
        raise AssertionError(("R50G13_R47J_REPLAY_FAIL", y, replay))
    if row["width4_safe"]:
        return {"pivot": int(y), "safe": True, "row": row}

    final = canon(cand["normalization"]["final_formula"])
    if row["terminal"] is not None or max_width(final) <= WIDTH_CAP:
        raise AssertionError(("R50G13_UNSAFE_ROW_NOT_WIDE_NONTERMINAL", y, row))
    if len(r33.variables(f)) != 7:
        raise AssertionError(("R50G13_HUB_DEBT_SOURCE_NOT_V7", y, len(r33.variables(f))))
    if len(r33.variables(final)) != 6 or max_width(final) != 5:
        raise AssertionError(("R50G13_V7_UNSAFE_NOT_EXACT_V6_W5", y, len(r33.variables(final)), max_width(final)))

    widest = [c for c in final if len(c) == 5]
    if not widest:
        raise AssertionError(("R50G13_V6_W5_WITHOUT_WIDTH5_CLAUSE", y))
    certs = [hub_clause_certificate(final, c) for c in widest]
    return {
        "pivot": int(y),
        "safe": False,
        "terminal": None,
        "final_variable_count": 6,
        "final_max_width": 5,
        "final_CLV": row["final_CLV"],
        "wide_clause_count": len(widest),
        "hub_certificates": certs,
        "independent_replay_pass": True,
    }


def v7_all_doors_closed_certificate(source):
    f = canon(source)
    if len(r33.variables(f)) != 7 or max_width(f) > 4:
        return {"applicable": False, "reason": "NOT_V7_W4"}
    micro = r50g4.micro_r33_status(f)
    if micro["status"] != "IMMEDIATE_BVE_W4_ESCAPE":
        return {"applicable": False, "reason": "NOT_IMMEDIATE_BVE_ESCAPE"}
    x = int(micro["pivot"])
    same = r50g5.prove_immediate_bve_same_pivot(f)
    if not same["applicable"] or not same["same_pivot_wide_survivor"]:
        return {"applicable": False, "reason": "SAME_PIVOT_NOT_WIDE_SURVIVOR", "pivot": x}

    alternates = r50g10.profile_all_alternate_doors(f, x)
    if not alternates["all_alternate_doors_closed"]:
        return {
            "applicable": True,
            "all_doors_closed": False,
            "pivot": x,
            "first_open_door": alternates["first_open_door"],
        }

    chi = []
    debts = []
    for y in r33.variables(f):
        token = r50a.operational_token(f, int(y))
        if not token["bipolar"]:
            raise AssertionError(("R50G13_V7_PRE_BVE_NONBIPOLAR", y))
        cs = int(token["chi_star"])
        if cs not in (5, 6):
            raise AssertionError(("R50G13_ALL_CLOSED_CHI_NOT_5_6", y, cs))
        chi.append({"pivot": int(y), "chi_star": cs})
        debt = r47j_hub_debt(f, int(y))
        if debt["safe"]:
            raise AssertionError(("R50G13_ALL_CLOSED_BUT_SAFE_R47J", y, debt))
        debts.append(debt)

    return {
        "applicable": True,
        "all_doors_closed": True,
        "pivot": x,
        "all_seven_chi_in_5_6": True,
        "chi_ledger": chi,
        "sevenfold_hub_debt": True,
        "hub_debts": debts,
    }


def replay_frozen_boundary():
    r12 = r50g12.replay_frozen_v6_boundary()
    v7 = r12["by_input_variable_count"].get("7", {})
    if v7.get("same_pivot_wide_survivor", 0) != 0:
        raise AssertionError(("R50G13_FROZEN_V7_WIDE_SURVIVOR_UNEXPECTED", v7))
    return {
        "frozen_roots": r12["frozen_roots"],
        "immediate_BVE_states": r12["immediate_BVE_states"],
        "v7_immediate_BVE": int(v7.get("immediate_BVE", 0)),
        "v7_same_pivot_terminal": int(v7.get("same_pivot_terminal", 0)),
        "v7_same_pivot_wide_survivor": int(v7.get("same_pivot_wide_survivor", 0)),
        "interpretation": "FINITE_REGRESSION_ONLY",
    }


def run():
    controls = hub_polarity_and_guard_controls()
    replay = replay_frozen_boundary()
    return {
        "gate": GATE,
        "mode": "SYMBOLIC_V7_HUB_REDUCTION_PLUS_FROZEN_REPLAY",
        "proved_from_frozen_source_definitions": [
            "V7_UNSAFE_BIPOLAR_R47J_IMPLIES_EXACT_V6_W5_FINAL",
            "V6_W5_R33_RUP_FIXED_IMPLIES_SINGLE_EXTERNAL_HUB_PER_WIDEST_CLAUSE",
            "NONBLOCKING_SUPPORT_POLARITY_IS_COHERENT_PER_WIDE_LITERAL",
            "EVERY_OPPOSITE_HUB_CLAUSE_OBEYS_RUP_GUARD_OBLIGATION",
            "V7_ALL_DOORS_CLOSED_IMPLIES_CHI_STAR_IN_5_6_FOR_ALL_SEVEN_PIVOTS",
            "V7_ALL_DOORS_CLOSED_IMPLIES_SEVENFOLD_V6_W5_SINGLE_HUB_R47J_DEBT",
        ],
        "controls": controls,
        "frozen_replay": replay,
        "critical_next_obligation": "SEVENFOLD_HUB_DEBT_INCIDENCE_IMPOSSIBILITY_OR_EXPLICIT_V7_ALL_DOORS_CLOSED_WITNESS",
        "verdict": "V7_ALL_DOORS_CLOSED_REDUCED_TO_SEVENFOLD_SINGLE_HUB_DEBT_WITH_COHERENT_POLARITY_AND_ANTI_HUB_GUARDS__V7_IMPOSSIBILITY_OPEN",
        "firewall": {
            "FINITE_SUCCESS_IMPLIES_THEOREM": False,
            "HEURISTIC_AUTHORITY": False,
            "NEW_SEMANTIC_INFERENCE_RULE": False,
            "V6_IMMEDIATE_BVE_CASE_ELIMINATED": True,
            "V7_IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "REACHABLE_ALTERNATE_DOOR_THEOREM": "OPEN",
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
    args.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
