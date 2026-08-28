#!/usr/bin/env python3
"""Exact scalable raw-cap labels for 2-CNF root navigation.

The canonical JANUS cap is charged on the raw deduplicated clause set BEFORE
`canon_cnf` subsumption compression. Training/ranking labels in the PIPPI
2-CNF gauntlet require exactly this raw_units value and pair count; they do not
require materializing the final canonically compressed CNF for every candidate.

This module computes the same raw set by exact width<=2 resolution and is gated
by equality tests against `eliminate_var_capped(..., UNBOUNDED_CAP)`.
Actual counted STATIC/KEYMASTER/ORACLE moves continue to call the canonical
engine and `verify_elimination_transition` in the gauntlet runtime.

This is an implementation optimization, not a heuristic approximation and not
a proof shortcut. P_VS_NP=OPEN.
"""
from __future__ import annotations

import json
from typing import Any

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.mad_lab import asymmetric_pq_track as pqtrack
from experiments.mad_lab import keymaster_scalable_feature_tokens as features
from experiments.mad_lab import adaptive_pippi_pitstop_ladder as v1

P_VS_NP = "OPEN"
SCHEMA = "JANUS/KEYMASTER/SCALABLE-EXACT-2CNF-ROOT-LABELS/v1.0.0"
UNBOUNDED_CAP = 10**18


def _lit_key(z: int) -> tuple[int, bool]:
    return (abs(z), z < 0)


def resolve_2cnf_exact(left: base.Clause, right: base.Clause, var: int) -> base.Clause | None:
    """Exact specialized form of base.resolve_on_var for width<=2 parents."""
    if var in left and -var in right:
        drop_l, drop_r = var, -var
    elif -var in left and var in right:
        drop_l, drop_r = -var, var
    else:
        raise ValueError("parents do not contain complementary pivot")
    a = [x for x in left if x != drop_l]
    b = [x for x in right if x != drop_r]
    if len(a) > 1 or len(b) > 1:
        raise ValueError("resolve_2cnf_exact only supports width<=2 parents")
    if not a and not b:
        return ()
    if not a:
        return (b[0],)
    if not b:
        return (a[0],)
    x, y = a[0], b[0]
    if x == -y:
        return None
    if x == y:
        return (x,)
    return tuple(sorted((x, y), key=_lit_key))


def raw_stats_2cnf(cnf: base.CNF, var: int) -> dict[str, int | bool]:
    if any(len(c) > 2 for c in cnf):
        raise ValueError("raw_stats_2cnf requires width<=2 CNF")
    pos = [c for c in cnf if var in c]
    neg = [c for c in cnf if -var in c]
    retained = [c for c in cnf if var not in c and -var not in c]
    raw: set[base.Clause] = set(retained)
    raw_units = 1 + len(raw) + sum(len(c) for c in raw)
    pairs = 0; tautologies = 0
    for p in pos:
        for n in neg:
            pairs += 1
            r = resolve_2cnf_exact(p, n, var)
            if r is None:
                tautologies += 1
                continue
            if r not in raw:
                raw.add(r)
                raw_units += 1 + len(r)
    return {
        "var": var, "positive": len(pos), "negative": len(neg),
        "retained": len(retained), "pairs": pairs,
        "tautologies": tautologies, "raw_units": raw_units,
        "aborted": False,
    }


def exact_track_episode_fast(cnf: base.CNF, p: int, q: int, seed: int, source: str, stage_serial: int) -> dict[str, Any]:
    sat2 = base.solve_2sat_exact(cnf)
    if sat2 is None or sat2[0] is not False:
        raise AssertionError("track formula not independently exact-UNSAT 2-CNF")
    fp = base.fingerprint(cnf); vs = list(base.vars_of(cnf)); root_units = base.state_units(cnf)
    tokens = []; raw = []; pairs = []
    for pivot in vs:
        tokens.append(features.candidate_tokens_fast(cnf, pivot))
        st = raw_stats_2cnf(cnf, pivot)
        raw.append(int(st["raw_units"])); pairs.append(int(st["pairs"]))
    order = sorted(range(len(vs)), key=lambda i: (raw[i], v1.stable_hash(tokens[i])))
    qidx = max(0, min(len(vs) - 1, int(0.30 * (len(vs) - 1))))
    cap = max(root_units, sorted(raw)[qidx])
    mn, mx = min(raw), max(raw)
    rel = [0.0 if mx == mn else (x - mn) / (mx - mn) for x in raw]
    best = {i for i, x in enumerate(raw) if x == mn}
    safe = {i for i, x in enumerate(raw) if x <= cap}
    return {
        "d": max(p, q), "p": p, "q": q, "difficulty": f"{p}:{q}",
        "seed": seed, "source": source, "stage_serial": stage_serial,
        "fingerprint": fp, "cnf": cnf, "vars": vs, "tokens": tokens,
        "raw": raw, "pair_labels": pairs, "after_units": [None] * len(vs),
        "raw_relative": rel, "best_indices": sorted(best), "safe_indices": sorted(safe),
        "local_stress_cap": cap, "root_units": root_units, "raw_span": mx - mn,
        "oracle_root_order": order, "independent_unsat_verifier": "EXACT_2SAT",
        "label_engine": "EXACT_RAW_SET_2CNF_BEFORE_CANONICAL_COMPRESSION",
    }


def self_test() -> dict[str, Any]:
    audit = []
    for p, q, seed in [(1, 1, 707), (3, 3, 708), (11, 11, 709), (13, 16, 710), (16, 13, 711)]:
        cnf, _ = pqtrack.construct(p, q, seed)
        for pivot in base.vars_of(cnf):
            fast = raw_stats_2cnf(cnf, pivot)
            out, canonical = base.eliminate_var_capped(cnf, pivot, UNBOUNDED_CAP)
            if out is None:
                raise AssertionError("unbounded canonical comparison unexpectedly overflowed")
            for key in ("positive", "negative", "retained", "pairs", "tautologies", "raw_units"):
                if int(fast[key]) != int(canonical[key]):
                    raise AssertionError((p, q, pivot, key, fast[key], canonical[key]))
            audit.append({"p": p, "q": q, "pivot": pivot, "raw_units": fast["raw_units"], "pairs": fast["pairs"]})
    return {
        "schema": SCHEMA + "/self-test", "status": "PASS",
        "comparisons": len(audit), "audit": audit,
        "raw_label_semantics_changed": False,
        "counted_move_verifier_removed": False,
        "P_VS_NP": P_VS_NP,
    }


if __name__ == "__main__":
    print(json.dumps(self_test(), indent=2, sort_keys=True))
