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


def independent_rref(rows: Iterable[int], dimension: int) -> tuple[int, ...]:
    limit = 1 << dimension
    work = [int(x) for x in rows]
    if any(x < 0 or x >= limit for x in work):
        raise AssertionError("vector outside ambient")
    result: list[int] = []
    for bit in range(dimension - 1, -1, -1):
        pivot_index = next((i for i, value in enumerate(work) if (value >> bit) & 1), None)
        if pivot_index is None:
            continue
        pivot = work.pop(pivot_index)
        work = [value ^ pivot if ((value >> bit) & 1) else value for value in work]
        result = [value ^ pivot if ((value >> bit) & 1) else value for value in result]
        result.append(pivot)
    return tuple(sorted((x for x in result if x), reverse=True))


def rank(rows: Iterable[int], dimension: int) -> int:
    return len(independent_rref(rows, dimension))


def span_basis(blocks: Iterable[Iterable[int]], dimension: int) -> tuple[int, ...]:
    return independent_rref((x for block in blocks for x in block), dimension)


def is_member(vector: int, basis: Iterable[int], dimension: int) -> bool:
    before = rank(basis, dimension)
    return rank(list(basis) + [int(vector)], dimension) == before


def canonical_original(raw: dict[str, Any], dimension: int) -> list[dict[str, Any]]:
    factors = raw.get("factors")
    if not isinstance(factors, list):
        raise AssertionError("factors")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for presentation_index, factor in enumerate(factors):
        if not isinstance(factor, dict) or "id" not in factor or "normal_space" not in factor:
            raise AssertionError("factor record")
        key = cb(factor["id"]).decode("utf-8")
        if key in seen:
            raise AssertionError("duplicate factor id")
        seen.add(key)
        out.append(
            {
                "factor_id": copy.deepcopy(factor["id"]),
                "presentation_index": presentation_index,
                "normal_space": list(independent_rref(factor["normal_space"], dimension)),
                "affine_offset": copy.deepcopy(factor.get("affine_offset")),
            }
        )
    out.sort(key=lambda record: cb(record["factor_id"]))
    for occurrence_index, record in enumerate(out):
        record["occurrence_index"] = occurrence_index
    return out


def expected_branch(count: int, dimensions: list[int], theta: int) -> str:
    if count == 0:
        return "TRIVIAL_EMPTY_INPUT"
    if count == 1:
        return "TRIVIAL_SINGLETON_INPUT"
    if any(value > theta for value in dimensions):
        return "LOCAL_NO_LAYOUT_SOURCE_CANDIDATE_PENDING_REVIEW"
    return "PREPROCESSING_BOUND"


