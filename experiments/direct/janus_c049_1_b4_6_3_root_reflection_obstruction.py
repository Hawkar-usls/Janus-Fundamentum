#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

SCHEMA = "C049.1-B4.6.3-ROOT-REFLECTION-OBSTRUCTION-v1"
SOURCE_HEAD = "babdf21ba20c1d24ed97fff4bb14121d0dfc1287"
PATH = ((0, 0), (1, 0), (2, 0), (2, 1))
LEFT = ((0, 1, 0), (1, 1, 0), (1, 0, 0))
RIGHT_LOWER = ((0, 1, 0), (1, 0, 0))
RIGHT_FINE = ((0, 1, 1), (1, 0, 0))


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def compact(values: Sequence[int]) -> tuple[int, ...]:
    seq = list(map(int, values))
    while True:
        changed = False
        for i in range(1, len(seq)):
            if seq[i - 1] == seq[i]:
                del seq[i]
                changed = True
                break
        if changed:
            continue
        for i in range(len(seq)):
            for j in range(i + 2, len(seq)):
                window = seq[i : j + 1]
                inc = window[0] <= window[-1] and all(window[0] <= z <= window[-1] for z in window[1:-1])
                dec = window[0] >= window[-1] and all(window[0] >= z >= window[-1] for z in window[1:-1])
                if inc or dec:
                    del seq[i + 1 : j]
                    changed = True
                    break
            if changed:
                break
        if not changed:
            return tuple(seq)


def evaluate(left: Sequence[tuple[int, int, int]], right: Sequence[tuple[int, int, int]]) -> dict[str, Any]:
    initial = left[0][1] & right[0][1]
    raw = []
    receipts = []
    for i, j in PATH:
        ll, lr, lv = left[i]
        rl, rr, rv = right[j]
        current = (ll | lr) & (rl | rr)
        join_correction = initial - current
        joined_left = ll | rl
        joined_right = lr | rr
        shrink_correction = joined_left & joined_right
        value = lv + rv + join_correction + shrink_correction
        raw.append(value)
        receipts.append({
            "child_indices": [i, j],
            "join_correction": join_correction,
            "shrink_correction": shrink_correction,
            "value": value,
        })
    compacted = compact(raw)
    return {
        "raw_values": raw,
        "compact_values": list(compacted),
        "width": max(compacted),
        "receipts": receipts,
    }


def build() -> dict[str, Any]:
    lower = evaluate(LEFT, RIGHT_LOWER)
    fine = evaluate(LEFT, RIGHT_FINE)
    if (lower["raw_values"], lower["compact_values"], lower["width"]) != ([0, 1, 1, 0], [0, 1, 0], 1):
        raise AssertionError("lower replay drift")
    if (fine["raw_values"], fine["compact_values"], fine["width"]) != ([1, 2, 2, 0], [1, 2, 0], 2):
        raise AssertionError("fine replay drift")
    payload = {
        "schema": SCHEMA,
        "source_exact_head": SOURCE_HEAD,
        "root_geometry": {
            "left_boundary": [1],
            "right_boundary": [1],
            "common_boundary": [1],
            "parent_boundary": [],
            "shrink_identity": False,
            "k": 1,
        },
        "source_binding": {
            "node9_retained_class_id": "N9-S02",
            "node9_left_entry_index": 14,
            "leaf5_fine_entry_index": 30,
            "root_child_pairs": 9072,
            "root_naive_refinements": 4954128,
        },
        "quotient_path": [list(x) for x in PATH],
        "left_trajectory": [list(x) for x in LEFT],
        "right_lower_envelope": [list(x) for x in RIGHT_LOWER],
        "right_fine_refinement": [list(x) for x in RIGHT_FINE],
        "lower_replay": lower,
        "fine_replay": fine,
        "obstruction": {
            "same_quotient_path": True,
            "lower_envelope_accepts": True,
            "fine_refinement_fails": True,
            "reflection_from_lower_envelope_to_entire_quotient_class": False,
            "forbidden_shortcut": "ROOT_QUOTIENT_PATH_CLASSIFIED_BY_LOWER_ENVELOPE_ONLY",
        },
        "strict_boundary": {
            "root_parent_refinement_complete": False,
            "root_full_set_computed": False,
            "root_empty_proved": False,
            "found_layout": "FORBIDDEN",
            "no_layout_at_cap": "FORBIDDEN",
            "current_global_terminal": "OPEN_TRAJECTORY_ENGINE_INCOMPLETE",
            "p_vs_np": "OPEN",
        },
        "next_gate": "ROOT_QUOTIENT_REFINEMENT_WITH_SUCCESS_FAILURE_SUBCLASS_PARTITION_AND_REFLECTION_PROOF",
    }
    return {"proof_payload": payload, "semantic_digest": digest(payload)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = build()
    args.output.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
