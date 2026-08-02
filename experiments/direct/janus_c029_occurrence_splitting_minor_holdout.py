#!/usr/bin/env python3
"""Independent negative control for the C029 branch-set minor certificate."""
from __future__ import annotations
import importlib.util
from pathlib import Path

BASE = Path(__file__).with_name("janus_c029_occurrence_splitting_minor.py")
spec = importlib.util.spec_from_file_location("c029_minor", BASE)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def main() -> None:
    formula = ((1, 2), (-1, 3))
    source = m.incidence(formula)
    target, branch_sets, occurrences = m.split(formula, m.random.Random(290032))

    # Delete the target edge representing the second occurrence of variable 1.
    occurrence = occurrences[(1, 0)]
    clause = "C:1"
    target[occurrence].discard(clause)
    target[clause].discard(occurrence)

    ok, reason = m.verify(source, target, branch_sets)
    assert not ok
    assert reason.startswith("missing:"), reason
    print({
        "artifact_id": "C029-OCCURRENCE-SPLITTING-HOLDOUT",
        "status": "PASS",
        "rejected_certificate": reason,
        "p_vs_np": "OPEN"
    })


if __name__ == "__main__":
    main()
