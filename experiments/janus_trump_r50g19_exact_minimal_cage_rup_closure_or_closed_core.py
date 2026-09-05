from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r50g17_v6_wide6_all_variable_bve_saturation_cage as r50g17
import janus_trump_r50g18_explicit_v7_full_sixfold_cage_ancestry_door_audit as r50g18

GATE = "JANUS_TRUMP_R50G19_EXACT_MINIMAL_CAGE_RUP_CLOSURE_OR_CLOSED_SUPPORT_CORE"


def canon(f):
    return r33.canonical_formula(f)


def edge_key(edge):
    return (edge["head"], tuple(edge["support_variables"]), tuple(edge["clause"]))


def closure(vertices, edges, seed):
    K = set(int(x) for x in seed)
    trace = []
    while True:
        additions = []
        for e in sorted(edges, key=edge_key):
            h = int(e["head"])
            S = set(int(x) for x in e["support_variables"])
            if h not in K and S <= K:
                additions.append((h, e))
        if not additions:
            break
        for h, e in additions:
            if h not in K:
                K.add(h)
                trace.append({
                    "added_head": h,
                    "via_clause": list(e["clause"]),
                    "support_variables": list(e["support_variables"]),
                })
    return {
        "closure": sorted(K),
        "trace": trace,
        "full": K == set(vertices),
    }


def is_closed(vertices, edges, K):
    K = set(int(x) for x in K)
    for e in edges:
        h = int(e["head"])
        S = set(int(x) for x in e["support_variables"])
        if h not in K and S <= K:
            return False
    return True


def extract_exact_minimal_hypergraph(formula, wide_clause):
    f = canon(formula)
    R = r33.canonical_clause(wide_clause)
    variables = sorted(abs(x) for x in R)
    if len(R) != 6 or len(set(variables)) != 6 or set(r33.variables(f)) != set(variables):
        raise ValueError("R50G19 requires exact six-variable all-variable R")

    reduced = r33.simplify(f)
    if reduced["terminal"] != "STALLED_STACK_LEAN_CORE" or canon(reduced["final_formula"]) != f:
        raise AssertionError(("R50G19_SCOPE_REQUIRES_R33_FIXED", reduced["terminal"], reduced["history"]))

    cage = r50g17.six_variable_saturation_cage(f, R)
    if not cage["all_six_variables_bve_blocked"]:
        raise AssertionError(("R50G19_SCOPE_REQUIRES_ALL_SIX_BVE_BLOCKED", cage))
    if any((int(p["p"]), int(p["n"])) != (3, 2) for p in cage["profiles"]):
        raise AssertionError(("R50G19_SCOPE_REQUIRES_EXACT_3x2", cage["profiles"]))

    r_by_var = {abs(l): int(l) for l in R}
    edges = []
    clause_heads = {}
    for profile in cage["profiles"]:
        lit = int(profile["literal"])
        head = abs(lit)
        found = 0
        for row in profile["wide_row"]:
            if row["resolvent"] is None:
                continue
            D = r33.canonical_clause(row["opposite_clause"])
            if -lit not in D:
                raise AssertionError(("R50G19_ROW_WITNESS_MISSING_OPPOSITE_HEAD", lit, D))
            support = tuple(q for q in D if q != -lit)
            if not support:
                raise AssertionError(("R50G19_UNIT_ROW_WITNESS_IN_R33_FIXED_STATE", lit, D))
            for q in support:
                if r_by_var.get(abs(q)) != int(q):
                    raise AssertionError(("R50G19_ROW_WITNESS_HAS_SECOND_SIGN_DISAGREEMENT", lit, D, q, R))
            key = tuple(D)
            old = clause_heads.get(key)
            if old is not None and old != head:
                raise AssertionError(("R50G19_ONE_ROW_WITNESS_SERVES_TWO_HEADS", D, old, head))
            clause_heads[key] = head
            edges.append({
                "head": head,
                "head_literal_in_R": lit,
                "opposite_head_literal": -lit,
                "clause": list(D),
                "support_literals": list(support),
                "support_variables": sorted(abs(q) for q in support),
            })
            found += 1
        if found == 0:
            raise AssertionError(("R50G19_EXACT_BOUNDARY_WITHOUT_NONTAUT_R_ROW_WITNESS", lit, profile))

    return {
        "variables": variables,
        "wide_clause": list(R),
        "edges": sorted(edges, key=edge_key),
        "edge_count": len(edges),
        "distinct_witness_clause_count": len(clause_heads),
        "cage": cage,
    }


