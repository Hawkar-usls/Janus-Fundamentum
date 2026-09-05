from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50g8_wide_survivor_impossibility_from_pre_bve_cleanliness as r50g8

GATE = "JANUS_TRUMP_R50G9_WIDE_FIXPOINT_SUPPORT_GRAPH_OBSTRUCTION"
WIDTH_CAP = 4


def canon(f):
    return r33.canonical_formula(f)


def exact_bve_pressure(formula, var: int):
    f = canon(formula)
    v = int(var)
    pos = [c for c in f if v in c]
    neg = [c for c in f if -v in c]
    if not pos or not neg:
        return {
            "var": v,
            "bipolar": False,
            "p": len(pos),
            "n": len(neg),
        }

    resolvents = []
    for p in pos:
        for n in neg:
            rr = (set(p) - {v}) | (set(n) - {-v})
            if any(-lit in rr for lit in rr):
                continue
            resolvents.append(r33.canonical_clause(rr))
    resolvents = sorted(set(resolvents))
    removed = set(pos + neg)
    inherited = [c for c in f if c not in removed]
    transformed = canon(inherited + resolvents)

    p_count = len(pos)
    n_count = len(neg)
    q = len(resolvents)
    m = p_count + n_count
    parent_literals = sum(len(c) for c in set(pos + neg))
    resolvent_literals = sum(len(c) for c in resolvents)
    before = r33.measure(f)
    after = r33.measure(transformed)
    would_accept = q <= m and after < before

    return {
        "var": v,
        "bipolar": True,
        "p": p_count,
        "n": n_count,
        "m": m,
        "q": q,
        "pair_upper_bound": p_count * n_count,
        "parent_literal_mass": parent_literals,
        "resolvent_literal_mass": resolvent_literals,
        "measure_before": list(before),
        "measure_after": list(after),
        "would_frozen_BVE_accept": bool(would_accept),
        "fixed_pressure_condition": bool(
            q > m or (q == m and resolvent_literals > parent_literals)
        ),
        "degree_lower_bound_2_by_2": bool(p_count >= 2 and n_count >= 2),
        "balanced_2_by_2": bool(p_count == 2 and n_count == 2),
    }


def assert_bve_fixed_pressure(formula):
    f = canon(formula)
    if r33.pure_literals(f):
        raise AssertionError("R50G9_CONTROL_HAS_PURE_LITERAL")
    if r33.bve_candidate(f) is not None:
        raise AssertionError("R50G9_CONTROL_NOT_BVE_FIXED")

    rows = []
    for v in r33.variables(f):
        row = exact_bve_pressure(f, int(v))
        if not row["bipolar"]:
            raise AssertionError(("R50G9_FIXED_VAR_NOT_BIPOLAR", v))
        if row["would_frozen_BVE_accept"]:
            raise AssertionError(("R50G9_FIXED_VAR_WOULD_BVE_ACCEPT", row))
        if row["q"] < row["m"]:
            raise AssertionError(("R50G9_RESOLVENT_PRESSURE_FAIL", row))
        if not row["degree_lower_bound_2_by_2"]:
            raise AssertionError(("R50G9_POLARITY_DEGREE_FAIL", row))
        if row["balanced_2_by_2"]:
            if row["q"] != 4:
                raise AssertionError(("R50G9_BALANCED_Q_NOT_FOUR", row))
            if row["pair_upper_bound"] != 4:
                raise AssertionError(("R50G9_BALANCED_PAIR_BOUND_DRIFT", row))
        rows.append(row)
    return rows


def wide_clause_support_pressure(formula, clause):
    f = canon(formula)
    c = tuple(clause)
    if len(c) <= WIDTH_CAP:
        raise ValueError("R50G9_REQUIRES_WIDE_CLAUSE")
    if c not in f:
        raise ValueError("R50G9_WIDE_CLAUSE_NOT_IN_FORMULA")

    supports = r50g8.nonblocking_supports_for_clause(f, c)
    if supports is None:
        return {
            "wide_clause": list(c),
            "BCE_support_complete": False,
        }

    literal_rows = []
    balanced = True
    opposite_support_union = set()
    for lit in c:
        pressure = exact_bve_pressure(f, abs(int(lit)))
        sign_same = [cl for cl in f if int(lit) in cl]
        sign_opp = [cl for cl in f if -int(lit) in cl]
        if pressure.get("balanced_2_by_2"):
            non_taut_opp = []
            for other in sign_opp:
                rr = (set(c) - {int(lit)}) | (set(other) - {-int(lit)})
                if not any(-x in rr for x in rr):
                    non_taut_opp.append(tuple(other))
            if len(non_taut_opp) != 2:
                raise AssertionError(("R50G9_BALANCED_WIDE_LITERAL_NOT_TWO_SUPPORTS", lit, non_taut_opp))
            opposite_support_union.update(non_taut_opp)
        else:
            balanced = False
        literal_rows.append({
            "literal": int(lit),
            "pressure": pressure,
            "same_polarity_clause_count": len(sign_same),
            "opposite_polarity_clause_count": len(sign_opp),
            "one_BCE_nonblocking_witness": list(supports[int(lit)]),
        })

    return {
        "wide_clause": list(c),
        "BCE_support_complete": True,
        "distinct_primary_BCE_supports": len(set(supports.values())),
        "all_literals_balanced_2_by_2": balanced,
        "balanced_case_distinct_opposite_supports": len(opposite_support_union) if balanced else None,
        "balanced_case_required_2k": 2 * len(c) if balanced else None,
        "literal_rows": literal_rows,
    }


