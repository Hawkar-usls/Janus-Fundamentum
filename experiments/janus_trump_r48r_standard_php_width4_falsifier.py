from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m
import janus_trump_r48q_width4_full_frozen_frontier_falsifier as r48q

GATE = "JANUS_TRUMP_R48R_STANDARD_PHP_WIDTH4_FALSIFIER"
PHP_NS = (4, 5, 6, 7)
WIDTH_CAP = 4
SEALED_PHP4_HASH = "1553aa063ac6c771e7ac781fb69e5adafb056a1c20a8b157250565b03ed0ca64"
SEALED_PHP4_CLV = (40, 120, 15)


def canon(formula):
    return r33.canonical_formula(formula)


def clv(formula):
    return r33.measure(canon(formula))


def formula_hash(formula):
    return r47f.formula_hash(canon(formula))


def standard_php_3cnf(n: int):
    if n < 1:
        raise ValueError(n)
    next_var = 1
    p = {}
    for i in range(1, n + 2):
        for j in range(1, n + 1):
            p[(i, j)] = next_var
            next_var += 1
    y = {}
    for i in range(1, n + 2):
        for j in range(0, n + 1):
            y[(i, j)] = next_var
            next_var += 1

    clauses = []
    for i in range(1, n + 2):
        clauses.append((-y[(i, 0)],))
        for j in range(1, n + 1):
            clauses.append((y[(i, j - 1)], p[(i, j)], -y[(i, j)]))
        clauses.append((y[(i, n)],))

    for i in range(1, n + 2):
        for k in range(i + 1, n + 2):
            for j in range(1, n + 1):
                clauses.append((-p[(i, j)], -p[(k, j)]))

    f = canon(clauses)
    expected_p = n * (n + 1)
    expected_y = (n + 1) * (n + 1)
    expected_vars = expected_p + expected_y
    expected_ep_clauses = (n + 1) * (n + 2)
    expected_collision = n * ((n + 1) * n // 2)
    expected_clauses = expected_ep_clauses + expected_collision
    if len(r33.variables(f)) != expected_vars:
        raise AssertionError(("R48R_PHP_VAR_COUNT_DRIFT", n, len(r33.variables(f)), expected_vars))
    if len(f) != expected_clauses:
        raise AssertionError(("R48R_PHP_CLAUSE_COUNT_DRIFT", n, len(f), expected_clauses))
    if any(len(c) < 1 or len(c) > 3 for c in f):
        raise AssertionError(("R48R_NOT_3CNF", n))
    if any(len(set(abs(lit) for lit in c)) != len(c) for c in f):
        raise AssertionError(("R48R_REPEATED_VARIABLE_IN_CLAUSE", n))
    return f, {
        "n_holes": n,
        "n_pigeons": n + 1,
        "p_variables": expected_p,
        "extension_variables": expected_y,
        "total_variables": expected_vars,
        "EP_clauses": expected_ep_clauses,
        "collision_clauses": expected_collision,
        "total_clauses": expected_clauses,
    }


def normalize_source(source):
    result = r47m.normalize_full_existing_stack(source)
    final = canon(result["final_formula"])
    return result, final


def compact_width_result(row):
    out = {
        "covered": bool(row["covered"]),
        "root_hash": row["root_hash"],
        "root_CLV": row["root_CLV"],
        "root_max_width": int(row["root_max_width"]),
        "selected_pivots": [int(x["var"]) for x in row["selected_path"]],
        "selected_step_count": len(row["selected_path"]),
        "candidate_probe_count": int(row["candidate_probe_count"]),
        "max_persisted_width": int(row["max_persisted_width"]),
        "terminal": row["terminal"],
        "obstruction": None,
    }
    if row["obstruction"] is not None:
        o = row["obstruction"]
        out["obstruction"] = {
            "kind": o["kind"],
            "state_hash": o["state_hash"],
            "state_CLV": o["state_CLV"],
            "state_max_width": int(o["state_max_width"]),
            "state_index": o.get("state_index"),
        }
    return out


def run(output: Path | None = None):
    rows = []
    first_obstruction = None
    max_observed_persisted_width = 0
    normalized_nonterminal_count = 0
    preterminal_count = 0

    for n in PHP_NS:
        source, counts = standard_php_3cnf(n)
        source_hash = formula_hash(source)
        source_clv = list(clv(source))
        source_max_width = r48q.max_width(source)
        if source_max_width > 3:
            raise AssertionError(("R48R_SOURCE_WIDTH_DRIFT", n, source_max_width))

        norm, residual = normalize_source(source)
        if norm["semantic_sat"] is True:
            raise AssertionError(("R48R_PHP_FALSE_SAT_TERMINAL", n, norm["terminal"]))

        base_row = {
            **counts,
            "source_hash": source_hash,
            "source_CLV": source_clv,
            "source_max_width": source_max_width,
            "normalization_terminal": norm["terminal"],
            "normalization_semantic_sat": norm["semantic_sat"],
            "normalization_segment_count": int(norm["segment_count"]),
            "normalization_SA_BVE_application_count": int(norm["SA_BVE_application_count"]),
            "residual_hash": formula_hash(residual),
            "residual_CLV": list(clv(residual)),
            "residual_max_width": r48q.max_width(residual),
        }

        if n == 4:
            if norm["terminal"] is not None:
                raise AssertionError(("R48R_PHP4_LINEAGE_TERMINAL_DRIFT", norm["terminal"]))
            if formula_hash(residual) != SEALED_PHP4_HASH or clv(residual) != SEALED_PHP4_CLV:
                raise AssertionError(("R48R_PHP4_LINEAGE_HASH_OR_CLV_DRIFT", formula_hash(residual), clv(residual)))

        if norm["terminal"] is not None:
            preterminal_count += 1
            row = {
                **base_row,
                "classification": "CERTIFIED_PREPROJECTION_UNSAT_TERMINAL",
                "width4": None,
            }
            rows.append(row)
            continue

        normalized_nonterminal_count += 1
        width_result = r48q.run_width4_root(
            residual,
            {"family": "STANDARD_3CNF_PHP", "n_holes": n, "source_hash": source_hash},
        )
        compact = compact_width_result(width_result)
        max_observed_persisted_width = max(max_observed_persisted_width, compact["max_persisted_width"])
        if compact["terminal"] is not None and compact["terminal"].get("semantic_sat") is True:
            raise AssertionError(("R48R_PHP_WIDTH_CHAIN_FALSE_SAT", n, compact["terminal"]))
        row = {
            **base_row,
            "classification": (
                "WIDTH4_CHAIN_COVERED__FINITE_ONLY"
                if compact["covered"]
                else "EXPLICIT_REACHABLE_WIDTH4_OBSTRUCTION"
            ),
            "width4": compact,
        }
        rows.append(row)
        if not compact["covered"]:
            first_obstruction = {
                "n_holes": n,
                "n_pigeons": n + 1,
                "source_hash": source_hash,
                "source_CLV": source_clv,
                "residual_hash": base_row["residual_hash"],
                "residual_CLV": base_row["residual_CLV"],
                "residual_max_width": base_row["residual_max_width"],
                "obstruction": compact["obstruction"],
                "selected_pivots_before_obstruction": compact["selected_pivots"],
            }
            break

    verdict = (
        "EXPLICIT_STANDARD_PHP_WIDTH4_OBSTRUCTION_FOUND"
        if first_obstruction is not None
        else "FROZEN_PHP_4_TO_7_ALL_COVERED_BY_WIDTH4_OR_PRETERMINAL__FINITE_ONLY"
    )
    out = {
        "gate": GATE,
        "parent_R48Q_commit": "e0be53e0cf25ae92549cf0d4f93f0bcafb78b071",
        "sealed_R47AD_commit": "9293cfcede4e2c47264314f214dbdf270d98373f",
        "sealed_R47AE_commit": "4170b49160eb4f4bed82196b185368cab87be3c8",
        "family": "STANDARD_NONDETERMINISTIC_3CNF_PIGEONHOLE_EXTENSION_EPH_n^{n+1}",
        "frozen_n": list(PHP_NS),
        "W": WIDTH_CAP,
        "verdict": verdict,
        "rows": rows,
        "first_obstruction": first_obstruction,
        "metrics": {
            "members_evaluated": len(rows),
            "preprojection_terminal_members": preterminal_count,
            "nonterminal_normalized_roots_tested_by_width4": normalized_nonterminal_count,
            "max_observed_persisted_width": max_observed_persisted_width,
        },
        "interpretation": {
            "structured_family_finite_only": True,
            "bare_resolution_lower_bound_transfer_to_TRUMP": False,
            "full_frozen_success_proves_universal_W4": False,
            "one_W4_obstruction_refutes_only_universal_W4_for_this_frozen_width_policy": True,
            "one_W4_obstruction_refutes_every_polynomial_envelope": False,
        },
        "firewall": {
            "UNIVERSAL_CONSTANT_WIDTH_EXISTS": "NOT_PROVED",
            "UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE": "OPEN",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, sort_keys=True))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    run(args.output)


if __name__ == "__main__":
    main()
