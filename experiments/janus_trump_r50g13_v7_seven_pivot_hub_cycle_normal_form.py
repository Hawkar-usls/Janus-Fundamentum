from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a
import janus_trump_r50g_smallest_first_exact_deadcore_falsifier as r50g
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g5_immediate_bve_exact_descent_algebraic_reduction as r50g5
import janus_trump_r50g10_wide_fixpoint_forces_alternate_certified_door as r50g10
import janus_trump_r50g12_v6_rup_external_support_elimination as r50g12

GATE = "JANUS_TRUMP_R50G13_V7_SEVEN_PIVOT_HUB_CYCLE_NORMAL_FORM"
WIDTH_CAP = 4
SOURCE_V = 7


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def vars_set(f):
    return set(int(v) for v in r33.variables(canon(f)))


def first_cycle(mapping):
    """Return the first deterministic directed cycle of a finite functional map."""
    done = set()
    for start in sorted(mapping):
        if start in done:
            continue
        order = []
        at = {}
        v = start
        while v not in at and v not in done:
            at[v] = len(order)
            order.append(v)
            if v not in mapping:
                raise AssertionError(("R50G13_NON_TOTAL_HUB_MAP", v, mapping))
            v = int(mapping[v])
        if v in at:
            return order[at[v]:] + [v]
        done.update(order)
    return None


def widest_clause(final):
    f = canon(final)
    w = max_width(f)
    rows = sorted(c for c in f if len(c) == w)
    return rows[0] if rows else tuple()


def dp_ancestor_certificate(source, y: int, final_clause):
    """Find a width-5/6 exact-DP resolvent that contains the final W5 clause."""
    f = canon(source)
    c = r33.canonical_clause(final_clause)
    _row, cand = r50a._fallback_candidate(f, int(y))
    if cand is None:
        raise AssertionError(("R50G13_R47J_CANDIDATE_MISSING", y))
    dp = cand["DP"]
    resolvents = [r33.canonical_clause(r) for r in dp["full_non_tautological_resolvents"]]
    candidates = sorted(
        (r for r in resolvents if len(r) in (5, 6) and set(c).issubset(set(r))),
        key=lambda r: (len(r), r),
    )
    if not candidates:
        raise AssertionError(("R50G13_FINAL_W5_WITHOUT_WIDE_DP_ANCESTOR", y, c, resolvents))
    ancestor = candidates[0]
    final_vars = vars_set(cand["normalization"]["final_formula"])
    cvars = {abs(int(l)) for l in c}
    omitted = sorted(final_vars - cvars)
    if len(omitted) != 1:
        raise AssertionError(("R50G13_FINAL_CLAUSE_NOT_SINGLE_HUB", y, c, final_vars, omitted))
    hub = omitted[0]
    avars = {abs(int(l)) for l in ancestor}
    if len(ancestor) == 5:
        if ancestor != c:
            raise AssertionError(("R50G13_W5_ANCESTOR_NOT_EQUAL_FINAL", y, ancestor, c))
        if hub in avars:
            raise AssertionError(("R50G13_W5_ANCESTOR_CONTAINS_HUB", y, hub, ancestor))
        mode = "WIDTH5_DP_RESOLVENT_OMITS_HUB"
        removed_literal = None
    else:
        if len(avars) != 6 or hub not in avars:
            raise AssertionError(("R50G13_W6_ANCESTOR_NOT_ALL_SIX_VARS", y, hub, ancestor, avars))
        missing = [int(l) for l in ancestor if abs(int(l)) == hub]
        if len(missing) != 1:
            raise AssertionError(("R50G13_W6_HUB_LITERAL_NOT_UNIQUE", y, hub, ancestor))
        if len(set(ancestor) - set(c)) != 1:
            raise AssertionError(("R50G13_W6_TO_W5_NOT_SINGLE_LITERAL", y, ancestor, c))
        mode = "WIDTH6_DP_RESOLVENT_DROPS_HUB_LITERAL"
        removed_literal = missing[0]
    return {
        "pivot": int(y),
        "final_clause": list(c),
        "hub": int(hub),
        "ancestor": list(ancestor),
        "ancestor_width": len(ancestor),
        "ancestry_mode": mode,
        "removed_hub_literal": removed_literal,
    }


