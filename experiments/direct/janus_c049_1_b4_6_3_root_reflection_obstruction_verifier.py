#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

SCHEMA = "C049.1-B4.6.3-ROOT-REFLECTION-OBSTRUCTION-v1"
PATH = ((0, 0), (1, 0), (2, 0), (2, 1))


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def compact(values: Sequence[int]) -> tuple[int, ...]:
    seq = list(map(int, values))
    while True:
        for i in range(1, len(seq)):
            if seq[i - 1] == seq[i]:
                del seq[i]
                break
        else:
            reduced = False
            for i in range(len(seq)):
                for j in range(i + 2, len(seq)):
                    window = seq[i : j + 1]
                    monotone = (
                        window[0] <= window[-1] and all(window[0] <= z <= window[-1] for z in window[1:-1])
                    ) or (
                        window[0] >= window[-1] and all(window[0] >= z >= window[-1] for z in window[1:-1])
                    )
                    if monotone:
                        del seq[i + 1 : j]
                        reduced = True
                        break
                if reduced:
                    break
            if not reduced:
                return tuple(seq)
            continue
        continue


def replay(left: Sequence[Sequence[int]], right: Sequence[Sequence[int]]) -> tuple[list[int], list[int], int]:
    l = [tuple(map(int, x)) for x in left]
    r = [tuple(map(int, x)) for x in right]
    initial = l[0][1] & r[0][1]
    raw = []
    for i, j in PATH:
        ll, lr, lv = l[i]
        rl, rr, rv = r[j]
        current = (ll | lr) & (rl | rr)
        joined_left = ll | rl
        joined_right = lr | rr
        raw.append(lv + rv + (initial - current) + (joined_left & joined_right))
    compacted = compact(raw)
    return raw, list(compacted), max(compacted)


def verify(value: dict[str, Any]) -> None:
    payload = value["proof_payload"]
    if payload["schema"] != SCHEMA:
        raise AssertionError("schema")
    if value["semantic_digest"] != digest(payload):
        raise AssertionError("semantic digest")
    if tuple(map(tuple, payload["quotient_path"])) != PATH:
        raise AssertionError("path")
    lower = replay(payload["left_trajectory"], payload["right_lower_envelope"])
    fine = replay(payload["left_trajectory"], payload["right_fine_refinement"])
    if lower != ([0, 1, 1, 0], [0, 1, 0], 1):
        raise AssertionError("lower semantics")
    if fine != ([1, 2, 2, 0], [1, 2, 0], 2):
        raise AssertionError("fine semantics")
    if payload["lower_replay"]["raw_values"] != lower[0] or payload["lower_replay"]["compact_values"] != lower[1] or payload["lower_replay"]["width"] != lower[2]:
        raise AssertionError("lower receipt")
    if payload["fine_replay"]["raw_values"] != fine[0] or payload["fine_replay"]["compact_values"] != fine[1] or payload["fine_replay"]["width"] != fine[2]:
        raise AssertionError("fine receipt")
    obstruction = payload["obstruction"]
    expected = {
        "same_quotient_path": True,
        "lower_envelope_accepts": True,
        "fine_refinement_fails": True,
        "reflection_from_lower_envelope_to_entire_quotient_class": False,
        "forbidden_shortcut": "ROOT_QUOTIENT_PATH_CLASSIFIED_BY_LOWER_ENVELOPE_ONLY",
    }
    if obstruction != expected:
        raise AssertionError("obstruction boundary")
    strict = payload["strict_boundary"]
    if strict != {
        "root_parent_refinement_complete": False,
        "root_full_set_computed": False,
        "root_empty_proved": False,
        "found_layout": "FORBIDDEN",
        "no_layout_at_cap": "FORBIDDEN",
        "current_global_terminal": "OPEN_TRAJECTORY_ENGINE_INCOMPLETE",
        "p_vs_np": "OPEN",
    }:
        raise AssertionError("strict boundary")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    value = json.loads(args.artifact.read_text(encoding="utf-8"))
    verify(value)
    if args.tamper_self_test:
        tampered = json.loads(json.dumps(value))
        tampered["proof_payload"]["fine_replay"]["width"] = 1
        tampered["semantic_digest"] = digest(tampered["proof_payload"])
        try:
            verify(tampered)
        except AssertionError:
            pass
        else:
            raise AssertionError("digest-repaired tamper accepted")
    print("ROOT_REFLECTION_OBSTRUCTION_VERIFIED")


if __name__ == "__main__":
    main()
