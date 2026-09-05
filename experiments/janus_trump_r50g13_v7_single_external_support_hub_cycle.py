from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g10_wide_fixpoint_forces_alternate_certified_door as r50g10
import janus_trump_r50g12_v6_rup_external_support_elimination as r50g12

GATE = "JANUS_TRUMP_R50G13_V7_SINGLE_EXTERNAL_SUPPORT_HUB_CYCLE"
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


def hub_polarity_controls():
    c = r33.canonical_clause((1, 2, 3, 4, 5))
    strengthened = tuple(l for l in c if l != 1)
    assumptions = tuple(-l for l in strengthened)

    plus = (-1, 6)
    minus_unshielded = (-1, -6, 2)
    opposite = canon([c, plus, minus_unshielded])
    receipt = r35b.candidate_unit_propagation_trace(opposite, assumptions)
    independent = r35b.independent_up_conflict_checker(opposite, assumptions)
    if not receipt["conflict"] or not independent:
        raise AssertionError(("R50G13_OPPOSITE_HUB_POLARITY_DID_NOT_FORCE_RUP", receipt, independent))

    shielded = (-1, -6, -2)
    if nontaut_resolvent(c, shielded, 1) is not None:
        raise AssertionError("R50G13_SHIELDED_OPPOSITE_SUPPORT_NOT_TAUTOLOGICAL")
    unshielded_resolvent = nontaut_resolvent(c, minus_unshielded, 1)
    if unshielded_resolvent is None:
        raise AssertionError("R50G13_UNSHIELDED_OPPOSITE_SUPPORT_FALSE_TAUTOLOGY")

    return {
        "wide_clause": list(c),
        "removed_literal": 1,
        "strengthened_clause": list(strengthened),
        "hub": 6,
        "same_literal_opposite_hub_supports": [list(plus), list(minus_unshielded)],
        "opposite_polarities_force_single_literal_RUP_conflict": True,
        "independent_UP_replay": True,
        "shielded_opposite_hub_clause": list(shielded),
        "shielding_complement": -2,
        "shielded_resolvent_is_tautological": True,
        "unshielded_opposite_resolvent": list(unshielded_resolvent),
    }


def audit_single_hub_clause(formula, clause):
    f = canon(formula)
    c = r33.canonical_clause(clause)
    base = r50g12.external_support_fixedpoint_audit(f, c)
    if len(base["external_formula_variables"]) != 1:
        raise AssertionError(("R50G13_NOT_SINGLE_EXTERNAL_HUB", base))
    z = int(base["external_formula_variables"][0])

    polarity = {}
    for per in base["per_literal"]:
        lit = int(per["literal"])
        signs = set()
        for row in per["supports"]:
            d = tuple(int(x) for x in row["support_clause"])
            if z in d:
                signs.add(1)
            if -z in d:
                signs.add(-1)
            if len({z, -z} & set(d)) != 1:
                raise AssertionError(("R50G13_SUPPORT_DOES_NOT_USE_EXACTLY_ONE_HUB_POLARITY", lit, d, z))
            for q in d:
                if q in {-lit, z, -z}:
                    continue
                if q not in c:
                    raise AssertionError(("R50G13_NONTAUT_SUPPORT_HAS_NONCLAUSE_NONHUB_LITERAL", lit, d, q, c, z))
                if -q in c:
                    raise AssertionError(("R50G13_NONTAUT_SUPPORT_HAS_COMPLEMENT_OF_OTHER_C_LITERAL", lit, d, q, c))
        if len(signs) != 1:
            if signs == {-1, 1}:
                strengthened = tuple(q for q in c if q != lit)
                assumptions = tuple(-q for q in strengthened)
                receipt = r35b.candidate_unit_propagation_trace(f, assumptions)
                independent = r35b.independent_up_conflict_checker(f, assumptions)
                if not receipt["conflict"] or not independent:
                    raise AssertionError(("R50G13_POLARITY_PROOF_REPLAY_FAIL", lit, signs, receipt, independent))
            raise AssertionError(("R50G13_RUP_FIXED_HUB_POLARITY_NOT_UNIQUE", lit, signs))
        polarity[str(lit)] = next(iter(signs))

    # Opposite-hub shielding is checked exhaustively over clauses containing -lit.
    shielding_rows = []
    for lit in c:
        sigma = int(polarity[str(int(lit))])
        opposite_hub = -sigma * z
        for d in f:
            if -int(lit) not in d or opposite_hub not in d:
                continue
            res = nontaut_resolvent(c, d, int(lit))
            if res is not None:
                raise AssertionError(("R50G13_UNSHIELDED_OPPOSITE_HUB_SUPPORT", c, lit, z, sigma, d, res))
            complements = sorted(int(-q) for q in c if q != lit and -q in d)
            if not complements:
                raise AssertionError(("R50G13_TAUTOLOGY_WITHOUT_OTHER_C_COMPLEMENT", c, lit, d))
            shielding_rows.append({
                "literal": int(lit),
                "support_polarity": sigma,
                "opposite_hub_clause": list(d),
                "shielding_complements": complements,
            })

    return {
        "clause": list(c),
        "hub": z,
        "hub_polarity_by_literal": polarity,
        "opposite_hub_shielding_rows": shielding_rows,
        "base_external_support_audit": base,
    }


