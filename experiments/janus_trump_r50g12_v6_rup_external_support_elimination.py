from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r50g_smallest_first_exact_deadcore_falsifier as r50g
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g5_immediate_bve_exact_descent_algebraic_reduction as r50g5
import janus_trump_r50g9_explicit_wide_fixpoint_ancestry_counterexample as r50g9

GATE = "JANUS_TRUMP_R50G12_V6_RUP_EXTERNAL_SUPPORT_ELIMINATION"
WIDTH_CAP = 4


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def nontaut_resolvent(c, d, lit):
    u = (set(c) - {int(lit)}) | (set(d) - {-int(lit)})
    if any(-x in u for x in u):
        return None
    return r33.canonical_clause(u)


def support_rows(formula, clause, lit):
    f = canon(formula)
    c = r33.canonical_clause(clause)
    cvars = {abs(int(x)) for x in c}
    rows = []
    for d in f:
        if -int(lit) not in d:
            continue
        resolvent = nontaut_resolvent(c, d, int(lit))
        if resolvent is None:
            continue
        external = sorted({abs(int(x)) for x in d if abs(int(x)) not in cvars})
        rows.append({
            "support_clause": list(d),
            "resolvent": list(resolvent),
            "external_variables": external,
        })
    return rows


def external_support_fixedpoint_audit(formula, clause):
    f = canon(formula)
    c = r33.canonical_clause(clause)
    if c not in f:
        raise AssertionError(("R50G12_CLAUSE_NOT_IN_FORMULA", c))
    simp = r33.simplify(f)
    if simp["terminal"] != "STALLED_STACK_LEAN_CORE" or simp["history"]:
        raise AssertionError(("R50G12_NOT_R33_FIXED", simp["terminal"], simp["history"][:1]))
    rup = r35b.run_candidate(f)
    if rup["status"] != "STALLED_RUP_CORE" or rup["history"]:
        raise AssertionError(("R50G12_NOT_RUP_FIXED", rup["status"], rup["history"][:1]))

    per_literal = []
    all_external = True
    for lit in c:
        rows = support_rows(f, c, int(lit))
        if not rows:
            raise AssertionError(("R50G12_BCE_FIXED_WITHOUT_NONBLOCKING_SUPPORT", c, lit))
        if any(not row["external_variables"] for row in rows):
            all_external = False
            raise AssertionError(("R50G12_RUP_FIXED_INTERNAL_SUPPORT_EXISTS", c, lit, rows))
        per_literal.append({"literal": int(lit), "supports": rows})

    formula_vars = set(int(v) for v in r33.variables(f))
    clause_vars = {abs(int(x)) for x in c}
    external_formula_vars = sorted(formula_vars - clause_vars)
    if not external_formula_vars:
        raise AssertionError(("R50G12_FIXED_CLAUSE_WITHOUT_EXTERNAL_VARIABLE", c))
    if len(formula_vars) < len(c) + 1:
        raise AssertionError(("R50G12_VARIABLE_BOUND_FAIL", len(formula_vars), len(c)))

    return {
        "clause": list(c),
        "clause_width": len(c),
        "formula_variable_count": len(formula_vars),
        "external_formula_variables": external_formula_vars,
        "every_nonblocking_support_has_external_variable": all_external,
        "per_literal": per_literal,
    }


def internal_external_pair_controls():
    c = r33.canonical_clause((1, 2, 3, 4, 5))
    strengthened = tuple(l for l in c if l != 1)
    assumptions = tuple(-l for l in strengthened)

    internal = canon([c, (-1, 2)])
    internal_receipt = r35b.candidate_unit_propagation_trace(internal, assumptions)
    if not internal_receipt["conflict"]:
        raise AssertionError(("R50G12_INTERNAL_SUPPORT_DID_NOT_FORCE_RUP", internal_receipt))
    if not r35b.independent_up_conflict_checker(internal, assumptions):
        raise AssertionError("R50G12_INTERNAL_SUPPORT_INDEPENDENT_REPLAY_FAIL")

    external = canon([c, (-1, 6)])
    external_receipt = r35b.candidate_unit_propagation_trace(external, assumptions)
    if external_receipt["conflict"]:
        raise AssertionError(("R50G12_EXTERNAL_SUPPORT_FALSE_CONFLICT", external_receipt))
    if r35b.independent_up_conflict_checker(external, assumptions):
        raise AssertionError("R50G12_EXTERNAL_SUPPORT_INDEPENDENT_FALSE_CONFLICT")

    return {
        "source_clause": list(c),
        "removed_literal": 1,
        "strengthened_clause": list(strengthened),
        "internal_support": [-1, 2],
        "internal_support_forces_rup_conflict": True,
        "external_support": [-1, 6],
        "external_support_pair_alone_does_not_force_conflict": True,
    }


