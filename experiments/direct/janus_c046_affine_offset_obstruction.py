#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from typing import Any

SCHEMA = "janus.c046.affine_offset_obstruction.v1"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def rank(vectors: list[int], dimension: int) -> int:
    rows = vectors[:]
    r = 0
    for bit in range(dimension - 1, -1, -1):
        pivot = next((i for i in range(r, len(rows)) if (rows[i] >> bit) & 1), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        for i in range(len(rows)):
            if i != r and ((rows[i] >> bit) & 1):
                rows[i] ^= rows[r]
        r += 1
    return r


def normal_matroid_signature(factors: list[dict[str, int]], dimension: int) -> dict[str, Any]:
    normals = [f["normal"] for f in factors]
    subset_ranks = []
    for mask in range(1 << len(normals)):
        subset = [normals[i] for i in range(len(normals)) if (mask >> i) & 1]
        subset_ranks.append(rank(subset, dimension))
    return {
        "dimension": dimension,
        "ordered_normals": normals,
        "subset_rank_function": subset_ranks,
    }


def arrangement(kind: str, dimension: int) -> list[dict[str, int]]:
    factors: list[dict[str, int]] = []
    for i in range(dimension):
        normal = 1 << i
        if kind == "duplicate_zero":
            offsets = (0, 0)
        elif kind == "complementary_offsets":
            offsets = (0, 1)
        else:
            raise ValueError(kind)
        for copy, offset in enumerate(offsets):
            factors.append({"factor_id": 2 * i + copy, "normal": normal, "offset": offset})
    return factors


def point_in_factor(point: int, factor: dict[str, int]) -> bool:
    return ((point & factor["normal"]).bit_count() & 1) == factor["offset"]


def avoidance_status(factors: list[dict[str, int]], dimension: int) -> dict[str, Any]:
    uncovered = [
        p for p in range(1 << dimension)
        if not any(point_in_factor(p, factor) for factor in factors)
    ]
    return {
        "status": "SAT" if uncovered else "UNSAT",
        "uncovered_count": len(uncovered),
        "least_witness": None if not uncovered else uncovered[0],
        "union_count": (1 << dimension) - len(uncovered),
    }


def build_artifact(max_dimension: int = 8) -> dict[str, Any]:
    cases = []
    for dimension in range(1, max_dimension + 1):
        left = arrangement("duplicate_zero", dimension)
        right = arrangement("complementary_offsets", dimension)
        left_sig = normal_matroid_signature(left, dimension)
        right_sig = normal_matroid_signature(right, dimension)
        if left_sig != right_sig:
            raise AssertionError("normal matroid signatures differ")
        left_sem = avoidance_status(left, dimension)
        right_sem = avoidance_status(right, dimension)
        if left_sem["status"] != "SAT" or right_sem["status"] != "UNSAT":
            raise AssertionError("offset separation failed")
        cases.append({
            "dimension": dimension,
            "normal_matroid_digest": digest(left_sig),
            "duplicate_zero": {"factors": left, **left_sem},
            "complementary_offsets": {"factors": right, **right_sem},
        })
    body = {
        "schema": SCHEMA,
        "theorem": "The linear normal matroid, including its complete subset-rank function, does not determine affine-subspace-union avoidance or satisfiability; affine offsets are essential.",
        "proof_family": "For each coordinate i use two hyperplanes with normal e_i. Offsets (0,0) leave the all-ones point uncovered; offsets (0,1) cover the whole ambient space.",
        "cases": cases,
        "consequence": "Any C046 decomposition or message language driven only by normal-space ranks/intersections is semantically incomplete unless it also carries affine consistency/offset signatures.",
        "p_vs_np": "OPEN",
    }
    body["integrity_sha256"] = digest(body)
    return body


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    artifact = build_artifact()
    if args.self_test:
        assert len(artifact["cases"]) == 8
        assert all(c["duplicate_zero"]["status"] == "SAT" for c in artifact["cases"])
        assert all(c["complementary_offsets"]["status"] == "UNSAT" for c in artifact["cases"])
    text = json.dumps(artifact, indent=2, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
