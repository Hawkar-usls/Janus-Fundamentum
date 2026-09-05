from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r50g14_v7_hub_cycle_ancestry_bifurcation as r50g14

GATE = "JANUS_TRUMP_R50G15_RUP6_HUB_BVE_BLOCKADE_SATURATION"


def canon(f):
    return r33.canonical_formula(f)


def resolvent(p, n, hub):
    u = (set(p) - {int(hub)}) | (set(n) - {-int(hub)})
    if any(-x in u for x in u):
        return None
    return r33.canonical_clause(u)


def exact_hub_bve_ledger(formula, hub: int):
    f = canon(formula)
    h = int(hub)
    pos = [c for c in f if h in c]
    neg = [c for c in f if -h in c]
    if not pos or not neg:
        raise AssertionError(("R50G15_HUB_NOT_BIPOLAR", h, pos, neg))
    rr = sorted({
        r for p in pos for n in neg
        for r in [resolvent(p, n, h)]
        if r is not None
    })
    removed = set(pos + neg)
    transformed = canon([c for c in f if c not in removed] + rr)
    before = r33.measure(f)
    after = r33.measure(transformed)
    accepted = len(rr) <= len(removed) and after < before
    return {
        "hub": h,
        "positive_count": len(pos),
        "negative_count": len(neg),
        "removed_count": len(removed),
        "distinct_nontaut_resolvent_count": len(rr),
        "positive": [list(c) for c in pos],
        "negative": [list(c) for c in neg],
        "resolvents": [list(c) for c in rr],
        "measure_before": list(before),
        "measure_after": list(after),
        "bve_accepted_for_hub": bool(accepted),
    }


def rup6_unit_witness_control():
    wide6 = r33.canonical_clause((1, 2, 3, 4, 5, 6))
    final5 = r33.canonical_clause((1, 2, 3, 4, 5))
    witness = r33.canonical_clause((-6, 1))
    f = canon([wide6, witness])
    assumptions = tuple(-x for x in final5)
    receipt = r35b.candidate_unit_propagation_trace(f, assumptions)
    independent = r35b.independent_up_conflict_checker(f, assumptions)
    if not receipt["conflict"] or not independent:
        raise AssertionError(("R50G15_RUP6_UNIT_WITNESS_CONTROL_FAIL", receipt, independent))
    return {
        "wide6": list(wide6),
        "final5": list(final5),
        "opposite_hub_unit_witness": list(witness),
        "RUP_conflict": True,
        "independent_UP_replay": True,
    }


def collapsed_wide_row(formula, wide6, hub: int):
    f = canon(formula)
    R = r33.canonical_clause(wide6)
    h = int(hub)
    C = tuple(x for x in R if abs(x) != abs(h))
    if len(R) != 6 or len(C) != 5:
        raise AssertionError(("R50G15_BAD_WIDE6_CONTROL", R, h))
    row = []
    nontaut = set()
    for n in f:
        if -h not in n:
            continue
        r = resolvent(R, n, h)
        row.append({"negative": list(n), "resolvent": None if r is None else list(r)})
        if r is not None:
            nontaut.add(r)
            if r != C:
                raise AssertionError(("R50G15_WIDTH6_ROW_DID_NOT_COLLAPSE_TO_C", R, n, r, C))
    if len(nontaut) > 1:
        raise AssertionError(("R50G15_COLLAPSED_ROW_HAS_GT1_DISTINCT", row))
    return {"target_C": list(C), "row": row, "distinct_nontaut_count": len(nontaut)}


def under_saturated_2x2_control():
    R = (1, 2, 3, 4, 5, 6)
    P = (6, -3, 4)
    N1 = (-6, 1)
    N2 = (-6, 2)
    f = canon([R, P, N1, N2])
    ledger = exact_hub_bve_ledger(f, 6)
    if ledger["positive_count"] != 2 or ledger["negative_count"] != 2:
        raise AssertionError(("R50G15_2x2_COUNT_DRIFT", ledger))
    if ledger["distinct_nontaut_resolvent_count"] >= ledger["removed_count"]:
        raise AssertionError(("R50G15_2x2_NOT_UNDERSATURATED", ledger))
    if not ledger["bve_accepted_for_hub"]:
        raise AssertionError(("R50G15_2x2_SHOULD_FORCE_BVE", ledger))
    collapsed = collapsed_wide_row(f, R, 6)
    return {"formula": [list(c) for c in f], "ledger": ledger, "collapsed_row": collapsed}