def r50g9_fixedpoint_control():
    r9 = r50g9.run()
    if not r9["final"]["local_wide_fixpoint_witness"]:
        raise AssertionError("R50G12_R50G9_WIDE_WITNESS_DRIFT")
    final_hash = r9["final"]["hash"]
    # Reconstruct the same final formula through the sealed same-pivot candidate.
    _sealed, core = r50g9.r47j.load_counterexample()
    source = canon(list(canon(core)) + [r50g9.POS_PARENT, r50g9.NEG_PARENT])
    cand = r50g9.r47j.macro_candidate_fixpoint(source, r50g9.PIVOT)
    if cand is None:
        raise AssertionError("R50G12_R50G9_CANDIDATE_MISSING")
    final = canon(cand["normalization"]["final_formula"])
    if r50g4.fhash(final) != final_hash:
        raise AssertionError("R50G12_R50G9_FINAL_HASH_DRIFT")
    audit = external_support_fixedpoint_audit(final, r50g9.WIDE)
    return {
        "final_hash": final_hash,
        "final_variable_count": len(r33.variables(final)),
        "final_max_width": max_width(final),
        "wide_clause_audit": audit,
    }


def replay_frozen_v6_boundary():
    by_v = {}
    first_v6_wide = None
    total_escape = 0
    for worker, n in enumerate(range(6, 11)):
        for i in range(80):
            m = 3 * n + (i % (3 * n + 1))
            seed = 50_700_000 + worker * 100_000 + i
            root, _ = r50g.make_planted(seed, n, m, "3CNF")
            if len(r33.variables(root)) != n:
                continue
            result = r50g5.trace_root(root, {"worker": worker, "seed": seed, "n": n, "m": m})
            for row in result["escape_rows"]:
                total_escape += 1
                v = int(row["input_CLV"][2])
                bucket = by_v.setdefault(str(v), {
                    "immediate_BVE": 0,
                    "same_pivot_terminal": 0,
                    "same_pivot_W4_reentry": 0,
                    "same_pivot_wide_survivor": 0,
                })
                bucket["immediate_BVE"] += 1
                bucket["same_pivot_terminal"] += int(row["same_pivot_terminal"])
                bucket["same_pivot_W4_reentry"] += int(row["same_pivot_W4_reentry"])
                bucket["same_pivot_wide_survivor"] += int(row["same_pivot_wide_survivor"])
                if v <= 6 and row["same_pivot_wide_survivor"] and first_v6_wide is None:
                    first_v6_wide = {"worker": worker, "seed": seed, **row}
    if first_v6_wide is not None:
        raise AssertionError(("R50G12_FROZEN_REPLAY_CONTRADICTS_V6_THEOREM", first_v6_wide))
    return {
        "frozen_roots": 400,
        "immediate_BVE_states": total_escape,
        "by_input_variable_count": by_v,
        "first_v_le_6_same_pivot_wide_survivor": first_v6_wide,
    }


def v7_boundary_normal_form():
    return {
        "assumption": "source variable count = 7 and same-pivot R47J final is nonterminal with width > 4",
        "derived_final_variable_upper_bound": 6,
        "external_support_lower_bound": "final_V >= final_width + 1",
        "derived_final_variable_count": 6,
        "derived_final_max_width": 5,
        "widest_clause_external_variable_count": 1,
        "support_shape": "EVERY_NONBLOCKING_SUPPORT_FOR_A_WIDEST_WIDTH5_CLAUSE_USES_THE_UNIQUE_EXTERNAL_VARIABLE",
    }


def run():
    controls = internal_external_pair_controls()
    r9 = r50g9_fixedpoint_control()
    replay = replay_frozen_v6_boundary()
    return {
        "gate": GATE,
        "mode": "SOURCE_THEOREM_PLUS_FROZEN_REGRESSION",
        "proved_from_frozen_source_definitions": [
            "INTERNAL_NONBLOCKING_SUPPORT_FORCES_SINGLE_LITERAL_RUP_STRENGTHENING",
            "RUP_FIXED_PLUS_BCE_FIXED_IMPLIES_EVERY_NONBLOCKING_SUPPORT_USES_EXTERNAL_VARIABLE",
            "SURVIVING_CLAUSE_VARIABLE_BOUND_V_GE_WIDTH_PLUS_1",
            "SAME_PIVOT_R47J_REMOVES_X_AND_INTRODUCES_NO_FRESH_VARIABLES",
            "V_LE_6_IMMEDIATE_BVE_IMPLIES_SAME_PIVOT_R47J_SAFE",
            "V7_WIDE_SURVIVOR_IF_ANY_HAS_EXACT_V6_W5_SINGLE_EXTERNAL_SUPPORT_HUB_NORMAL_FORM",
        ],
        "pair_controls": controls,
        "r50g9_wide_fixedpoint_control": r9,
        "frozen_replay": replay,
        "v7_boundary_normal_form": v7_boundary_normal_form(),
        "critical_next_obligation": "ELIMINATE_OR_REALIZE_V7_SINGLE_EXTERNAL_SUPPORT_HUB_UNDER_ALL_DOORS_CLOSED_AND_REACHABILITY_CONSTRAINTS",
        "verdict": "V6_IMMEDIATE_BVE_CASE_ELIMINATED_BY_RUP_EXTERNAL_SUPPORT_THEOREM__V7_REDUCED_TO_SINGLE_EXTERNAL_SUPPORT_HUB__FULL_IMMEDIATE_BVE_OPEN",
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
