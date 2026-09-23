#!/usr/bin/env python3
"""Enforce JANUS pre-math, canonical-route, and no-loop governance."""

from __future__ import annotations

import hashlib
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
NEW_MATH_CLASSES = {
    "NEW_MATH",
    "JANUS_NEW_CANDIDATE_AFTER_AUDIT",
    "JANUS_NEW_BARRIER_AFTER_AUDIT",
}
AUDIT_CLASSES = {"SOURCE_AUDIT_ONLY", "SOURCE_BOUND_REUSE", "INTERNAL_REUSE"}
NONMATH_CLASSES = {"EDITORIAL_OR_IMPLEMENTATION_ONLY"}
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
ROUTE_FIELDS = {
    "problem_id",
    "domain_atoms",
    "semantics_id",
    "promise_atoms",
    "complexity_target_id",
}
ATOM_CATEGORIES = {
    "problem_id": "problem_ids",
    "domain_atoms": "domain_atoms",
    "semantics_id": "semantics_ids",
    "promise_atoms": "promise_atoms",
    "complexity_target_id": "complexity_target_ids",
}
GRANDFATHERED_INTRODUCER = "GOVERNANCE_MIGRATION_2026_09_24"
GRANDFATHERED_ATOMS = {
    "problem_ids": {
        "RANK3_ALL_OR_NONE_TO_ORDINARY_MATCHING_LOCAL_GADGET",
        "CUBIC_MONOTONE_1IN3_BY_UNIFORM_TREEWIDTH_BOUND",
        "INDEPENDENT_IRREP_EXACT_SOLVE",
    },
    "domain_atoms": {
        "CAYLEY_DIGRAPH",
        "THREE_EXPOSED_TERMINALS",
        "KETTANI_ASSOCIATED_GRAPH",
        "REGULAR_CAYLEY_DIGRAPH",
        "PERMUTATION_MODULE_DECOMPOSITION",
    },
    "semantics_ids": {
        "BOUNDARY_RELATION_000_111",
        "CLAIMED_TREEWIDTH_AT_MOST_6",
        "GROUP_EQUALS_DISJOINT_UNION_S_AND_GENERATOR_INVERSE_TRANSLATES",
        "TWO_LETTER_COORDINATE_ALPHABET_MUST_RECONSTRUCT_EXACTLY",
    },
    "promise_atoms": {
        "ABELIAN_REGULAR_QUOTIENT",
        "P_Q_COMMUTING",
        "Z3_PHASE_PASS",
        "LOCAL_GADGET",
        "SAME_THREE_TERMINAL_INTERFACE",
        "AT_LEAST_3_TRIANGLES_PER_VERTEX",
        "DELTA_AT_MOST_6",
        "K1_4_FREE",
        "RENAMING_OR_NORMAL_FORM_ONLY",
        "IRREP_BLOCK_DIAGONALIZATION_ONLY",
    },
    "complexity_target_ids": {
        "EXACT_CLASSIFICATION",
        "LINEAR_TIME_WITNESS",
        "EXACT_WITNESS_PRESERVING_REPLACEMENT",
        "BOUNDED_TREEWIDTH_SOLVER",
        "NO_NOVELTY_CLAIM",
        "EXACT_SOLVER",
    },
}


class GateError(RuntimeError):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GateError(f"missing required file: {path.relative_to(ROOT)}") from exc
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
            "git command failed: " + " ".join(args) + "\n" + proc.stderr.strip()
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


def valid_atom_name(atom: str) -> bool:
    return bool(atom) and all(ch == "_" or ch.isdigit() or ("A" <= ch <= "Z") for ch in atom)


def validate_atom_catalog(raw: Any) -> dict[str, dict[str, dict[str, str]]]:
    if not isinstance(raw, dict):
        raise GateError("ledger missing semantic_atom_catalog")
    if raw.get("policy") != "CONTROLLED_ATOMS__NEW_ATOMS_REQUIRE_PREMATH_AUDIT":
        raise GateError("semantic_atom_catalog policy missing or changed")
    categories = raw.get("categories")
    if not isinstance(categories, dict):
        raise GateError("semantic_atom_catalog.categories must be an object")
    expected = set(ATOM_CATEGORIES.values())
    if set(categories) != expected:
        raise GateError(
            "semantic_atom_catalog categories must be exactly "
            + ", ".join(sorted(expected))
        )
    for category, atoms in categories.items():
        if not isinstance(atoms, dict) or not atoms:
            raise GateError(f"semantic atom category {category} must be a nonempty object")
        for atom, meta in atoms.items():
            if not isinstance(atom, str) or not valid_atom_name(atom):
                raise GateError(f"invalid controlled semantic atom {category}:{atom!r}")
            if not isinstance(meta, dict):
                raise GateError(f"{category}:{atom} metadata must be an object")
            intro = meta.get("introduced_by")
            if not isinstance(intro, str) or not intro:
                raise GateError(f"{category}:{atom} missing introduced_by")
            if intro == GRANDFATHERED_INTRODUCER and atom not in GRANDFATHERED_ATOMS[category]:
                raise GateError(
                    f"{category}:{atom} cannot be newly marked as grandfathered; "
                    "new atoms require a pre-math audit"
                )
    return categories


