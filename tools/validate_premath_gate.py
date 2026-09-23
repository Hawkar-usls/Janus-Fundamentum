#!/usr/bin/env python3
"""Enforce the global JANUS pre-math no-duplication gate.

This validator is intentionally process-level. It does not judge whether a theorem
is true. It enforces that every post-activation scientific artifact is accounted
for and that genuinely new mathematics has a completed, separate pre-math audit.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "registry" / "JANUS_P_VS_NP_PREMATH_AUDIT_LEDGER_2026-09-24_v1.0.json"

ALLOWED_DECISIONS = {
    "HOLD_NEW_MATH",
    "SOURCE_BOUND_REUSE",
    "INTERNAL_REUSE",
    "PASS_SCOPED_GAP_CONFIRMED",
    "PASS_NEW_BARRIER_SCOPE_CONFIRMED",
    "EDITORIAL_ONLY",
}

AUTHORIZING_DECISIONS = {
    "PASS_SCOPED_GAP_CONFIRMED",
    "PASS_NEW_BARRIER_SCOPE_CONFIRMED",
    "SOURCE_BOUND_REUSE",
    "INTERNAL_REUSE",
}

NEW_MATH_CLASSES = {
    "NEW_MATH",
    "JANUS_NEW_CANDIDATE_AFTER_AUDIT",
    "JANUS_NEW_BARRIER_AFTER_AUDIT",
}

AUDIT_CLASSES = {
    "SOURCE_AUDIT_ONLY",
    "SOURCE_BOUND_REUSE",
    "INTERNAL_REUSE",
}

NONMATH_CLASSES = {
    "EDITORIAL_OR_IMPLEMENTATION_ONLY",
}


class GateError(RuntimeError):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GateError(f"missing required ledger: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise GateError(
            f"invalid JSON in {path.relative_to(ROOT)} line {exc.lineno}: {exc.msg}"
        ) from exc


def git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise GateError(
            "git command failed: "
            + " ".join(args)
            + "\n"
            + proc.stderr.strip()
        )
    return proc.stdout


def changed_paths_since(baseline: str) -> set[str]:
    try:
        git("cat-file", "-e", f"{baseline}^{{commit}}")
    except GateError as exc:
        raise GateError(
            f"activation baseline {baseline} is unavailable; checkout must use fetch-depth: 0"
        ) from exc

    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", baseline, "HEAD"],
        cwd=ROOT,
        check=False,
    )
    if ancestor.returncode != 0:
        raise GateError(
            f"activation baseline {baseline} is not an ancestor of HEAD; "
            "the gate cannot safely determine post-activation work"
        )

    raw = git("diff", "--name-status", "--find-renames", f"{baseline}..HEAD")
    out: set[str] = set()
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        if status.startswith(("R", "C")) and len(parts) >= 3:
            out.add(parts[1])
            out.add(parts[2])
        elif len(parts) >= 2:
            out.add(parts[1])
    return out


def is_tracked(path: str, prefixes: list[str]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)


def require_nonempty_list(entry: dict[str, Any], field: str, minimum: int = 1) -> None:
    value = entry.get(field)
    if not isinstance(value, list) or len(value) < minimum:
        raise GateError(
            f"{entry.get('id','<audit>')} requires {field} with at least {minimum} item(s)"
        )
    if any(not isinstance(x, str) or not x.strip() for x in value):
        raise GateError(f"{entry.get('id','<audit>')} has invalid values in {field}")


def validate_audit_shape(entry: dict[str, Any]) -> None:
    aid = entry.get("id")
    if not isinstance(aid, str) or not aid:
        raise GateError("audit ledger entry has missing/invalid id")

    decision = entry.get("decision")
    if decision not in ALLOWED_DECISIONS:
        raise GateError(f"{aid} has unsupported decision {decision!r}")

    change_class = entry.get("change_class")
    if not isinstance(change_class, str) or not change_class:
        raise GateError(f"{aid} missing change_class")

    paths = entry.get("artifact_paths")
    if not isinstance(paths, list) or not paths or any(not isinstance(p, str) for p in paths):
        raise GateError(f"{aid} must list artifact_paths")

    if change_class in AUDIT_CLASSES or change_class in NEW_MATH_CLASSES:
        receipt = entry.get("receipt")
        if not isinstance(receipt, str) or not receipt.strip():
            raise GateError(f"{aid} missing receipt")
        receipt_path = ROOT / receipt
        if not receipt_path.is_file():
            raise GateError(f"{aid} receipt does not exist: {receipt}")
        if receipt_path.suffix == ".json":
            receipt_payload = load_json(receipt_path)
            receipt_decision = receipt_payload.get("decision", receipt_payload.get("status"))
            if receipt_decision != decision:
                raise GateError(
                    f"{aid} ledger decision {decision!r} disagrees with receipt "
                    f"{receipt_decision!r} in {receipt}"
                )
            if bool(receipt_payload.get("new_math_authorized", False)) != bool(
                entry.get("new_math_authorized", False)
            ):
                raise GateError(
                    f"{aid} new_math_authorized disagrees with receipt {receipt}"
                )

        canonical = entry.get("canonical_object")
        if not isinstance(canonical, str) or not canonical.strip():
            raise GateError(f"{aid} missing canonical_object")
        require_nonempty_list(entry, "internal_search_terms", 3)
        require_nonempty_list(entry, "external_names", 3)
        require_nonempty_list(entry, "external_queries", 3)
        require_nonempty_list(entry, "sources_checked", 2)
        require_nonempty_list(entry, "collision_status", 1)

    if change_class in NEW_MATH_CLASSES:
        if entry.get("new_math_authorized") is not True:
            raise GateError(f"{aid}: NEW_MATH requires new_math_authorized=true")
        auth = entry.get("authorizing_audit_id")
        if not isinstance(auth, str) or not auth:
            raise GateError(f"{aid}: NEW_MATH requires authorizing_audit_id")
        if decision not in {
            "PASS_SCOPED_GAP_CONFIRMED",
            "PASS_NEW_BARRIER_SCOPE_CONFIRMED",
        }:
            raise GateError(
                f"{aid}: NEW_MATH requires a scoped PASS decision, not {decision}"
            )

    if change_class in NONMATH_CLASSES:
        reason = entry.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise GateError(f"{aid}: non-math change requires reason")

    if change_class == "SOURCE_AUDIT_ONLY" and entry.get("new_math_authorized") is True:
        raise GateError(f"{aid}: SOURCE_AUDIT_ONLY cannot authorize new math by itself")


def validate() -> tuple[int, int, str]:
    ledger = load_json(LEDGER)

    baseline = ledger.get("activation_commit")
    if not isinstance(baseline, str) or len(baseline) < 12:
        raise GateError("ledger has invalid activation_commit")

    prefixes = ledger.get("tracked_prefixes")
    if not isinstance(prefixes, list) or not prefixes:
        raise GateError("ledger has no tracked_prefixes")

    exemptions = set(ledger.get("governance_exempt_paths", []))
    audits = ledger.get("audits")
    if not isinstance(audits, list):
        raise GateError("ledger audits must be a list")

    ids: dict[str, dict[str, Any]] = {}
    coverage: dict[str, str] = {}

    for entry in audits:
        if not isinstance(entry, dict):
            raise GateError("audit ledger entries must be objects")
        validate_audit_shape(entry)
        aid = entry["id"]
        if aid in ids:
            raise GateError(f"duplicate audit id {aid}")
        ids[aid] = entry
        for path in entry["artifact_paths"]:
            if path in coverage:
                raise GateError(
                    f"{path} is covered by multiple audits: {coverage[path]} and {aid}"
                )
            coverage[path] = aid

    # A new-math entry must point to a separate completed audit.
    for entry in audits:
        if entry["change_class"] not in NEW_MATH_CLASSES:
            continue
        auth_id = entry["authorizing_audit_id"]
        if auth_id == entry["id"]:
            raise GateError(f"{entry['id']}: audit cannot authorize itself")
        auth = ids.get(auth_id)
        if auth is None:
            raise GateError(f"{entry['id']}: missing authorizing audit {auth_id}")
        if auth.get("decision") not in {
            "PASS_SCOPED_GAP_CONFIRMED",
            "PASS_NEW_BARRIER_SCOPE_CONFIRMED",
        }:
            raise GateError(
                f"{entry['id']}: authorizing audit {auth_id} is not a completed scoped PASS"
            )
        if auth.get("new_math_authorized") is not True:
            raise GateError(
                f"{entry['id']}: authorizing audit {auth_id} does not authorize new math"
            )

    changed = changed_paths_since(baseline)
    tracked = {
        p for p in changed
        if is_tracked(p, prefixes) and p not in exemptions
    }

    missing = sorted(p for p in tracked if p not in coverage)
    if missing:
        raise GateError(
            "post-activation scientific artifacts are not covered by the pre-math ledger:\n"
            + "\n".join(f"  - {p}" for p in missing)
        )

    # Prevent ledger entries from silently pointing at unrelated/nonexistent current files,
    # except deletion records explicitly marked editorial.
    for path, aid in coverage.items():
        entry = ids[aid]
        if path in changed:
            continue
        if entry.get("change_class") != "EDITORIAL_OR_IMPLEMENTATION_ONLY":
            raise GateError(
                f"{aid} covers {path}, but that path is not changed since activation; "
                "remove stale coverage or classify it correctly"
            )

    return len(tracked), len(audits), baseline


def main() -> int:
    try:
        tracked_count, audit_count, baseline = validate()
    except GateError as exc:
        print("JANUS_PREMATH_GATE = FAIL", file=sys.stderr)
        print(f"ERROR = {exc}", file=sys.stderr)
        return 1

    print("JANUS_PREMATH_GATE = PASS")
    print(f"ACTIVATION_BASELINE = {baseline}")
    print(f"TRACKED_POST_ACTIVATION_ARTIFACTS = {tracked_count}")
    print(f"AUDIT_LEDGER_ENTRIES = {audit_count}")
    print("INVARIANT = NO_AUDIT_NO_NEW_MATH")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
