#!/usr/bin/env python3
"""Canonical C039 entrypoint.

The implementation was first committed under the legacy C038 path before the
parallel structured-vtree alignment reserved C038. This wrapper preserves exact
replayability while assigning the fixed-k recursive separator compiler to C039.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from janus_c038_recursive_separator_compiler import run as legacy_run


def run() -> dict:
    result = legacy_run()
    result.pop("integrity_sha256", None)
    result["artifact_id"] = (
        "C039-JANUS-PROOF-CARRYING-RECURSIVE-SEPARATOR-COMPILER"
    )
    result["canonical_cycle"] = "C039"
    result["legacy_implementation_path"] = (
        "experiments/direct/janus_c038_recursive_separator_compiler.py"
    )
    payload = json.dumps(
        result,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    result["integrity_sha256"] = hashlib.sha256(payload).hexdigest()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = run()
    if args.output:
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    print(json.dumps(result, indent=2, sort_keys=True))

    if args.self_test:
        assert result["status"] == "PASS"
        assert result["canonical_cycle"] == "C039"
        assert result["random_audit"]["mismatches"] == 0
        assert result["random_audit"]["verification_failures"] == 0
        assert result["equality_order_separation"][-1]["blocked_obdd_width"] == 4096
        assert result["open_controls"]["dense_clique_control"] == "NO_BALANCED_SEPARATOR"
        assert result["corrupt_control"]["corrupt_branch_assignment_rejected"]


if __name__ == "__main__":
    main()
