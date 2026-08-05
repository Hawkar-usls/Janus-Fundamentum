#!/usr/bin/env python3
"""Red contract for canonical input-order invariance of the dimension-two preorder.

This contract deliberately replays the same decoded 468-generator inventory in
three different list orders while preserving the same frozen source binding.
The canonical preorder proof payload must be byte-identical in every replay.

The contract is committed before any implementation repair. A failure therefore
records the exact gap between repeatability on one fixed order and true INV-07
input-order invariance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Callable

import janus_c049_1_b4_6_3_dimension_two_preorder_hardening as producer

SEED = 113846307
MODES = ("original", "reversed", "seeded-shuffle")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def reordered_reader(
    original_reader: Callable,
    mode: str,
) -> Callable:
    def read(root: Path, manifest: dict, node_id: int) -> list[dict]:
        records = list(original_reader(root, manifest, node_id))
        before = sorted(record["trajectory_digest"] for record in records)
        if mode == "original":
            reordered = records
        elif mode == "reversed":
            reordered = list(reversed(records))
        elif mode == "seeded-shuffle":
            reordered = list(records)
            random.Random(SEED).shuffle(reordered)
        else:
            raise ValueError(f"unknown order mode: {mode}")
        after = sorted(record["trajectory_digest"] for record in reordered)
        if before != after or len(reordered) != 468:
            raise AssertionError("permutation changed the decoded generator multiset")
        return reordered

    return read


def run_mode(transcript_root: Path, output: Path, mode: str) -> dict:
    original_reader = producer.read_generators
    producer.read_generators = reordered_reader(original_reader, mode)
    try:
        return producer.build(transcript_root, output)
    finally:
        producer.read_generators = original_reader


def differing_top_level_keys(left: dict, right: dict) -> list[str]:
    return sorted(key for key in set(left) | set(right) if left.get(key) != right.get(key))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("transcript_root", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    artifacts: dict[str, dict] = {}
    payloads: dict[str, bytes] = {}
    for mode in MODES:
        path = args.output_dir / f"{mode}.json"
        artifacts[mode] = run_mode(args.transcript_root, path, mode)
        payloads[mode] = path.read_bytes()

    reference = payloads["original"]
    failures = []
    for mode in MODES[1:]:
        if payloads[mode] != reference:
            failures.append(
                {
                    "mode": mode,
                    "original_sha256": sha256(reference),
                    "permuted_sha256": sha256(payloads[mode]),
                    "differing_top_level_keys": differing_top_level_keys(
                        artifacts["original"], artifacts[mode]
                    ),
                    "original_input_generator_family_digest": artifacts["original"].get(
                        "input_generator_family_digest"
                    ),
                    "permuted_input_generator_family_digest": artifacts[mode].get(
                        "input_generator_family_digest"
                    ),
                }
            )

    if failures:
        print("INV-07_INPUT_ORDER_INVARIANCE = FAIL")
        print(json.dumps(failures, indent=2, sort_keys=True))
        raise SystemExit(1)

    print("INV-07_INPUT_ORDER_INVARIANCE = PASS")
    print("ORDERS_REPLAYED =", len(MODES))
    print("CANONICAL_PAYLOAD_SHA256 =", sha256(reference))


if __name__ == "__main__":
    main()
