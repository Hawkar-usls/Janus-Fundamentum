from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50g8_wide_survivor_impossibility_from_pre_bve_cleanliness as r50g8

GATE = "JANUS_TRUMP_R50G9_WIDE_FIXPOINT_DOUBLE_WITNESS_CROWN"
WIDTH_CAP = 4


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def unique_nontaut_resolvents(formula, var: int):
    f = canon(formula)
    v = int(var)
    pos = [c for c in f if v in c]
    neg = [c for c in f if -v in c]
    resolvents = []
    for p in pos:
        for n in neg:
            rr = (set(p) - {v}) | (set(n) - {-v})
            if any(-lit in rr for lit in rr):
                continue
            resolvents.append(r33.canonical_clause(rr))
    resolvents = tuple(sorted(set(resolvents)))
    removed = set(pos + neg)
    inherited = tuple(c for c in f if c not in removed)
    transformed = canon(list(inherited) + list(resolvents))
    return {
        "var": v,
        "positive": tuple(pos),
        "negative": tuple(neg),
        "resolvents": resolvents,
        "inherited": inherited,
        "transformed": transformed,
    }


def bve_fixedpoint_rejection_certificate(formula, var: int):
    """Exact necessary certificate for a variable at an R33 BVE fixed point."""
    f = canon(formula)
    data = unique_nontaut_resolvents(f, var)
    p = len(data["positive"])
    n = len(data["negative"])
    if p == 0 or n == 0:
        raise AssertionError(("R50G9_PURE_OR_MISSING_POLARITY_AT_FIXEDPOINT", var, p, n))

    r = len(data["resolvents"])
    removed = p + n
    if r < removed:
        raise AssertionError(("R50G9_BVE_FIXEDPOINT_RESOLVENT_COUNT_TOO_SMALL", var, r, removed))
    if p < 2 or n < 2:
        raise AssertionError(("R50G9_BVE_FIXEDPOINT_POLARITY_DEGREE_LT_2", var, p, n, r))

    before_measure = r33.measure(f)
    after_measure = r33.measure(data["transformed"])
    parent_literals = sum(len(c) for c in data["positive"]) + sum(len(c) for c in data["negative"])
    resolvent_literals = sum(len(c) for c in data["resolvents"])

    if r > removed:
        rejection_kind = "RESOLVENT_SURPLUS"
    else:
        # With equal raw clause counts, any inherited duplicate would make the
        # transformed clause count smaller and frozen BVE would be accepted.
        if len(data["transformed"]) != len(f):
            raise AssertionError(("R50G9_EQUALITY_CASE_CLAUSE_COUNT_DESCENT", var, len(f), len(data["transformed"])))
        if not (resolvent_literals > parent_literals):
            raise AssertionError((
                "R50G9_EQUALITY_CASE_MUST_STRICTLY_INFLATE_LITERALS",
                var,
                parent_literals,
                resolvent_literals,
                before_measure,
                after_measure,
            ))
        rejection_kind = "LITERAL_INFLATION_EQUALITY"

    if after_measure < before_measure:
        raise AssertionError(("R50G9_CERTIFIED_REJECTED_VAR_WOULD_DESCEND", var, before_measure, after_measure))

    inherited_set = set(data["inherited"])
    inherited_resolvent_duplicates = sum(int(c in inherited_set) for c in data["resolvents"])
    if r == removed and inherited_resolvent_duplicates:
        raise AssertionError(("R50G9_EQUALITY_CASE_INHERITED_DUPLICATE", var, inherited_resolvent_duplicates))

    return {
        "var": int(var),
        "positive_occurrences": p,
        "negative_occurrences": n,
        "removed_parent_count": removed,
        "unique_nontaut_resolvent_count": r,
        "parent_literal_sum": parent_literals,
        "resolvent_literal_sum": resolvent_literals,
        "inherited_resolvent_duplicates": inherited_resolvent_duplicates,
        "before_measure": list(before_measure),
        "after_measure": list(after_measure),
        "rejection_kind": rejection_kind,
    }


