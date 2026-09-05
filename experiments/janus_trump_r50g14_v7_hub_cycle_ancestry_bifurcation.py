from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r50g12_v6_rup_external_support_elimination as r50g12
import janus_trump_r50g13_v7_single_external_support_hub_cycle as r50g13

GATE = "JANUS_TRUMP_R50G14_V7_HUB_CYCLE_ANCESTRY_BIFURCATION"
WIDTH_CAP = 4


def canon(f):
    return r33.canonical_formula(f)


def cross_resolvent(pos, neg, pivot):
    p = set(int(x) for x in pos)
    n = set(int(x) for x in neg)
    if int(pivot) not in p or -int(pivot) not in n:
        raise ValueError("parents do not carry opposite pivot polarities")
    u = (p - {int(pivot)}) | (n - {-int(pivot)})
    if any(-x in u for x in u):
        return None
    return r33.canonical_clause(u)


def parent_geometry(pos, neg, pivot):
    p = tuple(pos)
    n = tuple(neg)
    r = cross_resolvent(p, n, int(pivot))
    if r is None:
        return {"tautological": True}
    a = set(p) - {int(pivot)}
    b = set(n) - {-int(pivot)}
    overlap = len(a & b)
    return {
        "tautological": False,
        "positive_width": len(p),
        "negative_width": len(n),
        "positive_residual": len(a),
        "negative_residual": len(b),
        "overlap": overlap,
        "resolvent": list(r),
        "resolvent_width": len(r),
    }


def classify_hub_edge_ancestor(source, pivot: int, final_clause, hub: int):
    """Find exact source parent pairs capable of carrying a V7 hub edge.

    Proof authority is the source argument in the R50G14 note. This routine is a
    mechanical certificate extractor for a supplied source/final-clause pair.
    """
    f = canon(source)
    c = r33.canonical_clause(final_clause)
    if max((len(q) for q in f), default=0) > WIDTH_CAP:
        raise ValueError("source must be W<=4")
    if len(c) != 5:
        raise ValueError("R50G14 classifies width-5 final clauses")
    if abs(int(hub)) in {abs(x) for x in c}:
        raise ValueError("hub must be external to final clause")

    pos = [q for q in f if int(pivot) in q]
    neg = [q for q in f if -int(pivot) in q]
    rows = []
    for p in pos:
        for n in neg:
            r = cross_resolvent(p, n, int(pivot))
            if r is None or not set(c) <= set(r):
                continue
            g = parent_geometry(p, n, int(pivot))
            if len(r) == 5 and r == c:
                allowed = (
                    (len(p), len(n), g["overlap"]) in {
                        (4, 3, 0), (3, 4, 0), (4, 4, 1)
                    }
                )
                if not allowed:
                    raise AssertionError(("R50G14_DIRECT5_GEOMETRY_DRIFT", p, n, g))
                rows.append({
                    "type": "DIRECT5",
                    "positive_parent": list(p),
                    "negative_parent": list(n),
                    "geometry": g,
                })
            elif len(r) == 6 and len(set(r) - set(c)) == 1:
                removed = next(iter(set(r) - set(c)))
                if abs(int(removed)) != abs(int(hub)):
                    continue
                if not (len(p) == 4 and len(n) == 4 and g["overlap"] == 0):
                    raise AssertionError(("R50G14_RUP6_GEOMETRY_DRIFT", p, n, g))
                rows.append({
                    "type": "RUP6_DROP_HUB",
                    "positive_parent": list(p),
                    "negative_parent": list(n),
                    "removed_hub_literal": int(removed),
                    "geometry": g,
                })
    return rows


def rup6_control():
    wide6 = r33.canonical_clause((2, 3, 4, 5, 6, 7))
    final5 = r33.canonical_clause((2, 3, 4, 5, 6))
    formula = canon([wide6, (-7, 2)])
    assumptions = tuple(-x for x in final5)
    receipt = r35b.candidate_unit_propagation_trace(formula, assumptions)
    independent = r35b.independent_up_conflict_checker(formula, assumptions)
    if not receipt["conflict"] or not independent:
        raise AssertionError(("R50G14_RUP6_CONTROL_FAIL", receipt, independent))
    return {
        "wide6": list(wide6),
        "final5": list(final5),
        "removed_hub_literal": 7,
        "RUP_conflict": True,
        "independent_replay": True,
    }


