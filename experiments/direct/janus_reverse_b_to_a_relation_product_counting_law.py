#!/usr/bin/env python3
"""C025 reverse B->A exact relation-product counting law.

Goal
----
Derive a parametric proof object from RAW CNF without supplied pigeon/hole
labels, block ids, center ids, or block width.

The admitted CNF class is discovered and certified as an exact Cartesian
relation product:

  all-positive disjoint equal hyperedges              -> ROWS
  all-negative binary clauses within each row         -> EXACTLY-ONE local law
  cross-row negative relation vs canonical first row  -> UNIQUE PERFECT MATCHING
  consistency across every row pair                   -> COLUMNS
  reconstruct all clauses from ROW-ALO / ROW-AMO / COLUMN-AMO templates
  certify adjacent row and column transpositions      -> S_p x S_h
  derive counting invariant                           -> p selected row states,
                                                       each column capacity <= 1

If p > h, UNSAT follows by counting.  If p <= h, the verifier constructs and
checks an injective SAT witness.  The decision therefore applies only to CNFs
that pass exact structural replay; anything else fails closed as NOT_RECOGNIZED.

This is a polynomial recognizer/certificate for this exact relation-product CNF
class (including the standard pairwise pigeonhole encoding).  It is NOT an
arbitrary-SAT algorithm and says nothing by itself about P versus NP.
P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
from itertools import combinations
import json
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct.janus_php54_macro_restore_attack import pigeonhole


def negative_pair(a: int, b: int) -> base.Clause:
    out = base.canon_clause((-a, -b))
    assert out is not None
    return out


def rename_cnf(cnf: base.CNF, mapping: dict[int, int]) -> base.CNF:
    rows = []
    for clause in cnf:
        row = []
        for lit in clause:
            v = mapping.get(abs(lit), abs(lit))
            row.append(v if lit > 0 else -v)
        rows.append(row)
    return base.canon_cnf(rows)


def expected_from_grid(grid: tuple[tuple[int, ...], ...]) -> base.CNF:
    p = len(grid)
    if p == 0:
        raise AssertionError("EMPTY_GRID")
    h = len(grid[0])
    if h == 0 or any(len(row) != h for row in grid):
        raise AssertionError("NON_RECTANGULAR_GRID")

    clauses: list[tuple[int, ...]] = []
    for row in grid:
        clauses.append(tuple(row))
        for a, b in combinations(row, 2):
            clauses.append(negative_pair(a, b))

    for j in range(h):
        column = tuple(grid[i][j] for i in range(p))
        for a, b in combinations(column, 2):
            clauses.append(negative_pair(a, b))
    return base.canon_cnf(clauses)


def certify_product_symmetry(cnf: base.CNF, grid: tuple[tuple[int, ...], ...]):
    p = len(grid)
    h = len(grid[0])
    row_generators = []
    for i in range(p - 1):
        mapping = {}
        for j in range(h):
            mapping[grid[i][j]] = grid[i + 1][j]
            mapping[grid[i + 1][j]] = grid[i][j]
        ok = rename_cnf(cnf, mapping) == cnf
        row_generators.append({"swap": [i, i + 1], "preserves_cnf": ok})
        if not ok:
            raise AssertionError(f"ROW_ADJACENT_SWAP_{i}_{i+1}_FAILED")

    column_generators = []
    for j in range(h - 1):
        mapping = {}
        for i in range(p):
            mapping[grid[i][j]] = grid[i][j + 1]
            mapping[grid[i][j + 1]] = grid[i][j]
        ok = rename_cnf(cnf, mapping) == cnf
        column_generators.append({"swap": [j, j + 1], "preserves_cnf": ok})
        if not ok:
            raise AssertionError(f"COLUMN_ADJACENT_SWAP_{j}_{j+1}_FAILED")
    return row_generators, column_generators


def infer_relation_product(raw_clauses) -> dict:
    cnf = base.canon_cnf(raw_clauses)
    variables = base.vars_of(cnf)
    if not cnf or not variables:
        raise AssertionError("EMPTY_INPUT")

    positive = [c for c in cnf if c and all(lit > 0 for lit in c)]
    negative = [c for c in cnf if c and all(lit < 0 for lit in c)]
    if len(positive) + len(negative) != len(cnf):
        raise AssertionError("MIXED_POLARITY_CLAUSE_NOT_IN_RELATION_PRODUCT_GRAMMAR")
    if not positive or any(len(c) != 2 for c in negative):
        raise AssertionError("RELATION_PRODUCT_POLARITY_WIDTH_SHAPE_FAILED")

    rows = tuple(sorted((tuple(sorted(c)) for c in positive)))
    row_sizes = {len(row) for row in rows}
    if len(row_sizes) != 1:
        raise AssertionError("UNEQUAL_POSITIVE_ROW_WIDTHS")
    h = next(iter(row_sizes))
    p = len(rows)
    if h < 2 or p < 2:
        raise AssertionError("DEGENERATE_RELATION_PRODUCT")

    flattened = tuple(v for row in rows for v in row)
    if len(flattened) != len(set(flattened)):
        raise AssertionError("POSITIVE_ROWS_OVERLAP")
    if set(flattened) != set(variables):
        raise AssertionError("POSITIVE_ROWS_DO_NOT_COVER_ALL_VARIABLES")

    negative_pairs = {
        tuple(sorted((abs(c[0]), abs(c[1]))))
        for c in negative
    }

    # Each positive row is ALO; the complete negative clique makes it AMO too.
    for row in rows:
        for a, b in combinations(row, 2):
            if tuple(sorted((a, b))) not in negative_pairs:
                raise AssertionError("ROW_EXACTLY_ONE_CLIQUE_INCOMPLETE")

    # Infer the second coordinate without labels.  The lexicographically first
    # positive row is merely a canonical gauge.  Cross-negative edges to every
    # other row must be a unique perfect matching.
    anchor = rows[0]
    aligned_rows = [anchor]
    alignment_certificate = []
    for row_index, row in enumerate(rows[1:], start=1):
        matched = []
        used = set()
        for anchor_var in anchor:
            hits = [
                v for v in row
                if tuple(sorted((anchor_var, v))) in negative_pairs
            ]
            if len(hits) != 1:
                raise AssertionError(
                    f"ANCHOR_CROSS_RELATION_NOT_UNIQUE_PERFECT_MATCHING_ROW={row_index}"
                )
            v = hits[0]
            if v in used:
                raise AssertionError("ANCHOR_CROSS_RELATION_NOT_BIJECTIVE")
            used.add(v)
            matched.append(v)
        if len(used) != h:
            raise AssertionError("ANCHOR_CROSS_RELATION_NOT_SURJECTIVE")
        aligned_rows.append(tuple(matched))
        alignment_certificate.append({
            "row_index": row_index,
            "anchor_to_row": [[anchor[j], matched[j]] for j in range(h)],
        })

    grid = tuple(aligned_rows)
    columns = tuple(tuple(grid[i][j] for i in range(p)) for j in range(h))

    # Exact replay is the semantic admission gate.  It simultaneously checks
    # all non-anchor row-pair consistency and rejects missing/extra clauses.
    rebuilt = expected_from_grid(grid)
    if rebuilt != cnf:
        missing = sorted(set(cnf) - set(rebuilt), key=lambda c: (len(c), c))
        extra = sorted(set(rebuilt) - set(cnf), key=lambda c: (len(c), c))
        raise AssertionError(
            f"RELATION_PRODUCT_EXACT_REPLAY_FAILED missing={missing[:4]} extra={extra[:4]}"
        )

    row_generators, column_generators = certify_product_symmetry(cnf, grid)

    # Exactly-one semantics gives h local states per row without enumerating 2^h:
    # the single chosen column index.  The global capacity law is one selected
    # row state per row and at most one use of each column.
    w = h
    k = p
    q = h
    template_count = 3  # ROW_ALO, ROW_AMO, COLUMN_AMO
    row_histogram_count = comb(k + q - 1, q - 1)

    status = "UNSAT" if p > h else "SAT"
    witness = None
    if status == "SAT":
        assignment = {v: 0 for v in variables}
        for i in range(p):
            assignment[grid[i][i]] = 1
        if not base.verify_total_assignment(cnf, assignment):
            raise AssertionError("CONSTRUCTED_INJECTION_WITNESS_FAILED")
        witness = dict(sorted(assignment.items()))

    certificate = {
        "kind": "EXACT_RELATION_PRODUCT_COUNTING_CERTIFICATE",
        "source_fingerprint": base.fingerprint(cnf),
        "rows": [list(row) for row in grid],
        "columns": [list(column) for column in columns],
        "p": p,
        "h": h,
        "w": w,
        "k": k,
        "q": q,
        "template_program": ["ROW_ALO", "ROW_AMO", "COLUMN_AMO"],
        "template_count": template_count,
        "row_histogram_count_if_materialized": row_histogram_count,
        "symmetry_group_generators": {
            "row_adjacent_transpositions_generate": f"S_{p}",
            "column_adjacent_transpositions_generate": f"S_{h}",
            "row_generators": row_generators,
            "column_generators": column_generators,
        },
        "counting_invariant": {
            "required_exactly_one_row_selections": p,
            "available_columns": h,
            "capacity_per_column": 1,
            "necessary_condition_for_sat": "p <= h",
            "observed_relation": "p > h" if p > h else "p <= h",
        },
        "decision": status,
        "witness": witness,
        "alignment_certificate": alignment_certificate,
        "exact_clause_replay": True,
    }
    return certificate


def verify_relation_product_certificate(raw_clauses, certificate: dict) -> bool:
    """Independent verifier: never calls the producer/inference routine."""
    try:
        cnf = base.canon_cnf(raw_clauses)
        if certificate.get("kind") != "EXACT_RELATION_PRODUCT_COUNTING_CERTIFICATE":
            return False
        if certificate.get("source_fingerprint") != base.fingerprint(cnf):
            return False

        grid = tuple(tuple(int(v) for v in row) for row in certificate["rows"])
        if not grid or not grid[0]:
            return False
        p = len(grid)
        h = len(grid[0])
        if any(len(row) != h for row in grid):
            return False
        flattened = [v for row in grid for v in row]
        if len(flattened) != len(set(flattened)):
            return False
        if set(flattened) != set(base.vars_of(cnf)):
            return False

        columns = tuple(tuple(grid[i][j] for i in range(p)) for j in range(h))
        supplied_columns = tuple(tuple(int(v) for v in col) for col in certificate["columns"])
        if columns != supplied_columns:
            return False
        if base.canon_cnf(expected_from_grid(grid)) != cnf:
            return False

        if int(certificate["p"]) != p or int(certificate["h"]) != h:
            return False
        if int(certificate["w"]) != h:
            return False
        if int(certificate["k"]) != p:
            return False
        if int(certificate["q"]) != h:
            return False
        if list(certificate["template_program"]) != ["ROW_ALO", "ROW_AMO", "COLUMN_AMO"]:
            return False
        if int(certificate["template_count"]) != 3:
            return False
        if int(certificate["row_histogram_count_if_materialized"]) != comb(p + h - 1, h - 1):
            return False

        # Independently replay the claimed generators.
        certify_product_symmetry(cnf, grid)

        decision = certificate["decision"]
        if p > h:
            if decision != "UNSAT" or certificate.get("witness") is not None:
                return False
            # Pigeonhole/counting proof: p exactly-one row selections must map
            # injectively into h capacity-one columns.  p>h is impossible.
            return True

        if decision != "SAT":
            return False
        witness = {int(v): int(bit) for v, bit in certificate["witness"].items()}
        return base.verify_total_assignment(cnf, witness)
    except (AssertionError, KeyError, TypeError, ValueError):
        return False


def training_case(p: int, h: int) -> dict:
    raw = pigeonhole(p, h)
    cert = infer_relation_product(raw)
    verified = verify_relation_product_certificate(raw, cert)
    if not verified:
        raise AssertionError(f"INDEPENDENT_PRODUCT_VERIFIER_FAILED_PHP_{p}_{h}")
    expected_clauses = p + p * comb(h, 2) + h * comb(p, 2)
    if len(base.canon_cnf(raw)) != expected_clauses:
        raise AssertionError("CLAUSE_COUNT_FORMULA_DRIFT")
    return {
        "case": f"PHP_{p}_{h}",
        "inferred_without_coordinate_labels": {
            "p": cert["p"],
            "h": cert["h"],
            "w": cert["w"],
            "k": cert["k"],
            "q": cert["q"],
            "template_count": cert["template_count"],
            "row_histogram_count_if_materialized": cert["row_histogram_count_if_materialized"],
        },
        "raw_variables": p * h,
        "raw_clauses": expected_clauses,
        "source_fingerprint": cert["source_fingerprint"],
        "exact_clause_replay": cert["exact_clause_replay"],
        "independent_certificate_verifier": verified,
        "decision": cert["decision"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="5:4,6:5,7:6")
    args = ap.parse_args()
    requested = []
    for token in args.cases.split(","):
        p, h = (int(x) for x in token.split(":"))
        requested.append((p, h))

    rows = [training_case(p, h) for p, h in requested]
    report = {
        "schema": "JANUS/C025/REVERSE-B-TO-A-RELATION-PRODUCT-COUNTING-LAW/v1",
        "direction": "B_TO_A",
        "training_rows": rows,
        "derived_parametric_law": {
            "scope": "ANY_CNF_EXACTLY_ADMITTED_BY_THE_RELATION_PRODUCT_REPLAY_VERIFIER",
            "parameters": {
                "p": "NUMBER_OF_DISCOVERED_DISJOINT_EQUAL_POSITIVE_ROWS",
                "h": "DISCOVERED_ROW_WIDTH_AND_NUMBER_OF_MATCHED_COLUMNS",
                "w": "h",
                "k": "p",
                "q": "h",
                "templates": 3,
                "template_program": ["ROW_ALO", "ROW_AMO", "COLUMN_AMO"],
                "symmetry": "S_p_X_S_h"
            },
            "decision_law": {
                "UNSAT_if": "p > h",
                "SAT_if": "p <= h",
                "reason": "EXACTLY_ONE_SELECTION_PER_ROW_PLUS_AT_MOST_ONE_SELECTION_PER_COLUMN"
            },
            "standard_PHP_m_plus_1_m_specialization": {
                "p": "m+1",
                "h": "m",
                "w": "m",
                "k": "m+1",
                "q": "m",
                "templates": 3,
                "decision": "UNSAT"
            },
            "law_source": "STRUCTURAL_CERTIFICATE_SCHEMA_NOT_NUMERICAL_CURVE_FIT"
        },
        "complexity_ledger": {
            "certificate_size": "O(V+C)",
            "exact_replay_verification": "POLYNOMIAL_IN_EXPLICIT_CNF_SIZE",
            "pair_relation_alignment": "POLYNOMIAL_IN_EXPLICIT_CNF_SIZE",
            "adjacent_generator_replay_count": "p+h-2",
            "histogram_enumeration_required_for_decision": false,
            "exponential_assignment_enumeration_required_for_decision": false,
            "counting_certificate": "p,h_AND_EXACT_PRODUCT_REPLAY"
        },
        "holdout_policy": {
            "PHP_8_7": "NOT_RUN_IN_THIS_TRAINING_COMMIT",
            "next_action": "FREEZE_EXACT_PHP_8_7_PREDICTION_FROM_THE_DERIVED_LAW_BEFORE_ANY_HOLDOUT_EXECUTION"
        },
        "scientific_boundary": {
            "theorem_scope": "EXACT_RECOGNIZED_RELATION_PRODUCT_CNF_CLASS",
            "standard_pairwise_PHP_family_is_in_scope": true,
            "general_CNF": "NOT_IN_SCOPE",
            "arbitrary_SAT": "OPEN",
            "P_VS_NP": "OPEN"
        },
        "P_VS_NP": "OPEN"
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
