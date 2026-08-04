#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "C049.1-B4.6.3-TERMINAL-COMPLETENESS-ATTACK-v1"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def basis(rows: Iterable[int], d: int) -> tuple[int, ...]:
    rows = [int(row) & ((1 << d) - 1) for row in rows if int(row)]
    out: list[int] = []
    for bit in range(d - 1, -1, -1):
        pivot = next((row for row in rows if (row >> bit) & 1), None)
        if pivot is None:
            continue
        rows.remove(pivot)
        rows = [row ^ pivot if (row >> bit) & 1 else row for row in rows]
        out = [row ^ pivot if (row >> bit) & 1 else row for row in out]
        out.append(pivot)
    return tuple(sorted(out, reverse=True))


def width(blocks: Sequence[Sequence[int]], order: Sequence[int], d: int) -> tuple[int, list[int]]:
    vector = []
    for cut in range(len(order) + 1):
        left = basis((row for factor in order[:cut] for row in blocks[factor]), d)
        right = basis((row for factor in order[cut:] for row in blocks[factor]), d)
        joined = basis((*left, *right), d)
        vector.append(len(left) + len(right) - len(joined))
    return max(vector, default=0), vector


def replay_case(record: dict) -> None:
    supplied_digest = record["case_digest"]
    clean = dict(record)
    clean.pop("case_digest")
    if digest(clean) != supplied_digest:
        raise AssertionError("case digest mismatch")
    case = record["case"]
    blocks = [tuple(int(row) for row in block) for block in case["blocks"]]
    records = []
    for order in itertools.permutations(range(len(blocks))):
        maximum, vector = width(blocks, order, int(case["d"]))
        records.append({"order": list(order), "maximum_width": maximum, "width_vector": vector})
    accepting = [item for item in records if item["maximum_width"] <= int(case["k"])]
    expected_terminal = "FOUND_LAYOUT" if accepting else "NO_LAYOUT_AT_CAP"
    if record["permutation_count"] != len(records):
        raise AssertionError("permutation count mismatch")
    if record["minimum_width"] != min(item["maximum_width"] for item in records):
        raise AssertionError("minimum width mismatch")
    if record["accepting_layout_count"] != len(accepting):
        raise AssertionError("accepting count mismatch")
    if record["terminal"] != expected_terminal:
        raise AssertionError("terminal mismatch")
    if record["all_layouts_digest"] != digest(records):
        raise AssertionError("layout transcript digest mismatch")
    canonical = accepting[0] if accepting else None
    if record["canonical_accepting_layout"] != canonical:
        raise AssertionError("canonical witness mismatch")
    if accepting:
        if record["negative_certificate"] is not None:
            raise AssertionError("positive case carries negative certificate")
    else:
        expected_negative = {
            "complete_permutation_space": len(records),
            "every_layout_above_cap": True,
        }
        if record["negative_certificate"] != expected_negative:
            raise AssertionError("negative certificate mismatch")


def verify(artifact: dict) -> None:
    if artifact["schema"] != SCHEMA:
        raise AssertionError("schema mismatch")
    supplied = artifact["semantic_digest"]
    clean = dict(artifact)
    clean.pop("semantic_digest")
    if digest(clean) != supplied:
        raise AssertionError("semantic digest mismatch")
    for record in artifact["results"]:
        replay_case(record)
    summary = artifact["summary"]
    if summary != {
        "case_count": 4,
        "found_layout_cases": 3,
        "no_layout_at_cap_cases": 1,
        "permutations_replayed": 734,
        "false_negative_controls": 1,
        "failures": 0,
    }:
        raise AssertionError("summary mismatch")
    boundary = artifact["strict_boundary"]
    if boundary["engine_terminal_completeness_proved"] is not False:
        raise AssertionError("bounded oracle promoted to engine theorem")
    if boundary["no_layout_at_cap_enabled_in_engine"] is not False:
        raise AssertionError("negative terminal enabled prematurely")
    if boundary["p_vs_np"] != "OPEN":
        raise AssertionError("P versus NP boundary altered")


def repair(artifact: dict) -> dict:
    out = json.loads(json.dumps(artifact))
    for record in out["results"]:
        clean = dict(record)
        clean.pop("case_digest", None)
        record["case_digest"] = digest(clean)
    clean = dict(out)
    clean.pop("semantic_digest", None)
    out["semantic_digest"] = digest(clean)
    return out


def tamper_self_test(artifact: dict) -> None:
    controls = []
    a = json.loads(json.dumps(artifact)); a["results"][1]["terminal"] = "FOUND_LAYOUT"; controls.append(a)
    a = json.loads(json.dumps(artifact)); a["results"][2]["accepting_layout_count"] = 0; controls.append(a)
    a = json.loads(json.dumps(artifact)); a["results"][0]["canonical_accepting_layout"]["order"] = [2,1,0]; controls.append(a)
    a = json.loads(json.dumps(artifact)); a["strict_boundary"]["no_layout_at_cap_enabled_in_engine"] = True; controls.append(a)
    for index, control in enumerate(controls):
        try:
            verify(repair(control))
        except AssertionError:
            continue
        raise AssertionError(f"tamper control {index} accepted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    artifact = json.loads(args.artifact.read_text())
    verify(artifact)
    if args.tamper_self_test:
        tamper_self_test(artifact)
    print("B4.6.3 terminal-completeness attack oracle verified")


if __name__ == "__main__":
    main()
