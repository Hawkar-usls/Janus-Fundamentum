#!/usr/bin/env python3
"""JANUS TIME-SAT-004D4D: complete supported-sign-mask coverage by paging.

Research-only, source-preserving. Each pass indexes at most max_groups
distinct variable supports. All source clauses for a selected support are
handled in that pass; any support that could not enter the index is retried
in a later pass. All unselected clauses stay verbatim residual CNF.

A complete source sign-mask class yields an XOR equation by propositional
equivalence. This does not prove arbitrary implicit parity absent and does
not solve SAT or certify UNSAT. No persistent growth in support-index cap.
"""
from __future__ import annotations

from janus_time_sat_004d1_xor import (
    MAX_N, MAX_ROWS, MAX_LITERALS, MAX_GROUPS, MAX_WIDTH, source_digest
)


def extract_paged_mixed_xor(rows, n, *, max_groups=MAX_GROUPS):
    if type(n) is not int or not 1 <= n <= MAX_N:
        return {"status": "ABSTAIN_INVALID_N"}
    if type(max_groups) is not int or not 1 <= max_groups <= MAX_GROUPS:
        return {"status": "ABSTAIN_INVALID_SUPPORT_BUDGET"}
    if len(rows) > MAX_ROWS:
        return {"status": "ABSTAIN_ROW_BUDGET"}

    scanned_literals = 0
    eligible = []
    unsupported = 0
    for i, row in enumerate(rows):
        scanned_literals += len(row)
        if scanned_literals > MAX_LITERALS:
            return {"status": "ABSTAIN_LITERAL_BUDGET"}
        if any(type(lit) is not int or not 1 <= abs(lit) <= n for lit in row):
            return {"status": "ABSTAIN_INVALID_LITERAL"}
        if not 1 <= len(row) <= MAX_WIDTH:
            unsupported += 1
            continue
        if len({abs(lit) for lit in row}) != len(row):
            unsupported += 1
            continue
        eligible.append(i)

    pending = eligible
    consumed = set()
    equations = []
    page_stats = []
    first_skipped = 0
    # Progress invariant: every non-final page admits max_groups new
    # distinct supports, so max pages <= ceil(len(eligible)/max_groups).
    while pending:
        previous = len(pending)
        indexed = {}
        skipped = []
        for index in pending:
            row = rows[index]
            support = tuple(sorted(abs(lit) for lit in row))
            if support not in indexed:
                if len(indexed) == max_groups:
                    skipped.append(index)
                    continue
                indexed[support] = {}
            negated = {abs(lit) for lit in row if lit < 0}
            mask = sum(1 << j for j, variable in enumerate(support)
                       if variable in negated)
            indexed[support].setdefault(mask, []).append(index)

        if not page_stats:
            first_skipped = len(skipped)
        page_equations = 0
        page_extracted_clauses = 0
        for support, masks_to_indices in sorted(indexed.items()):
            for p in (0, 1):
                complete_masks = [
                    mask for mask in range(1 << len(support))
                    if mask.bit_count() % 2 == p
                ]
                if not all(mask in masks_to_indices for mask in complete_masks):
                    continue
                indices = [masks_to_indices[mask][0] for mask in complete_masks]
                if any(index in consumed for index in indices):
                    raise AssertionError("source clause reused in parity equation")
                for mask, index in zip(complete_masks, indices):
                    expected = {
                        (-variable if (mask >> j) & 1 else variable)
                        for j, variable in enumerate(support)
                    }
                    if len(rows[index]) != len(support) or set(rows[index]) != expected:
                        raise AssertionError("equation not implied by original source block")
                consumed.update(indices)
                page_extracted_clauses += len(indices)
                page_equations += 1
                equations.append({
                    "variables": list(support), "rhs": 1 ^ p,
                    "original_clause_indices": indices,
                })
        page_stats.append({
            "page": len(page_stats) + 1,
            "candidate_clause_rows": previous,
            "indexed_unique_supports": len(indexed),
            "unindexed_rows_forwarded": len(skipped),
            "xor_equations": page_equations,
            "xor_source_clauses": page_extracted_clauses,
        })
        if skipped and len(indexed) != max_groups:
            raise AssertionError("nonprogressing partial support page")
        if len(skipped) >= previous:
            raise AssertionError("support scan did not make progress")
        pending = skipped
        # Previous indexed dict goes out of scope before next page is built.
        # No page-to-page support union is constructed.

    source_indices = sorted(consumed)
    residual_indices = [i for i in range(len(rows)) if i not in consumed]
    if sorted(source_indices + residual_indices) != list(range(len(rows))):
        raise AssertionError("source indices not exactly partitioned")
    if len(source_indices) != sum(len(eq["original_clause_indices"])
                                  for eq in equations):
        raise AssertionError("source equation overlaps")
    if sum(x["xor_equations"] for x in page_stats) != len(equations):
        raise AssertionError("page equation count mismatch")

    return {
        "schema": "JANUS-TIME-SAT-004D4D-PAGED-LOSSLESS-XOR-COVER-V1",
        "status": "SOURCE_PARTITION_VERIFIED",
        "source_n": n,
        "source_clauses": len(rows),
        "source_logical_sha256": source_digest(rows, n),
        "complete_xor_equation_count": len(equations),
        "equations": equations,
        "xor_source_clause_indices": source_indices,
        "residual_source_clause_indices": residual_indices,
        "residual_clauses": [list(rows[i]) for i in residual_indices],
        "source_xor_clauses": len(source_indices),
        "source_residual_clauses": len(residual_indices),
        "indexed_support_limit_per_page": max_groups,
        "page_count": len(page_stats),
        "page_stats": page_stats,
        "first_page_unindexed_source_clause_rows": first_skipped,
        "eligible_original_clause_rows": len(eligible),
        "unsupported_or_repeated_clause_rows": unsupported,
        "exhaustive_supported_sign_mask_coverage": True,
        "scope_of_zero_yield": "NO_EXPLICIT_COMPLETE_SOURCE_SIGN_MASK_XOR_WITH_WIDTH_LE_6",
        "no_implicit_xor_absence_claim": True,
        "SAT_or_UNSAT": "NOT_ATTEMPTED_SOURCE_ONLY",
        "original_clauses_unmodified": True,
        "external_witness": "NOT_PERFORMED",
        "production_C023": "UNCHANGED",
    }
