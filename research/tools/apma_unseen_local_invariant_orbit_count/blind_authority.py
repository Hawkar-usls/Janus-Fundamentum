from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable


STAGE_A_FREEZE_PATH = Path(
    "research/TRUMP_APMA_UNSEEN_LOCAL_INVARIANT_STAGE_A_FREEZE_2026-09-16.json"
)
STAGE_B_DESIGN_PATH = Path(
    "research/TRUMP_APMA_UNSEEN_LOCAL_INVARIANT_STAGE_B_BLIND_AUTHORITY_DESIGN_2026-09-16.json"
)
PREREG_PATH = Path(
    "research/TRUMP_APMA_UNSEEN_LOCAL_INVARIANT_INDUCTION_FALSIFIER_GATE_PREREGISTRATION_2026-09-16.json"
)
STAGE_A_DESIGN_PATH = Path(
    "research/TRUMP_APMA_UNSEEN_LOCAL_INVARIANT_STAGE_A_DESIGN_2026-09-16.json"
)
CANDIDATE_PATH = Path(
    "research/tools/apma_unseen_local_invariant_orbit_count/candidate.py"
)
CHECKER_PATH = Path(
    "research/tools/apma_unseen_local_invariant_orbit_count/independent_checker.py"
)
STAGE_A_WORKFLOW_PATH = Path(
    ".github/workflows/trump-apma-unseen-local-invariant-stage-a.yml"
)

EXPECTED_BLOBS = {
    "stage_a_freeze": "57df060a6bcde5efef0ca4a2d2521c62e7208831",
    "stage_b_design": "14dd451aabe8f95ddbe0baab8847df0a77819ccb",
    "prereg": "5f02f06a920d838bca37f88c27c5053d7a606271",
    "stage_a_design": "bc6fedb8d8d7da8f17ccc53d30c8356745068ccd",
    "candidate": "a076cfc56d68aad0348415e313705da1f6b9cdcd",
    "checker": "0e12304d843ef0bcce6b6c032fd2af2c68abcd14",
    "stage_a_workflow": "f9dcf2f55ecbacbb493d23308e122e0480ce7705",
}

POSITIVE_REFERENCE_ID = "BLIND_POSITIVE_TRIPARTITE_EXACT1_4_5_6_V1"
NEGATIVE_REFERENCE_ID = "BLIND_NEGATIVE_ASYMMETRIC_EXACT1_H9_V1"
EXACT1_ROWS = ((0, 0, 1), (0, 1, 0), (1, 0, 0))
GROUP_A = (0, 1, 2, 3)
GROUP_B = (100, 101, 102, 103, 104)
GROUP_C = (200, 201, 202, 203, 204, 205)
NEGATIVE_VARIABLES = tuple(range(8))
NEGATIVE_EDGES = (
    (0, 1, 2),
    (0, 3, 4),
    (0, 5, 6),
    (1, 3, 5),
    (1, 4, 7),
    (2, 3, 7),
    (2, 4, 6),
    (3, 6, 7),
    (4, 5, 7),
)


class AuthorityError(RuntimeError):
    pass


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    h = hashlib.sha1()
    h.update(f"blob {len(data)}\0".encode("ascii"))
    h.update(data)
    return h.hexdigest()


def source_guard() -> dict[str, Any]:
    paths = {
        "stage_a_freeze": STAGE_A_FREEZE_PATH,
        "stage_b_design": STAGE_B_DESIGN_PATH,
        "prereg": PREREG_PATH,
        "stage_a_design": STAGE_A_DESIGN_PATH,
        "candidate": CANDIDATE_PATH,
        "checker": CHECKER_PATH,
        "stage_a_workflow": STAGE_A_WORKFLOW_PATH,
    }
    observed = {name: git_blob_sha1(path) for name, path in paths.items()}
    if observed != EXPECTED_BLOBS:
        raise AuthorityError(
            f"SOURCE_GUARD_MISMATCH expected={EXPECTED_BLOBS} observed={observed}"
        )
    return {
        "source_guard": True,
        "observed_blobs": observed,
        "candidate_imported": False,
        "checker_imported": False,
        "candidate_executed": False,
        "checker_executed": False,
    }


