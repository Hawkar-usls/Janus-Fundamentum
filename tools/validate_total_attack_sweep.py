#!/usr/bin/env python3
"""Validate the historical C012 breadth-first attack snapshot.

Later cycles may add descendants or terminally shadow C012 survivors. Coverage is
therefore checked against the hypothesis-number and terminal snapshot declared
in schema.json, not against the repository's present live set.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"


class SweepError(RuntimeError):
    pass


def load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SweepError(f"missing file: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SweepError(
            f"invalid JSON in {path.relative_to(ROOT)} at "
            f"line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc


def collect(pattern: str, key: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    paths = sorted(REGISTRY.glob(pattern))
    if not paths:
        raise SweepError(f"no files match {pattern}")
    for path in paths:
        payload = load(path)
        values = payload.get(key)
        if not isinstance(values, list):
            raise SweepError(f"{path.relative_to(ROOT)} lacks list field {key!r}")
        items.extend(values)
    return items


def hnum(hid: str) -> int:
    if not isinstance(hid, str) or not hid.startswith("H") or not hid[1:].isdigit():
        raise SweepError(f"invalid hypothesis id: {hid!r}")
    return int(hid[1:])


def main() -> int:
    try:
        schema = load(REGISTRY / "schema.json")
        policy = schema.get("total_attack_policy")
        if not isinstance(policy, dict):
            raise SweepError("schema lacks total_attack_policy")

        sweep_path = REGISTRY / policy["campaign_file"]
        protocol_path = REGISTRY / policy["protocol_file"]
        sweep = load(sweep_path)
        protocol_payload = load(protocol_path)

        hypotheses = collect("hypotheses*.json", "hypotheses")
        graveyard = collect("graveyard*.json", "entries")
        historical_ids = {item.get("id") for item in hypotheses}
        all_terminal_ids = {item.get("id") for item in graveyard}
        if None in historical_ids or None in all_terminal_ids:
            raise SweepError("hypothesis or graveyard entry has no id")

        snapshot_max = int(policy["snapshot_max_hypothesis_number"])
        terminal_at_snapshot = set(policy["terminal_ids_at_snapshot"])
        if not terminal_at_snapshot <= all_terminal_ids:
            raise SweepError(
                "historical terminal snapshot names an id absent from the current graveyard"
            )
        snapshot_historical = {
            hid for hid in historical_ids if hnum(hid) <= snapshot_max
        }
        snapshot_live = snapshot_historical - terminal_at_snapshot

        listed_live = sweep.get("live_hypothesis_ids")
        if not isinstance(listed_live, list):
            raise SweepError("campaign lacks live_hypothesis_ids list")
        if len(listed_live) != len(set(listed_live)):
            raise SweepError("campaign repeats a snapshot hypothesis id")
        if set(listed_live) != snapshot_live:
            missing = sorted(snapshot_live - set(listed_live))
            extra = sorted(set(listed_live) - snapshot_live)
            raise SweepError(
                f"campaign/snapshot mismatch; missing={missing}, extra={extra}"
            )
        if any(hid in terminal_at_snapshot for hid in listed_live):
            raise SweepError("snapshot terminal shadow included in C012 sweep")

        protocols = protocol_payload.get("protocols")
        if not isinstance(protocols, list):
            raise SweepError("protocol file lacks protocols list")
        protocol_ids: list[str] = []
        for item in protocols:
            for field in ("id", "title", "method", "failure_signal"):
                value = item.get(field)
                if not isinstance(value, str) or not value.strip():
                    raise SweepError(f"protocol has empty {field}: {item!r}")
            protocol_ids.append(item["id"])
        if len(protocol_ids) != len(set(protocol_ids)):
            raise SweepError("duplicate protocol id")
        if sweep.get("protocol_ids") != protocol_ids:
            raise SweepError("campaign protocol order differs from protocol ledger")

        allowed_results = set(schema.get("allowed_attack_results", []))
        default_result = sweep.get("default_cell_result")
        if default_result not in allowed_results:
            raise SweepError(f"invalid default cell result: {default_result!r}")

        cells: dict[tuple[str, str], str] = {
            (hid, pid): default_result for hid in listed_live for pid in protocol_ids
        }
        override_pairs: set[tuple[str, str]] = set()
        for override in sweep.get("overrides", []):
            pair = (override.get("hypothesis_id"), override.get("protocol_id"))
            if pair in override_pairs:
                raise SweepError(f"duplicate campaign override: {pair}")
            override_pairs.add(pair)
            if pair not in cells:
                raise SweepError(f"override references unknown cell: {pair}")
            result = override.get("result")
            if result not in allowed_results or result == default_result:
                raise SweepError(f"invalid or redundant override result {result!r}: {pair}")
            note = override.get("note")
            if not isinstance(note, str) or not note.strip():
                raise SweepError(f"override lacks explanatory note: {pair}")
            cells[pair] = result

        cell_counts = Counter(cells.values())
        clean: list[str] = []
        conflicted: list[str] = []
        pressured: list[str] = []
        destroyed: list[str] = []
        for hid in listed_live:
            results = {cells[(hid, pid)] for pid in protocol_ids}
            if "DESTROYED" in results:
                destroyed.append(hid)
            elif "WEAKENED" in results:
                pressured.append(hid)
            elif "INCONCLUSIVE" in results:
                conflicted.append(hid)
            else:
                clean.append(hid)

        actual_summary = {
            "live_hypotheses": len(listed_live),
            "protocols": len(protocol_ids),
            "logical_attack_cells": len(cells),
            "clean_survivors": len(clean),
            "conflicted_survivors": len(conflicted),
            "pressured_survivors": len(pressured),
            "destroyed_or_rejected": len(destroyed),
            "cell_results": {
                result: cell_counts.get(result, 0)
                for result in ("SURVIVED", "INCONCLUSIVE", "WEAKENED", "DESTROYED")
            },
        }
        expected_summary = sweep.get("summary_expected")
        if actual_summary != expected_summary:
            raise SweepError(
                f"summary mismatch; actual={actual_summary}, expected={expected_summary}"
            )

        expected_live = int(policy["expected_live_hypotheses"])
        expected_protocols = int(policy["expected_protocols"])
        expected_cells = int(policy["expected_logical_cells"])
        if len(listed_live) != expected_live:
            raise SweepError(
                f"snapshot count {len(listed_live)} differs from policy {expected_live}"
            )
        if len(protocol_ids) != expected_protocols:
            raise SweepError(
                f"protocol count {len(protocol_ids)} differs from policy {expected_protocols}"
            )
        if len(cells) != expected_cells:
            raise SweepError(
                f"cell count {len(cells)} differs from policy {expected_cells}"
            )
        if destroyed:
            raise SweepError(
                "a C012 standardized cell cannot terminally remove a hypothesis without "
                "a later decisive attack ledger entry and graveyard shadow"
            )

    except (KeyError, TypeError, ValueError, SweepError) as exc:
        print(f"JANUS_TOTAL_ATTACK_SWEEP = FAIL\nERROR = {exc}", file=sys.stderr)
        return 1

    print("JANUS_TOTAL_ATTACK_SWEEP = PASS")
    print(f"SNAPSHOT_MAX_HYPOTHESIS = H{snapshot_max:03d}")
    print(f"SNAPSHOT_HYPOTHESES_ATTACKED = {len(listed_live)}")
    print(f"ATTACK_PROTOCOLS = {len(protocol_ids)}")
    print(f"LOGICAL_ATTACK_CELLS = {len(cells)}")
    print(f"CLEAN_SURVIVORS_AT_C012 = {len(clean)}")
    print(f"CONFLICTED_SURVIVORS_AT_C012 = {len(conflicted)}")
    print(f"PRESSURED_SURVIVORS_AT_C012 = {len(pressured)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
