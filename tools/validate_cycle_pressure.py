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

        actual_h = {item["id"] for item in hypotheses}
        if actual_h != expected_h:
            raise PressureError(
                f"cycle hypotheses mismatch; expected={sorted(expected_h)}, "
                f"actual={sorted(actual_h)}"
            )

        by_target: dict[str, list[dict]] = {}
        for item in attacks:
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

        decisive = [item for item in attacks if item.get("decisive")]
        if decisive:
            raise PressureError(
                "C010 declares no terminal result, so decisive attacks are forbidden"
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
    print("TERMINAL_RESULT = NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