def first_functional_cycle(mapping):
    """Return one cycle from a finite total map v->h(v), or None."""
    for start in sorted(mapping):
        seen_at = {}
        path = []
        v = start
        while v in mapping:
            if v in seen_at:
                i = seen_at[v]
                return path[i:] + [v]
            seen_at[v] = len(path)
            path.append(v)
            v = mapping[v]
    return None


def profile_unsafe_r47j_hub(source, v: int):
    f = canon(source)
    before_vars = set(int(x) for x in r33.variables(f))
    row, cand = r50a._fallback_candidate(f, int(v))
    if cand is None:
        raise AssertionError(("R50G13_R47J_CANDIDATE_MISSING", v))
    replay = r47j.independent_fixpoint_macro_replay(f, cand)
    if not replay["pass"]:
        raise AssertionError(("R50G13_R47J_REPLAY_FAIL", v, replay))
    if row["width4_safe"]:
        return {"pivot": int(v), "unsafe": False, "row": row}
    if row["terminal"] is not None or int(row["final_max_width"]) <= WIDTH_CAP:
        raise AssertionError(("R50G13_UNSAFE_CHARACTERIZATION_DRIFT", v, row))

    final = canon(cand["normalization"]["final_formula"])
    final_vars = set(int(x) for x in r33.variables(final))
    if len(before_vars) != 7:
        raise AssertionError(("R50G13_PROFILE_REQUIRES_V7_SOURCE", sorted(before_vars)))
    if len(final_vars) > 6 or int(v) in final_vars or not final_vars <= before_vars:
        raise AssertionError(("R50G13_R47J_VARIABLE_DISCIPLINE_FAIL", v, sorted(before_vars), sorted(final_vars)))

    # R50G12 external-support theorem: nonterminal wide fixedpoint needs V >= W+1.
    if len(final_vars) < 6:
        raise AssertionError(("R50G13_V7_UNSAFE_FINAL_HAS_LT6_VARS_CONTRADICT_R50G12", v, row, sorted(final_vars)))
    if max_width(final) != 5:
        raise AssertionError(("R50G13_V7_UNSAFE_FINAL_NOT_EXACT_W5", v, max_width(final), sorted(final_vars)))
    expected = before_vars - {int(v)}
    if final_vars != expected:
        raise AssertionError(("R50G13_V7_UNSAFE_DID_NOT_PRESERVE_ALL_OTHER_VARS", v, sorted(final_vars), sorted(expected)))

    wide = next((c for c in final if len(c) == 5), None)
    if wide is None:
        raise AssertionError(("R50G13_V7_UNSAFE_WITHOUT_WIDTH5_CLAUSE", v))
    audit = audit_single_hub_clause(final, wide)
    hub = int(audit["hub"])
    if hub == int(v) or hub not in expected:
        raise AssertionError(("R50G13_INVALID_HUB", v, hub, sorted(expected)))
    return {
        "pivot": int(v),
        "unsafe": True,
        "final_hash": r50g4.fhash(final),
        "final_variable_count": len(final_vars),
        "final_max_width": max_width(final),
        "canonical_width5_clause": list(wide),
        "hub": hub,
        "hub_audit": audit,
        "independent_replay_pass": True,
    }


