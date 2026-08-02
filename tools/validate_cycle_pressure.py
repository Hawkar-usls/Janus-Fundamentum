#!/usr/bin/env python3
"""Validate schema-selected attack pressure for the current JANUS cycle."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"


class PressureError(RuntimeError):
    pass


def load(name: str) -> dict:
    try:
        return json.loads((REGISTRY / name).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PressureError(f"cannot read {name}: {exc}") from exc


def collect(pattern: str, key: str) -> list[dict]:
    result: list[dict] = []
    for path in sorted(REGISTRY.glob(pattern)):
        payload = load(path.name)
        values = payload.get(key)
        if not isinstance(values, list):
            raise PressureError(f"{path.name} lacks list field {key!r}")
        result.extend(values)
    return result


def main() -> int:
    try:
        schema = load("schema.json")
        policy = schema.get("cycle_pressure_policy")
        if not isinstance(policy, dict):
            raise PressureError("schema lacks cycle_pressure_policy")

        hypotheses = load(policy["hypothesis_file"])["hypotheses"]
        attacks = load(policy["attack_file"])["attacks"]
        expected_h = set(policy["expected_hypothesis_ids"])
        minimum_per_h = int(policy["minimum_attacks_per_new_hypothesis"])
        minimum_total = int(policy["minimum_total_attacks"])
        inherited_targets = set(policy["reattacked_inherited_targets"])
        expected_decisive = set(policy.get("expected_decisive_attacks", []))
        expected_terminal = set(policy.get("expected_terminal_ids", []))

        actual_h = {item["id"] for item in hypotheses}
        if actual_h != expected_h:
            raise PressureError(
                f"cycle hypotheses mismatch; expected={sorted(expected_h)}, "
                f"actual={sorted(actual_h)}"
            )

        by_target: dict[str, list[dict]] = {}
        by_id: dict[str, dict] = {}
        for item in attacks:
            aid = item["id"]
            if aid in by_id:
                raise PressureError(f"duplicate current-cycle attack id {aid}")
            by_id[aid] = item
            by_target.setdefault(item["hypothesis_id"], []).append(item)

        for hid in expected_h:
            count = len(by_target.get(hid, []))
            if count < minimum_per_h:
                raise PressureError(
                    f"{hid} has {count} current-cycle attacks; "
                    f"minimum is {minimum_per_h}"
                )

        missing_targets = sorted(
            hid for hid in inherited_targets if hid not in by_target
        )
        if missing_targets:
            raise PressureError(
                f"inherited targets received no current-cycle attack: "
                f"{missing_targets}"
            )

        if len(attacks) < minimum_total:
            raise PressureError(
                f"cycle has {len(attacks)} attacks; minimum is {minimum_total}"
            )

        decisive = {item["id"] for item in attacks if item.get("decisive")}
        if decisive != expected_decisive:
            raise PressureError(
                f"decisive attack mismatch; expected={sorted(expected_decisive)}, "
                f"actual={sorted(decisive)}"
            )
        decisive_targets = {by_id[aid]["hypothesis_id"] for aid in decisive}
        if decisive_targets != expected_terminal:
            raise PressureError(
                f"terminal target mismatch; expected={sorted(expected_terminal)}, "
                f"actual={sorted(decisive_targets)}"
            )

        graveyard = collect("graveyard*.json", "entries")
        graveyard_by_id = {item.get("id"): item for item in graveyard}
        for hid in expected_terminal:
            entry = graveyard_by_id.get(hid)
            if entry is None:
                raise PressureError(f"expected terminal id lacks graveyard entry: {hid}")
            linked = set(entry.get("decisive_attacks", []))
            required = {
                aid for aid in expected_decisive if by_id[aid]["hypothesis_id"] == hid
            }
            if not required <= linked:
                raise PressureError(
                    f"graveyard entry {hid} does not link decisive attacks "
                    f"{sorted(required - linked)}"
                )

    except PressureError as exc:
        print(
            f"JANUS_CYCLE_PRESSURE_VALIDATION = FAIL\nERROR = {exc}",
            file=sys.stderr,
        )
        return 1

    print("JANUS_CYCLE_PRESSURE_VALIDATION = PASS")
    print(f"CYCLE_ID = {policy['cycle_id']}")
    print(f"CYCLE_HYPOTHESES = {len(hypotheses)}")
    print(f"CYCLE_ATTACKS = {len(attacks)}")
    print(f"INHERITED_TARGETS_REATTACKED = {len(inherited_targets)}")
    print(f"DECISIVE_ATTACKS = {len(decisive)}")
    print(f"TERMINAL_TARGETS = {','.join(sorted(expected_terminal))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
