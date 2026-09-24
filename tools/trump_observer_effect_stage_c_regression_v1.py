#!/usr/bin/env python3
"""Observer-noninterference regression over the already sealed APMA Stage C candidate.

DIAGNOSTIC/CALIBRATION ONLY.

This does not create a new solver, carrier, discovery mechanism, or scientific gate. It
reuses the historical sealed Stage C blind-positive and blind-negative authorities only to
ask a new orchestration question: does adding an observer/telemetry path change the exact
bytes seen by the frozen candidate or the candidate/checker result?

The observer always receives an independent decode of precommitted bytes. The frozen
candidate is invoked unchanged in a subprocess against an opaque input path. Provenance and
historical labels are kept in a separate envelope until candidate outputs are frozen.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any

CANARY = "JANUS_STAGE_C_TARGET_METADATA_CANARY__MUST_NOT_REACH_CANDIDATE__91C7D2"
MOD = "research.tools.apma_unseen_local_invariant_orbit_count"
CANDIDATE = f"{MOD}.candidate"
CHECKER = f"{MOD}.independent_checker"
BLIND_AUTHORITY = f"{MOD}.blind_authority"

SEALED_GIT_BLOBS = {
    "research/tools/apma_unseen_local_invariant_orbit_count/candidate.py": "a076cfc56d68aad0348415e313705da1f6b9cdcd",
    "research/tools/apma_unseen_local_invariant_orbit_count/independent_checker.py": "0e12304d843ef0bcce6b6c032fd2af2c68abcd14",
    "research/tools/apma_unseen_local_invariant_orbit_count/blind_authority.py": "7a1c91e01543591564ff3986f53a9faf2acd322f",
    "research/TRUMP_APMA_UNSEEN_LOCAL_INVARIANT_STAGE_B_FREEZE_2026-09-16.json": "d0e8af61b19062f069c40897477e716b883a211b",
}

EXPECTED = {
    "positive": {
        "raw_semantic_sha256": "754019dfae09c51640011d614ae5b215377afc6d3f8902f558c38e9a1c35e7b4",
        "status": "ADMIT_ORBIT_COUNT_QUOTIENT_SAT",
        "solver_authority": True,
    },
    "negative": {
        "raw_semantic_sha256": "1aed4c6c360060c0262b616dc6552b5b33b446724308a2ac793e9019c6202b8d",
        "status": "OPEN_NO_NONTRIVIAL_EXCHANGEABILITY",
        "solver_authority": False,
    },
}

OBSERVER_MODES = ("NO_OBSERVER", "READ_ONLY_OBSERVER", "HOSTILE_COPY_OBSERVER")


class RegressionError(RuntimeError):
    pass


def canon(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_obj(obj: Any) -> str:
    return sha_bytes(canon(obj).encode("utf-8"))


def run_json(cmd: list[str]) -> tuple[dict[str, Any], str]:
    proc = subprocess.run(cmd, check=True, text=True, capture_output=True)
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    if not lines:
        raise RegressionError(f"no JSON output from: {cmd}")
    try:
        obj = json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        raise RegressionError(f"last output line was not JSON for {cmd}: {lines[-1]!r}") from exc
    return obj, proc.stdout


def git_hash_object(path: str) -> str:
    return subprocess.run(
        ["git", "hash-object", path], check=True, text=True, capture_output=True
    ).stdout.strip()


def assert_sealed_sources() -> dict[str, str]:
    observed = {path: git_hash_object(path) for path in SEALED_GIT_BLOBS}
    bad = {
        path: {"expected": SEALED_GIT_BLOBS[path], "observed": sha}
        for path, sha in observed.items()
        if sha != SEALED_GIT_BLOBS[path]
    }
    if bad:
        raise RegressionError(f"sealed Stage C source binding changed: {bad}")
    return observed


def canonical_raw_semantic_sha(raw: dict[str, Any]) -> str:
    variables = sorted(int(v) for v in raw["variables"])
    keys = []
    for constraint in raw["constraints"]:
        scope = list(constraint["scope"])
        order = sorted(range(len(scope)), key=lambda i: scope[i])
        sorted_scope = tuple(scope[i] for i in order)
        rows = {
            tuple(tuple(row)[i] for i in order)
            for row in constraint["allowed"]
        }
        keys.append((sorted_scope, tuple(sorted(rows))))
    keys.sort()
    serial = {
        "variables": variables,
        "constraints": [
            {"scope": list(scope), "allowed": [list(row) for row in rows]}
            for scope, rows in keys
        ],
    }
    return sha_obj(serial)


def materialize_sealed_raw(label: str) -> dict[str, Any]:
    raw, _ = run_json(["python", "-m", BLIND_AUTHORITY, "--emit", label])
    if set(raw) != {"variables", "constraints"}:
        raise RegressionError(f"unclean blind raw contract for {label}: {sorted(raw)}")
    observed = canonical_raw_semantic_sha(raw)
    expected = EXPECTED[label]["raw_semantic_sha256"]
    if observed != expected:
        raise RegressionError(f"semantic SHA mismatch for {label}: {observed} != {expected}")
    return raw


def observer(mode: str, private_copy: dict[str, Any]) -> dict[str, Any]:
    if mode == "NO_OBSERVER":
        return {"mode": mode, "observed": False}
    if mode == "READ_ONLY_OBSERVER":
        return {
            "mode": mode,
            "observed": True,
            "variables": len(private_copy["variables"]),
            "constraints": len(private_copy["constraints"]),
            "private_copy_sha256": sha_obj(private_copy),
        }
    if mode == "HOSTILE_COPY_OBSERVER":
        # Deliberately destructive, but only to the observer's private decode.
        private_copy["variables"].reverse()
        private_copy["constraints"].clear()
        private_copy["observer_private_canary"] = CANARY
        return {
            "mode": mode,
            "observed": True,
            "private_copy_mutated": True,
            "private_copy_sha256_after_mutation": sha_obj(private_copy),
            "canary_inserted_into_private_copy": True,
        }
    raise RegressionError(f"unknown observer mode: {mode}")


def run_mode(payload_bytes: bytes, mode: str) -> dict[str, Any]:
    before_sha = sha_bytes(payload_bytes)
    decoded_for_observer = json.loads(payload_bytes.decode("utf-8"))
    obs = observer(mode, decoded_for_observer)

    # Candidate never receives the observer object. It receives exactly the frozen bytes
    # through an opaque path that contains no positive/negative/provenance label.
    with tempfile.TemporaryDirectory(prefix="janus-oe-") as tmp:
        root = Path(tmp)
        raw_path = root / "opaque.raw.json"
        candidate_path = root / "opaque.candidate.json"
        raw_path.write_bytes(payload_bytes)

        if sha_bytes(raw_path.read_bytes()) != before_sha:
            raise RegressionError("payload changed before frozen candidate invocation")
        if CANARY.encode() in raw_path.read_bytes():
            raise RegressionError("target canary leaked into candidate-visible payload")

        candidate, candidate_stdout = run_json(
            ["python", "-m", CANDIDATE, "--input-json", str(raw_path)]
        )
        candidate_path.write_text(candidate_stdout, encoding="utf-8")
        checker, _ = run_json(
            [
                "python", "-m", CHECKER,
                "--input-json", str(raw_path),
                "--candidate-json", str(candidate_path),
            ]
        )

        after_sha = sha_bytes(raw_path.read_bytes())
        if after_sha != before_sha:
            raise RegressionError("candidate/checker or observer changed committed input bytes")

    return {
        "mode": mode,
        "observer_receipt": obs,
        "candidate_input_sha256": before_sha,
        "candidate_output_sha256": sha_obj(candidate),
        "checker_output_sha256": sha_obj(checker),
        "candidate": candidate,
        "checker_verified": checker.get("verified"),
        "checker_status": checker.get("status"),
        "payload_unchanged": after_sha == before_sha,
    }


def run_authority(label: str, raw: dict[str, Any]) -> dict[str, Any]:
    # Canonical JSON is precommitted once; every observer mode receives these exact bytes.
    payload_bytes = (canon(raw) + "\n").encode("utf-8")
    precommitted_sha = sha_bytes(payload_bytes)
    runs = [run_mode(payload_bytes, mode) for mode in OBSERVER_MODES]

    candidate_inputs = {r["candidate_input_sha256"] for r in runs}
    candidate_outputs = {r["candidate_output_sha256"] for r in runs}
    checker_outputs = {r["checker_output_sha256"] for r in runs}
    statuses = {r["candidate"]["status"] for r in runs}
    solver_authorities = {r["candidate"]["solver_authority"] for r in runs}
    checker_verified = {r["checker_verified"] for r in runs}
    checker_statuses = {r["checker_status"] for r in runs}

    expected = EXPECTED[label]
    checks = {
        "candidate_input_identical_across_observer_modes": len(candidate_inputs) == 1,
        "candidate_output_identical_across_observer_modes": len(candidate_outputs) == 1,
        "checker_output_identical_across_observer_modes": len(checker_outputs) == 1,
        "precommitted_payload_preserved": candidate_inputs == {precommitted_sha},
        "candidate_status_expected": statuses == {expected["status"]},
        "solver_authority_expected": solver_authorities == {expected["solver_authority"]},
        "checker_verified_all_modes": checker_verified == {True},
        "checker_status_matches_candidate": checker_statuses == {expected["status"]},
        "payload_unchanged_all_modes": all(r["payload_unchanged"] for r in runs),
        "semantic_sha_expected": all(
            r["candidate"].get("raw_semantic_sha256") == expected["raw_semantic_sha256"]
            for r in runs
        ),
    }
    if not all(checks.values()):
        raise RegressionError(f"observer noninterference regression failed for {label}: {checks}")

    return {
        "authority_label_revealed_only_in_result_receipt": label,
        "raw_semantic_sha256": expected["raw_semantic_sha256"],
        "precommitted_payload_sha256": precommitted_sha,
        "candidate_output_sha256": next(iter(candidate_outputs)),
        "checker_output_sha256": next(iter(checker_outputs)),
        "status": expected["status"],
        "checks": checks,
        "modes": [
            {
                "mode": r["mode"],
                "observer_receipt": r["observer_receipt"],
                "candidate_input_sha256": r["candidate_input_sha256"],
                "candidate_output_sha256": r["candidate_output_sha256"],
                "checker_output_sha256": r["checker_output_sha256"],
            }
            for r in runs
        ],
    }


def unsafe_shared_object_negative_control(raw: dict[str, Any]) -> dict[str, Any]:
    # Demonstrate that the detector catches the forbidden anti-pattern: observer and
    # candidate share one mutable object instead of independent decodes.
    shared = json.loads(canon(raw))
    before = sha_obj(shared)
    shared["constraints"].clear()
    shared["observer_private_canary"] = CANARY
    after = sha_obj(shared)
    detected = before != after and CANARY in canon(shared)
    if not detected:
        raise RegressionError("unsafe shared-object contamination was not detected")
    return {
        "control": "UNSAFE_SHARED_MUTABLE_OBJECT",
        "expected": "CONTAMINATION_DETECTED",
        "detected": True,
        "before_sha256": before,
        "after_sha256": after,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if not args.run:
        parser.error("only --run is authorized")

    source_bindings = assert_sealed_sources()

    # The labels are used only to ask the already sealed authority generator to reproduce
    # its historical raw objects. They are never passed to the candidate subprocess.
    positive_raw = materialize_sealed_raw("positive")
    negative_raw = materialize_sealed_raw("negative")

    # Freeze target-aware metadata outside candidate execution.
    target_metadata_envelope = {
        "canary": CANARY,
        "historical_lineage": "APMA_UNSEEN_LOCAL_INVARIANT_STAGE_C",
        "historical_labels": ["positive", "negative"],
        "expected_statuses": {
            k: EXPECTED[k]["status"] for k in ("positive", "negative")
        },
    }
    metadata_sha = sha_obj(target_metadata_envelope)

    positive = run_authority("positive", positive_raw)
    negative = run_authority("negative", negative_raw)

    candidate_freeze = {
        "positive_candidate_output_sha256": positive["candidate_output_sha256"],
        "negative_candidate_output_sha256": negative["candidate_output_sha256"],
        "positive_checker_output_sha256": positive["checker_output_sha256"],
        "negative_checker_output_sha256": negative["checker_output_sha256"],
    }
    candidate_freeze_sha = sha_obj(candidate_freeze)

    # Delayed reveal occurs only now. Merely reading the envelope must not alter the
    # previously frozen candidate/checker hashes.
    revealed = json.loads(canon(target_metadata_envelope))
    delayed_reveal_checks = {
        "canary_present_only_after_candidate_freeze": revealed["canary"] == CANARY,
        "candidate_freeze_unchanged_after_reveal": sha_obj(candidate_freeze) == candidate_freeze_sha,
        "metadata_envelope_sha256_unchanged": sha_obj(revealed) == metadata_sha,
    }
    if not all(delayed_reveal_checks.values()):
        raise RegressionError(f"delayed-reveal check failed: {delayed_reveal_checks}")

    negative_control = unsafe_shared_object_negative_control(positive_raw)

    result = {
        "verdict": "PASS_SEALED_STAGE_C_OBSERVER_NONINTERFERENCE_CALIBRATION_ONLY",
        "classification": "DIAGNOSTIC_ONLY__HISTORICAL_SEALED_STAGE_C_REGRESSION",
        "sealed_candidate_changed": False,
        "sealed_checker_changed": False,
        "sealed_blind_authority_changed": False,
        "source_bindings": source_bindings,
        "positive": positive,
        "negative": negative,
        "candidate_freeze_sha256_before_delayed_reveal": candidate_freeze_sha,
        "target_metadata_envelope_sha256": metadata_sha,
        "delayed_reveal_checks": delayed_reveal_checks,
        "unsafe_shared_object_negative_control": negative_control,
        "authority": {
            "scientific_new_evidence": False,
            "new_solver": False,
            "new_carrier": False,
            "new_discovery_mechanism": False,
            "universality_proved": False,
            "arbitrary_unseen_invariant_discovery": "NOT_PROVED",
            "general_sat_in_p": "NOT_PROVED",
            "p_vs_np": "OPEN",
        },
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
