#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "C049.1-B4.6.3-TERMINAL-COMPLETENESS-ATTACK-v1"
SOURCE_HEAD = "ce7b665e7964f813af12d49a20a1b915bc998398"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def xor_basis(rows: Iterable[int], d: int) -> tuple[int, ...]:
    pending = [int(row) & ((1 << d) - 1) for row in rows if int(row)]
    basis: list[int] = []
    for bit in range(d - 1, -1, -1):
        pivot = next((row for row in pending if (row >> bit) & 1), None)
        if pivot is None:
            continue
        pending.remove(pivot)
        pending = [row ^ pivot if (row >> bit) & 1 else row for row in pending]
        basis = [row ^ pivot if (row >> bit) & 1 else row for row in basis]
        basis.append(pivot)
    return tuple(sorted(basis, reverse=True))


def intersection_dimension(left: Sequence[int], right: Sequence[int], d: int) -> int:
    left_basis = xor_basis(left, d)
    right_basis = xor_basis(right, d)
    joined = xor_basis((*left_basis, *right_basis), d)
    return len(left_basis) + len(right_basis) - len(joined)


def layout_width(blocks: Sequence[Sequence[int]], order: Sequence[int], d: int) -> tuple[int, list[int]]:
    widths: list[int] = []
    for cut in range(len(order) + 1):
        left = [row for factor in order[:cut] for row in blocks[factor]]
        right = [row for factor in order[cut:] for row in blocks[factor]]
        widths.append(intersection_dimension(left, right, d))
    return max(widths, default=0), widths


def exhaustive_oracle(case: dict) -> dict:
    blocks = [tuple(int(row) for row in block) for block in case["blocks"]]
    d = int(case["d"])
    k = int(case["k"])
    records = []
    for order in itertools.permutations(range(len(blocks))):
        maximum, vector = layout_width(blocks, order, d)
        records.append({"order": list(order), "maximum_width": maximum, "width_vector": vector})
    accepting = [record for record in records if record["maximum_width"] <= k]
    minimum = min(record["maximum_width"] for record in records)
    terminal = "FOUND_LAYOUT" if accepting else "NO_LAYOUT_AT_CAP"
    result = {
        "case": case,
        "permutation_count": len(records),
        "minimum_width": minimum,
        "accepting_layout_count": len(accepting),
        "terminal": terminal,
        "canonical_accepting_layout": accepting[0] if accepting else None,
        "all_layouts_digest": digest(records),
        "negative_certificate": {
            "complete_permutation_space": len(records),
            "every_layout_above_cap": all(record["maximum_width"] > k for record in records),
        } if not accepting else None,
    }
    result["case_digest"] = digest(result)
    return result


def cases() -> list[dict]:
    return [
        {
            "name": "B4_6_2_POSITIVE_REPEATED_BLOCK",
            "d": 2,
            "k": 1,
            "blocks": [[1], [2], [1]],
            "affine_offsets": [0, 1, 1],
            "expected_terminal": "FOUND_LAYOUT",
            "purpose": "positive cycle control; offsets and factor identity retained",
        },
        {
            "name": "TWO_GROUPED_FULL_SPACES_NEGATIVE",
            "d": 2,
            "k": 1,
            "blocks": [[1, 2], [1, 2]],
            "affine_offsets": [0, 1],
            "expected_terminal": "NO_LAYOUT_AT_CAP",
            "purpose": "small exact negative fixture with grouped width two",
        },
        {
            "name": "INSERTION_ONLY_FALSE_NEGATIVE_CONTROL",
            "d": 4,
            "k": 1,
            "blocks": [[1], [2], [4], [8], [3], [12]],
            "affine_offsets": [0, 0, 0, 0, 0, 0],
            "expected_terminal": "FOUND_LAYOUT",
            "purpose": "all insertions into one prior order fail although 72 width-one layouts exist",
        },
        {
            "name": "ZERO_WIDTH_DISJOINT_CONTROL",
            "d": 3,
            "k": 0,
            "blocks": [[1], [2], [4]],
            "affine_offsets": [0, 1, 0],
            "expected_terminal": "FOUND_LAYOUT",
            "purpose": "endpoint and zero-boundary completeness control",
        },
    ]


def build() -> dict:
    results = [exhaustive_oracle(case) for case in cases()]
    for result in results:
        if result["terminal"] != result["case"]["expected_terminal"]:
            raise AssertionError("fixture expectation drift")
    artifact = {
        "schema": SCHEMA,
        "source_head": SOURCE_HEAD,
        "role": "JANUS_LAB_AGENT",
        "mode": "DEFENSIVE_SOFTWARE_VERIFICATION",
        "runtime_authority": "NONE",
        "attack_target": "C049.1_B4.6.3_TERMINAL_COMPLETENESS",
        "results": results,
        "summary": {
            "case_count": len(results),
            "found_layout_cases": sum(r["terminal"] == "FOUND_LAYOUT" for r in results),
            "no_layout_at_cap_cases": sum(r["terminal"] == "NO_LAYOUT_AT_CAP" for r in results),
            "permutations_replayed": sum(r["permutation_count"] for r in results),
            "false_negative_controls": 1,
            "failures": 0,
        },
        "attack_ledger": [
            {
                "id": "A1_ROOT_EMPTY_IFF_NO_LAYOUT",
                "status": "OPEN_ENGINE_OBLIGATION",
                "oracle_side": "CLOSED_BOUNDED",
                "required_engine_claim": "accepting root entry exists iff a width-k whole-factor order exists",
            },
            {
                "id": "A2_OPEN_MUST_NOT_COLLAPSE_TO_NO",
                "status": "OPEN_ENGINE_OBLIGATION",
                "oracle_side": "CLASSIFIER_CONTRACT_FROZEN",
                "required_engine_claim": "every capability refusal preserves OPEN and the tested prefix",
            },
            {
                "id": "A3_INSERTION_FAILURE_IS_NOT_NO_LAYOUT",
                "status": "CLOSED_BY_COUNTEREXAMPLE",
                "oracle_side": "72_WIDTH_ONE_LAYOUTS_REPLAYED",
                "required_engine_claim": "terminal completeness cannot depend on insertion-only search",
            },
            {
                "id": "A4_NEGATIVE_REQUIRES_COMPLETE_ROOT_REPLAY",
                "status": "OPEN_ENGINE_OBLIGATION",
                "oracle_side": "TWO_PERMUTATIONS_EXHAUSTED",
                "required_engine_claim": "verifier reconstructs the full empty root set before NO_LAYOUT_AT_CAP",
            },
        ],
        "strict_boundary": {
            "bounded_oracle_only": True,
            "engine_terminal_completeness_proved": False,
            "found_layout_enabled_in_engine": False,
            "no_layout_at_cap_enabled_in_engine": False,
            "current_global_terminal": "OPEN_TRAJECTORY_ENGINE_INCOMPLETE",
            "p_vs_np": "OPEN",
        },
    }
    artifact["semantic_digest"] = digest(artifact)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = build()
    args.output.write_bytes(canonical_json(artifact) + b"\n")
    print(json.dumps(artifact["summary"], sort_keys=True))
    print(artifact["semantic_digest"])


if __name__ == "__main__":
    main()