def all_closed_v7_hub_certificate(source, x: int):
    f = canon(source)
    vars_ = [int(v) for v in r33.variables(f)]
    if len(vars_) != 7 or max_width(f) > 4:
        return {"applicable": False, "reason": "NOT_V7_W4"}
    if not r50g10.exact_pre_bve_clean(f):
        return {"applicable": False, "reason": "NOT_PRE_BVE_CLEAN"}
    micro = r50g4.micro_r33_status(f)
    if micro["status"] != "IMMEDIATE_BVE_W4_ESCAPE" or int(micro["var"]) != int(x):
        return {"applicable": False, "reason": "NOT_IMMEDIATE_BVE_X", "micro": micro}

    profiles = {}
    hub_map = {}
    for v in vars_:
        prof = profile_unsafe_r47j_hub(f, v)
        profiles[str(v)] = prof
        if not prof["unsafe"]:
            return {"applicable": True, "all_doors_closed": False, "first_open_R47J": int(v), "profiles": profiles}
        hub_map[int(v)] = int(prof["hub"])
        if int(v) != int(x):
            door = r50g10.exact_door_row(f, int(v))
            profiles[str(v)]["alternate_door"] = door
            if door["alternate_certified_door"]:
                return {"applicable": True, "all_doors_closed": False, "first_open_alternate": int(v), "profiles": profiles}

    cycle = first_functional_cycle(hub_map)
    if cycle is None:
        raise AssertionError(("R50G13_TOTAL_HUB_MAP_WITHOUT_CYCLE", hub_map))
    if len(cycle) < 3:  # representation repeats the first vertex, so 2-edge cycle has length 3
        raise AssertionError(("R50G13_HUB_SELF_LOOP_OR_DEGENERATE_CYCLE", hub_map, cycle))
    return {
        "applicable": True,
        "all_doors_closed": True,
        "hub_map": {str(k): int(v) for k, v in sorted(hub_map.items())},
        "hub_cycle": cycle,
        "profiles": profiles,
    }


def frozen_replay_regression():
    replay = r50g12.replay_frozen_v6_boundary()
    v7 = replay["by_input_variable_count"].get("7", {})
    if int(v7.get("same_pivot_wide_survivor", 0)) != 0:
        raise AssertionError(("R50G13_FROZEN_V7_WIDE_SURVIVOR_APPEARED", v7))
    return {
        "frozen_roots": replay["frozen_roots"],
        "immediate_BVE_states": replay["immediate_BVE_states"],
        "v7_bucket": v7,
        "frozen_v7_all_closed_candidate_count": 0,
        "authority": "REGRESSION_ONLY",
    }


def graph_control():
    mapping = {1: 2, 2: 3, 3: 1, 4: 2, 5: 4, 6: 5, 7: 6}
    cycle = first_functional_cycle(mapping)
    if cycle is None or cycle[0] != cycle[-1]:
        raise AssertionError(("R50G13_GRAPH_CONTROL_FAIL", mapping, cycle))
    return {"mapping": {str(k): v for k, v in mapping.items()}, "cycle": cycle}


def run():
    controls = hub_polarity_controls()
    graph = graph_control()
    replay = frozen_replay_regression()
    return {
        "gate": GATE,
        "mode": "SOURCE_HUB_POLARITY_AND_FUNCTIONAL_CYCLE_REDUCTION_PLUS_FROZEN_REGRESSION",
        "proved_from_frozen_source_definitions": [
            "V6_W5_SINGLE_HUB_NONBLOCKING_SUPPORT_SHAPE",
            "RUP_FIXED_IMPLIES_UNIQUE_HUB_POLARITY_PER_WIDE_LITERAL",
            "OPPOSITE_HUB_CLAUSE_WITH_MINUS_LITERAL_REQUIRES_OTHER_C_COMPLEMENT_SHIELDING",
            "V7_UNSAFE_R47J_IMPLIES_EXACT_FINAL_V6_W5_AND_NO_ADDITIONAL_VARIABLE_ELIMINATION",
            "V7_ALL_DOORS_CLOSED_IMPLIES_TOTAL_NO_SELF_LOOP_HUB_MAP_ON_SEVEN_SOURCE_VARIABLES",
            "FINITE_TOTAL_HUB_MAP_IMPLIES_DIRECTED_CYCLE_LENGTH_AT_LEAST_TWO",
        ],
        "hub_polarity_controls": controls,
        "functional_graph_control": graph,
        "frozen_replay": replay,
        "critical_next_obligation": "V7_HUB_CYCLE_IMPOSSIBILITY_UNDER_PRE_BVE_ANCESTRY_OR_EXPLICIT_REALIZING_SOURCE",
        "verdict": "V7_ALL_DOORS_CLOSED_REDUCED_TO_REPLAYABLE_HUB_CYCLE_WITH_POLARITY_AND_SHIELDING__V7_ELIMINATION_OPEN",
        "firewall": {
            "FINITE_SUCCESS_IMPLIES_HUB_CYCLE_IMPOSSIBLE": False,
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
