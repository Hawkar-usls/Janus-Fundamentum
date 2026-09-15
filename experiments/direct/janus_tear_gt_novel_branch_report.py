#!/usr/bin/env python3
"""Persist the C024 failure-tolerant novelty overlay as JSON."""

from __future__ import annotations

import json
from pathlib import Path

from janus_tear_gt_novel_branch_audit_v2 import audit


def self_test() -> None:
    rows = [audit(n) for n in range(4, 9)]
    payload = {
        "artifact": "JANUS_C024_NOVEL_BRANCH_REPORT",
        "rows": rows,
        "claim_boundary": "finite failure-tolerant overlay; no transferred Formula-Caching lower bound",
    }
    path = Path("diagnostics/C024_NOVEL_BRANCH_REPORT.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"JANUS_C024_NOVEL_BRANCH_REPORT = {path}")
    print(json.dumps(rows, sort_keys=True))


if __name__ == "__main__":
    self_test()
