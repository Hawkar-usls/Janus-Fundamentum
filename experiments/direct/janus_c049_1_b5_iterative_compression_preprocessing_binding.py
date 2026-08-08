from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "janus.c049_1.b5.iterative_compression_preprocessing_binding_candidate.v1"
SPEC_SCHEMA = "janus.c049_1.b5.iterative_compression_preprocessing_binding_spec.v1"


def cb(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(value: Any) -> str:
    return hashlib.sha256(cb(value)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def xor_basis(rows: Iterable[int], dimension: int) -> tuple[int, ...]:
    pivots: dict[int, int] = {}
    limit = 1 << dimension
    for raw in rows:
        x = int(raw)
        if x < 0 or x >= limit:
            raise ValueError("vector outside ambient space")
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                for q, y in list(pivots.items()):
                    if q != p and ((y >> p) & 1):
                        pivots[q] = y ^ x
                break
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def span_basis(blocks: Iterable[Iterable[int]], dimension: int) -> tuple[int, ...]:
    return xor_basis((x for block in blocks for x in block), dimension)


def reduce_mod(vector: int, basis: tuple[int, ...]) -> tuple[int, int]:
    x = int(vector)
    ops = 0
    for b in basis:
        p = b.bit_length() - 1
        if p >= 0 and ((x >> p) & 1):
            x ^= b
            ops += 1
    return x, ops


def intersection_basis(
    left_rows: Iterable[int], right_rows: Iterable[int], dimension: int
) -> tuple[tuple[int, ...], int]:
    left = xor_basis(left_rows, dimension)
    right = xor_basis(right_rows, dimension)
    pivot_relations: dict[int, tuple[int, int]] = {}
    kernel_combinations: list[int] = []
    work = len(left) + len(right)

    for index, source in enumerate(left):
        remainder, ops = reduce_mod(source, right)
        work += ops + 1
        combination = 1 << index
        while remainder:
            p = remainder.bit_length() - 1
            if p not in pivot_relations:
                pivot_relations[p] = (remainder, combination)
                break
            old_remainder, old_combination = pivot_relations[p]
            remainder ^= old_remainder
            combination ^= old_combination
            work += 1
        if remainder == 0:
            kernel_combinations.append(combination)

    vectors: list[int] = []
    for combination in kernel_combinations:
        value = 0
        for index, source in enumerate(left):
            if (combination >> index) & 1:
                value ^= source
                work += 1
        vectors.append(value)
    return xor_basis(vectors, dimension), work


def canonical_factor_catalog(raw: dict[str, Any], dimension: int) -> list[dict[str, Any]]:
    factors = raw.get("factors")
    if not isinstance(factors, list):
        raise ValueError("factors must be a list")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for presentation_index, factor in enumerate(factors):
        if not isinstance(factor, dict) or "id" not in factor or "normal_space" not in factor:
            raise ValueError("bad factor record")
        key = cb(factor["id"]).decode("utf-8")
        if key in seen:
            raise ValueError("duplicate factor id")
        seen.add(key)
        out.append(
            {
                "factor_id": copy.deepcopy(factor["id"]),
                "presentation_index": presentation_index,
                "normal_space": list(xor_basis(factor["normal_space"], dimension)),
                "affine_offset": copy.deepcopy(factor.get("affine_offset")),
            }
        )
    out.sort(key=lambda record: cb(record["factor_id"]))
    for occurrence_index, record in enumerate(out):
        record["occurrence_index"] = occurrence_index
    return out


def build(spec: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any]:
    if spec.get("schema") != SPEC_SCHEMA:
        raise AssertionError("preprocessing spec schema")
    if spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY_NO_ORCHESTRATOR_OR_TERMINAL_PROMOTION":
        raise AssertionError("preprocessing spec status")

    dimension = int(raw["ambient_dim"])
    k = int(raw["k"])
    if dimension < 0 or k < 0:
        raise ValueError("ambient_dim and k must be nonnegative")
    theta = 2 * k
    original = canonical_factor_catalog(raw, dimension)
    original_blocks = [tuple(record["normal_space"]) for record in original]

    reductions: list[dict[str, Any]] = []
    discovery: list[dict[str, Any]] = []
    bijection: list[dict[str, Any]] = []
    charged_work = 0

    for i, record in enumerate(original):
        other = span_basis((original_blocks[j] for j in range(len(original)) if j != i), dimension)
        reduced, work = intersection_basis(original_blocks[i], other, dimension)
        charged_work += work + len(other) + len(reduced) + 1
        affine_digest = dg(record["affine_offset"])
        reduced_record = {
            "factor_id": copy.deepcopy(record["factor_id"]),
            "occurrence_index": i,
            "normal_space": list(reduced),
            "affine_offset": copy.deepcopy(record["affine_offset"]),
        }
        discovery.append(reduced_record)
        reductions.append(
            {
                "occurrence_index": i,
                "factor_id": copy.deepcopy(record["factor_id"]),
                "original_normal_space_rref": list(original_blocks[i]),
                "other_span_rref": list(other),
                "reduced_intersection_rref": list(reduced),
                "original_dimension": len(original_blocks[i]),
                "reduced_dimension": len(reduced),
                "theta_2k": theta,
                "dimension_at_most_2k": len(reduced) <= theta,
                "affine_offset_identity_digest": affine_digest,
            }
        )
        bijection.append(
            {
                "occurrence_index": i,
                "factor_id": copy.deepcopy(record["factor_id"]),
                "original_normal_space_digest": dg(list(original_blocks[i])),
                "discovery_normal_space_digest": dg(list(reduced)),
                "affine_offset_identity_digest": affine_digest,
                "affine_offset_bytes_preserved": cb(record["affine_offset"]) == cb(reduced_record["affine_offset"]),
            }
        )

    obstruction = [r for r in reductions if not r["dimension_at_most_2k"]]
    if not original:
        branch = "TRIVIAL_EMPTY_INPUT"
    elif len(original) == 1:
        branch = "TRIVIAL_SINGLETON_INPUT"
    elif obstruction:
        branch = "LOCAL_NO_LAYOUT_SOURCE_CANDIDATE_PENDING_REVIEW"
    else:
        branch = "PREPROCESSING_BOUND"

    payload: dict[str, Any] = {
        "gate": spec["gate"],
        "status": "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW",
        "ambient_dim": dimension,
        "k": k,
        "theta": theta,
        "theta_equals_2k": theta == 2 * k,
        "original_catalog": original,
        "discovery_catalog": discovery,
        "original_catalog_semantic_digest": dg(original),
        "discovery_catalog_semantic_digest": dg(discovery),
        "factor_occurrence_bijection": bijection,
        "per_factor_reduction_receipts": reductions,
        "preprocessing_branch": branch,
        "obstruction_occurrence_indices": [int(r["occurrence_index"]) for r in obstruction],
        "source_theorem_binding": copy.deepcopy(spec["published_source_binding"]),
        "dual_catalog_contract": copy.deepcopy(spec["dual_catalog_contract"]),
        "algebraic_cut_equivalence_proof": copy.deepcopy(spec["algebraic_cut_equivalence_proof"]),
        "charged_gf2_work": charged_work,
        "certificate_bytes": 0,
        "strict_boundary": copy.deepcopy(spec["strict_boundary"]),
    }
    payload["strict_boundary"]["preprocessing_local_no_layout_terminal"] = "FORBIDDEN_PENDING_REVIEW"
    payload["strict_boundary"]["original_order_lift"] = False
    payload["strict_boundary"]["iterative_compression_orchestrator"] = False
    payload["strict_boundary"]["b5_complete"] = False
    payload["strict_boundary"]["p_vs_np"] = "OPEN"

    artifact: dict[str, Any] = {}
    for _ in range(8):
        artifact = {
            "schema": SCHEMA,
            "proof_payload": payload,
            "semantic_digest_scope": "proof_payload",
            "semantic_digest": dg(payload),
        }
        size = len(cb(artifact)) + 1
        if payload["certificate_bytes"] == size:
            break
        payload["certificate_bytes"] = size
    else:
        raise AssertionError("certificate byte fixed point")
    artifact["semantic_digest"] = dg(payload)
    if len(cb(artifact)) + 1 != payload["certificate_bytes"]:
        raise AssertionError("certificate bytes")
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = build(load(args.spec), load(args.input))
    args.output.write_bytes(cb(artifact) + b"\n")
    p = artifact["proof_payload"]
    print("JANUS_B5_ITERATIVE_COMPRESSION_PREPROCESSING_BINDING = PASS")
    print("PREPROCESSING_BRANCH =", p["preprocessing_branch"])
    print("FACTOR_OCCURRENCES =", len(p["original_catalog"]))
    print("THETA_2K =", p["theta"])
    print("OBSTRUCTION_OCCURRENCES =", len(p["obstruction_occurrence_indices"]))
    print("ORIGINAL_CATALOG_SEMANTIC_DIGEST =", p["original_catalog_semantic_digest"])
    print("DISCOVERY_CATALOG_SEMANTIC_DIGEST =", p["discovery_catalog_semantic_digest"])
    print("PREPROCESSING_LOCAL_NO_LAYOUT_TERMINAL = FORBIDDEN_PENDING_REVIEW")
    print("ORIGINAL_ORDER_LIFT = FALSE")
    print("ITERATIVE_COMPRESSION_ORCHESTRATOR = FALSE")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    print("SEMANTIC_DIGEST =", artifact["semantic_digest"])


if __name__ == "__main__":
    main()
