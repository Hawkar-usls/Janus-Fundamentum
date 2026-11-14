#!/usr/bin/env python3
"""JANUS-PENROSE-002: independently check source-bound UFR→oracle→proof DAG.

Run in fresh CI job. Archive full UFR serialized wire certificate separately,
with SHA256 embedded in report. The report *is independently rechecked* from
its on-disk certificate before marking PASS. An impossible cycle must fail.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import time

from janus_penrose_002_integration import (
    REQUIRED_EDGES, build_bundle, check_dependencies, verify_bundle,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", choices=("MAJ3_K4",
        "TSEITIN_K4_NONAFFINE_WRAPPED", "RENAMED_TWIN_POSITIVE_CONTROL"),
        default="MAJ3_K4")
    parser.add_argument("--out", type=Path, default=Path("evidence/penrose-002.json"))
    parser.add_argument("--proof", type=Path, default=Path("evidence/penrose-002-ufr.json"))
    parser.add_argument("--samples", type=int, default=32)
    parser.add_argument("--max-iso-edges", type=int, default=8)
    args = parser.parse_args()
    start = time.perf_counter()
    report, wire = build_bundle(
        args.fixture, samples=args.samples, max_iso_edges=args.max_iso_edges)
    build_seconds = time.perf_counter() - start
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.proof.parent.mkdir(parents=True, exist_ok=True)
    args.proof.write_text(wire, encoding="utf-8")
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")

    # Actual readback from disk, not trusting the mutable producer objects.
    independent = json.loads(args.out.read_text(encoding="utf-8"))
    wire2 = args.proof.read_text(encoding="utf-8")
    check_start = time.perf_counter()
    assert verify_bundle(independent, wire2)
    replay_seconds = time.perf_counter() - check_start

    # The last->first edge is inconsistent even though all normal individual
    # stages are locally valid. We test the NEGATIVE graph inside the same job.
    try:
        check_dependencies(REQUIRED_EDGES + (("FINAL_GATE", "UFR_PRODUCE"),))
    except AssertionError as error:
        cycle_error = str(error)
    else:
        raise AssertionError("malicious cross-contour dependency cycle accepted")
    output = {
        "schema": "JANUS-PENROSE-002-RUN-EVIDENCE-V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "provenance": {"repository": "Hawkar-usls/Janus-Fundamentum",
                       "head_sha": os.getenv("GITHUB_SHA", "local"),
                       "workflow_run": os.getenv("GITHUB_RUN_ID", "local")},
        "fixture": args.fixture,
        "status": "PASS_INDEPENDENT_REPLAY_DAG_ORACLE",
        "source_sha256": report["stage_payloads"]["SOURCE"]["source_sha256"],
        "proof_sha256": report["proof_file_sha256"],
        "certificate_size_bytes": report["stage_payloads"]["UFR_CERTIFICATE"]["bytes"],
        "solver": report["stage_payloads"]["UFR_PRODUCE"],
        "independent_verifier": report["stage_payloads"]["INDEPENDENT_REPLAY"],
        "oracle": report["stage_payloads"]["ORACLE_COMPILE"],
        "schedule": report["stage_payloads"]["SCHEDULE_AUDIT"],
        "oracle_truth": report["stage_payloads"]["ORACLE_TRUTH"],
        "actual_UFR_oracle_map_crosschecks": report["stage_payloads"]["UFR_ORACLE_COVARIANCE"],
        "strict_causal_stage_count": len(report["stage_order"]),
        "strict_dependency_edges": len(report["dependencies"]),
        "injected_invalid_dependency_rejected": True,
        "negative_cycle_error": cycle_error,
        "first_build_and_replay_seconds": build_seconds,
        "second_independent_replay_seconds": replay_seconds,
        "report_file": str(args.out),
        "certificate_file": str(args.proof),
        "limitations": [
            "Separate process is not a cryptographically isolated external lab",
            "UFR independently replayed as SAT Boolean proof; C023 production untouched",
            "Reversible oracle is a classical sampled circuit evaluation, not a quantum device",
            "UFR real isomorphic cache mappings are checked on bounded sampled assignments",
            "MAJ3_K4 UNSAT is supported by independent proof, not sampling",
            "No P=NP, no SAT speedup, no automatic merge",
        ],
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
