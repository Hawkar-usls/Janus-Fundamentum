#!/usr/bin/env python3
"""JANUS-PENROSE-003: explicitly bounded producer->external-job handoff.

The producer writes an UNTRUSTED manifest and source-bound evidence files.
A separate clean GitHub-hosted job on a different OS must check actual bytes,
GitHub event SHA/run ID, and replay the full UFR certificate itself.

The manifest is neither a signature nor a substitute for independent proof.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path

from janus_penrose_002_integration import STAGES, REQUIRED_EDGES, source_id, get_fixture

MAX_REPORT_BYTES = 2_000_000
MAX_PROOF_BYTES = 200_000_000
FIXTURE = "MAJ3_K4"
SCHEMA = "JANUS-PENROSE-003-HANDOFF-V1"


def digest_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def strict_object(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        raise ValueError("unexpected manifest fields")


def handoff_manifest(report_bytes: bytes, proof_bytes: bytes,
                     *, head_sha: str, run_id: str) -> dict:
    if not (1 <= len(report_bytes) <= MAX_REPORT_BYTES):
        raise ValueError("report byte bound exceeded")
    if not (1 <= len(proof_bytes) <= MAX_PROOF_BYTES):
        raise ValueError("certificate byte bound exceeded")
    if type(head_sha) is not str or len(head_sha) != 40 or any(
        c not in "0123456789abcdef" for c in head_sha):
        raise ValueError("invalid SHA provenance")
    if type(run_id) is not str or not run_id.isascii() or not run_id.isdecimal():
        raise ValueError("invalid run ID provenance")
    report = json.loads(report_bytes)
    root, n = get_fixture(FIXTURE)
    if report.get("fixture") != FIXTURE:
        raise ValueError("wrong fixture")
    if report.get("stage_order") != list(STAGES):
        raise ValueError("wrong stage order")
    if list(map(tuple, report.get("dependencies", []))) != list(REQUIRED_EDGES):
        raise ValueError("unapproved dependency edge")
    if report.get("stage_payloads", {}).get("SOURCE", {}).get("source_sha256") != source_id(root, n):
        raise ValueError("source SHA mismatch")
    if report.get("proof_file_sha256") != digest_bytes(proof_bytes):
        raise ValueError("certificate SHA mismatch")
    return {
        "schema": SCHEMA,
        "fixture": FIXTURE,
        "head_sha": head_sha,
        "run_id": run_id,
        "source_sha256": source_id(root, n),
        "proof_sha256": digest_bytes(proof_bytes),
        "proof_bytes": len(proof_bytes),
        "report_sha256": digest_bytes(report_bytes),
        "report_bytes": len(report_bytes),
        "strict_stages": len(STAGES),
        "strict_edges": len(REQUIRED_EDGES),
    }


def inspect_transfer(manifest: dict, report_bytes: bytes, proof_bytes: bytes,
                     *, trusted_head: str, trusted_run: str) -> dict:
    """No producer outputs trusted; independent runner supplies event identity."""
    strict_object(manifest, (
        "schema", "fixture", "head_sha", "run_id", "source_sha256",
        "proof_sha256", "proof_bytes", "report_sha256", "report_bytes",
        "strict_stages", "strict_edges",
    ))
    if manifest["schema"] != SCHEMA or manifest["fixture"] != FIXTURE:
        raise ValueError("handoff schema/fixture mismatch")
    if manifest["head_sha"] != trusted_head or manifest["run_id"] != trusted_run:
        raise ValueError("handoff job provenance does not match trusted workflow event")
    if not (1 <= len(report_bytes) <= MAX_REPORT_BYTES and
            1 <= len(proof_bytes) <= MAX_PROOF_BYTES):
        raise ValueError("handoff evidence exceeds byte bounds")
    rebuilt = handoff_manifest(report_bytes, proof_bytes,
                               head_sha=trusted_head, run_id=trusted_run)
    if manifest != rebuilt:
        raise ValueError("handoff altered or stale; recomputed manifest disagrees")
    return rebuilt


def read_files(manifest_path: Path, report_path: Path, proof_path: Path):
    if not (manifest_path.is_file() and report_path.is_file() and proof_path.is_file()):
        raise ValueError("missing file in cross-runner transfer")
    if (report_path.stat().st_size > MAX_REPORT_BYTES or
            proof_path.stat().st_size > MAX_PROOF_BYTES):
        raise ValueError("too-large transferred artifact")
    return (json.loads(manifest_path.read_text(encoding="utf-8")),
            report_path.read_bytes(), proof_path.read_bytes())


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--proof", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    args = p.parse_args()
    head = os.environ.get("GITHUB_SHA", "")
    run = os.environ.get("GITHUB_RUN_ID", "")
    manifest = handoff_manifest(args.report.read_bytes(), args.proof.read_bytes(),
                                head_sha=head, run_id=run)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n",
                             encoding="utf-8")
    print(json.dumps({"status": "UNTRUSTED_HANDOFF_PREPARED",
                      "utc": datetime.now(timezone.utc).isoformat(),
                      "manifest": manifest}, sort_keys=True))


if __name__ == "__main__":
    main()
