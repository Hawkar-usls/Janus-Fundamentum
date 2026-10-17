#!/usr/bin/env python3
"""Run the frozen JANUS pre-math gate with additive supplemental audits.

The base validator is not weakened or reimplemented. This wrapper only merges
append-only supplemental audit entries into the in-memory ledger, then delegates
every semantic-route, no-loop, source-audit, coverage, and atom-origin check to
the existing validator.
"""
from __future__ import annotations

from pathlib import Path

import validate_premath_gate as base

SUPPLEMENT_GLOB = "JANUS_P_VS_NP_PREMATH_SUPPLEMENT_*.json"
SUPPLEMENT_DIR = base.ROOT / "governance"
_ORIGINAL_LOAD_JSON = base.load_json


def load_json_with_supplements(path: Path):
    data = _ORIGINAL_LOAD_JSON(path)
    if Path(path).resolve() != base.LEDGER.resolve():
        return data

    if not isinstance(data, dict):
        raise base.GateError("base pre-math ledger must be an object")
    base_audits = data.get("audits")
    if not isinstance(base_audits, list):
        raise base.GateError("base pre-math ledger audits must be a list")

    merged_audits = list(base_audits)
    supplements = sorted(SUPPLEMENT_DIR.glob(SUPPLEMENT_GLOB))
    if not supplements:
        raise base.GateError("no supplemental pre-math audit ledger found")

    for supplement_path in supplements:
        supplement = _ORIGINAL_LOAD_JSON(supplement_path)
        extra = supplement.get("audits")
        if not isinstance(extra, list):
            raise base.GateError(
                f"{supplement_path.name}: supplement audits must be a list"
            )
        merged_audits.extend(extra)

    merged = dict(data)
    merged["audits"] = merged_audits
    return merged


base.load_json = load_json_with_supplements


if __name__ == "__main__":
    raise SystemExit(base.main())
