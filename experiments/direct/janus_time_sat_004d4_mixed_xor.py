#!/usr/bin/env python3
"""TIME-SAT-004D4: sound partial-XOR extraction from bounded mixed CNF.

Research-only. Preserve every original clause: complete source-derived parity
blocks become XOR equations; all unconsumed clauses are retained verbatim.
This is a representation-equivalence transformation, NOT a general speedup.
SAT models are rechecked against ALL original clauses. Native-solver UNSAT
has no portable certificate here and is explicitly labelled SOLVER_ONLY.
"""
from __future__ import annotations

from hashlib import sha256
import json

from janus_time_sat_004d1_xor import (
    MAX_N, MAX_ROWS, MAX_LITERALS, MAX_GROUPS, MAX_WIDTH,
    check_original_cnf, source_digest,
)


def extract_mixed_xor(rows, n):
    """Find complete XOR sign-mask blocks while retaining every other clause.

    Each selected block contains exactly one original clause for each
    falsifying assignment with parity p. It is equivalent to XOR(vars)=1^p.
    Other parities, incomplete blocks, duplicates, wide clauses, tautologies,
    and empty clauses remain in the residual CNF. No synthetic CNF is dropped.
    """
    if type(n) is not int or not 1 <= n <= MAX_N:
        return {"status": "ABSTAIN_INVALID_N"}
    if len(rows) > MAX_ROWS:
        return {"status": "ABSTAIN_ROW_BUDGET"}
    by_support = {}
    literals = 0
    for index, row in enumerate(rows):
        literals += len(row)
        if literals > MAX_LITERALS:
            return {"status": "ABSTAIN_LITERAL_BUDGET"}
        if any(type(v) is not int or not 1 <= abs(v) <= n for v in row):
            return {"status": "ABSTAIN_INVALID_LITERAL"}
        if not 1 <= len(row) <= MAX_WIDTH:
            continue  # retained in residual
        support = tuple(sorted(abs(v) for v in row))
        if len(set(support)) != len(support):
            continue  # repeated-variable/tautological clause retained
        if support not in by_support and len(by_support) >= MAX_GROUPS:
            return {"status": "ABSTAIN_GROUP_BUDGET"}
        signs = by_support.setdefault(support, {})
        negated = {abs(v) for v in row if v < 0}
        mask = sum(1 << i for i, v in enumerate(support) if v in negated)
        signs.setdefault(mask, []).append(index)

    equations = []
    consumed = set()
    for support, signs in sorted(by_support.items()):
        width = len(support)
        for parity in (0, 1):
            masks = [m for m in range(1 << width) if m.bit_count() % 2 == parity]
            if not all(m in signs for m in masks):
                continue
            indices = [signs[m][0] for m in masks]  # duplicates retained
            if any(i in consumed for i in indices):
                raise AssertionError("Overlapping source clause allocation")
            # Source-derived syntactic check independent of SAT search.
            for m, i in zip(masks, indices):
                actual = rows[i]
                expected = {(-v if (m >> k) & 1 else v)
                            for k, v in enumerate(support)}
                if len(actual) != len(support) or set(actual) != expected:
                    raise AssertionError("XOR block does not match original CNF")
            consumed.update(indices)
            equations.append({
                "variables": list(support),
                "rhs": 1 ^ parity,
                "original_clause_indices": indices,
            })

    residual_indices = [i for i in range(len(rows)) if i not in consumed]
    if len(consumed) + len(residual_indices) != len(rows):
        raise AssertionError("Lost source clause")
    return {
        "schema": "JANUS-TIME-SAT-004D4-MIXED-XOR-LOSSLESS-V1",
        "status": "SOURCE_PARTITION_VERIFIED",
        "source_n": n,
        "source_clauses": len(rows),
        "source_logical_sha256": source_digest(rows, n),
        "equations": equations,
        "xor_source_clause_indices": sorted(consumed),
        "residual_source_clause_indices": residual_indices,
        "residual_clauses": [list(rows[i]) for i in residual_indices],
        "complete_xor_equation_count": len(equations),
        "source_xor_clauses": len(consumed),
        "source_residual_clauses": len(residual_indices),
        "source_original_clauses_unmodified": True,
        "no_hidden_holdout_or_speed_claim": True,
        "external_witness": "NOT_PERFORMED",
        "production_C023": "UNCHANGED",
    }


def representation_satisfied(partition, values):
    """Reference truth evaluator for tests: extracted XOR + residual."""
    return (all(
        (sum(int(values[v]) for v in eq["variables"]) & 1) == eq["rhs"]
        for eq in partition["equations"]
    ) and all(
        any(bool(values[abs(v)]) == (v > 0) for v in clause)
        for clause in partition["residual_clauses"]
    ))


def solve_mixed_native(rows, n):
    """Run native XOR+CNF only after source proof; abstain on missing solver.

    UNSAT from a solver is not a verified portable proof. A dedicated
    independent proof checker is required before upgrading that claim.
    """
    p = extract_mixed_xor(rows, n)
    if p["status"] != "SOURCE_PARTITION_VERIFIED":
        return {"verdict": "ABSTAIN_NO_CLAIM", "structural_status": p["status"]}
    result = {
        "schema": "JANUS-TIME-SAT-004D4-MIXED-NATIVE-RESEARCH-V1",
        "structural_status": p["status"],
        "original_logical_sha256": p["source_logical_sha256"],
        "native_xor_equations": len(p["equations"]),
        "original_residual_clauses": len(p["residual_clauses"]),
        "external_admin_witness": "NOT_PERFORMED",
        "production_C023": "UNCHANGED",
    }
    if not p["equations"]:
        result["verdict"] = "ABSTAIN_NO_COMPLETE_XOR_BLOCK"
        return result
    try:
        import pycryptosat
    except ImportError:
        result["verdict"] = "ABSTAIN_NATIVE_SOLVER_NOT_INSTALLED"
        return result
    solver = pycryptosat.Solver(threads=1)
    for eq in p["equations"]:
        solver.add_xor_clause(eq["variables"], bool(eq["rhs"]))
    for clause in p["residual_clauses"]:
        solver.add_clause(clause)
    sat, model = solver.solve()
    if sat is True:
        if model is None or len(model) <= n:
            raise AssertionError("Incomplete native SAT model")
        assignment = [bool(model[i]) for i in range(1, n + 1)]
        bits = sum(1 << i for i, value in enumerate(assignment) if value)
        if not check_original_cnf(rows, n, bits):
            raise AssertionError("Native SAT model fails ORIGINAL source CNF")
        result["verdict"] = "SAT_ORIGINAL_MODEL_VERIFIED"
        result["model"] = [i if assignment[i - 1] else -i
                           for i in range(1, n + 1)]
    elif sat is False:
        result["verdict"] = "UNSAT_SOLVER_ONLY_NO_PORTABLE_CERTIFICATE"
        result["portable_DRUP_LRAT"] = "NOT_PRODUCED"
    else:
        result["verdict"] = "UNKNOWN_NO_SAT_UNSAT_CLAIM"
    return result