def source_ancestry_controls():
    # DIRECT5: 4x3 disjoint residuals; variable 7 exists elsewhere and is the hub.
    direct_source = canon([
        (1, 2, 3, 4),
        (-1, 5, 6),
        (7, -2),
        (-7, 3),
    ])
    direct_c = r33.canonical_clause((2, 3, 4, 5, 6))
    direct_rows = classify_hub_edge_ancestor(direct_source, 1, direct_c, 7)
    if not any(r["type"] == "DIRECT5" for r in direct_rows):
        raise AssertionError(("R50G14_DIRECT5_CONTROL_MISSING", direct_rows))

    # RUP6 ancestry: exact 4x4 disjoint residuals; hypothetical final drops hub 7.
    rup_source = canon([
        (1, 2, 3, 4),
        (-1, 5, 6, 7),
        (7, -2),
        (-7, 3),
    ])
    rup_c = r33.canonical_clause((2, 3, 4, 5, 6))
    rup_rows = classify_hub_edge_ancestor(rup_source, 1, rup_c, 7)
    if not any(r["type"] == "RUP6_DROP_HUB" for r in rup_rows):
        raise AssertionError(("R50G14_RUP6_CONTROL_MISSING", rup_rows))
    return {
        "DIRECT5": direct_rows,
        "RUP6_DROP_HUB": rup_rows,
    }


def cycle_label_bifurcation(labels):
    labels = list(labels)
    allowed = {"DIRECT5", "RUP6_DROP_HUB"}
    if not labels or any(x not in allowed for x in labels):
        raise ValueError("cycle labels must be nonempty and exact")
    if all(x == "DIRECT5" for x in labels):
        return "ALL_DIRECT5_CYCLE"
    return "RUP_BEARING_CYCLE"


def frozen_regression():
    r13 = r50g13.run()
    if r13["firewall"]["V6_IMMEDIATE_BVE_CASE_ELIMINATED"] is not True:
        raise AssertionError("R50G14_V6_FIREWALL_DRIFT")
    if r13["firewall"]["V7_IMMEDIATE_BVE_CASE_ELIMINATED"] is not False:
        raise AssertionError("R50G14_V7_FALSE_PROMOTION")
    return {
        "frozen_roots": r13["frozen_replay"]["frozen_roots"],
        "immediate_BVE_states": r13["frozen_replay"]["immediate_BVE_states"],
        "v7_bucket": r13["frozen_replay"]["v7_bucket"],
        "authority": "REGRESSION_ONLY",
    }


def run():
    controls = source_ancestry_controls()
    rup = rup6_control()
    graph_controls = {
        "all_direct": cycle_label_bifurcation(["DIRECT5", "DIRECT5", "DIRECT5"]),
        "rup_bearing": cycle_label_bifurcation(["DIRECT5", "RUP6_DROP_HUB", "DIRECT5"]),
    }
    replay = frozen_regression()
    return {
        "gate": GATE,
        "mode": "SOURCE_ANCESTRY_BIFURCATION_PLUS_FROZEN_REGRESSION",
        "proved_from_frozen_source_definitions": [
            "V7_UNSAFE_FINAL_IS_EXACT_V6_W5",
            "NO_POST_DP_VARIABLE_ELIMINATION_ON_V7_UNSAFE_TRACE",
            "NO_POST_DP_BVE_UNIT_OR_PURE_ON_V7_UNSAFE_TRACE",
            "FINAL_W5_CLAUSE_HAS_INITIAL_DP_ANCESTOR",
            "W5_OR_W6_ARE_THE_ONLY_POSSIBLE_WIDE_ANCESTOR_WIDTHS",
            "DIRECT5_PARENT_GEOMETRY_IS_4x3_3x4_DISJOINT_OR_4x4_OVERLAP1",
            "RUP6_DROP_HUB_PARENT_GEOMETRY_IS_4x4_DISJOINT",
            "EVERY_V7_HUB_CYCLE_IS_ALL_DIRECT5_OR_RUP_BEARING",
        ],
        "source_ancestry_controls": controls,
        "rup6_control": rup,
        "cycle_bifurcation_controls": graph_controls,
        "frozen_replay": replay,
        "critical_next_obligation": "ELIMINATE_ALL_DIRECT5_HUB_CYCLE_OR_RUP_BEARING_HUB_CYCLE_UNDER_PRE_BVE_CLEAN_SOURCE_OR_BUILD_EXPLICIT_V7_REALIZER",
        "verdict": "V7_HUB_EDGE_ANCESTRY_REDUCED_TO_DIRECT5_OR_RUP6_DROP_HUB__CYCLE_SPLIT_INTO_TWO_EXACT_CASES__V7_ELIMINATION_OPEN",
        "firewall": {
            "FINITE_SUCCESS_IMPLIES_V7_ELIMINATION": False,
            "HEURISTIC_AUTHORITY": False,
            "V6_IMMEDIATE_BVE_CASE_ELIMINATED": True,
            "V7_IMMEDIATE_BVE_CASE_ELIMINATED": False,
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
    args.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
