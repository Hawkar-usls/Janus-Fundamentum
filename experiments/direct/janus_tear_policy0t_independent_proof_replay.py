#!/usr/bin/env python3
"""Independently replay serialized proofs emitted by the C022 translator.

The checker deliberately does not call ResolutionProof.verify or the
translator's resolve_clauses helper.  It consumes primitive dictionaries and
contains negative controls that must reject corrupted certificates.
"""

from __future__ import annotations

import copy
import random
from itertools import combinations, product
from typing import Iterable

from janus_tear_policy0t_random_translation_fuzz import clause_pool, is_unsat
from janus_tear_policy0t_recursive_trace_translator import TraceTranslator
from janus_tear_policy0t_recursive_translator_fuzz import CASES
from janus_tear_policy0t_trace_certificate import (
    TracePolicy,
    UNSAT_FORMULA,
    canonical_cnf,
    verify_trace,
    visible_affine_root_decision,
)

Clause = tuple[int, ...]
CertificateLine = dict[str, object]


def normalize_clause(values: Iterable[int]) -> Clause:
    literals = set(int(value) for value in values)
    if 0 in literals:
        raise ValueError("literal zero is illegal")
    if any(-literal in literals for literal in literals):
        raise ValueError("tautological clause is illegal in certificate")
    return tuple(sorted(literals, key=lambda literal: (abs(literal), literal < 0)))


def independent_resolve(left: Clause, right: Clause, pivot: int) -> Clause:
    if pivot <= 0:
        raise ValueError("pivot must be a positive variable index")
    if pivot in left and -pivot in right:
        merged = (set(left) - {pivot}) | (set(right) - {-pivot})
    elif -pivot in left and pivot in right:
        merged = (set(left) - {-pivot}) | (set(right) - {pivot})
    else:
        raise ValueError("parents do not contain complementary pivot literals")
    return normalize_clause(merged)


def serialize_proof(lines) -> list[CertificateLine]:
    certificate: list[CertificateLine] = []
    for line in lines:
        if hasattr(line, "left"):
            certificate.append(
                {
                    "kind": "resolution",
                    "clause": list(line.clause),
                    "left": int(line.left),
                    "right": int(line.right),
                    "pivot": int(line.pivot),
                }
            )
        else:
            certificate.append(
                {"kind": "axiom", "clause": list(line.clause)}
            )
    return certificate


def check_certificate(root, certificate: list[CertificateLine]) -> tuple[int, int, int]:
    root_axioms = {normalize_clause(clause) for clause in root}
    clauses: list[Clause] = []
    depths: list[int] = []
    resolution_lines = 0

    if not certificate:
        raise ValueError("empty certificate")

    for index, raw in enumerate(certificate):
        kind = raw.get("kind")
        clause = normalize_clause(raw.get("clause", []))

        if kind == "axiom":
            if set(raw) != {"kind", "clause"}:
                raise ValueError("unexpected axiom fields")
            if clause not in root_axioms:
                raise ValueError("certificate axiom is absent from root CNF")
            depth = 0
        elif kind == "resolution":
            if set(raw) != {"kind", "clause", "left", "right", "pivot"}:
                raise ValueError("unexpected resolution fields")
            left = int(raw["left"])
            right = int(raw["right"])
            pivot = int(raw["pivot"])
            if not (0 <= left < index and 0 <= right < index and left != right):
                raise ValueError("invalid parent indices")
            derived = independent_resolve(clauses[left], clauses[right], pivot)
            if derived != clause:
                raise ValueError("claimed clause differs from independent resolvent")
            depth = 1 + max(depths[left], depths[right])
            resolution_lines += 1
        else:
            raise ValueError("unknown proof line kind")

        clauses.append(clause)
        depths.append(depth)

    if clauses[-1] != ():
        raise ValueError("certificate does not end with the empty clause")

    maximum_width = max(len(clause) for clause in clauses)
    return resolution_lines, maximum_width, depths[-1]


