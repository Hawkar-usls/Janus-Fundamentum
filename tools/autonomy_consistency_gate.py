#!/usr/bin/env python3
"""JANUS Fundamentum offline structural consistency gate.

No GitHub API calls, model providers, writes, or claim promotion.
The checker validates submitted claims, NOT the underlying external facts.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1] / "registry/JANUS_AUTONOMY_CONSISTENCY_CONTRACT_v1.json"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def is_hex(value: object, pattern: re.Pattern[str]) -> bool:
    return isinstance(value, str) and bool(pattern.fullmatch(value))


def evaluate(contract: dict, evidence: dict) -> dict:
    """Fail closed on missing/duplicate/inconsistent stated receipts."""
    problems: list[str] = []
    if contract.get("schema") != "janus.autonomy.consistency_contract.v1":
        problems.append("invalid_contract_schema")
    if evidence.get("schema") != "janus.autonomy.snapshot.v1":
        problems.append("invalid_snapshot_schema")
    if evidence.get("scope") not in ("SYNTHETIC_TEST", "LIVE_EVIDENCE"):
        problems.append("invalid_evidence_scope")
    if not isinstance(evidence.get("snapshot_id"), str) or not evidence["snapshot_id"]:
        problems.append("missing_snapshot_id")
    expected = {x["id"]: x for x in contract["required_routes"]}
    if len(expected) != len(contract["required_routes"]):
        problems.append("duplicate_contract_route")
    entries = evidence.get("routes")
    if not isinstance(entries, list):
        entries = []
        problems.append("missing_routes")
    seen: set[str] = set()
    event_ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            problems.append("invalid_route_entry")
            continue
        rid = entry.get("route_id")
        if not isinstance(rid, str):
            problems.append("invalid_route_id")
            continue
        if rid in seen:
            problems.append(f"{rid}:duplicate_route")
            continue
        seen.add(rid)
        spec = expected.get(rid)
        if spec is None:
            problems.append(f"{rid}:unknown_route")
            continue
        for key in ("source", "target", "kind"):
            if entry.get(key) != spec[key]:
                problems.append(f"{rid}:{key}_mismatch")
        kind = spec["kind"]
        if kind == "DELIVERY_ACK":
            event_id = entry.get("event_id")
            if not isinstance(event_id, str) or not event_id:
                problems.append(f"{rid}:missing_event_id")
            elif event_id in event_ids:
                problems.append(f"{rid}:reused_event_id")
            else:
                event_ids.add(event_id)
            for key, pattern in (("source_commit_sha", HEX40), ("payload_sha256", HEX64)):
                if not is_hex(entry.get(key), pattern):
                    problems.append(f"{rid}:invalid_{key}")
            ack = entry.get("ack")
            if not isinstance(ack, dict):
                problems.append(f"{rid}:missing_ack")
                continue
            if ack.get("event_id") != event_id:
                problems.append(f"{rid}:ack_event_mismatch")
            if ack.get("payload_sha256") != entry.get("payload_sha256"):
                problems.append(f"{rid}:ack_payload_mismatch")
            if ack.get("consumer") != spec["target"]:
                problems.append(f"{rid}:ack_consumer_mismatch")
            if ack.get("status") != "APPLIED":
                problems.append(f"{rid}:not_applied")
            if not is_hex(ack.get("consumer_commit_sha"), HEX40):
                problems.append(f"{rid}:invalid_consumer_commit")
            if not isinstance(ack.get("receipt_ref"), str) or not ack["receipt_ref"].startswith("https://"):
                problems.append(f"{rid}:missing_receipt_ref")
        elif kind == "DIGEST_ALIGNMENT":
            for key in ("source_digest_sha256", "registry_pointer_digest_sha256"):
                if not is_hex(entry.get(key), HEX64):
                    problems.append(f"{rid}:invalid_{key}")
            if entry.get("source_digest_sha256") != entry.get("registry_pointer_digest_sha256"):
                problems.append(f"{rid}:stale_or_mismatched_pointer")
            if not isinstance(entry.get("source_ref"), str) or not entry["source_ref"]:
                problems.append(f"{rid}:missing_source_ref")
            if not isinstance(entry.get("registry_ref"), str) or not entry["registry_ref"]:
                problems.append(f"{rid}:missing_registry_ref")
        elif kind == "RECOVERY_REPLAY":
            for key in ("source_commit_sha", "restored_commit_sha"):
                if not is_hex(entry.get(key), HEX40):
                    problems.append(f"{rid}:invalid_{key}")
            for key in ("checkpoint_sha256", "restored_state_sha256"):
                if not is_hex(entry.get(key), HEX64):
                    problems.append(f"{rid}:invalid_{key}")
            if entry.get("checkpoint_sha256") != entry.get("restored_state_sha256"):
                problems.append(f"{rid}:restore_hash_mismatch")
            if not isinstance(entry.get("worker_source"), str) or not entry["worker_source"]:
                problems.append(f"{rid}:missing_source_worker")
            if not isinstance(entry.get("worker_restored"), str) or not entry["worker_restored"]:
                problems.append(f"{rid}:missing_restored_worker")
            if entry.get("worker_source") == entry.get("worker_restored"):
                problems.append(f"{rid}:not_independent_worker")
            if type(entry.get("fencing_token")) is not int or entry["fencing_token"] < 1:
                problems.append(f"{rid}:invalid_fencing_token")
            if type(entry.get("applied_count")) is not int or entry["applied_count"] != 1:
                problems.append(f"{rid}:not_single_application")
            if not isinstance(entry.get("receipt_ref"), str) or not entry["receipt_ref"].startswith("https://"):
                problems.append(f"{rid}:missing_recovery_receipt")
    for rid in expected.keys() - seen:
        problems.append(f"{rid}:missing_required_route")
    return {
        "schema": "janus.fundamentum.autonomy_consistency_report.v1",
        "snapshot_id": evidence.get("snapshot_id"),
        "scope": evidence.get("scope"),
        "checked_routes": len(seen & expected.keys()),
        "required_routes": len(expected),
        "status": "BLOCKED" if problems else (
            "SYNTHETIC_CONSISTENCY_PASS_NOT_LIVE"
            if evidence.get("scope") == "SYNTHETIC_TEST"
            else "DECLARED_CONSISTENCY_PASS_EXTERNAL_VERIFICATION_REQUIRED"
        ),
        "issues": sorted(problems),
        "live_transport_verified": False,
        "independent_witness_verified": False,
        "end_to_end_autonomy_proved": False,
        "p_vs_np_status": "OPEN",
    }


def synthetic_snapshot(contract: dict) -> dict:
    """Only for adversarial unit tests; fabricated hashes do not represent events."""
    routes = []
    for i, spec in enumerate(contract["required_routes"]):
        x = {"route_id": spec["id"], "source": spec["source"],
             "target": spec["target"], "kind": spec["kind"]}
        if spec["kind"] == "DELIVERY_ACK":
            x.update(event_id=f"synthetic-event-{i}", source_commit_sha="a" * 40,
                     payload_sha256="b" * 64,
                     ack={"event_id": f"synthetic-event-{i}", "payload_sha256": "b" * 64,
                          "consumer": spec["target"], "status": "APPLIED",
                          "consumer_commit_sha": "c" * 40,
                          "receipt_ref": "https://example.invalid/synthetic"})
        elif spec["kind"] == "DIGEST_ALIGNMENT":
            x.update(source_digest_sha256="d" * 64,
                     registry_pointer_digest_sha256="d" * 64,
                     source_ref="synthetic:rowan", registry_ref="synthetic:meta")
        else:
            x.update(source_commit_sha="a" * 40, restored_commit_sha="c" * 40,
                     checkpoint_sha256="e" * 64, restored_state_sha256="e" * 64,
                     worker_source="worker-a", worker_restored="worker-b",
                     fencing_token=1, applied_count=1,
                     receipt_ref="https://example.invalid/synthetic")
        routes.append(x)
    return {"schema": "janus.autonomy.snapshot.v1",
            "scope": "SYNTHETIC_TEST", "snapshot_id": "synthetic-test-only", "routes": routes}


def self_test(contract: dict) -> None:
    good = synthetic_snapshot(contract)
    assert evaluate(contract, good)["status"] == "SYNTHETIC_CONSISTENCY_PASS_NOT_LIVE"
    mutations = [
        lambda s: s["routes"].pop(),
        lambda s: s["routes"].append(copy.deepcopy(s["routes"][0])),
        lambda s: s["routes"][0].pop("ack"),
        lambda s: s["routes"][0]["ack"].update(payload_sha256="f" * 64),
        lambda s: s["routes"][0]["ack"].update(status="PENDING"),
        lambda s: s["routes"][1].update(registry_pointer_digest_sha256="f" * 64),
        lambda s: s["routes"][4].update(worker_restored="worker-a"),
        lambda s: s["routes"][4].update(applied_count=2),
        lambda s: s["routes"][4].update(restored_state_sha256="f" * 64),
        lambda s: s.update(scope="UNKNOWN"),
        lambda s: s["routes"][0].update(source_commit_sha="not-a-sha"),
    ]
    for i, mutate in enumerate(mutations):
        bad = copy.deepcopy(good)
        mutate(bad)
        result = evaluate(contract, bad)
        assert result["status"] == "BLOCKED", f"adversarial case {i} incorrectly passed"
    assert not evaluate(contract, good)["end_to_end_autonomy_proved"]
    print(json.dumps({"self_test": "PASS", "negative_cases": len(mutations),
                      "scope": "SYNTHETIC_ONLY", "live_transport_verified": False}))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--contract", type=Path, default=CONTRACT)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--evidence", type=Path)
    args = ap.parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    if args.self_test:
        self_test(contract)
        return 0
    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    result = evaluate(contract, evidence)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] != "BLOCKED" else 2


if __name__ == "__main__":
    sys.exit(main())