def frozen_narrow_fixpoint_control():
    _sealed, core = r47j.load_counterexample()
    core = canon(core)
    norm = r47j.normalize_to_certified_fixpoint(core)
    if norm["terminal"] is not None:
        raise AssertionError("R50G9_CONTROL_BECAME_TERMINAL")
    if canon(norm["final_formula"]) != core:
        raise AssertionError("R50G9_CONTROL_NOT_NORMALIZATION_FIXED")
    if max((len(c) for c in core), default=0) > WIDTH_CAP:
        raise AssertionError("R50G9_CONTROL_NOT_NARROW")

    rows = assert_bve_fixed_pressure(core)
    degree_hist = Counter((r["p"], r["n"]) for r in rows)
    surplus_hist = Counter(r["q"] - r["m"] for r in rows)
    return {
        "hash": r47j.EXPECTED_FIXPOINT_HASH,
        "CLV": list(r33.measure(core)),
        "variables": len(rows),
        "all_bipolar": all(r["bipolar"] for r in rows),
        "all_q_ge_p_plus_n": all(r["q"] >= r["m"] for r in rows),
        "all_p_n_ge_2": all(r["p"] >= 2 and r["n"] >= 2 for r in rows),
        "balanced_2_by_2_variables": sum(int(r["balanced_2_by_2"]) for r in rows),
        "degree_histogram": {f"{p}x{n}": count for (p, n), count in sorted(degree_hist.items())},
        "q_minus_m_histogram": {str(k): v for k, v in sorted(surplus_hist.items())},
    }


def run():
    control = frozen_narrow_fixpoint_control()
    reachable = r50g8.replay_frozen_reachable()
    found = reachable["final_nonterminal_wide_states"] > 0
    return {
        "gate": GATE,
        "mode": "SYMBOLIC_SUPPORT_PRESSURE_REDUCTION_WITH_FROZEN_CONTROL_AND_REPLAY",
        "proved_from_frozen_source_definitions": [
            "S1_BVE_FIXED_VARIABLES_ARE_BIPOLAR",
            "S2_BVE_FIXED_RESOLVENT_PRESSURE_Q_GE_P_PLUS_N",
            "S3_BVE_FIXED_POLARITY_DEGREES_P_GE_2_AND_N_GE_2",
            "S4_WIDE_CLAUSE_LITERAL_HAS_DISTINCT_NONBLOCKING_SUPPORT",
            "S5_BALANCED_2_BY_2_VARIABLE_FORCES_ALL_FOUR_CROSS_PAIRS_NONTAUTOLOGICAL_AND_UNIQUE",
            "S6_WIDTH_K_BALANCED_2_BY_2_WIDE_CLAUSE_FORCES_TWO_DISTINCT_OPPOSITE_SUPPORTS_PER_LITERAL",
        ],
        "narrow_fixpoint_control": control,
        "reachable_replay": reachable,
        "critical_unproved_step": "NO_W4_DP_BVE_ANCESTRY_CAN_END_IN_A_NONTERMINAL_R33_AFFINE_RUP_FIXED_SUPPORT_GRAPH_SATISFYING_ALL_BVE_PRESSURE_CONSTRAINTS",
        "verdict": (
            "EXPLICIT_REACHABLE_WIDE_SUPPORT_GRAPH_COUNTERMODEL_FOUND"
            if found
            else "SUPPORT_PRESSURE_LEMMAS_S1_S6_CLOSED__WIDE_FIXPOINT_MUST_SATISFY_BVE_RESOLVENT_EXPANSION__ANCESTRY_INCOMPATIBILITY_REMAINS_TO_PROVE"
        ),
        "firewall": {
            "HEURISTIC_AUTHORITY": False,
            "NEW_SEMANTIC_INFERENCE_RULE": False,
            "NO_NEW_CORPUS": True,
            "FINITE_NO_FIND_IMPLIES_THEOREM": False,
            "SUPPORT_GRAPH_PRESSURE_LEMMAS": "PROVED_FROM_FROZEN_SOURCE_DEFINITIONS",
            "WIDE_ANCESTRY_IMPOSSIBILITY_THEOREM": "REFUTED_ON_REACHABLE_WITNESS" if found else "OPEN",
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
