#!/usr/bin/env python3
"""Validate the JANUS machine-readable proof-search registry.

All major ledgers are modular. Historical hypothesis snapshots are append-only:
a later graveyard entry terminally shadows an earlier live record without deleting
or rewriting the cycle in which it was proposed.
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
SCHEMA_PATH = REGISTRY / "schema.json"


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


def load_modular(pattern: str, key: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    paths = sorted(REGISTRY.glob(pattern))
    if not paths:
        raise RegistryError(f"no registry files match {pattern}")
    payloads = {path.name: load_json(path) for path in paths}
    items: list[dict[str, Any]] = []
    for path in paths:
        payload = payloads[path.name]
        value = payload.get(key)
        if not isinstance(value, list):
            raise RegistryError(f"{path.relative_to(ROOT)} has no list field {key!r}")
        items.extend(value)
    return items, payloads


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


def validate() -> tuple[str, int, int]:
    schema = load_json(SCHEMA_PATH)

    hypotheses, hypothesis_payloads = load_modular("hypotheses*.json", "hypotheses")
    attacks, attack_payloads = load_modular("attacks*.json", "attacks")
    graveyard, graveyard_payloads = load_modular("graveyard*.json", "entries")
    observations, observation_payloads = load_modular("observations*.json", "observations")
    cycles, journal_payloads = load_modular("journal*.json", "cycles")
    genealogy, genealogy_payloads = load_modular("genealogy*.json", "nodes")
    references, reference_payloads = load_modular("references*.json", "references")

    required_h = schema["required_hypothesis_fields"]
    required_a = schema["required_attack_fields"]
    required_r = schema["required_reference_fields"]
    live_statuses = set(schema["allowed_hypothesis_statuses"])
    terminal_statuses = set(schema["allowed_terminal_statuses"])
    attack_results = set(schema["allowed_attack_results"])
    reproduction_levels = set(schema["allowed_reproducibility_levels"])
    h_pattern = re.compile(schema["id_patterns"]["hypothesis"])
    a_pattern = re.compile(schema["id_patterns"]["attack"])
    o_pattern = re.compile(schema["id_patterns"]["observation"])
    c_pattern = re.compile(schema["id_patterns"]["cycle"])
    r_pattern = re.compile(schema["id_patterns"]["reference"])

    raw_hypothesis_ids = unique_ids(hypotheses, "historical hypothesis")
    attack_ids = unique_ids(attacks, "attack")
    graveyard_ids = unique_ids(graveyard, "graveyard")
    unique_ids(observations, "observation")
    unique_ids(cycles, "cycle")
    reference_ids = unique_ids(references, "reference")

    # A graveyard record terminally shadows an earlier historical hypothesis.
    live_hypotheses = [item for item in hypotheses if item["id"] not in graveyard_ids]
    live_hypothesis_ids = {item["id"] for item in live_hypotheses}
    all_hypothesis_ids = raw_hypothesis_ids | graveyard_ids
    terminal_shadows = raw_hypothesis_ids & graveyard_ids

    for item in hypotheses:
        hid = item["id"]
        require_fields(item, required_h, hid)
        if not h_pattern.fullmatch(hid):
            raise RegistryError(f"invalid hypothesis id format: {hid}")
        if item["status"] not in live_statuses:
            raise RegistryError(f"{hid} has invalid historical status: {item['status']}")
        if item["reproducibility"] not in reproduction_levels:
            raise RegistryError(f"{hid} has invalid reproducibility level")
        if item["status"] == "PROVED" and item["reproducibility"] != "R5":
            raise RegistryError(f"{hid}: PROVED requires R5")
        if not item["falsification_conditions"]:
            raise RegistryError(f"{hid} has no falsification conditions")
        for aid in item["registered_attacks"]:
            if aid not in attack_ids:
                raise RegistryError(f"{hid} references missing attack {aid}")
        for rid in item.get("literature_refs", []):
            if rid not in reference_ids:
                raise RegistryError(f"{hid} references missing literature source {rid}")

    for item in attacks:
        aid = item["id"]
        require_fields(item, required_a, aid)
        if not a_pattern.fullmatch(aid):
            raise RegistryError(f"invalid attack id format: {aid}")
        if item["hypothesis_id"] not in all_hypothesis_ids:
            raise RegistryError(f"{aid} references unknown hypothesis {item['hypothesis_id']}")
        if item["result"] not in attack_results:
            raise RegistryError(f"{aid} has invalid result: {item['result']}")
        if item["decisive"] and item["result"] != "DESTROYED":
            raise RegistryError(f"{aid}: decisive attack must have result DESTROYED")

    for item in graveyard:
        gid = item["id"]
        status = item.get("terminal_status")
        if status not in terminal_statuses:
            raise RegistryError(f"{gid} has invalid terminal status: {status}")
        if not item.get("reason"):
            raise RegistryError(f"{gid} has no terminal reason")
        for aid in item.get("decisive_attacks", []):
            if aid not in attack_ids:
                raise RegistryError(f"{gid} references missing decisive attack {aid}")
            attack = next(entry for entry in attacks if entry["id"] == aid)
            if attack["hypothesis_id"] != gid or not attack["decisive"]:
                raise RegistryError(f"{gid} has invalid decisive attack reference {aid}")

    for item in observations:
        if not o_pattern.fullmatch(item["id"]):
            raise RegistryError(f"invalid observation id format: {item['id']}")

    # Cycles are historical snapshots, so an old survivor may now be terminal.
    for item in cycles:
        if not c_pattern.fullmatch(item["id"]):
            raise RegistryError(f"invalid cycle id format: {item['id']}")
        for hid in item.get("surviving_hypotheses", []):
            if hid not in all_hypothesis_ids:
                raise RegistryError(f"{item['id']} references unknown historical survivor {hid}")
        for hid in item.get("destroyed_or_rejected", []):
            if hid not in graveyard_ids:
                raise RegistryError(f"{item['id']} references missing graveyard entry {hid}")
        for aid in item.get("attacks", []):
            if aid not in attack_ids:
                raise RegistryError(f"{item['id']} references missing attack {aid}")

    for item in references:
        rid = item["id"]
        require_fields(item, required_r, rid)
        if not r_pattern.fullmatch(rid):
            raise RegistryError(f"invalid reference id format: {rid}")
        if not isinstance(item["url"], str) or not item["url"].startswith("https://"):
            raise RegistryError(f"{rid} has invalid URL")
        for hid in item["supports"]:
            if hid not in all_hypothesis_ids:
                raise RegistryError(f"{rid} supports unknown hypothesis {hid}")

    genealogy_ids = unique_ids(genealogy, "genealogy node")
    active_genealogy_ids = genealogy_ids - graveyard_ids
    if active_genealogy_ids != live_hypothesis_ids:
        missing = sorted(live_hypothesis_ids - active_genealogy_ids)
        extra = sorted(active_genealogy_ids - live_hypothesis_ids)
        raise RegistryError(f"active genealogy mismatch; missing={missing}, extra={extra}")
    for node in genealogy:
        if node["id"] not in all_hypothesis_ids:
            raise RegistryError(f"genealogy has unknown node {node['id']}")
        for parent in node.get("parents", []):
            if parent not in all_hypothesis_ids:
                raise RegistryError(f"{node['id']} has unknown parent {parent}")
        for child in node.get("children", []):
            if child not in all_hypothesis_ids:
                raise RegistryError(f"{node['id']} has unknown child {child}")

    payloads = {
        "schema": schema,
        "hypothesis_files": hypothesis_payloads,
        "attack_files": attack_payloads,
        "graveyard_files": graveyard_payloads,
        "observation_files": observation_payloads,
        "journal_files": journal_payloads,
        "genealogy_files": genealogy_payloads,
        "reference_files": reference_payloads,
    }
    return canonical_digest(payloads), len(live_hypothesis_ids), len(terminal_shadows)


def main() -> int:
    try:
        digest, live_count, terminal_shadow_count = validate()
    except RegistryError as exc:
        print(f"JANUS_REGISTRY_VALIDATION = FAIL\nERROR = {exc}", file=sys.stderr)
        return 1

    print("JANUS_REGISTRY_VALIDATION = PASS")
    print(f"LIVE_HYPOTHESES = {live_count}")
    print(f"TERMINAL_SHADOWS = {terminal_shadow_count}")
    print(f"CANONICAL_SHA256 = {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
