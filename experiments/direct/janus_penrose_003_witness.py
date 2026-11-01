#!/usr/bin/env python3
"""JANUS-PENROSE-003: read-only witness on a DIFFERENT GitHub runner.

Evidence is transferred via actions/upload-artifact + download-artifact.
Do not invoke the solver, trust claimed answers, or treat a hash as a proof.
The witness reads files, pins job event identity, reconstructs the original CNF,
replays the portable UFR proof, re-derives the Deutsch oracle and DAG, and
rejects controlled corruptions of the producer->witness handoff.

This is process/runner independence, not independence from the shared source
repository, GitHub platform, or a distinct external laboratory.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import time

from janus_penrose_002_integration import (
    build_receipts, verify_bundle,
)
from janus_penrose_003_transfer import (
    FIXTURE, handoff_manifest, inspect_transfer, read_files,
)


def expect_rejection(name, operation, errors=(AssertionError, ValueError, KeyError,
                                               TypeError, UnicodeError)):
    try:
        operation()
    except errors as exc:
        return {"scenario": name, "status": "REJECTED",
                "exception": type(exc).__name__,
                "message": str(exc)[:300]}
    raise AssertionError(f"transit fault {name} was not rejected")


def run_witness(manifest: dict, report_bytes: bytes, proof_bytes: bytes,
                *, trusted_head: str, trusted_run: str):
    """All paths fail closed; no positive result without complete replay."""
    started = time.perf_counter()
    preflight = inspect_transfer(manifest, report_bytes, proof_bytes,
                                 trusted_head=trusted_head, trusted_run=trusted_run)
    report = json.loads(report_bytes)
    proof_wire = proof_bytes.decode("utf-8", errors="strict")
    if not verify_bundle(report, proof_wire):
        raise AssertionError("independent proof replay returned False")
    payloads = report["stage_payloads"]
    if payloads["INDEPENDENT_REPLAY"]["answer"] is not False:
        raise AssertionError("MAJ3-K4 known-UNSAT fixture did not replay UNSAT")
    if payloads["UFR_PRODUCE"]["iso_hits"] != 165:
        raise AssertionError("UFR 165-hit regression control failed")
    if payloads["UFR_PRODUCE"]["states"] != 2354:
        raise AssertionError("UFR 2354-state regression control failed")
    if payloads["UFR_ORACLE_COVARIANCE"]["oracle_checked_iso_edges"] < 8:
        raise AssertionError("not enough UFR-to-oracle edge checks")
    if payloads["SCHEDULE_AUDIT"]["events"] != 4161:
        raise AssertionError("incomplete reversible schedule")
    trusted_seconds = time.perf_counter() - started

    # Transfer mutation cases. No mutation to the original artifact.
    faults = []
    def check(tag, m=manifest, r=report_bytes, p=proof_bytes):
        return inspect_transfer(m, r, p, trusted_head=trusted_head, trusted_run=trusted_run)

    faults.append(expect_rejection("PROOF_BYTE_CORRUPTED",
        lambda: check(p=bytes([proof_bytes[0] ^ 1]) + proof_bytes[1:])))
    faults.append(expect_rejection("REPORT_BYTE_CORRUPTED",
        lambda: check(r=report_bytes + b" ")))
    wrong_run = dict(manifest, run_id=str(int(trusted_run) + 1))
    faults.append(expect_rejection("STALE_RUN_ID",
        lambda: check(m=wrong_run)))
    wrong_head = dict(manifest, head_sha="0" * 40)
    faults.append(expect_rejection("WRONG_HEAD_SHA",
        lambda: check(m=wrong_head)))
    wrong_source = dict(manifest, source_sha256="0" * 64)
    faults.append(expect_rejection("WRONG_CNF_SHA",
        lambda: check(m=wrong_source)))
    missing_proof = proof_bytes[:1024]
    faults.append(expect_rejection("TRUNCATED_PROOF",
        lambda: check(p=missing_proof)))
    wrong_certificate = dict(manifest, proof_sha256="f" * 64)
    faults.append(expect_rejection("CROSSED_PROOF_HASH",
        lambda: check(m=wrong_certificate)))

    # The producer may FORGE all report bytes and recompute matching handoff
    # hashes. Transport checks are intentionally not sufficient; the
    # independent circuit+proof verifier must reject its semantic lie.
    forged = deepcopy(report)
    forged["stage_payloads"]["ORACLE_TRUTH"]["all_match"] = False
    graph_edges = tuple(map(tuple, forged["dependencies"]))
    forged["stage_receipts"] = build_receipts(forged["stage_payloads"], graph_edges)
    forged_bytes = (json.dumps(forged, indent=2, sort_keys=True) + "\n").encode("utf-8")
    matching_forged_manifest = handoff_manifest(
        forged_bytes, proof_bytes, head_sha=trusted_head, run_id=trusted_run)
    assert inspect_transfer(matching_forged_manifest, forged_bytes, proof_bytes,
                            trusted_head=trusted_head, trusted_run=trusted_run)
    faults.append(expect_rejection("SELF_CONSISTENT_FORGED_ORACLE_VERDICT",
        lambda: verify_bundle(forged, proof_wire)))

    # Impossible future-to-producer feedback. A forged checksum cannot make
    # an invalid strict dependency graph valid even before replay.
    forged_cycle = deepcopy(report)
    forged_cycle["dependencies"].append(["FINAL_GATE", "UFR_PRODUCE"])
    cycle_bytes = (json.dumps(forged_cycle, sort_keys=True) + "\n").encode("utf-8")
    faults.append(expect_rejection("FUTURE_FEEDBACK_CYCLE",
        lambda: handoff_manifest(cycle_bytes, proof_bytes,
                                 head_sha=trusted_head, run_id=trusted_run)))
    # For the exact same trusted formula/proof pair, cross-using a report
    # from a DIFFERENT named fixture is never acceptable.
    wrong_fixture = deepcopy(report)
    wrong_fixture["fixture"] = "RENAMED_TWIN_POSITIVE_CONTROL"
    foreign_bytes = (json.dumps(wrong_fixture, sort_keys=True) + "\n").encode("utf-8")
    faults.append(expect_rejection("CROSSED_FORMULA",
        lambda: handoff_manifest(foreign_bytes, proof_bytes,
                                 head_sha=trusted_head, run_id=trusted_run)))
    if len(faults) != 10 or any(f["status"] != "REJECTED" for f in faults):
        raise AssertionError("not all corruption cases failed closed")

    return {
        "schema": "JANUS-PENROSE-003-INDEPENDENT-RUNNER-WITNESS-V1",
        "status": "PASS_INDEPENDENT_RUNNER_REPLAY_AND_TAMPER_REJECTION",
        "verified_utc": datetime.now(timezone.utc).isoformat(),
        "runner": {"os": platform.platform(),
                   "runner_name": os.getenv("RUNNER_NAME", "local"),
                   "github_job": os.getenv("GITHUB_JOB", "local"),
                   "python": platform.python_version()},
        "trusted_event": {"head_sha": trusted_head, "run_id": trusted_run},
        "manifest_verified": preflight,
        "live": {"fixture": FIXTURE, "replayed_answer": False,
                 "proof_replay_and_oracle_seconds": trusted_seconds,
                 "UFR_verified_ISO_hits": payloads["UFR_PRODUCE"]["iso_hits"],
                 "UFR_unique_states": payloads["UFR_PRODUCE"]["states"],
                 "source_sha256": payloads["SOURCE"]["source_sha256"],
                 "certificate_sha256": preflight["proof_sha256"],
                 "certificate_bytes": preflight["proof_bytes"],
                 "oracle_iso_edges_crosschecked": payloads["UFR_ORACLE_COVARIANCE"]["oracle_checked_iso_edges"],
                 "circuit_events": payloads["SCHEDULE_AUDIT"]["events"],
                 "source_assignments_checked": payloads["ORACLE_TRUTH"]["independent_checks"]},
        "tamper_checks": faults,
        "tamper_checks_rejected": len(faults),
        "limitations": [
            "Distinct cloud runner and separate process/checkout; not a separately governed trusted codebase",
            "Shared GitHub account, workflow code and source repository remain common trust dependencies",
            "SHA256 is tamper evidence, not a digital signature; full proof replay is independently executed",
            "Only bounded UFR cache edges additionally oracle-sampled, all UFR iso edges checked by proof replay",
            "No quantum hardware, no SAT speedup, no permission to merge experimental UFR",
            "Fail-close witness does not turn these controls into general P=NP proof",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--proof", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--trusted-head", required=True)
    p.add_argument("--trusted-run", required=True)
    a = p.parse_args()
    manifest, report, proof = read_files(a.manifest, a.report, a.proof)
    result = run_witness(manifest, report, proof,
                         trusted_head=a.trusted_head, trusted_run=a.trusted_run)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                     encoding="utf-8")
    print(json.dumps({k: result[k] for k in
                      ("schema", "status", "runner", "live",
                       "tamper_checks_rejected", "tamper_checks")},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