def canonical_atom_list(owner: str, field: str, value: Any) -> list[str]:
    if not isinstance(value, list):
        raise GateError(f"{owner} semantic_route {field} must be a list")
    if any(not isinstance(x, str) or not valid_atom_name(x) for x in value):
        raise GateError(f"{owner} semantic_route {field} contains invalid atom(s)")
    canonical = sorted(set(value))
    if value != canonical:
        raise GateError(
            f"{owner} semantic_route {field} must be SORTED + UNIQUE; "
            "list order is not semantic identity"
        )
    return canonical


def validate_semantic_route(
    owner: str, route: Any, catalog: dict[str, dict[str, dict[str, str]]]
) -> dict[str, Any]:
    if not isinstance(route, dict):
        raise GateError(f"{owner} requires semantic_route object")
    if set(route) != ROUTE_FIELDS:
        raise GateError(
            f"{owner} semantic_route fields must be exactly {sorted(ROUTE_FIELDS)}; "
            "human labels/descriptions are not identity fields"
        )

    problem_id = route.get("problem_id")
    semantics_id = route.get("semantics_id")
    complexity_target_id = route.get("complexity_target_id")
    for field, value in (
        ("problem_id", problem_id),
        ("semantics_id", semantics_id),
        ("complexity_target_id", complexity_target_id),
    ):
        if not isinstance(value, str) or not valid_atom_name(value):
            raise GateError(f"{owner} semantic_route missing/invalid {field}")

    domain_atoms = canonical_atom_list(owner, "domain_atoms", route.get("domain_atoms"))
    promise_atoms = canonical_atom_list(owner, "promise_atoms", route.get("promise_atoms"))

    normalized = {
        "problem_id": problem_id,
        "domain_atoms": domain_atoms,
        "semantics_id": semantics_id,
        "promise_atoms": promise_atoms,
        "complexity_target_id": complexity_target_id,
    }

    checks = {
        "problem_ids": [problem_id],
        "domain_atoms": domain_atoms,
        "semantics_ids": [semantics_id],
        "promise_atoms": promise_atoms,
        "complexity_target_ids": [complexity_target_id],
    }
    for category, atoms in checks.items():
        unknown = [atom for atom in atoms if atom not in catalog[category]]
        if unknown:
            raise GateError(
                f"{owner} uses uncontrolled semantic atom(s) in {category}: {unknown}; "
                "new atoms require a pre-math audit"
            )
    return normalized