def positive_raw() -> dict[str, Any]:
    constraints: list[dict[str, Any]] = []
    ordinal = 0
    for a in GROUP_A:
        for b in GROUP_B:
            for c in GROUP_C:
                constraints.append(
                    {
                        "id": f"c{ordinal:04d}",
                        "scope": [a, b, c],
                        "allowed": [list(row) for row in EXACT1_ROWS],
                    }
                )
                ordinal += 1
    return {
        "variables": list(GROUP_A + GROUP_B + GROUP_C),
        "constraints": constraints,
    }


def negative_raw() -> dict[str, Any]:
    return {
        "variables": list(NEGATIVE_VARIABLES),
        "constraints": [
            {
                "id": f"c{i:04d}",
                "scope": list(edge),
                "allowed": [list(row) for row in EXACT1_ROWS],
            }
            for i, edge in enumerate(NEGATIVE_EDGES)
        ],
    }


def _canon_constraint(scope: Iterable[int], rows: Iterable[Iterable[int]]) -> tuple[Any, ...]:
    scope_list = list(scope)
    order = sorted(range(len(scope_list)), key=lambda i: scope_list[i])
    sorted_scope = tuple(scope_list[i] for i in order)
    canon_rows = {
        tuple(tuple(row)[i] for i in order)
        for row in rows
    }
    return sorted_scope, tuple(sorted(canon_rows))


