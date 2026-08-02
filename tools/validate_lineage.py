#!/usr/bin/env python3
"""Validate JANUS inheritance and append-only reverse lineage."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"


class LineageError(RuntimeError):
    pass


def load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LineageError(f"cannot read {path.relative_to(ROOT)}: {exc}") from exc


def collect(pattern: str, key: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    paths = sorted(REGISTRY.glob(pattern))
    if not paths:
        raise LineageError(f"no files match {pattern}")
    for path in paths:
        payload = load(path)
        value = payload.get(key)
        if not isinstance(value, list):
            raise LineageError(f"{path.relative_to(ROOT)} lacks list field {key!r}")
        items.extend(value)
    return items


def number(hid: str) -> int:
    if not isinstance(hid, str) or not hid.startswith("H") or not hid[1:].isdigit():
        raise LineageError(f"invalid hypothesis id in lineage: {hid!r}")
    return int(hid[1:])


def main() -> int:
    try:
        schema = load(REGISTRY / "schema.json")
        inheritance_from = int(
            schema.get("inheritance_requirement_from_hypothesis_number", 10**9)
        )
        reverse_from = int(
            schema.get("reverse_lineage_requirement_from_hypothesis_number", 10**9)
        )
        reverse_file = schema.get("reverse_lineage_file")

        hypotheses = collect("hypotheses*.json", "hypotheses")
        genealogy = collect("genealogy*.json", "nodes")

        hypothesis_by_id = {item.get("id"): item for item in hypotheses}
        if len(hypothesis_by_id) != len(hypotheses):
            raise LineageError("duplicate historical hypothesis id")

        node_by_id = {item.get("id"): item for item in genealogy}
        if len(node_by_id) != len(genealogy):
            raise LineageError("duplicate genealogy node id")

        checked = 0
        reverse_checked = 0
        for hid, item in hypothesis_by_id.items():
            if number(hid) < inheritance_from:
                continue
            checked += 1

            parents = item.get("derived_from")
            delta = item.get("delta_from_parents")
            if not isinstance(parents, list) or not parents:
                raise LineageError(f"{hid} has no nonempty derived_from list")
            if len(set(parents)) != len(parents):
                raise LineageError(f"{hid} repeats a parent")
            if not isinstance(delta, str) or not delta.strip():
                raise LineageError(f"{hid} has empty delta_from_parents")

            for parent in parents:
                if parent not in hypothesis_by_id:
                    raise LineageError(f"{hid} references unknown parent {parent}")
                if number(parent) >= number(hid):
                    raise LineageError(f"{hid} parent {parent} is not older")

            node = node_by_id.get(hid)
            if node is None:
                raise LineageError(f"{hid} has no genealogy node")
            if node.get("parents") != parents:
                raise LineageError(
                    f"{hid} genealogy parents {node.get('parents')!r} "
                    f"do not match derived_from {parents!r}"
                )
            if node.get("relation") != delta:
                raise LineageError(
                    f"{hid} genealogy relation differs from delta_from_parents"
                )

        if reverse_from < 10**9:
            if not isinstance(reverse_file, str) or not reverse_file:
                raise LineageError("schema requires reverse lineage but names no file")
            reverse_payload = load(REGISTRY / reverse_file)
            reverse_map = reverse_payload.get("children_by_parent")
            if not isinstance(reverse_map, dict):
                raise LineageError(f"{reverse_file} lacks children_by_parent object")

            normalized: dict[str, list[str]] = {}
            for parent, children in reverse_map.items():
                if parent not in hypothesis_by_id:
                    raise LineageError(f"reverse lineage has unknown parent {parent}")
                if not isinstance(children, list) or not children:
                    raise LineageError(
                        f"reverse lineage parent {parent} has no child list"
                    )
                if len(set(children)) != len(children):
                    raise LineageError(
                        f"reverse lineage parent {parent} repeats a child"
                    )
                for child in children:
                    if child not in hypothesis_by_id:
                        raise LineageError(
                            f"reverse lineage {parent} references unknown child {child}"
                        )
                    if number(child) < reverse_from:
                        raise LineageError(
                            f"reverse lineage file may not rewrite historical child {child}"
                        )
                normalized[parent] = children

            for child, item in hypothesis_by_id.items():
                if number(child) < reverse_from:
                    continue
                reverse_checked += 1
                for parent in item["derived_from"]:
                    if child not in normalized.get(parent, []):
                        raise LineageError(
                            f"reverse lineage missing edge {parent} -> {child}"
                        )

            for parent, children in normalized.items():
                for child in children:
                    if parent not in hypothesis_by_id[child].get("derived_from", []):
                        raise LineageError(
                            f"reverse lineage has extra edge {parent} -> {child}"
                        )

    except LineageError as exc:
        print(f"JANUS_LINEAGE_VALIDATION = FAIL\nERROR = {exc}", file=sys.stderr)
        return 1

    print("JANUS_LINEAGE_VALIDATION = PASS")
    print(f"INHERITED_HYPOTHESES = {checked}")
    print(f"REVERSE_INDEXED_HYPOTHESES = {reverse_checked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