def rup_escape_receipts_for_clause(formula, clause):
    """At a frozen RUP fixpoint every one-literal deletion must fail by non-conflict."""
    f = canon(formula)
    c = tuple(clause)
    rows = []
    for removed_literal in sorted(c, key=r33.lit_key):
        strengthened = tuple(l for l in c if l != removed_literal)
        assumptions = tuple(-l for l in sorted(strengthened, key=r33.lit_key))
        receipt = r35b.candidate_unit_propagation_trace(f, assumptions)
        independent_conflict = r35b.independent_up_conflict_checker(f, assumptions)
        if receipt["conflict"] or independent_conflict:
            raise AssertionError((
                "R50G9_RUP_FIXEDPOINT_SINGLE_LITERAL_DELETION_CONFLICTED",
                c,
                removed_literal,
                receipt,
                independent_conflict,
            ))
        rows.append({
            "removed_literal": int(removed_literal),
            "strengthened_clause": list(strengthened),
            "assumptions": list(assumptions),
            "candidate_conflict": False,
            "independent_conflict": False,
            "trail_length": len(receipt.get("trail", [])),
            "clause_scans": int(receipt["clause_scans"]),
            "literal_inspections": int(receipt["literal_inspections"]),
        })
    return rows


def verify_certified_normalization_fixpoint(formula):
    f = canon(formula)
    reduced = r33.simplify(f)
    if reduced["history"] or reduced["terminal"] != "STALLED_STACK_LEAN_CORE" or canon(reduced["final_formula"]) != f:
        raise AssertionError(("R50G9_NOT_R33_FIXED", reduced["terminal"], reduced["history"][:1]))
    if r33.pure_literals(f):
        raise AssertionError("R50G9_FIXEDPOINT_HAS_PURE_LITERAL")
    if r33.bve_candidate(f) is not None:
        raise AssertionError("R50G9_FIXEDPOINT_HAS_BVE_CANDIDATE")
    affine = r34.recognize_complete_affine_cnf(f)
    if affine["recognized"]:
        raise AssertionError("R50G9_FIXEDPOINT_AFFINE_TERMINAL")
    rup = r35b.run_candidate(f)
    if rup["status"] != "STALLED_RUP_CORE" or canon(rup["final_formula"]) != f:
        raise AssertionError(("R50G9_NOT_RUP_FIXED", rup["status"], len(rup.get("history", []))))
    return True


def fixedpoint_double_witness_crowns(formula):
    f = canon(formula)
    verify_certified_normalization_fixpoint(f)

    var_certificates = {
        int(v): bve_fixedpoint_rejection_certificate(f, int(v))
        for v in r33.variables(f)
    }
    wide_rows = []
    for clause in f:
        if len(clause) <= WIDTH_CAP:
            continue
        supports = r50g8.nonblocking_supports_for_clause(f, clause)
        if supports is None:
            raise AssertionError(("R50G9_WIDE_CLAUSE_MISSING_BCE_CROWN", clause))
        rup_rows = rup_escape_receipts_for_clause(f, clause)
        occurrence_rows = []
        for lit in clause:
            cert = var_certificates[abs(int(lit))]
            same = cert["positive_occurrences"] if lit > 0 else cert["negative_occurrences"]
            opposite = cert["negative_occurrences"] if lit > 0 else cert["positive_occurrences"]
            if same < 2 or opposite < 2:
                raise AssertionError(("R50G9_WIDE_LITERAL_MISSING_2X2_OCCURRENCE_CROWN", clause, lit, cert))
            occurrence_rows.append({
                "literal": int(lit),
                "same_polarity_occurrences": same,
                "opposite_polarity_occurrences": opposite,
                "bve_rejection_kind": cert["rejection_kind"],
            })
        wide_rows.append({
            "wide_clause": list(clause),
            "width": len(clause),
            "distinct_BCE_support_count": len(set(supports.values())),
            "BCE_supports": [
                {"literal": int(lit), "witness_clause": list(w)}
                for lit, w in sorted(supports.items(), key=lambda kv: r33.lit_key(kv[0]))
            ],
            "RUP_escape_receipts": rup_rows,
            "occurrence_crown": occurrence_rows,
        })

    return {
        "variable_count": len(var_certificates),
        "all_variables_have_2x2_polarity_degree": all(
            c["positive_occurrences"] >= 2 and c["negative_occurrences"] >= 2
            for c in var_certificates.values()
        ),
        "resolvent_surplus_variables": sum(c["rejection_kind"] == "RESOLVENT_SURPLUS" for c in var_certificates.values()),
        "literal_inflation_equality_variables": sum(c["rejection_kind"] == "LITERAL_INFLATION_EQUALITY" for c in var_certificates.values()),
        "variable_certificates": [var_certificates[v] for v in sorted(var_certificates)],
        "wide_clause_count": len(wide_rows),
        "wide_clause_crowns": wide_rows,
    }