def canonical_semantics(raw: dict[str, Any]) -> tuple[bytes, tuple[Any, ...]]:
    variables = tuple(sorted(int(v) for v in raw["variables"]))
    if len(set(variables)) != len(variables):
        raise AuthorityError("duplicate variable")
    keys = [
        _canon_constraint(c["scope"], c["allowed"])
        for c in raw["constraints"]
    ]
    keys.sort()
    serial = {
        "variables": list(variables),
        "constraints": [
            {"scope": list(scope), "allowed": [list(r) for r in rows]}
            for scope, rows in keys
        ],
    }
    data = json.dumps(serial, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return data, tuple(keys)


def semantic_sha256(raw: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_semantics(raw)[0]).hexdigest()


def raw_contract_clean(raw: dict[str, Any]) -> bool:
    if set(raw) != {"variables", "constraints"}:
        return False
    for c in raw["constraints"]:
        if not set(c).issubset({"id", "scope", "allowed"}):
            return False
        if "scope" not in c or "allowed" not in c:
            return False
    return True


def _and(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x & y for x, y in zip(a, b, strict=True))


def _or(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x | y for x, y in zip(a, b, strict=True))


def _maj(a: tuple[int, ...], b: tuple[int, ...], c: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(int(x + y + z >= 2) for x, y, z in zip(a, b, c, strict=True))


def _xor3(a: tuple[int, ...], b: tuple[int, ...], c: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x ^ y ^ z for x, y, z in zip(a, b, c, strict=True))


def schaefer_fingerprint(rows: tuple[tuple[int, ...], ...]) -> dict[str, bool]:
    allowed = set(rows)
    zero = tuple(0 for _ in rows[0]) in allowed
    one = tuple(1 for _ in rows[0]) in allowed
    horn = all(_and(a, b) in allowed for a in rows for b in rows)
    dual_horn = all(_or(a, b) in allowed for a in rows for b in rows)
    bijunctive = all(
        _maj(a, b, c) in allowed
        for a in rows
        for b in rows
        for c in rows
    )
    affine = all(
        _xor3(a, b, c) in allowed
        for a in rows
        for b in rows
        for c in rows
    )
    return {
        "ZERO_VALID": zero,
        "ONE_VALID": one,
        "HORN": horn,
        "DUAL_HORN": dual_horn,
        "BIJUNCTIVE": bijunctive,
        "AFFINE": affine,
    }


def connected_incidence(raw: dict[str, Any]) -> bool:
    variables = [int(v) for v in raw["variables"]]
    if not variables:
        return True
    adjacency = {v: set() for v in variables}
    for c in raw["constraints"]:
        scope = [int(v) for v in c["scope"]]
        for i, u in enumerate(scope):
            for v in scope[i + 1 :]:
                adjacency[u].add(v)
                adjacency[v].add(u)
    seen = {variables[0]}
    stack = [variables[0]]
    while stack:
        u = stack.pop()
        for v in adjacency[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen == set(variables)


def incidence_degrees(raw: dict[str, Any]) -> dict[int, int]:
    degree = {int(v): 0 for v in raw["variables"]}
    for c in raw["constraints"]:
        for v in c["scope"]:
            degree[int(v)] += 1
    return degree


def _swapped_formula_key(raw: dict[str, Any], u: int, v: int) -> tuple[Any, ...]:
    keys = []
    for c in raw["constraints"]:
        scope = [v if x == u else u if x == v else x for x in c["scope"]]
        keys.append(_canon_constraint(scope, c["allowed"]))
    keys.sort()
    return tuple(keys)


def transposition_automorphisms(raw: dict[str, Any]) -> list[tuple[int, int]]:
    _, base_key = canonical_semantics(raw)
    variables = sorted(int(v) for v in raw["variables"])
    out: list[tuple[int, int]] = []
    for i, u in enumerate(variables):
        for v in variables[i + 1 :]:
            if _swapped_formula_key(raw, u, v) == base_key:
                out.append((u, v))
    return out


def components_from_edges(
    variables: Iterable[int], edges: Iterable[tuple[int, int]]
) -> list[list[int]]:
    variables = sorted(int(v) for v in variables)
    adjacency = {v: set() for v in variables}
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    seen: set[int] = set()
    out: list[list[int]] = []
    for start in variables:
        if start in seen:
            continue
        seen.add(start)
        stack = [start]
        cell: list[int] = []
        while stack:
            u = stack.pop()
            cell.append(u)
            for v in sorted(adjacency[u], reverse=True):
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        out.append(sorted(cell))
    out.sort(key=lambda c: (c[0], len(c), c))
    return out


def quotient_q(cells: list[list[int]]) -> int:
    q = 1
    for cell in cells:
        q *= len(cell) + 1
    return q


def satisfies(raw: dict[str, Any], assignment: dict[int, int]) -> bool:
    for c in raw["constraints"]:
        row = tuple(assignment[int(v)] for v in c["scope"])
        if row not in {tuple(r) for r in c["allowed"]}:
            return False
    return True


def positive_reference_receipt(raw: dict[str, Any]) -> dict[str, Any]:
    if len(raw["constraints"]) != 120:
        raise AuthorityError("positive constraint count is not 120")
    expected_scopes = {
        (a, b, c)
        for a in GROUP_A
        for b in GROUP_B
        for c in GROUP_C
    }
    observed_scopes = {tuple(c["scope"]) for c in raw["constraints"]}
    if observed_scopes != expected_scopes:
        raise AuthorityError("positive is not complete A x B x C")
    if any(tuple(tuple(r) for r in c["allowed"]) != EXACT1_ROWS for c in raw["constraints"]):
        raise AuthorityError("positive relation rows differ from EXACT1")

    degrees = incidence_degrees(raw)
    if {degrees[v] for v in GROUP_A} != {30}:
        raise AuthorityError("A degree profile mismatch")
    if {degrees[v] for v in GROUP_B} != {24}:
        raise AuthorityError("B degree profile mismatch")
    if {degrees[v] for v in GROUP_C} != {20}:
        raise AuthorityError("C degree profile mismatch")

    assignments: list[dict[int, int]] = []
    for selected in ("A", "B", "C"):
        a: dict[int, int] = {}
        for v in GROUP_A:
            a[v] = int(selected == "A")
        for v in GROUP_B:
            a[v] = int(selected == "B")
        for v in GROUP_C:
            a[v] = int(selected == "C")
        if not satisfies(raw, a):
            raise AuthorityError(f"reference assignment {selected} does not satisfy raw formula")
        assignments.append(a)

    # Exactness is symbolic: completeness of A x B x C plus EXACT1 functionality
    # forces every pair of variables in each group equal under any satisfying assignment.
    # One representative cross-triple then leaves exactly the three group-bit EXACT1 states.
    for fixed_pair in ((0, 0), (0, 1), (1, 0), (1, 1)):
        possible_first = [
            row[0]
            for row in EXACT1_ROWS
            if (row[1], row[2]) == fixed_pair
        ]
        if len(possible_first) > 1:
            raise AuthorityError("EXACT1 is not functional in the first coordinate")
    for coordinate in (1, 2):
        other = [i for i in range(3) if i != coordinate]
        for fixed_pair in ((0, 0), (0, 1), (1, 0), (1, 1)):
            possible = [
                row[coordinate]
                for row in EXACT1_ROWS
                if (row[other[0]], row[other[1]]) == fixed_pair
            ]
            if len(possible) > 1:
                raise AuthorityError(f"EXACT1 is not functional in coordinate {coordinate}")

    edges = transposition_automorphisms(raw)
    cells = components_from_edges(raw["variables"], edges)
    sizes = sorted(len(c) for c in cells)
    if sizes != [4, 5, 6]:
        raise AuthorityError(f"positive orbit cell sizes mismatch: {sizes}")
    expected_cells = [list(GROUP_A), list(GROUP_B), list(GROUP_C)]
    if {tuple(c) for c in cells} != {tuple(c) for c in expected_cells}:
        raise AuthorityError(f"positive cells mismatch: {cells}")
    q = quotient_q(cells)
    if q != 210:
        raise AuthorityError(f"positive Q mismatch: {q}")

    expected_within = (
        len(GROUP_A) * (len(GROUP_A) - 1) // 2
        + len(GROUP_B) * (len(GROUP_B) - 1) // 2
        + len(GROUP_C) * (len(GROUP_C) - 1) // 2
    )
    if len(edges) != expected_within:
        raise AuthorityError(
            f"positive transposition count mismatch {len(edges)} != {expected_within}"
        )

    return {
        "complete_tripartite_scopes": True,
        "constraint_count": 120,
        "degree_profile": {
            "A": 30,
            "B": 24,
            "C": 20,
        },
        "group_constancy_reference_proof": True,
        "reference_satisfying_assignment_count": 3,
        "reference_assignments_replayed": 3,
        "transposition_automorphisms": len(edges),
        "cells": cells,
        "cell_sizes": sizes,
        "Q": q,
        "strict_compression": q < (1 << len(raw["variables"])),
        "full_variable_cube_enumerated": 0,
    }


def negative_reference_receipt(raw: dict[str, Any]) -> dict[str, Any]:
    if tuple(tuple(c["scope"]) for c in raw["constraints"]) != NEGATIVE_EDGES:
        raise AuthorityError("negative hyperedge list mismatch")
    if any(tuple(tuple(r) for r in c["allowed"]) != EXACT1_ROWS for c in raw["constraints"]):
        raise AuthorityError("negative relation rows differ from EXACT1")
    edges = transposition_automorphisms(raw)
    if edges:
        raise AuthorityError(f"negative has unexpected transposition automorphisms: {edges}")
    return {
        "constraint_count": len(raw["constraints"]),
        "pair_transpositions_tested": len(NEGATIVE_VARIABLES) * (len(NEGATIVE_VARIABLES) - 1) // 2,
        "exact_transposition_automorphisms": 0,
        "expected_stage_c_fail_closed_behavior": "OPEN_NO_NONTRIVIAL_EXCHANGEABILITY",
        "negative_truth_not_computed": True,
        "full_variable_cube_enumerated": 0,
    }


def source_nonreference_scan(
    positive_sha: str, negative_sha: str
) -> dict[str, Any]:
    forbidden_needles = [
        POSITIVE_REFERENCE_ID,
        NEGATIVE_REFERENCE_ID,
        positive_sha,
        negative_sha,
        "TRUMP_APMA_UNSEEN_LOCAL_INVARIANT_STAGE_B_BLIND_AUTHORITY_DESIGN_2026-09-16",
        "blind_authority.py",
    ]
    receipt: dict[str, Any] = {}
    for label, path in (("candidate", CANDIDATE_PATH), ("checker", CHECKER_PATH)):
        text = path.read_text(encoding="utf-8")
        hits = [needle for needle in forbidden_needles if needle in text]
        receipt[label] = {
            "clean": not hits,
            "hits": hits,
            "blob": git_blob_sha1(path),
        }
        if hits:
            raise AuthorityError(f"{label} source references Stage B authority: {hits}")
    return receipt


def reference_receipt() -> dict[str, Any]:
    guards = source_guard()
    positive = positive_raw()
    negative = negative_raw()
    if not raw_contract_clean(positive) or not raw_contract_clean(negative):
        raise AuthorityError("raw candidate input contract contains forbidden authority metadata")

    fingerprint = schaefer_fingerprint(EXACT1_ROWS)
    if any(fingerprint.values()):
        raise AuthorityError(f"EXACT1 unexpectedly admitted by fixed six: {fingerprint}")
    if not connected_incidence(positive):
        raise AuthorityError("positive incidence is disconnected")
    if not connected_incidence(negative):
        raise AuthorityError("negative incidence is disconnected")

    positive_sha = semantic_sha256(positive)
    negative_sha = semantic_sha256(negative)
    source_scan = source_nonreference_scan(positive_sha, negative_sha)
    positive_ref = positive_reference_receipt(positive)
    negative_ref = negative_reference_receipt(negative)

    checks = {
        "stage_a_source_blobs_unchanged": guards["source_guard"],
        "candidate_not_imported_or_executed": not guards["candidate_imported"] and not guards["candidate_executed"],
        "checker_not_imported_or_executed": not guards["checker_imported"] and not guards["checker_executed"],
        "positive_raw_contract_clean": raw_contract_clean(positive),
        "negative_raw_contract_clean": raw_contract_clean(negative),
        "exact1_outside_all_fixed_six": not any(fingerprint.values()),
        "positive_connected": connected_incidence(positive),
        "negative_connected": connected_incidence(negative),
        "positive_exact_three_solution_reference": positive_ref["reference_satisfying_assignment_count"] == 3,
        "positive_cells_4_5_6": positive_ref["cell_sizes"] == [4, 5, 6],
        "positive_Q_210": positive_ref["Q"] == 210,
        "negative_zero_exact_transpositions": negative_ref["exact_transposition_automorphisms"] == 0,
        "candidate_source_nonreference_scan_clean": source_scan["candidate"]["clean"],
        "checker_source_nonreference_scan_clean": source_scan["checker"]["clean"],
        "full_assignment_cube_enumeration_zero": positive_ref["full_variable_cube_enumerated"] == 0 and negative_ref["full_variable_cube_enumerated"] == 0,
    }
    if not all(checks.values()):
        raise AuthorityError(f"Stage B reference checks failed: {checks}")

    return {
        "stage": "B_BLIND_AUTHORITY_REFERENCE_ONLY",
        "authority": "BLIND_AUTHORITY_FREEZE_PREPARATION__NO_CANDIDATE_EXECUTION",
        "source_guards": guards,
        "raw_authorities": {
            "positive": {
                "reference_identifier": POSITIVE_REFERENCE_ID,
                "semantic_sha256": positive_sha,
                "variables": len(positive["variables"]),
                "constraints": len(positive["constraints"]),
            },
            "negative": {
                "reference_identifier": NEGATIVE_REFERENCE_ID,
                "semantic_sha256": negative_sha,
                "variables": len(negative["variables"]),
                "constraints": len(negative["constraints"]),
            },
        },
        "fixed_six_fingerprint": fingerprint,
        "positive_reference": positive_ref,
        "negative_reference": negative_ref,
        "source_nonreference_scan": source_scan,
        "checks": checks,
        "resource_receipt": {
            "candidate_executions": 0,
            "checker_executions": 0,
            "full_variable_cube_states_enumerated": 0,
            "reference_pair_transpositions_positive": len(positive["variables"]) * (len(positive["variables"]) - 1) // 2,
            "reference_pair_transpositions_negative": len(negative["variables"]) * (len(negative["variables"]) - 1) // 2,
        },
        "scientific_firewall": {
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE__STAGE_B_REFERENCE_ONLY",
            "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", choices=["positive", "negative"])
    parser.add_argument("--reference-receipt", action="store_true")
    args = parser.parse_args()
    if args.emit and args.reference_receipt:
        raise SystemExit("choose --emit or --reference-receipt")
    source_guard()
    if args.emit == "positive":
        out = positive_raw()
    elif args.emit == "negative":
        out = negative_raw()
    else:
        out = reference_receipt()
    print(json.dumps(out, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
