#!/usr/bin/env python3
"""Validate the schema-selected cumulative JANUS inversion matrix."""

from __future__ import annotations

import json
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"


class MatrixError(RuntimeError):
    pass


def load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise MatrixError(f"missing file: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise MatrixError(
            f"invalid JSON in {path.relative_to(ROOT)} at "
            f"line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc


def load_all(pattern: str, key: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for path in sorted(REGISTRY.glob(pattern)):
        payload = load(path)
        value = payload.get(key)
        if not isinstance(value, list):
            raise MatrixError(f"{path.relative_to(ROOT)} lacks list field {key}")
        items.extend(value)
    if not items:
        raise MatrixError(f"no items loaded from {pattern}")
    return items


def hnum(hid: str) -> int:
    match = re.fullmatch(r"H([0-9]+)", hid)
    if not match:
        raise MatrixError(f"invalid hypothesis id: {hid}")
    return int(match.group(1))


def resolve_matrix(name: str, active: set[str] | None = None) -> dict[str, Any]:
    active = set() if active is None else set(active)
    if name in active:
        raise MatrixError(f"matrix inheritance cycle at {name}")
    active.add(name)

    payload = load(REGISTRY / name)
    base_name = payload.get("base_matrix")
    if base_name:
        base = resolve_matrix(base_name, active)
        hypotheses = base["hypotheses"] + payload.get("hypotheses_added", [])
        tests = base["tests"] + payload.get("tests_added", [])
        overrides = base["overrides"] + payload.get("overrides_added", [])
        default_status = payload.get(
            "default_cell_status", base["default_cell_status"]
        )
    else:
        hypotheses = payload.get("hypotheses", [])
        tests = payload.get("tests", [])
        overrides = payload.get("overrides", [])
        default_status = payload.get("default_cell_status")

    return {
        "payload": payload,
        "hypotheses": hypotheses,
        "tests": tests,
        "overrides": overrides,
        "default_cell_status": default_status,
    }


def main() -> int:
    try:
        schema = load(REGISTRY / "schema.json")
        policy = schema.get("inversion_matrix_policy")
        if not isinstance(policy, dict):
            raise MatrixError("schema lacks inversion_matrix_policy")
        current_file = policy.get("current_file")
        if not isinstance(current_file, str):
            raise MatrixError("matrix policy lacks current_file")

        resolved = resolve_matrix(current_file)
        matrix = resolved["payload"]
        selected_h = resolved["hypotheses"]
        selected_t = resolved["tests"]
        overrides = resolved["overrides"]
        default_status = resolved["default_cell_status"]

        hypotheses = load_all("hypotheses*.json", "hypotheses")
        graveyard = load_all("graveyard*.json", "entries")
        known_h = {item["id"] for item in hypotheses} | {
            item["id"] for item in graveyard
        }

        test_entries = load_all("inversion-tests*.json", "tests")
        test_ids = [item["id"] for item in test_entries]
        if len(set(test_ids)) != len(test_ids):
            raise MatrixError("duplicate inversion-test id")

        allowed = set(schema.get("allowed_inversion_cell_statuses", []))
        expected_h_count = int(policy["hypothesis_count"])
        expected_t_count = int(policy["test_count"])
        cycle_from = int(policy["cycle_first_hypothesis_number"])
        expected_new = set(policy["cycle_hypothesis_ids"])
        minimum_fraction = Fraction(policy["minimum_inherited_fraction"])

        if len(selected_h) != expected_h_count or len(set(selected_h)) != expected_h_count:
            raise MatrixError(
                f"matrix must contain exactly {expected_h_count} unique hypotheses"
            )
        if len(selected_t) != expected_t_count or len(set(selected_t)) != expected_t_count:
            raise MatrixError(
                f"matrix must contain exactly {expected_t_count} unique tests"
            )
        if selected_t != test_ids:
            raise MatrixError(
                "cumulative matrix test order must match inversion-tests files"
            )
        if default_status not in allowed:
            raise MatrixError(f"invalid default cell status: {default_status}")
        if any(hid not in known_h for hid in selected_h):
            missing = sorted(hid for hid in selected_h if hid not in known_h)
            raise MatrixError(f"unknown matrix hypotheses: {missing}")

        inherited = [hid for hid in selected_h if hnum(hid) < cycle_from]
        new = [hid for hid in selected_h if hnum(hid) >= cycle_from]
        if Fraction(len(inherited), len(selected_h)) < minimum_fraction:
            raise MatrixError(
                f"existing-hypothesis reuse too low: {len(inherited)}/"
                f"{len(selected_h)}; minimum is {minimum_fraction}"
            )
        if set(new) != expected_new:
            raise MatrixError(
                f"unexpected cycle descendants in matrix: {sorted(new)}"
            )

        expected_pairs = {(hid, tid) for hid in selected_h for tid in selected_t}
        seen: set[tuple[str, str]] = set()
        for cell in overrides:
            pair = (cell.get("hypothesis_id"), cell.get("test_id"))
            if pair in seen:
                raise MatrixError(f"duplicate override: {pair}")
            seen.add(pair)
            if pair not in expected_pairs:
                raise MatrixError(f"out-of-matrix override: {pair}")
            status = cell.get("status")
            if status not in allowed or status == default_status:
                raise MatrixError(
                    f"invalid or redundant status {status!r} for {pair}"
                )
            note = cell.get("note")
            if not isinstance(note, str) or not note.strip():
                raise MatrixError(f"override {pair} must explain its status")

        dimensions = matrix.get("current_dimensions")
        expected_dimensions = {
            "hypotheses": expected_h_count,
            "inversion_tests": expected_t_count,
            "logical_cells": expected_h_count * expected_t_count,
        }
        if dimensions != expected_dimensions:
            raise MatrixError(
                f"incorrect current_dimensions: {dimensions}; "
                f"expected {expected_dimensions}"
            )

    except MatrixError as exc:
        print(
            f"JANUS_INVERSION_MATRIX_VALIDATION = FAIL\nERROR = {exc}",
            file=sys.stderr,
        )
        return 1

    print("JANUS_INVERSION_MATRIX_VALIDATION = PASS")
    print(f"INHERITED_HYPOTHESES = {len(inherited)}")
    print(f"CYCLE_DESCENDANTS = {len(new)}")
    print(f"INVERSION_TESTS = {len(selected_t)}")
    print(f"LOGICAL_MATRIX_CELLS = {len(expected_pairs)}")
    print(f"NON_DEFAULT_CELLS = {len(overrides)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