def closed_pivot_v7_normal_form(source, y: int):
    f = canon(source)
    if len(r33.variables(f)) != SOURCE_V or max_width(f) > WIDTH_CAP:
        raise AssertionError(("R50G13_SOURCE_NOT_V7_W4", len(r33.variables(f)), max_width(f)))
    door = r50g10.exact_door_row(f, int(y))
    if not door["closed_door_certificate"]:
        return {"pivot": int(y), "closed": False, "door": door}
    if int(door["chi_star"]) not in (5, 6):
        raise AssertionError(("R50G13_CLOSED_CHI_NOT_5_6", y, door))

    row, cand = r50a._fallback_candidate(f, int(y))
    if cand is None:
        raise AssertionError(("R50G13_CANDIDATE_MISSING", y))
    final = canon(cand["normalization"]["final_formula"])
    final_vars = vars_set(final)
    source_vars = vars_set(f)
    expected_vars = source_vars - {int(y)}
    if row["terminal"] is not None or int(row["final_max_width"]) <= WIDTH_CAP:
        raise AssertionError(("R50G13_CLOSED_R47J_NOT_WIDE_NONTERMINAL", y, row))

    if len(final_vars) != 6 or max_width(final) != 5:
        raise AssertionError(("R50G13_V7_CLOSED_FINAL_NOT_EXACT_V6_W5", y, len(final_vars), max_width(final)))
    if final_vars != expected_vars:
        raise AssertionError(("R50G13_FINAL_VARS_NOT_ALL_OTHER_SOURCE_VARS", y, sorted(final_vars), sorted(expected_vars)))

    c = widest_clause(final)
    if len(c) != 5:
        raise AssertionError(("R50G13_WIDEST_NOT_W5", y, c))
    audit = r50g12.external_support_fixedpoint_audit(final, c)
    external = audit["external_formula_variables"]
    if len(external) != 1:
        raise AssertionError(("R50G13_NOT_SINGLE_EXTERNAL_HUB", y, c, external))
    hub = int(external[0])
    if hub == int(y) or hub not in expected_vars:
        raise AssertionError(("R50G13_INVALID_HUB", y, hub, expected_vars))
    for per in audit["per_literal"]:
        for support in per["supports"]:
            if hub not in support["external_variables"]:
                raise AssertionError(("R50G13_SUPPORT_MISSES_UNIQUE_HUB", y, hub, per, support))

    ancestry = dp_ancestor_certificate(f, int(y), c)
    if int(ancestry["hub"]) != hub:
        raise AssertionError(("R50G13_ANCESTRY_HUB_MISMATCH", y, hub, ancestry))

    return {
        "pivot": int(y),
        "closed": True,
        "door": door,
        "final_hash": r50g4.fhash(final),
        "final_variable_count": len(final_vars),
        "final_max_width": max_width(final),
        "final_variables": sorted(final_vars),
        "widest_clause": list(c),
        "hub": hub,
        "support_audit": audit,
        "dp_ancestry": ancestry,
    }


