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

SCOPED_PASS_DECISIONS = {
    "PASS_SCOPED_GAP_CONFIRMED",
    "PASS_NEW_BARRIER_SCOPE_CONFIRMED",
}

CLOSED_ROUTE_STATUSES = {
    "SOURCE_BOUND",
    "SOLVED_POLY_ISLAND",
    "FALSIFIED",
    "BLOCKED_THEOREM_LEVEL",
    "SOURCE_BOUND_LANGUAGE_COLLISION",
    "BLOCKED_WITHOUT_ALPHABET_LIFT",
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


def require_nonempty_string(entry: dict[str, Any], field: str) -> str:
    value = entry.get(field)
    if not isinstance(value, str) or not value.strip():
        raise GateError(f"{entry.get('id','<audit>')} requires non-empty {field}")
    return value


def validate_semantic_route(owner: str, route: Any) -> None:
    if not isinstance(route, dict):
        raise GateError(f"{owner} requires semantic_route object")
    for field in ("problem", "domain", "semantics", "complexity_target"):
        value = route.get(field)
        if not isinstance(value, str) or not value.strip():
            raise GateError(f"{owner} semantic_route missing/invalid {field}")
    promises = route.get("promises")
    if not isinstance(promises, list) or any(
        not isinstance(x, str) or not x.strip() for x in promises
    ):
        raise GateError(f"{owner} semantic_route promises must be a string list")


def semantic_key(route: dict[str, Any]) -> str:
    return json.dumps(route, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


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

    if entry.get("new_math_authorized") is True:
        require_nonempty_string(entry, "route_fingerprint")
        validate_semantic_route(aid, entry.get("semantic_route"))
        if entry.get("loop_check_status") != "PASS_NO_LOOP":
            raise GateError(
                f"{aid}: authorized work requires loop_check_status=PASS_NO_LOOP"
            )
        require_nonempty_string(entry, "authorized_scope")

    if change_class in NEW_MATH_CLASSES:
        if entry.get("new_math_authorized") is not True:
            raise GateError(f"{aid}: NEW_MATH requires new_math_authorized=true")
        auth = entry.get("authorizing_audit_id")
        if not isinstance(auth, str) or not auth:
            raise GateError(f"{aid}: NEW_MATH requires authorizing_audit_id")
        if decision not in SCOPED_PASS_DECISIONS:
            raise GateError(
                f"{aid}: NEW_MATH requires a scoped PASS decision, not {decision}"
            )
        require_nonempty_string(entry, "scope_id")
        require_nonempty_string(entry, "novelty_delta")
        require_nonempty_string(entry, "progress_claim")
        require_nonempty_list(entry, "predecessor_ids", 1)


    if change_class in NONMATH_CLASSES:
        reason = entry.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise GateError(f"{aid}: non-math change requires reason")

    if change_class == "SOURCE_AUDIT_ONLY" and entry.get("new_math_authorized") is True:
        if decision not in {
            "PASS_SCOPED_GAP_CONFIRMED",
            "PASS_NEW_BARRIER_SCOPE_CONFIRMED",
        }:
            raise GateError(
                f"{aid}: SOURCE_AUDIT_ONLY may authorize later new math only after a scoped PASS"
            )


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

    no_loop = ledger.get("no_loop")
    if not isinstance(no_loop, dict):
        raise GateError("ledger missing no_loop policy block")
    if no_loop.get("invariant") != "NO_CLOSED_ROUTE_REENTRY_WITHOUT_EXPLICIT_REAUDIT":
        raise GateError("ledger no_loop invariant is missing or changed")
    closed_routes = no_loop.get("closed_routes")
    if not isinstance(closed_routes, list):
        raise GateError("ledger no_loop.closed_routes must be a list")

    closed_by_fingerprint: dict[str, list[str]] = {}
    closed_by_semantics: dict[str, list[str]] = {}
    closed_ids: set[str] = set()
    for route in closed_routes:
        if not isinstance(route, dict):
            raise GateError("closed route entries must be objects")
        rid = route.get("id")
        fp = route.get("fingerprint")
        status = route.get("status")
        authority = route.get("authority")
        if not isinstance(rid, str) or not rid:
            raise GateError("closed route missing id")
        if rid in closed_ids:
            raise GateError(f"duplicate closed route id {rid}")
        closed_ids.add(rid)
        if not isinstance(fp, str) or not fp:
            raise GateError(f"{rid}: closed route missing fingerprint")
        if status not in CLOSED_ROUTE_STATUSES:
            raise GateError(f"{rid}: unsupported closed route status {status!r}")
        if not isinstance(authority, str) or not authority.strip():
            raise GateError(f"{rid}: closed route missing authority")
        validate_semantic_route(rid, route.get("semantic_route"))
        closed_by_fingerprint.setdefault(fp, []).append(rid)
        closed_by_semantics.setdefault(
            semantic_key(route["semantic_route"]), []
        ).append(rid)

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

    # Every active authorization is bound to one exact semantic route and must not
    # silently reopen a tombstoned route.
    for entry in audits:
        if entry.get("new_math_authorized") is not True:
            continue
        fp = entry["route_fingerprint"]
        skey = semantic_key(entry["semantic_route"])
        collided = set(closed_by_fingerprint.get(fp, []))
        collided.update(closed_by_semantics.get(skey, []))
        if collided:
            supersedes = set(entry.get("supersedes_closed_route_ids", []))
            reopen_basis = entry.get("reopen_basis")
            if (
                not collided.issubset(supersedes)
                or not isinstance(reopen_basis, str)
                or not reopen_basis.strip()
            ):
                raise GateError(
                    f"{entry['id']}: semantic route collides with closed route(s) "
                    f"{sorted(collided)}; explicit re-audit supersession + "
                    "reopen_basis required"
                )

    # A new-math entry must point to a separate completed audit and remain
    # exactly inside that audit's semantic route and scope.
    seen_new_fp: dict[str, str] = {}
    seen_new_semantics: dict[str, str] = {}
    for entry in audits:
        if entry["change_class"] not in NEW_MATH_CLASSES:
            continue
        auth_id = entry["authorizing_audit_id"]
        if auth_id == entry["id"]:
            raise GateError(f"{entry['id']}: audit cannot authorize itself")
        auth = ids.get(auth_id)
        if auth is None:
            raise GateError(f"{entry['id']}: missing authorizing audit {auth_id}")
        if auth.get("decision") not in SCOPED_PASS_DECISIONS:
            raise GateError(
                f"{entry['id']}: authorizing audit {auth_id} "
                "is not a completed scoped PASS"
            )
        if auth.get("new_math_authorized") is not True:
            raise GateError(
                f"{entry['id']}: authorizing audit {auth_id} "
                "does not authorize new math"
            )
        if entry.get("scope_id") != auth.get("authorized_scope"):
            raise GateError(
                f"{entry['id']}: scope_id {entry.get('scope_id')!r} does not "
                f"exactly match authorizing scope {auth.get('authorized_scope')!r}"
            )
        if entry.get("route_fingerprint") != auth.get("route_fingerprint"):
            raise GateError(
                f"{entry['id']}: route_fingerprint differs from "
                f"authorizing audit {auth_id}"
            )
        if entry.get("semantic_route") != auth.get("semantic_route"):
            raise GateError(
                f"{entry['id']}: semantic_route differs from authorizing audit "
                f"{auth_id}; changed semantics require a new pre-math audit"
            )
        if auth_id not in entry.get("predecessor_ids", []):
            raise GateError(
                f"{entry['id']}: predecessor_ids must include "
                f"authorizing audit {auth_id}"
            )

        fp = entry["route_fingerprint"]
        skey = semantic_key(entry["semantic_route"])
        prior = seen_new_fp.get(fp) or seen_new_semantics.get(skey)
        if prior is not None and entry.get("continuation_of") != prior:
            raise GateError(
                f"{entry['id']}: route already used by {prior}; "
                "continuation_of must explicitly chain same-route work"
            )
        seen_new_fp[fp] = entry["id"]
        seen_new_semantics[skey] = entry["id"]


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
    print("NO_LOOP_INVARIANT = NO_CLOSED_ROUTE_REENTRY_WITHOUT_EXPLICIT_REAUDIT")
    print("SCOPE_BINDING = EXACT_SEMANTIC_ROUTE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
