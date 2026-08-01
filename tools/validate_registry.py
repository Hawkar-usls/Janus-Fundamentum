#!/usr/bin/env python3
"""Validate the JANUS machine-readable proof-search registry.

The validator checks syntax, IDs, cross-references, status rules, and a stable
SHA-256 digest of the canonical JSON payloads. It uses only the Python standard
library so that independent reproduction is straightforward.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"
FILES = {
    "schema": REGISTRY / "schema.json",
    "hypotheses": REGISTRY / "hypotheses.json",
    "attacks": REGISTRY / "attacks.json",
    "graveyard": REGISTRY / "graveyard.json",
    "observations": REGISTRY / "observations.json",
    "journal": REGISTRY / "journal.json",
    "genealogy": REGISTRY / "genealogy.json",
}


class RegistryError(RuntimeError):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RegistryError(f"missing required file: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise RegistryError(
            f"invalid JSON in {path.relative_to(ROOT)} at line {exc.lineno}, "
            f"column {exc.colno}: {exc.msg}"
        ) from exc


def require_fields(item: dict[str, Any], fields: list[str], label: str) -> None:
    missing = [field for field in fields if field not in item]
    if missing:
        raise RegistryError(f"{label} missing fields: {', '.join(missing)}")


def unique_ids(items: list[dict[str, Any]], label: str) -> set[str]:
    ids: set[str] = set()
    for item in items:
        value = item.get("id")
        if not isinstance(value, str) or not value:
            raise RegistryError(f"{label} contains an invalid id: {value!r}")
        if value in ids:
            raise RegistryError(f"duplicate {label} id: {value}")
        ids.add(value)
    return ids


def canonical_digest(payloads: dict[str, Any]) -> str:
    canonical = json.dumps(
        payloads,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def validate() -> str:
    data = {name: load_json(path) for name, path in FILES.items()}
    schema = data["schema"]

    required_h = schema["required_hypothesis_fields"]
    required_a = schema["required_attack_fields"]
    live_statuses = set(schema["allowed_hypothesis_statuses"])
    terminal_statuses = set(schema["allowed_terminal_statuses"])
    attack_results = set(schema["allowed_attack_results"])
    reproduction_levels = set(schema["allowed_reproducibility_levels"])
    h_pattern = re.compile(schema["id_patterns"]["hypothesis"])
    a_pattern = re.compile(schema["id_patterns"]["attack"])
    o_pattern = re.compile(schema["id_patterns"]["observation"])
    c_pattern = re.compile(schema["id_patterns"]["cycle"])

    hypotheses = data["hypotheses"]["hypotheses"]
    attacks = data["attacks"]["attacks"]
    graveyard = data["graveyard"]["entries"]
    observations = data["observations"]["observations"]
    cycles = data["journal"]["cycles"]
    genealogy = data["genealogy"]["nodes"]

    hypothesis_ids = unique_ids(hypotheses, "hypothesis")
    attack_ids = unique_ids(attacks, "attack")
    graveyard_ids = unique_ids(graveyard, "graveyard")
    observation_ids = unique_ids(observations, "observation")
    cycle_ids = unique_ids(cycles, "cycle")

    for item in hypotheses:
        hid = item["id"]
        require_fields(item, required_h, hid)
        if not h_pattern.fullmatch(hid):
            raise RegistryError(f"invalid hypothesis id format: {hid}")
        if item["status"] not in live_statuses:
            raise RegistryError(f"{hid} has non-live status in hypotheses.json: {item['status']}")
        if item["reproducibility"] not in reproduction_levels:
            raise RegistryError(f"{hid} has invalid reproducibility level")
        if item["status"] == "PROVED" and item["reproducibility"] != "R5":
            raise RegistryError(f"{hid}: PROVED requires R5")
        if not item["falsification_conditions"]:
            raise RegistryError(f"{hid} has no falsification conditions")
        for aid in item["registered_attacks"]:
            if aid not in attack_ids:
                raise RegistryError(f"{hid} references missing attack {aid}")

    all_hypothesis_ids = hypothesis_ids | graveyard_ids
    for item in attacks:
        aid = item["id"]
        require_fields(item, required_a, aid)
        if not a_pattern.fullmatch(aid):
            raise RegistryError(f"invalid attack id format: {aid}")
        if item["hypothesis_id"] not in all_hypothesis_ids:
            raise RegistryError(
                f"{aid} references unknown hypothesis {item['hypothesis_id']}"
            )
        if item["result"] not in attack_results:
            raise RegistryError(f"{aid} has invalid result: {item['result']}")
        if item["decisive"] and item["result"] != "DESTROYED":
            raise RegistryError(f"{aid}: decisive attack must have result DESTROYED")

    for item in graveyard:
        status = item.get("terminal_status")
        if status not in terminal_statuses:
            raise RegistryError(
                f"{item['id']} has invalid terminal status: {status}"
            )
        if not item.get("reason"):
            raise RegistryError(f"{item['id']} has no terminal reason")

    for item in observations:
        if not o_pattern.fullmatch(item["id"]):
            raise RegistryError(f"invalid observation id format: {item['id']}")

    for item in cycles:
        if not c_pattern.fullmatch(item["id"]):
            raise RegistryError(f"invalid cycle id format: {item['id']}")
        for hid in item.get("surviving_hypotheses", []):
            if hid not in hypothesis_ids:
                raise RegistryError(f"{item['id']} references missing survivor {hid}")
        for aid in item.get("attacks", []):
            if aid not in attack_ids:
                raise RegistryError(f"{item['id']} references missing attack {aid}")

    genealogy_ids = unique_ids(genealogy, "genealogy node")
    if genealogy_ids != hypothesis_ids:
        missing = sorted(hypothesis_ids - genealogy_ids)
        extra = sorted(genealogy_ids - hypothesis_ids)
        raise RegistryError(
            f"genealogy mismatch; missing={missing}, extra={extra}"
        )
    for node in genealogy:
        for parent in node.get("parents", []):
            if parent not in all_hypothesis_ids:
                raise RegistryError(f"{node['id']} has unknown parent {parent}")
        for child in node.get("children", []):
            if child not in hypothesis_ids:
                raise RegistryError(f"{node['id']} has unknown child {child}")

    if hypothesis_ids & graveyard_ids:
        overlap = sorted(hypothesis_ids & graveyard_ids)
        raise RegistryError(f"live/graveyard id overlap: {overlap}")

    return canonical_digest(data)


def main() -> int:
    try:
        digest = validate()
    except RegistryError as exc:
        print(f"JANUS_REGISTRY_VALIDATION = FAIL\nERROR = {exc}", file=sys.stderr)
        return 1

    print("JANUS_REGISTRY_VALIDATION = PASS")
    print(f"CANONICAL_SHA256 = {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