def verify(candidate: dict[str, Any], spec: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any]:
    assert spec.get("schema") == SPEC_SCHEMA
    assert spec.get("status") == "SPEC_FROZEN_CANDIDATE_ONLY_NO_ORCHESTRATOR_OR_TERMINAL_PROMOTION"
    assert spec.get("base_interface_closure_evidence_head") == "3d077cd5d410109bea9d91544e1bb137bc6d31c7"
    assert candidate.get("schema") == SCHEMA
    assert candidate.get("semantic_digest_scope") == "proof_payload"
    payload = candidate["proof_payload"]
    assert candidate.get("semantic_digest") == dg(payload)
    assert payload.get("certificate_bytes") == len(cb(candidate)) + 1

    dimension = int(raw["ambient_dim"])
    k = int(raw["k"])
    assert dimension >= 0 and k >= 0
    theta = 2 * k
    assert payload["ambient_dim"] == dimension
    assert payload["k"] == k
    assert payload["theta"] == theta
    assert payload["theta_equals_2k"] is True

    original = canonical_original(raw, dimension)
    assert payload["original_catalog"] == original
    assert payload["original_catalog_semantic_digest"] == dg(original)
    discovery = payload["discovery_catalog"]
    reductions = payload["per_factor_reduction_receipts"]
    bijection = payload["factor_occurrence_bijection"]
    assert len(discovery) == len(original) == len(reductions) == len(bijection)

    original_blocks = [tuple(record["normal_space"]) for record in original]
    reduced_dimensions: list[int] = []
    independent_work = 0
    for i, (orig, reduced_record, receipt, binding) in enumerate(zip(original, discovery, reductions, bijection)):
        assert reduced_record["factor_id"] == orig["factor_id"]
        assert reduced_record["occurrence_index"] == i
        assert receipt["factor_id"] == orig["factor_id"] and receipt["occurrence_index"] == i
        assert binding["factor_id"] == orig["factor_id"] and binding["occurrence_index"] == i
        assert cb(reduced_record["affine_offset"]) == cb(orig["affine_offset"])
        assert receipt["affine_offset_identity_digest"] == dg(orig["affine_offset"])
        assert binding["affine_offset_identity_digest"] == dg(orig["affine_offset"])
        assert binding["affine_offset_bytes_preserved"] is True

        other = span_basis((original_blocks[j] for j in range(len(original)) if j != i), dimension)
        assert receipt["other_span_rref"] == list(other)
        assert receipt["original_normal_space_rref"] == list(original_blocks[i])
        reduced = independent_rref(reduced_record["normal_space"], dimension)
        assert reduced_record["normal_space"] == list(reduced)
        assert receipt["reduced_intersection_rref"] == list(reduced)
        expected_dim = rank(original_blocks[i], dimension) + rank(other, dimension) - rank(list(original_blocks[i]) + list(other), dimension)
        assert len(reduced) == expected_dim
        for vector in reduced:
            assert is_member(vector, original_blocks[i], dimension)
            assert is_member(vector, other, dimension)
        assert receipt["original_dimension"] == len(original_blocks[i])
        assert receipt["reduced_dimension"] == len(reduced)
        assert receipt["theta_2k"] == theta
        assert receipt["dimension_at_most_2k"] == (len(reduced) <= theta)
        assert binding["original_normal_space_digest"] == dg(list(original_blocks[i]))
        assert binding["discovery_normal_space_digest"] == dg(list(reduced))
        reduced_dimensions.append(len(reduced))
        independent_work += len(other) + len(reduced) + expected_dim + 1

    assert payload["discovery_catalog_semantic_digest"] == dg(discovery)
    assert payload["preprocessing_branch"] == expected_branch(len(original), reduced_dimensions, theta)
    assert payload["obstruction_occurrence_indices"] == [i for i, value in enumerate(reduced_dimensions) if value > theta]
    assert payload["source_theorem_binding"] == spec["published_source_binding"]
    assert payload["dual_catalog_contract"] == spec["dual_catalog_contract"]
    assert payload["algebraic_cut_equivalence_proof"] == spec["algebraic_cut_equivalence_proof"]
    assert int(payload["charged_gf2_work"]) >= independent_work

    boundary = payload["strict_boundary"]
    assert boundary == spec["strict_boundary"]
    assert boundary["preprocessing_local_no_layout_terminal"] == "FORBIDDEN_PENDING_REVIEW"
    assert boundary["original_order_lift"] is False
    assert boundary["iterative_compression_orchestrator"] is False
    assert boundary["b5_complete"] is False
    assert boundary["all_input_termination"] == "NOT_ESTABLISHED"
    assert boundary["polynomial_runtime"] == "NOT_ESTABLISHED"
    assert boundary["p_vs_np"] == "OPEN"

    return {
        "branch": payload["preprocessing_branch"],
        "factor_count": len(original),
        "reduced_dimensions": reduced_dimensions,
        "original_catalog_digest": payload["original_catalog_semantic_digest"],
        "discovery_catalog_digest": payload["discovery_catalog_semantic_digest"],
    }


def repair(candidate: dict[str, Any]) -> dict[str, Any]:
    payload = candidate["proof_payload"]
    for _ in range(8):
        candidate["semantic_digest"] = dg(payload)
        size = len(cb(candidate)) + 1
        if payload["certificate_bytes"] == size:
            break
        payload["certificate_bytes"] = size
    candidate["semantic_digest"] = dg(payload)
    if payload["certificate_bytes"] != len(cb(candidate)) + 1:
        raise AssertionError("repair byte fixed point")
    return candidate


