#!/usr/bin/env python3
"""Run the frozen JANUS pre-math gate with additive supplemental audits.

The base validator is not weakened or reimplemented.  This wrapper only merges
supplemental audit entries into the in-memory ledger, then delegates every
semantic-route, no-loop, source-audit, coverage, and atom-origin check to the
existing validator.
"""
from __future__ import annotations

from pathlib import Path

import validate_premath_gate as base

SUPPLEMENT = (
    base.ROOT
    / "governance"
    / "JANUS_P_VS_NP_PREMATH_SUPPLEMENT_2026-09-27_v1.0.json"
)
_ORIGINAL_LOAD_JSON = base.load_json


def load_json_with_supplement(path: Path):
    data = _ORIGINAL_LOAD_JSON(path)
    if Path(path).resolve() != base.LEDGER.resolve():
        return data

    supplement = _ORIGINAL_LOAD_JSON(SUPPLEMENT)
    extra = supplement.get("audits")
    if not isinstance(extra, list):
        raise base.GateError("supplement audits must be a list")

    if not isinstance(data, dict):
        raise base.GateError("base pre-math ledger must be an object")
    base_audits = data.get("audits")
    if not isinstance(base_audits, list):
        raise base.GateError("base pre-math ledger audits must be a list")

    merged = dict(data)
    merged["audits"] = [*base_audits, *extra]
    return merged


base.load_json = load_json_with_supplement


if __name__ == "__main__":
    raise SystemExit(base.main())