def all_closed_v7_normal_form(source, x: int):
    f = canon(source)
    if not r50g10.exact_pre_bve_clean(f):
        raise AssertionError("R50G13_SOURCE_NOT_PRE_BVE_CLEAN")
    if len(r33.variables(f)) != SOURCE_V:
        raise AssertionError(("R50G13_SOURCE_V_NOT7", len(r33.variables(f))))
    micro = r50g4.micro_r33_status(f)
    direct = r50g4.first_r33_micro_candidate(f)
    if (
        micro["status"] != "IMMEDIATE_BVE_W4_ESCAPE"
        or direct["kind"] != "PROPOSAL"
        or direct["rule"] != "BOUNDED_VARIABLE_ELIMINATION"
        or int(direct["var"]) != int(x)
    ):
        raise AssertionError(("R50G13_NOT_IMMEDIATE_BVE_X", x, micro, direct))

    same = r50g5.prove_immediate_bve_same_pivot(f)
    if not same["applicable"] or not same["same_pivot_wide_survivor"]:
        return {
            "applicable": False,
            "reason": "SAME_PIVOT_NOT_WIDE_SURVIVOR",
            "same_pivot": same,
        }

    rows = [closed_pivot_v7_normal_form(f, int(y)) for y in sorted(r33.variables(f))]
    if not all(r["closed"] for r in rows):
        return {
            "applicable": False,
            "reason": "AT_LEAST_ONE_CERTIFIED_DOOR_OPEN",
            "first_open": next(r for r in rows if not r["closed"]),
            "rows": rows,
        }

    mapping = {int(r["pivot"]): int(r["hub"]) for r in rows}
    if any(k == v for k, v in mapping.items()):
        raise AssertionError(("R50G13_HUB_MAP_FIXED_POINT", mapping))
    cycle = first_cycle(mapping)
    if cycle is None or len(cycle) < 3:
        raise AssertionError(("R50G13_FIXED_POINT_FREE_MAP_WITHOUT_NONTRIVIAL_CYCLE", mapping, cycle))
    if len(cycle) - 1 not in range(2, 8):
        raise AssertionError(("R50G13_CYCLE_LENGTH_OUT_OF_RANGE", cycle))

    return {
        "applicable": True,
        "source_hash": r50g4.fhash(f),
        "source_CLV": list(r33.measure(f)),
        "distinguished_pivot": int(x),
        "all_seven_pivots_closed": True,
        "hub_map": {str(k): v for k, v in sorted(mapping.items())},
        "hub_cycle": cycle,
        "hub_cycle_length": len(cycle) - 1,
        "rows": rows,
    }


def replay_frozen_roots():
    immediate_v7 = 0
    same_wide_v7 = 0
    open_door_v7 = 0
    all_closed_v7 = []
    for worker, n in enumerate(range(6, 11)):
        for i in range(80):
            m = 3 * n + (i % (3 * n + 1))
            seed = 50_700_000 + worker * 100_000 + i
            root, _ = r50g.make_planted(seed, n, m, "3CNF")
            if len(r33.variables(root)) != n:
                continue
            state = canon(root)
            seen = set()
            bound = 8 * max(1, len(r33.variables(state))) + 4 * max(1, len(state)) + 32
            for step_index in range(bound):
                h = r50g4.fhash(state)
                if h in seen:
                    raise AssertionError(("R50G13_TRACE_CYCLE", worker, seed, h))
                seen.add(h)
                if len(r33.variables(state)) == 7:
                    proof = r50g5.prove_immediate_bve_same_pivot(state)
                    if proof["applicable"]:
                        immediate_v7 += 1
                        if proof["same_pivot_wide_survivor"]:
                            same_wide_v7 += 1
                            x = int(proof["pivot"])
                            nf = all_closed_v7_normal_form(state, x)
                            if nf["applicable"]:
                                all_closed_v7.append({
                                    "worker": worker,
                                    "seed": seed,
                                    "step": step_index,
                                    **nf,
                                })
                            else:
                                open_door_v7 += 1
                step = r50g4.refined_exact_step(state)
                if step["kind"] in ("TERMINAL", "OPEN_OBSTRUCTION"):
                    break
                state = canon(step["successor"])
            else:
                raise AssertionError(("R50G13_TRACE_BOUND", worker, seed))
    return {
        "frozen_roots": 400,
        "reachable_v7_immediate_BVE_states": immediate_v7,
        "reachable_v7_same_pivot_wide_survivors": same_wide_v7,
        "reachable_v7_wide_with_open_alternate_door": open_door_v7,
        "reachable_v7_all_doors_closed": len(all_closed_v7),
        "first_reachable_v7_all_doors_closed": all_closed_v7[0] if all_closed_v7 else None,
    }


