#!/usr/bin/env python3
"""Compact diagnostic wrapper for the historical novelty audit."""

from __future__ import annotations

import json
import traceback

from janus_tear_gt_novel_branch_audit import audit


def self_test() -> None:
    records = []
    failed = False
    for n in range(4, 9):
        try:
            data = audit(n)
            record = {
                "n": n,
                "status": "PASS",
                "calls": data["calls"],
                "states": data["states"],
                "maximum_novelty": data["maximum_novelty"],
                "target_level": data["target_level"],
                "first_target_distinct_restrictions": data[
                    "first_target_distinct_restrictions"
                ],
            }
            records.append(record)
            print("NOVEL_DEBUG_JSON=" + json.dumps(record, sort_keys=True))
        except Exception as error:  # diagnostic artifact intentionally broad
            frames = traceback.extract_tb(error.__traceback__)
            last = frames[-1] if frames else None
            record = {
                "n": n,
                "status": "FAILURE",
                "exception_type": type(error).__name__,
                "message": str(error),
                "file": last.filename if last else None,
                "line": last.lineno if last else None,
                "function": last.name if last else None,
                "source": last.line if last else None,
                "traceback": [
                    {
                        "file": frame.filename,
                        "line": frame.lineno,
                        "function": frame.name,
                        "source": frame.line,
                    }
                    for frame in frames
                ],
            }
            records.append(record)
            print("NOVEL_DEBUG_JSON=" + json.dumps(record, sort_keys=True))
            failed = True
            break

    print("NOVEL_DEBUG_SUMMARY=" + json.dumps(records, sort_keys=True))
    print("claim_boundary = diagnostic wrapper; a failure is data, not a theorem")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    self_test()
