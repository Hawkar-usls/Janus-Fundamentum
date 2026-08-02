#!/usr/bin/env python3
"""Validate the latest JANUS inversion matrix and inherited-hypothesis ratio."""

from __future__ import annotations

import json
import re
import sys
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
    paths = sorted(REGISTRY.glob(pattern))
    if not paths:
        raise MatrixError(f"no files match {pattern}")
    for path in paths:
        payload = load(path)
        value = payload.get(key)
        if not isinstance(value, list):
            raise MatrixError(f"{path.relative_to(ROOT)} lacks list field {key}")
        items.extend(value)
    return items


def hnum(hid: str) -> int:
    match = re.fullmatch(r"H([0-9]+)", hid)
    if not match:
        raise MatrixError(f"invalid hypothesis id: {hid}")
    return int(match.group(1))


def main() -> int:
    try:
        matrix = load(REGISTRY / "inversion-matrix-c009.json")
        hypotheses = load_all("hypotheses*.json", "hypotheses")
        graveyard = load_all("graveyard*.json", "entries")
        test_entries = load_all("inversion-tests*.json", "tests")

        known_h = {item["id"] for item in hypotheses} | {item["id"] for item in graveyard}
        test_ids = [item.get("id") for item in test_entries]
        if len(test_ids) != len(set(test_ids)):
            raise MatrixError("duplicate inversion test id")
        allowed = {
            "UNRUN", "NOT_APPLICABLE", "ACTIVE", "SURVIVED",
            "WEAKENED", "DESTROYED", "BLOCKED"
        }
        selected_h = matrix.get("hypotheses", [])
        selected_t = matrix.get("tests", [])
        overrides = matrix.get("overrides", [])
        default_status = matrix.get("default_cell_status")

        if len(selected_h) != 30 or len(set(selected_h)) != 30:
            raise MatrixError("matrix must contain exactly 30 unique hypotheses")
        if len(selected_t) != 30 or len(set(selected_t)) != 30:
            raise MatrixError("matrix must contain exactly 30 unique tests")
        if selected_t != test_ids:
            raise MatrixError("matrix test order must match modular inversion test ledgers")
        if default_status not in allowed:
            raise MatrixError(f"invalid default cell status: {default_status}")
        missing = sorted(hid for hid in selected_h if hid not in known_h)
        if missing:
            raise MatrixError(f"unknown matrix hypotheses: {missing}")

        inherited = [hid for hid in selected_h if hnum(hid) < 75]
        new = [hid for hid in selected_h if hnum(hid) >= 75]
        if len(inherited) < 21:
            raise MatrixError(
                f"existing-hypothesis reuse too low: {len(inherited)}/30; minimum is 21"
            )
        expected_new = {f"H{i:03d}" for i in range(75, 84)}
        if set(new) != expected_new:
            raise MatrixError(f"unexpected C009 descendants: {sorted(new)}")
        if "H074" in selected_h:
            raise MatrixError("rejected H074 must not remain in the active matrix")

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
                raise MatrixError(f"invalid or redundant status {status!r} for {pair}")
            note = cell.get("note")
            if not isinstance(note, str) or not note.strip():
                raise MatrixError(f"override {pair} must explain its status")

        dims = matrix.get("current_dimensions", {})
        expected_dims = {"hypotheses": 30, "inversion_tests": 30, "logical_cells": 900}
        if dims != expected_dims:
            raise MatrixError(f"incorrect current_dimensions: {dims}")

    except MatrixError as exc:
        print(f"JANUS_INVERSION_MATRIX_VALIDATION = FAIL\nERROR = {exc}", file=sys.stderr)
        return 1

    print("JANUS_INVERSION_MATRIX_VALIDATION = PASS")
    print(f"INHERITED_HYPOTHESES = {len(inherited)}")
    print(f"C009_DESCENDANTS = {len(new)}")
    print(f"INVERSION_TESTS = {len(selected_t)}")
    print(f"LOGICAL_MATRIX_CELLS = {len(expected_pairs)}")
    print(f"NON_DEFAULT_CELLS = {len(overrides)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