def closure_dichotomy(formula, wide_clause):
    f = canon(formula)
    hg = extract_exact_minimal_hypergraph(f, wide_clause)
    vertices = hg["variables"]
    edge_rows = []
    full = []
    proper = []

    for e in hg["edges"]:
        c = closure(vertices, hg["edges"], e["support_variables"])
        row = {"seed_edge": e, **c}
        edge_rows.append(row)
        if c["full"]:
            assumptions = tuple(-int(q) for q in e["support_literals"])
            receipt = r35b.candidate_unit_propagation_trace(f, assumptions)
            independent = r35b.independent_up_conflict_checker(f, assumptions)
            if not receipt["conflict"] or not independent:
                raise AssertionError(("R50G19_FULL_CLOSURE_DID_NOT_REPLAY_AS_RUP", e, c, receipt, independent))
            full.append({
                **row,
                "strengthening_source_clause": e["clause"],
                "removed_literal": e["opposite_head_literal"],
                "strengthened_clause": e["support_literals"],
                "assumptions": list(assumptions),
                "UP_conflict": True,
                "independent_UP_replay": True,
            })
        else:
            if not c["closure"] or not is_closed(vertices, hg["edges"], c["closure"]):
                raise AssertionError(("R50G19_PROPER_CLOSURE_NOT_NONEMPTY_CLOSED", e, c))
            proper.append(row)

    if full:
        outcome = "FULL_RUP_CLOSURE_WITNESS"
        certificate = sorted(full, key=lambda r: edge_key(r["seed_edge"]))[0]
    else:
        outcome = "PROPER_CLOSED_SUPPORT_CORE"
        certificate = sorted(
            proper,
            key=lambda r: (len(r["closure"]), tuple(r["closure"]), edge_key(r["seed_edge"]))
        )[0]
        if certificate["full"]:
            raise AssertionError("R50G19_CLOSED_CORE_MARKED_FULL")

    return {
        "hypergraph": hg,
        "seed_closures": edge_rows,
        "outcome": outcome,
        "certificate": certificate,
        "full_closure_witness_count": len(full),
        "proper_closed_seed_count": len(proper),
    }


def abstract_closed_core_control():
    vertices = [1, 2, 3, 4, 5, 6]
    edges = [
        {"head": 1, "support_variables": [2], "clause": [-1, 2]},
        {"head": 2, "support_variables": [3], "clause": [-2, 3]},
        {"head": 3, "support_variables": [1], "clause": [1, -3]},
        {"head": 4, "support_variables": [5], "clause": [-4, 5]},
        {"head": 5, "support_variables": [6], "clause": [-5, 6]},
        {"head": 6, "support_variables": [4], "clause": [4, -6]},
    ]
    rows = [closure(vertices, edges, e["support_variables"]) for e in edges]
    if any(r["full"] for r in rows):
        raise AssertionError(("R50G19_CLOSED_CORE_CONTROL_UNEXPECTED_FULL", rows))
    cores = [r["closure"] for r in rows]
    if [1, 2, 3] not in cores or [4, 5, 6] not in cores:
        raise AssertionError(("R50G19_CLOSED_CORE_CONTROL_MISSING_COMPONENTS", cores))
    return {"vertices": vertices, "edges": edges, "closures": rows}


def run():
    r18 = closure_dichotomy(r50g18.EXPECTED_CAGE, r50g18.R)
    abstract = abstract_closed_core_control()
    if r18["outcome"] != "FULL_RUP_CLOSURE_WITNESS":
        raise AssertionError(("R50G19_R50G18_EXPECTED_FULL_CLOSURE", r18))
    return {
        "gate": GATE,
        "mode": "SOURCE_HYPERGRAPH_DICHOTOMY_PLUS_INDEPENDENT_RUP_REPLAY_CONTROL",
        "proved_from_frozen_source_definitions": [
            "EXACT_3x2_BVE_BLOCKADE_FORCES_NONTAUT_R_ROW_WITNESS_FOR_EVERY_HEAD_LITERAL",
            "R33_UNIT_FIXEDNESS_FORCES_NONEMPTY_SAME_POLARITY_SUPPORT_FOR_EVERY_ROW_WITNESS",
            "DISTINCT_HEADS_REQUIRE_DISTINCT_ROW_WITNESS_CLAUSES",
            "SUPPORT_HYPERGRAPH_MONOTONE_CLOSURE_TERMINATES_IN_AT_MOST_SIX_HEAD_ADDITIONS",
            "FULL_SUPPORT_CLOSURE_CERTIFIES_SINGLE_LITERAL_RUP_BY_UNIT_PROPAGATION_TO_EMPTY_R",
            "NO_FULL_SEED_CLOSURE_YIELDS_A_NONEMPTY_PROPER_SUPPORT_CLOSED_CORE_CERTIFICATE"
        ],
        "r50g18_full_cage_control": r18,
        "abstract_proper_closed_core_control": abstract,
        "critical_next_obligation": "PROVE_PROPER_SUPPORT_CLOSED_CORE_INCOMPATIBLE_WITH_EXACT_MINIMAL_CAGE_PLUS_PRE_BVE_V7_ANCESTRY_OR_BUILD_AN_EXPLICIT_CAGE_REALIZER_WITH_SUCH_A_CORE_AND_AUDIT_ITS_DOORS",
        "verdict": "EXACT_MINIMAL_CAGE_REDUCED_TO_RUP_FULL_CLOSURE_OR_PROPER_CLOSED_SUPPORT_CORE__R50G18_HAS_CERTIFIED_FULL_CLOSURE__CLOSED_CORE_OBSTRUCTION_OPEN",
        "firewall": {
            "FULL_CLOSURE_ON_R50G18_IMPLIES_ALL_EXACT_MINIMAL_CAGES_RUP_REDUCIBLE": False,
            "PROPER_CLOSED_CORE_IMPOSSIBLE": False,
            "RUP_BEARING_V7_HUB_CYCLE_ELIMINATED": False,
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