def build_certificate(root):
    root = canonical_cnf(root)
    variable_count = max(abs(literal) for clause in root for literal in clause)
    affine_answer, _ = visible_affine_root_decision(root, variable_count)
    if affine_answer is not None:
        raise ValueError("fixture is outside the non-affine core")

    policy = TracePolicy()
    answer, root_id = policy.search(root)
    if answer is not False or verify_trace(policy.nodes, root_id, root) is not False:
        raise ValueError("fixture is not a verified UNSAT trace")

    translator = TraceTranslator(root, policy.nodes)
    final_line = translator.translate(root_id)
    if translator.proof.clause(final_line) != ():
        raise ValueError("translator did not emit empty clause")
    return root, serialize_proof(translator.proof.lines)


def expect_rejected(root, certificate: list[CertificateLine]) -> None:
    try:
        check_certificate(root, certificate)
    except (ValueError, TypeError, KeyError, IndexError):
        return
    raise AssertionError("corrupted certificate was accepted")


def negative_controls(root, certificate: list[CertificateLine]) -> None:
    # Corrupt the final pivot.
    bad_pivot = copy.deepcopy(certificate)
    bad_pivot[-1]["pivot"] = int(bad_pivot[-1]["pivot"]) + 1
    expect_rejected(root, bad_pivot)

    # Corrupt the final clause while keeping parents unchanged.
    bad_final = copy.deepcopy(certificate)
    bad_final[-1]["clause"] = [1]
    expect_rejected(root, bad_final)

    # Replace the first root axiom by a legal-looking absent clause.
    bad_axiom = copy.deepcopy(certificate)
    bad_axiom[0]["clause"] = [999]
    expect_rejected(root, bad_axiom)

    # Point one Resolution line forward rather than backward.
    bad_parent = copy.deepcopy(certificate)
    first_resolution = next(
        index for index, line in enumerate(bad_parent)
        if line["kind"] == "resolution"
    )
    bad_parent[first_resolution]["left"] = len(bad_parent) - 1
    expect_rejected(root, bad_parent)


def audit_fixture(name: str, cnf) -> tuple[int, int]:
    root, certificate = build_certificate(cnf)
    resolution_lines, maximum_width, proof_depth = check_certificate(root, certificate)
    negative_controls(root, certificate)

    print(f"CASE = {name}")
    print(f"  certificate_lines = {len(certificate)}")
    print(f"  resolution_lines = {resolution_lines}")
    print(f"  maximum_width = {maximum_width}")
    print(f"  proof_depth = {proof_depth}")
    print("  final_clause = EMPTY")
    print("  corrupted_certificates_rejected = 4/4")
    return len(certificate), proof_depth


def self_test() -> None:
    maximum_lines = 0
    maximum_depth = 0

    lines, depth = audit_fixture("BASE", UNSAT_FORMULA)
    maximum_lines = max(maximum_lines, lines)
    maximum_depth = max(maximum_depth, depth)

    for name, payload in CASES.items():
        lines, depth = audit_fixture(name, payload["cnf"])
        maximum_lines = max(maximum_lines, lines)
        maximum_depth = max(maximum_depth, depth)

    # A second deterministic random sample is disjoint from earlier fuzz seeds.
    seed = 221376
    rng = random.Random(seed)
    variables = 4
    pool = clause_pool(variables)
    checked = 0
    attempts = 0
    while attempts < 3000 and checked < 200:
        attempts += 1
        cnf = canonical_cnf(rng.sample(pool, rng.randint(4, 14)))
        if not is_unsat(cnf, variables):
            continue
        affine_answer, _ = visible_affine_root_decision(cnf, variables)
        if affine_answer is not None:
            continue
        root, certificate = build_certificate(cnf)
        _, _, depth = check_certificate(root, certificate)
        maximum_lines = max(maximum_lines, len(certificate))
        maximum_depth = max(maximum_depth, depth)
        checked += 1

    assert checked == 200

    print("JANUS_POLICY0T_INDEPENDENT_PROOF_REPLAY = PASS")
    print(f"random_seed = {seed}")
    print(f"random_certificates_checked = {checked}")
    print(f"maximum_certificate_lines = {maximum_lines}")
    print(f"maximum_proof_depth = {maximum_depth}")
    print("negative_control_classes = pivot,final_clause,axiom,parent_index")
    print("claim_boundary = independent finite checker; universal theorem still requires mathematical review")


if __name__ == "__main__":
    self_test()
