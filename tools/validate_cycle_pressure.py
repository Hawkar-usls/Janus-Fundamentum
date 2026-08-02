#!/usr/bin/env python3
"""Validate attack pressure and terminal discipline for cycle C009."""

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
        hypotheses = load("hypotheses-c009.json")["hypotheses"]
        attacks = load("attacks-c009.json")["attacks"]
        graveyard = load("graveyard-c009.json")["entries"]
        expected_h = {f"H{i:03d}" for i in range(75, 84)}
        if {item["id"] for item in hypotheses} != expected_h:
            raise PressureError("C009 must contain exactly H075-H083")
        by_target: dict[str, list[dict]] = {}
        for item in attacks:
            by_target.setdefault(item["hypothesis_id"], []).append(item)
        for hid in expected_h:
            if len(by_target.get(hid, [])) < 3:
                raise PressureError(f"{hid} has fewer than three C009 attacks")
        inherited_targets = {"H045", "H062", "H070", "H071", "H072", "H073", "H074"}
        missing_targets = sorted(hid for hid in inherited_targets if hid not in by_target)
        if missing_targets:
            raise PressureError(f"inherited targets received no C009 attack: {missing_targets}")
        if len(attacks) < 40:
            raise PressureError("C009 must register at least forty attacks")
        terminal = {item["id"]: item for item in graveyard}
        h074 = terminal.get("H074")
        if not h074 or h074.get("terminal_status") != "REJECTED":
            raise PressureError("H074 must be terminally rejected")
        decisive_ids = set(h074.get("decisive_attacks", []))
        decisive = {item["id"] for item in attacks if item["decisive"] and item["hypothesis_id"] == "H074"}
        if decisive_ids != decisive or decisive_ids != {"A203", "A204"}:
            raise PressureError("H074 decisive attack linkage is inconsistent")
    except PressureError as exc:
        print(f"JANUS_C009_PRESSURE_VALIDATION = FAIL\nERROR = {exc}", file=sys.stderr)
        return 1

    print("JANUS_C009_PRESSURE_VALIDATION = PASS")
    print(f"C009_HYPOTHESES = {len(hypotheses)}")
    print(f"C009_ATTACKS = {len(attacks)}")
    print(f"INHERITED_TARGETS_REATTACKED = {len(inherited_targets)}")
    print("TERMINAL_RESULT = H074:REJECTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
