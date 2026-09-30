#!/usr/bin/env python3
"""Adversarial tamper tests for the standalone stage-4 JEC proof object."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_jec_extension_progress_proof as proof_object


def rejected(raw, proof: dict) -> bool:
    return not proof_object.verify_extension_progress_proof(
        raw,
        proof,
        require_initial_context=True,
    )


def main() -> int:
    raw = ((1, 2, 3), (-1, 4))
    original = proof_object.discover_initial_extension_progress(raw)
    if original is None:
        raise AssertionError("TAMPER_GATE_NEEDS_BASE_PROOF")
    if not proof_object.verify_extension_progress_proof(raw, original, require_initial_context=True):
        raise AssertionError("BASE_PROOF_FAILED_BEFORE_TAMPER_TESTS")

    mutants: list[tuple[str, dict]] = []

    row = deepcopy(original)
    row["mode"] = "INVENTED_MODE"
    mutants.append(("MODE", row))

    row = deepcopy(original)
    row["N"] = int(row["N"]) + 1
    mutants.append(("FROZEN_N", row))

    row = deepcopy(original)
    row["macro_certificate"]["extension"] = int(row["macro_certificate"]["extension"]) + 1
    mutants.append(("MACRO_EXTENSION", row))

    row = deepcopy(original)
    row["elimination_steps"][0]["pivot"] = int(row["macro_certificate"]["extension"])
    mutants.append(("PIVOT", row))

    row = deepcopy(original)
    row["elimination_steps"][0]["after_cnf"] = []
    mutants.append(("AFTER_STATE", row))

    row = deepcopy(original)
    row["after_phi"] = int(row["after_phi"]) + 1
    mutants.append(("PHI", row))

    row = deepcopy(original)
    row["result_fingerprint"] = "0" * 64
    mutants.append(("RESULT_FINGERPRINT", row))

    results = []
    for name, mutant in mutants:
        was_rejected = rejected(raw, mutant)
        results.append({"tamper": name, "rejected": was_rejected})
        if not was_rejected:
            raise AssertionError(f"TAMPER_WAS_ACCEPTED:{name}")

    report = {
        "schema": "JANUS/C025/JEC-EXTENSION-PROGRESS-TAMPER-GATE/v1",
        "status": "PASS",
        "base_proof_verified": True,
        "tamper_cases": results,
        "all_tampers_rejected": True,
        "P_VS_NP": "OPEN",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