def semantic_key(route: dict[str, Any]) -> str:
    return json.dumps(route, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def semantic_route_hash(route: dict[str, Any]) -> str:
    return hashlib.sha256(semantic_key(route).encode("ascii")).hexdigest()


def validate_route_identity(
    owner: str,
    holder: dict[str, Any],
    catalog: dict[str, dict[str, dict[str, str]]],
    fingerprint_field: str,
) -> tuple[dict[str, Any], str, str]:
    route = validate_semantic_route(owner, holder.get("semantic_route"), catalog)
    key = semantic_key(route)
    expected_hash = semantic_route_hash(route)
    declared_hash = holder.get("semantic_route_hash")
    if declared_hash != expected_hash:
        raise GateError(
            f"{owner}: semantic_route_hash must be computed SHA256 {expected_hash}, "
            f"got {declared_hash!r}"
        )
    fingerprint = holder.get(fingerprint_field)
    if fingerprint != expected_hash:
        raise GateError(
            f"{owner}: {fingerprint_field} must equal semantic_route_hash; "
            "manual route fingerprints are forbidden"
        )
    return route, key, expected_hash


def register_route_bijection(
    owner: str,
    key: str,
    route_hash: str,
    hash_to_key: dict[str, str],
    key_to_hash: dict[str, str],
) -> None:
    prior_key = hash_to_key.get(route_hash)
    if prior_key is not None and prior_key != key:
        raise GateError(
            f"{owner}: one semantic_route_hash maps to two canonical routes"
        )
    prior_hash = key_to_hash.get(key)
    if prior_hash is not None and prior_hash != route_hash:
        raise GateError(
            f"{owner}: one canonical semantic route maps to two hashes"
        )
    hash_to_key[route_hash] = key
    key_to_hash[key] = route_hash


def validate_audit_shape(
    entry: dict[str, Any],
    catalog: dict[str, dict[str, dict[str, str]]],
) -> None:
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

    receipt_payload: dict[str, Any] | None = None
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
        route, _, expected_hash = validate_route_identity(
            aid, entry, catalog, "route_fingerprint"
        )
        if entry.get("loop_check_status") != "PASS_NO_LOOP":
            raise GateError(
                f"{aid}: authorized work requires loop_check_status=PASS_NO_LOOP"
            )
        require_nonempty_string(entry, "authorized_scope")
        if receipt_payload is not None:
            receipt_route = validate_semantic_route(
                f"{aid} receipt", receipt_payload.get("semantic_route"), catalog
            )
            if receipt_route != route:
                raise GateError(f"{aid}: ledger semantic_route disagrees with receipt")
            if receipt_payload.get("semantic_route_hash") != expected_hash:
                raise GateError(f"{aid}: receipt semantic_route_hash disagrees with ledger")
            if receipt_payload.get("route_fingerprint") != expected_hash:
                raise GateError(f"{aid}: receipt route_fingerprint is not computed identity")

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
        if decision not in SCOPED_PASS_DECISIONS:
            raise GateError(
                f"{aid}: SOURCE_AUDIT_ONLY may authorize later new math only after a scoped PASS"
            )


def validate_atom_origins(
    catalog: dict[str, dict[str, dict[str, str]]],
    ids: dict[str, dict[str, Any]],
) -> None:
    declared_by_audit: dict[str, dict[str, set[str]]] = {}
    for aid, entry in ids.items():
        receipt = entry.get("receipt")
        if not isinstance(receipt, str) or not receipt.endswith(".json"):
            continue
        payload = load_json(ROOT / receipt)
        additions = payload.get("semantic_atom_additions", {})
        if additions is None:
            additions = {}
        if not isinstance(additions, dict):
            raise GateError(f"{aid}: semantic_atom_additions must be an object")
        per_cat: dict[str, set[str]] = {}
        for category in ATOM_CATEGORIES.values():
            values = additions.get(category, [])
            if not isinstance(values, list) or any(
                not isinstance(v, str) or not valid_atom_name(v) for v in values
            ):
                raise GateError(
                    f"{aid}: semantic_atom_additions.{category} must be a string list"
                )
            if values != sorted(set(values)):
                raise GateError(
                    f"{aid}: semantic_atom_additions.{category} must be SORTED + UNIQUE"
                )
            per_cat[category] = set(values)
        declared_by_audit[aid] = per_cat

    for category, atoms in catalog.items():
        for atom, meta in atoms.items():
            intro = meta["introduced_by"]
            if intro == GRANDFATHERED_INTRODUCER:
                continue
            if intro not in ids:
                raise GateError(
                    f"{category}:{atom} introduced_by unknown audit {intro}; "
                    "new semantic atoms require a pre-math audit"
                )
            if atom not in declared_by_audit.get(intro, {}).get(category, set()):
                raise GateError(
                    f"{category}:{atom} is not declared in {intro} receipt "
                    "semantic_atom_additions"
                )

    for aid, categories in declared_by_audit.items():
        for category, atoms in categories.items():
            for atom in atoms:
                meta = catalog[category].get(atom)
                if meta is None or meta.get("introduced_by") != aid:
                    raise GateError(
                        f"{aid} receipt declares semantic atom {category}:{atom}, "
                        "but catalog does not bind it back to that audit"
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

    catalog = validate_atom_catalog(ledger.get("semantic_atom_catalog"))

    no_loop = ledger.get("no_loop")
    if not isinstance(no_loop, dict):
        raise GateError("ledger missing no_loop policy block")
    if no_loop.get("invariant") != "NO_CLOSED_ROUTE_REENTRY_WITHOUT_EXPLICIT_REAUDIT":
        raise GateError("ledger no_loop invariant is missing or changed")
    if no_loop.get("route_identity_rule") != "CANONICAL_CONTROLLED_SEMANTIC_ATOMS_SHA256":
        raise GateError("ledger canonical semantic route identity rule is missing or changed")
    closed_routes = no_loop.get("closed_routes")
    if not isinstance(closed_routes, list):
        raise GateError("ledger no_loop.closed_routes must be a list")

    hash_to_key: dict[str, str] = {}
    key_to_hash: dict[str, str] = {}
    closed_by_hash: dict[str, list[str]] = {}
    closed_by_semantics: dict[str, list[str]] = {}
    closed_ids: set[str] = set()

    for closed in closed_routes:
        if not isinstance(closed, dict):
            raise GateError("closed route entries must be objects")
        rid = closed.get("id")
        status = closed.get("status")
        authority = closed.get("authority")
        if not isinstance(rid, str) or not rid:
            raise GateError("closed route missing id")
        if rid in closed_ids:
            raise GateError(f"duplicate closed route id {rid}")
        closed_ids.add(rid)
        if status not in CLOSED_ROUTE_STATUSES:
            raise GateError(f"{rid}: unsupported closed route status {status!r}")
        if not isinstance(authority, str) or not authority.strip():
            raise GateError(f"{rid}: closed route missing authority")
        _, key, route_hash = validate_route_identity(
            rid, closed, catalog, "fingerprint"
        )
        register_route_bijection(rid, key, route_hash, hash_to_key, key_to_hash)
        closed_by_hash.setdefault(route_hash, []).append(rid)
        closed_by_semantics.setdefault(key, []).append(rid)

    ids: dict[str, dict[str, Any]] = {}
    coverage: dict[str, str] = {}
    for entry in audits:
        if not isinstance(entry, dict):
            raise GateError("audit ledger entries must be objects")
        validate_audit_shape(entry, catalog)
        aid = entry["id"]
        if aid in ids:
            raise GateError(f"duplicate audit id {aid}")
        ids[aid] = entry
        if entry.get("new_math_authorized") is True:
            _, key, route_hash = validate_route_identity(
                aid, entry, catalog, "route_fingerprint"
            )
            register_route_bijection(aid, key, route_hash, hash_to_key, key_to_hash)
        for path in entry["artifact_paths"]:
            if path in coverage:
                raise GateError(
                    f"{path} is covered by multiple audits: {coverage[path]} and {aid}"
                )
            coverage[path] = aid

    validate_atom_origins(catalog, ids)

    # An active authorization must not silently reopen a tombstoned semantic route.
    for entry in audits:
        if entry.get("new_math_authorized") is not True:
            continue
        _, key, route_hash = validate_route_identity(
            entry["id"], entry, catalog, "route_fingerprint"
        )
        collided = set(closed_by_hash.get(route_hash, []))
        collided.update(closed_by_semantics.get(key, []))
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

    # New math must remain exactly inside the canonical route authorized by its audit.
    seen_new_hash: dict[str, str] = {}
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
                f"{entry['id']}: authorizing audit {auth_id} is not a completed scoped PASS"
            )
        if auth.get("new_math_authorized") is not True:
            raise GateError(
                f"{entry['id']}: authorizing audit {auth_id} does not authorize new math"
            )
        if entry.get("scope_id") != auth.get("authorized_scope"):
            raise GateError(
                f"{entry['id']}: scope_id {entry.get('scope_id')!r} does not exactly "
                f"match authorizing scope {auth.get('authorized_scope')!r}"
            )
        entry_route, entry_key, entry_hash = validate_route_identity(
            entry["id"], entry, catalog, "route_fingerprint"
        )
        auth_route, auth_key, auth_hash = validate_route_identity(
            auth_id, auth, catalog, "route_fingerprint"
        )
        if entry_hash != auth_hash or entry_key != auth_key or entry_route != auth_route:
            raise GateError(
                f"{entry['id']}: canonical semantic route differs from authorizing audit "
                f"{auth_id}; changed semantics require a new pre-math audit"
            )
        if auth_id not in entry.get("predecessor_ids", []):
            raise GateError(
                f"{entry['id']}: predecessor_ids must include authorizing audit {auth_id}"
            )
        prior = seen_new_hash.get(entry_hash) or seen_new_semantics.get(entry_key)
        if prior is not None and entry.get("continuation_of") != prior:
            raise GateError(
                f"{entry['id']}: route already used by {prior}; continuation_of must "
                "explicitly chain same-route work"
            )
        seen_new_hash[entry_hash] = entry["id"]
        seen_new_semantics[entry_key] = entry["id"]

    changed = changed_paths_since(baseline)
    tracked = {
        p for p in changed if is_tracked(p, prefixes) and p not in exemptions
    }
    missing = sorted(p for p in tracked if p not in coverage)
    if missing:
        raise GateError(
            "post-activation scientific artifacts are not covered by the pre-math ledger:\n"
            + "\n".join(f"  - {p}" for p in missing)
        )

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
    print("ROUTE_IDENTITY = SHA256_CANONICAL_CONTROLLED_SEMANTIC_ATOMS")
    print("LIST_IDENTITY = SORTED_UNIQUE_ATOMS")
    print("LAW_II = CLOSED_ROAD_DOES_NOT_BECOME_NEW_BY_RENAMING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