def tamper_suite(base: dict[str, Any], spec: dict[str, Any], raw: dict[str, Any]) -> tuple[int, int]:
    attacks: list[tuple[str, dict[str, Any]]] = []

    def add(name: str, mutation) -> None:
        candidate = copy.deepcopy(base)
        mutation(candidate["proof_payload"])
        attacks.append((name, repair(candidate)))

    add("T01_REDUCED_BASIS", lambda p: p["discovery_catalog"][0].__setitem__("normal_space", [999]))
    add("T02_OTHER_SPAN", lambda p: p["per_factor_reduction_receipts"][0].__setitem__("other_span_rref", [999]))
    add("T03_REDUCED_DIMENSION", lambda p: p["per_factor_reduction_receipts"][0].__setitem__("reduced_dimension", 999))
    add("T04_DROP_OCCURRENCE", lambda p: p["discovery_catalog"].pop())
    add("T05_GEOMETRIC_DEDUP", lambda p: p["factor_occurrence_bijection"].pop())
    add("T06_AFFINE_OFFSET", lambda p: p["discovery_catalog"][0].__setitem__("affine_offset", {"tamper": True}))
    add("T07_OCCURRENCE_INDEX", lambda p: p["discovery_catalog"][0].__setitem__("occurrence_index", 999))
    add("T08_FACTOR_ID", lambda p: p["factor_occurrence_bijection"][0].__setitem__("factor_id", "__fake__"))
    add("T09_THETA", lambda p: p.__setitem__("theta", p["theta"] + 1))
    add("T10_BRANCH", lambda p: p.__setitem__("preprocessing_branch", "FOUND_LAYOUT"))
    add("T11_ORIGINAL_CATALOG", lambda p: p["original_catalog"][0].__setitem__("normal_space", []))
    add("T12_DISCOVERY_DIGEST", lambda p: p.__setitem__("discovery_catalog_semantic_digest", "0" * 64))
    add("T13_SOURCE_BINDING", lambda p: p["source_theorem_binding"].__setitem__("theta_policy_for_iterative_compression", "RAW_DIMENSION"))
    add("T14_CUT_EQUIVALENCE", lambda p: p["algebraic_cut_equivalence_proof"].__setitem__("reverse_inclusion", "FALSE"))
    add("T15_DIRECT_B5_4", lambda p: p["dual_catalog_contract"].__setitem__("direct_b5_4_on_reduced_catalog", "ALLOWED"))
    add("T16_PROMOTE_LOCAL_NEGATIVE", lambda p: p["strict_boundary"].__setitem__("preprocessing_local_no_layout_terminal", "ADMITTED"))
    add("T17_ORIGINAL_ORDER_LIFT", lambda p: p["strict_boundary"].__setitem__("original_order_lift", True))
    add("T18_ORCHESTRATOR", lambda p: p["strict_boundary"].__setitem__("iterative_compression_orchestrator", True))
    add("T19_B5_COMPLETE", lambda p: p["strict_boundary"].__setitem__("b5_complete", True))
    add("T20_P_VS_NP", lambda p: p["strict_boundary"].__setitem__("p_vs_np", "CLOSED"))

    rejected = 0
    for name, candidate in attacks:
        try:
            verify(candidate, spec, raw)
        except Exception:
            rejected += 1
            print(name + " = REJECTED")
            continue
        raise AssertionError(name + " survived")
    return rejected, len(attacks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--tamper-suite", action="store_true")
    args = parser.parse_args()
    spec = load(args.spec)
    raw = load(args.input)
    candidate = load(args.candidate)
    result = verify(candidate, spec, raw)
    print("JANUS_B5_ITERATIVE_COMPRESSION_PREPROCESSING_BINDING_INDEPENDENT_VERIFIER = PASS")
    print("PREPROCESSING_BRANCH =", result["branch"])
    print("FACTOR_OCCURRENCES =", result["factor_count"])
    print("REDUCED_DIMENSIONS =", result["reduced_dimensions"])
    print("ORIGINAL_DISCOVERY_OCCURRENCE_BIJECTION = PASS")
    print("AFFINE_OFFSET_IDENTITY = PASS")
    print("EXACT_INTERSECTION_REPLAY = PASS")
    print("RAW_DIMENSION_SUBSTITUTION = FORBIDDEN")
    print("DIRECT_B5_4_ON_REDUCED_CATALOG = FORBIDDEN")
    if args.tamper_suite:
        rejected, total = tamper_suite(candidate, spec, raw)
        print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {rejected}/{total}")
    print("PREPROCESSING_LOCAL_NO_LAYOUT_TERMINAL = FORBIDDEN_PENDING_REVIEW")
    print("ORIGINAL_ORDER_LIFT = FALSE")
    print("ITERATIVE_COMPRESSION_ORCHESTRATOR = FALSE")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