def combinatorial_control():
    mapping = {1: 2, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6}
    cycle = first_cycle(mapping)
    if cycle != [1, 2, 1]:
        raise AssertionError(("R50G13_CYCLE_CONTROL_FAIL", cycle))
    return {
        "fixed_point_free_map": {str(k): v for k, v in mapping.items()},
        "first_cycle": cycle,
        "cycle_length": 2,
    }


def run():
    replay = replay_frozen_roots()
    control = combinatorial_control()
    if replay["reachable_v7_all_doors_closed"]:
        verdict = "EXPLICIT_REACHABLE_V7_ALL_DOORS_CLOSED_HUB_CYCLE_WITNESS_FOUND"
        reachable_status = "REFUTED"
    else:
        verdict = "V7_ALL_CLOSED_REDUCED_TO_SEVEN_PIVOT_V6W5_HUB_CYCLE_NORMAL_FORM__FROZEN_REPLAY_NO_WITNESS__V7_ELIMINATION_OPEN"
        reachable_status = "OPEN"
    return {
        "gate": GATE,
        "mode": "SOURCE_NORMAL_FORM_PLUS_FROZEN_REACHABLE_REGRESSION",
        "proved_from_frozen_source_definitions": [
            "IMMEDIATE_BVE_WIDE_X_CLOSES_R49H_ON_X",
            "ALL_ALTERNATE_DOORS_CLOSED_PLUS_SAME_PIVOT_WIDE_IMPLIES_ALL_SEVEN_PIVOTS_CLOSED",
            "EVERY_CLOSED_V7_R47J_FINAL_HAS_EXACTLY_SIX_VARIABLES_AND_WIDTH_FIVE",
            "EVERY_CLOSED_V7_R47J_FINAL_RETAINS_ALL_SOURCE_VARIABLES_EXCEPT_ITS_PIVOT",
            "EVERY_CANONICAL_W5_FINAL_CLAUSE_HAS_ONE_UNIQUE_EXTERNAL_SUPPORT_HUB",
            "EVERY_NONBLOCKING_SUPPORT_OF_THAT_W5_CLAUSE_USES_THE_UNIQUE_HUB",
            "NO_VARIABLE_REMOVING_NORMALIZATION_CAN_OCCUR_AFTER_DP_Y_IN_THE_CLOSED_V7_NORMAL_FORM",
            "EVERY_FINAL_W5_CLAUSE_HAS_A_WIDTH5_OR_WIDTH6_EXACT_DP_ANCESTOR",
            "ALL_CLOSED_V7_INDUCES_A_TOTAL_FIXED_POINT_FREE_SEVEN_VERTEX_HUB_MAP_WITH_A_DIRECTED_CYCLE",
        ],
        "combinatorial_control": control,
        "frozen_replay": replay,
        "critical_next_obligation": "ELIMINATE_OR_REALIZE_A_SHARED_W4_PARENT_SYSTEM_THAT_REALIZES_A_CYCLIC_SEVEN_PIVOT_HUB_MAP",
        "verdict": verdict,
        "firewall": {
            "FINITE_SUCCESS_IMPLIES_THEOREM": False,
            "HEURISTIC_AUTHORITY": False,
            "NEW_SEMANTIC_INFERENCE_RULE": False,
            "V6_IMMEDIATE_BVE_CASE_ELIMINATED": True,
            "V7_HUB_CYCLE_NORMAL_FORM": "CLOSED",
            "V7_IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "REACHABLE_V7_ALL_DOORS_CLOSED": reachable_status,
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
