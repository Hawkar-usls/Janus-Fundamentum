#!/usr/bin/env python3
"""Scalable implementation of the existing Keymaster candidate token semantics.

This module is an implementation optimization only. It computes the same 7x7
cheap structural token values as adaptive_pippi_pitstop_ladder.candidate_tokens,
but replaces repeated membership scans over every parent clause for every other
variable with one incidence-count pass per positive/negative pivot parent set.

No feature is added, removed, reweighted, or renamed. Numeric pivot IDs remain
absent. Exact raw units/resolvents remain labels, not inputs. P_VS_NP=OPEN.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from typing import Any

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.mad_lab import adaptive_pippi_pitstop_ladder as legacy
from experiments.mad_lab import asymmetric_pq_track as pqtrack
from experiments.mad_lab import juxtapose_50x50_multiformula_corpus as j50

P_VS_NP = "OPEN"
FEATURE_DIM = 7
SCHEMA = "JANUS/KEYMASTER/SCALABLE-FEATURE-TOKENS/v1.0.0"


def avg_rows(rows: list[list[float]]) -> list[float]:
    if not rows:
        return [0.0] * FEATURE_DIM
    return [sum(r[j] for r in rows) / len(rows) for j in range(FEATURE_DIM)]


def _parent_incidence(clauses: list[base.Clause], pivot: int) -> tuple[Counter[int], Counter[int]]:
    positive: Counter[int] = Counter()
    negative: Counter[int] = Counter()
    for clause in clauses:
        for lit in clause:
            if abs(lit) == pivot:
                continue
            if lit > 0:
                positive[lit] += 1
            else:
                negative[-lit] += 1
    return positive, negative


def candidate_tokens_fast(cnf: base.CNF, pivot: int) -> list[list[float]]:
    """Exactly match legacy.candidate_tokens with asymptotically cheaper counting."""
    pos = [c for c in cnf if pivot in c]
    neg = [c for c in cnf if -pivot in c]
    retained_count = sum(1 for c in cnf if pivot not in c and -pivot not in c)
    others = [v for v in base.vars_of(cnf) if v != pivot]
    pairs = max(1, len(pos) * len(neg))

    pos_plus, pos_minus = _parent_incidence(pos, pivot)
    neg_plus, neg_minus = _parent_incidence(neg, pivot)

    rows: list[list[float]] = []
    conflicts: list[float] = []
    aligned: list[float] = []
    overlaps: list[float] = []
    for v in others:
        pp = pos_plus[v]; pm = pos_minus[v]; np = neg_plus[v]; nm = neg_minus[v]
        conf = pp * nm + pm * np
        same = pp * np + pm * nm
        ov = (pp + pm) * (np + nm)
        conflicts.append(conf / pairs); aligned.append(same / pairs); overlaps.append(ov / pairs)
        rows.append([
            pp / max(1, len(pos)), pm / max(1, len(pos)),
            np / max(1, len(neg)), nm / max(1, len(neg)),
            conf / pairs, same / pairs, ov / pairs,
        ])

    rows.sort(key=lambda r: tuple(round(x, 12) for x in r))
    pooled: list[list[float]] = []
    if rows:
        n = len(rows)
        for b in range(6):
            a = (b * n) // 6; z = ((b + 1) * n) // 6
            pooled.append(avg_rows(rows[a:z]))
    else:
        pooled = [[0.0] * FEATURE_DIM for _ in range(6)]
    while len(pooled) < 6:
        pooled.append([0.0] * FEATURE_DIM)

    summary = [
        sum(conflicts) / max(1, len(conflicts)),
        sum(aligned) / max(1, len(aligned)),
        sum(overlaps) / max(1, len(overlaps)),
        max(conflicts, default=0.0),
        max(conflicts, default=0.0) - min(conflicts, default=0.0),
        retained_count / max(1, len(cnf)),
        math.log1p(len(cnf)) / 10.0,
    ]
    return pooled[:6] + [summary]


def _max_abs_delta(a: list[list[float]], b: list[list[float]]) -> float:
    return max((abs(x - y) for ra, rb in zip(a, b) for x, y in zip(ra, rb)), default=0.0)


def self_test() -> dict[str, Any]:
    cases: list[tuple[str, base.CNF]] = []
    for p, q, seed in [(11, 11, 1001), (13, 16, 1002), (16, 13, 1003)]:
        cnf, _ = pqtrack.construct(p, q, seed)
        cases.append((f"PQ_{p}x{q}", cnf))
    # Width-5 historical bootstrap checks generic-CNF equivalence too.
    cases.append(("HISTORICAL_50x50_WIDTH5", j50.construct(1)))

    audit = []
    for name, cnf in cases:
        pivots = list(base.vars_of(cnf))
        probes = pivots if len(pivots) <= 12 else [pivots[0], pivots[len(pivots)//2], pivots[-1]]
        for pivot in probes:
            old = legacy.candidate_tokens(cnf, pivot)
            new = candidate_tokens_fast(cnf, pivot)
            delta = _max_abs_delta(old, new)
            if delta > 1e-15:
                raise AssertionError((name, pivot, delta))
            audit.append({"case": name, "pivot": pivot, "max_abs_delta": delta})
    return {
        "schema": SCHEMA + "/self-test",
        "status": "PASS",
        "semantic_equivalence_cases": audit,
        "feature_semantics_changed": False,
        "pivot_numeric_id_is_feature": False,
        "P_VS_NP": P_VS_NP,
    }


if __name__ == "__main__":
    print(json.dumps(self_test(), indent=2, sort_keys=True))