def frozen_core_regression():
    _sealed, core = r47j.load_counterexample()
    core = canon(core)
    crowns = fixedpoint_double_witness_crowns(core)
    if crowns["wide_clause_count"] != 0:
        raise AssertionError("R50G9_FROZEN_R47J_CORE_UNEXPECTEDLY_WIDE")
    return {
        "core_hash": r47j.EXPECTED_FIXPOINT_HASH,
        "core_CLV": list(r47j.EXPECTED_FIXPOINT_CLV),
        "max_width": max_width(core),
        "variable_count": crowns["variable_count"],
        "all_variables_have_2x2_polarity_degree": crowns["all_variables_have_2x2_polarity_degree"],
        "resolvent_surplus_variables": crowns["resolvent_surplus_variables"],
        "literal_inflation_equality_variables": crowns["literal_inflation_equality_variables"],
    }


def replay_frozen_reachable():
    r = r50g8.replay_frozen_reachable()
    # R50G8 already emits a full certificate if a final wide fixpoint occurs.
    # If such a witness appears, independently rebuild the stronger R50G9 crown.
    first = r.get("first_wide_fixpoint_certificate")
    crown = None
    if first is not None:
        raise AssertionError("R50G9_EXPECTED_FORMULA_BYTES_FOR_WIDE_CERTIFICATE_NOT_PRESENT_IN_R50G8_COMPACT_ROW")
    return {
        **r,
        "first_double_witness_crown": crown,
    }


def firewall(reachable_wide_found: bool):
    return {
        "HEURISTIC_AUTHORITY": False,
        "LEARNED_SELECTOR": False,
        "PROBABILISTIC_AUTHORITY": False,
        "NEW_SEMANTIC_INFERENCE_RULE": False,
        "NO_NEW_CORPUS": True,
        "FINITE_NO_FIND_IMPLIES_THEOREM": False,
        "DOUBLE_WITNESS_CROWN_IMPOSSIBILITY_THEOREM": "REFUTED_ON_REACHABLE_WITNESS" if reachable_wide_found else "OPEN",
        "WIDE_ANCESTRY_IMPOSSIBILITY_THEOREM": "REFUTED_ON_REACHABLE_WITNESS" if reachable_wide_found else "OPEN",
        "REACHABLE_SAME_PIVOT_W4_SAFETY": "REFUTED" if reachable_wide_found else "OPEN",
        "IMMEDIATE_BVE_CASE_ELIMINATED": False,
        "U_MU": "OPEN",
        "SAT_IN_P": "NOT_PROVED",
        "P_EQ_NP": "NOT_PROVED",
        "P_NE_NP": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "TRUMP_finished": False,
    }


def run():
    core = frozen_core_regression()
    reachable = replay_frozen_reachable()
    found = reachable["final_nonterminal_wide_states"] > 0
    verdict = (
        "EXPLICIT_REACHABLE_DOUBLE_WITNESS_CROWN_FIXPOINT_FOUND"
        if found
        else "BVE_FIXEDPOINT_DENSITY_AND_RUP_ESCAPE_CROWN_LEMMAS_CLOSED__FINAL_WIDE_OBSTRUCTION_REDUCED_TO_DOUBLE_WITNESS_CROWN_FIXPOINT__IMPOSSIBILITY_OPEN"
    )
    return {
        "gate": GATE,
        "mode": "SYMBOLIC_FIXEDPOINT_NECESSARY_CONDITIONS_WITH_FROZEN_REPLAY",
        "proved_from_frozen_source_definitions": [
            "S1_BVE_FIXED_IMPLIES_UNIQUE_NONTAUT_RESOLVENT_COUNT_GE_REMOVED_PARENT_COUNT",
            "S1_COROLLARY_EVERY_FIXEDPOINT_VARIABLE_HAS_POS_DEGREE_GE_2_AND_NEG_DEGREE_GE_2",
            "S2_EQUAL_RESOLVENT_COUNT_REJECTION_REQUIRES_STRICT_LITERAL_INFLATION_AND_NO_INHERITED_DUPLICATE",
            "S3_WIDE_LITERAL_OCCURRENCE_CROWN",
            "S4_DISTINCT_BCE_NONBLOCKING_SUPPORT_CROWN",
            "S5_RUP_FIXED_IMPLIES_CONFLICT_FREE_UP_RECEIPT_FOR_EVERY_SINGLE_LITERAL_DELETION",
        ],
        "critical_unproved_step": "NO_DP_OR_BVE_WIDE_ANCESTRY_CAN_TERMINATE_IN_A_NONTERMINAL_DOUBLE_WITNESS_CROWN_FIXPOINT_REACHABLE_FROM_A_PRE_BVE_CLEAN_W4_SOURCE",
        "frozen_fixed_core_regression": core,
        "reachable_replay": reachable,
        "verdict": verdict,
        "firewall": firewall(found),
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
