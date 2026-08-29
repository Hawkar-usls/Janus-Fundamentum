#!/usr/bin/env python3
"""Isolated implementation repair for frozen E2_BALANCED_4CNF.

The original run1 harness is imported unchanged.  Only its BALANCED_4CNF
constructor entry is replaced according to the append-only repair contract.
After execution, the six non-E2 epoch summaries must exactly match run1.
"""
from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_structural_lambda_roosters_multi_epoch_gate as gate

P_VS_NP = "OPEN"
REPAIR_SPEC = Path("research/C025_STRUCTURAL_LAMBDA_E2_BALANCED_CONSTRUCTOR_REPAIR_2026-08-29.json")


def repaired_make_balanced_4cnf(spec: dict) -> dict:
    rng = random.Random(int(spec["seed"]))
    n = int(spec["nvars"])
    m = int(spec["budget"])
    variables = list(range(1, n + 1))
    total = Counter({v: 0 for v in variables})
    pos = Counter({v: 0 for v in variables})
    neg = Counter({v: 0 for v in variables})
    rows: set[base.Clause] = set()
    tries = 0
    while len(rows) < m:
        tries += 1
        if tries > 200000:
            raise RuntimeError("REPAIRED_BALANCED_INIT_EXHAUSTED")
        # Pick among least-used variables; random tie keys are search-order only.
        keyed = [(total[v], rng.random(), v) for v in variables]
        keyed.sort()
        support = sorted(v for _, _, v in keyed[:4])
        lits = []
        for v in support:
            if pos[v] < neg[v]:
                sign = 1
            elif neg[v] < pos[v]:
                sign = -1
            else:
                sign = 1 if rng.getrandbits(1) else -1
            lits.append(sign * v)
        c = base.canon_clause(lits)
        if c is None or c in rows:
            continue
        rows.add(c)
        for lit in c:
            v = abs(lit)
            total[v] += 1
            if lit > 0:
                pos[v] += 1
            else:
                neg[v] += 1
    cnf = base.canon_cnf(rows)
    if len(cnf) != m or any(len(c) != 4 for c in cnf):
        raise AssertionError("REPAIRED_BALANCED_SHAPE_DRIFT")
    if set(base.vars_of(cnf)) != set(variables):
        raise AssertionError("REPAIRED_BALANCED_VARIABLE_COVERAGE_DRIFT")
    degree_values = [total[v] for v in variables]
    if max(degree_values) - min(degree_values) > 2:
        raise AssertionError("REPAIRED_BALANCED_TOTAL_DEGREE_DRIFT")
    if any(abs(pos[v] - neg[v]) > 1 for v in variables):
        raise AssertionError("REPAIRED_BALANCED_SIGN_DEGREE_DRIFT")
    return {
        "kind": spec["constructor"],
        "rows": list(cnf),
        "variables": variables,
        "repair_invariants": {
            "clauses": len(cnf),
            "width": 4,
            "min_total_degree": min(degree_values),
            "max_total_degree": max(degree_values),
            "max_sign_imbalance": max(abs(pos[v] - neg[v]) for v in variables),
        },
    }


def close(a: float, b: float) -> bool:
    return abs(a - b) <= 1e-12 * max(1.0, abs(a), abs(b))


def verify_non_e2_immutable(report: dict) -> None:
    expected = {
        "E1_RANDOM_3CNF": ("OUTSIDE", 32.0, 1.7629428790753605),
        "E3_PLANTED_3SAT": ("OUTSIDE", 32.0, 2.3225590822710305),
        "E4_XOR3_SYSTEM": ("OUTSIDE", 32.0, 1.1498994491259047),
        "E5_PHP_CORE_PLUS_NOISE": ("BROAD_SUPPORT", 21.333333333333332, 1.0821709849993055),
        "E6_GRAPH_3COLOR": ("OUTSIDE", 8.0, 1.079636362810167),
        "E7_CONTRADICTORY_CORE_PLUS_NOISE": ("OUTSIDE", 32.0, 10.961778043692377),
    }
    seen = {e["epoch_id"]: e for e in report["epochs"]}
    for eid, (label, wavelength, ratio) in expected.items():
        e = seen[eid]
        c = e["classification"]
        if c["label"] != label:
            raise AssertionError(f"NON_E2_LABEL_DRIFT:{eid}")
        if not close(float(c["primary"]["wavelength_generations"]), wavelength):
            raise AssertionError(f"NON_E2_LAMBDA_DRIFT:{eid}")
        if not close(float(c["top_to_second_power_ratio"]), ratio):
            raise AssertionError(f"NON_E2_RATIO_DRIFT:{eid}")


def main() -> int:
    repair = json.loads(REPAIR_SPEC.read_text(encoding="utf-8"))
    if repair["status"] != "FROZEN_IMPLEMENTATION_REPAIR_BEFORE_RERUN":
        raise ValueError("REPAIR_SPEC_NOT_FROZEN")
    prereg = json.loads(gate.PREREG_PATH.read_text(encoding="utf-8"))
    e2 = next(x for x in prereg["voting_epochs"] if x["id"] == "E2_BALANCED_4CNF")
    smoke = repaired_make_balanced_4cnf(e2)
    inv = smoke["repair_invariants"]
    assert inv["clauses"] == 50
    assert inv["width"] == 4
    assert inv["max_total_degree"] - inv["min_total_degree"] <= 2
    assert inv["max_sign_imbalance"] <= 1

    gate.BUILDERS["BALANCED_4CNF"] = repaired_make_balanced_4cnf
    rc = gate.main()
    if rc != 0:
        return rc
    report = json.loads(gate.OUT_PATH.read_text(encoding="utf-8"))
    verify_non_e2_immutable(report)
    report["implementation_repair"] = {
        "spec": str(REPAIR_SPEC),
        "E2_initial_invariants": inv,
        "non_E2_epoch_summary_immutable": True,
        "run1_unknown_remains_immutable": True,
    }
    gate.OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E2_REPAIR_INVARIANTS=" + json.dumps(inv, sort_keys=True))
    print("NON_E2_IMMUTABLE=PASS")
    print("FINAL_STATUS=" + report["status"])
    print("P_VS_NP=OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