def minimal_3x2_blockade_control():
    R = (1, 2, 3, 4, 5, 6)
    P1 = (6, -3, 4)
    P2 = (6, -4, 5)
    N1 = (-6, 1)
    N2 = (-6, 2)
    f = canon([R, P1, P2, N1, N2])
    ledger = exact_hub_bve_ledger(f, 6)
    if ledger["positive_count"] != 3 or ledger["negative_count"] != 2:
        raise AssertionError(("R50G15_3x2_COUNT_DRIFT", ledger))
    if ledger["distinct_nontaut_resolvent_count"] != ledger["removed_count"]:
        raise AssertionError(("R50G15_3x2_NOT_EQUAL_COUNT_BOUNDARY", ledger))
    if ledger["bve_accepted_for_hub"]:
        raise AssertionError(("R50G15_3x2_EXPECTED_LOCAL_BLOCKADE", ledger))
    if tuple(ledger["measure_after"]) <= tuple(ledger["measure_before"]):
        raise AssertionError(("R50G15_3x2_MEASURE_DID_NOT_BLOCK", ledger))
    collapsed = collapsed_wide_row(f, R, 6)
    return {"formula": [list(c) for c in f], "ledger": ledger, "collapsed_row": collapsed}


def integer_saturation_boundary():
    feasible = []
    infeasible = []
    for p in range(1, 7):
        for n in range(1, 7):
            upper = 1 + (p - 1) * n
            needed = p + n
            row = {"p": p, "n": n, "collapsed_row_upper": upper, "bve_fixed_required": needed}
            if upper >= needed:
                feasible.append(row)
            else:
                infeasible.append(row)
    if not feasible:
        raise AssertionError("R50G15_NO_INTEGER_FEASIBLE_BOUNDARY")
    min_total = min(r["p"] + r["n"] for r in feasible)
    minimal = [r for r in feasible if r["p"] + r["n"] == min_total]
    if min_total != 5 or minimal != [{"p": 3, "n": 2, "collapsed_row_upper": 5, "bve_fixed_required": 5}]:
        raise AssertionError(("R50G15_INTEGER_BOUNDARY_DRIFT", min_total, minimal))
    return {
        "necessary_inequality": "1+(p-1)n >= p+n",
        "equivalent": "(p-2)(n-1) >= 1",
        "minimum_total_hub_occurrences": min_total,
        "unique_minimal_integer_pair": minimal[0],
    }


def frozen_regression():
    old = r50g14.run()
    if old["firewall"]["V6_IMMEDIATE_BVE_CASE_ELIMINATED"] is not True:
        raise AssertionError("R50G15_V6_FIREWALL_DRIFT")
    if old["firewall"]["V7_IMMEDIATE_BVE_CASE_ELIMINATED"] is not False:
        raise AssertionError("R50G15_V7_FALSE_PROMOTION")
    return {
        "frozen_roots": old["frozen_replay"]["frozen_roots"],
        "immediate_BVE_states": old["frozen_replay"]["immediate_BVE_states"],
        "v7_bucket": old["frozen_replay"]["v7_bucket"],
        "authority": "REGRESSION_ONLY",
    }


def run():
    rup = rup6_unit_witness_control()
    under = under_saturated_2x2_control()
    boundary = minimal_3x2_blockade_control()
    integer = integer_saturation_boundary()
    replay = frozen_regression()
    return {
        "gate": GATE,
        "mode": "SOURCE_COUNTING_THEOREM_PLUS_EXACT_LOCAL_CONTROLS_AND_FROZEN_REGRESSION",
        "proved_from_frozen_source_definitions": [
            "RUP6_DELETE_HUB_IN_V6_SUBSUMPTION_FIXED_STATE_REQUIRES_OPPOSITE_HUB_UNIT_WITNESS",
            "WIDTH6_ALL_VARIABLE_ROW_COLLAPSES_TO_AT_MOST_ONE_DISTINCT_NONTAUT_RESOLVENT",
            "BVE_FIXEDNESS_REQUIRES_DISTINCT_NONTAUT_RESOLVENT_COUNT_AT_LEAST_REMOVED_HUB_CLAUSE_COUNT",
            "RUP6_HUB_BVE_BLOCKADE_FORCES_P_GE_3_AND_N_GE_2",
            "MINIMUM_HUB_INCIDENCE_IS_FIVE_CLAUSES_AT_THE_3x2_BOUNDARY"
        ],
        "rup6_unit_witness_control": rup,
        "under_saturated_2x2_control": under,
        "minimal_3x2_blockade_control": boundary,
        "integer_saturation_boundary": integer,
        "frozen_replay": replay,
        "critical_next_obligation": "PULL_BACK_THE_3x2_OR_STRONGER_HUB_SATURATION_THROUGH_THE_EXACT_V7_DP_ANCESTRY_AND_FORCE_AN_ALTERNATE_CERTIFIED_DOOR_OR_BUILD_AN_EXPLICIT_V7_REALIZER",
        "verdict": "RUP6_HUB_EDGE_REQUIRES_3x2_OR_STRONGER_BVE_BLOCKADE_SATURATION__LOCAL_3x2_BOUNDARY_IS_REALIZABLE__V7_RUP_BEARING_CYCLE_OPEN",
        "firewall": {
            "FINITE_SUCCESS_IMPLIES_V7_ELIMINATION": False,
            "RUP_BEARING_V7_HUB_CYCLE_ELIMINATED": False,
            "V6_IMMEDIATE_BVE_CASE_ELIMINATED": True,
            "V7_IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "U_MU": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False
        }
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
