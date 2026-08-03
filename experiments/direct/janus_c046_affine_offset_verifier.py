#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from typing import Any

EXPECTED_SCHEMA = "janus.c046.affine_offset_obstruction.v1"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def gf2_rank(rows: list[int], dimension: int) -> int:
    rows = rows[:]
    rank = 0
    for column in range(dimension - 1, -1, -1):
        pivot = next((i for i in range(rank, len(rows)) if rows[i] & (1 << column)), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i] & (1 << column):
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def full_rank_signature(normals: list[int], dimension: int) -> list[int]:
    return [
        gf2_rank([normals[i] for i in range(len(normals)) if mask & (1 << i)], dimension)
        for mask in range(1 << len(normals))
    ]


def covered(point: int, factors: list[dict[str, int]]) -> bool:
    return any(((point & f["normal"]).bit_count() & 1) == f["offset"] for f in factors)


def verify(payload: dict[str, Any]) -> None:
    if payload.get("schema") != EXPECTED_SCHEMA:
        raise ValueError("schema mismatch")
    integrity = payload.get("integrity_sha256")
    body = dict(payload)
    body.pop("integrity_sha256", None)
    if integrity != digest(body):
        raise ValueError("integrity mismatch")
    for expected_dimension, case in enumerate(payload["cases"], start=1):
        dimension = int(case["dimension"])
        if dimension != expected_dimension:
            raise ValueError("dimension order mismatch")
        left = case["duplicate_zero"]["factors"]
        right = case["complementary_offsets"]["factors"]
        left_normals = [int(f["normal"]) for f in left]
        right_normals = [int(f["normal"]) for f in right]
        if left_normals != right_normals:
            raise ValueError("normal lists differ")
        signature = {
            "dimension": dimension,
            "ordered_normals": left_normals,
            "subset_rank_function": full_rank_signature(left_normals, dimension),
        }
        if case["normal_matroid_digest"] != digest(signature):
            raise ValueError("normal matroid digest mismatch")
        for i in range(dimension):
            pair_left = left[2 * i:2 * i + 2]
            pair_right = right[2 * i:2 * i + 2]
            if [f["normal"] for f in pair_left] != [1 << i, 1 << i]:
                raise ValueError("unexpected left normal pair")
            if [f["offset"] for f in pair_left] != [0, 0]:
                raise ValueError("unexpected duplicate offsets")
            if [f["normal"] for f in pair_right] != [1 << i, 1 << i]:
                raise ValueError("unexpected right normal pair")
            if [f["offset"] for f in pair_right] != [0, 1]:
                raise ValueError("unexpected complementary offsets")
        left_uncovered = [p for p in range(1 << dimension) if not covered(p, left)]
        right_uncovered = [p for p in range(1 << dimension) if not covered(p, right)]
        if left_uncovered != [(1 << dimension) - 1]:
            raise ValueError("left avoidance semantics mismatch")
        if right_uncovered:
            raise ValueError("right arrangement must cover ambient space")
        if case["duplicate_zero"]["status"] != "SAT" or case["duplicate_zero"]["least_witness"] != left_uncovered[0]:
            raise ValueError("left terminal mismatch")
        if case["complementary_offsets"]["status"] != "UNSAT":
            raise ValueError("right terminal mismatch")
    if payload.get("p_vs_np") != "OPEN":
        raise ValueError("claim boundary mismatch")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    with open(args.artifact, encoding="utf-8") as handle:
        verify(json.load(handle))
    print("C046 independent verification: PASS")


if __name__ == "__main__":
    main()
