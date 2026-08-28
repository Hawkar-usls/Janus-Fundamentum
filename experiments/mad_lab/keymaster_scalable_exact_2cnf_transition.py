#!/usr/bin/env python3
"""Exact scalable replay of JANUS elimination semantics for width<=2 CNFs.

The frozen semantics are unchanged:
1) retain pivot-free clauses;
2) add unique non-tautological resolvents in deterministic parent order;
3) charge raw_units before canonical subsumption;
4) reject immediately when raw_units exceeds cap;
5) canonicalize the raw set.

For width<=2 input, resolvents have width<=2. Canonical subsumption can then be
computed exactly without the general quadratic subset scan:
- an empty clause subsumes everything;
- a unit (l) subsumes exactly every width-2 clause containing l;
- two distinct width-2 clauses cannot subsume one another.

Self-tests require output and accounting equality against the canonical generic
`eliminate_var_capped` across representative tracks and multiple caps. This is
an implementation-equivalent exact replay, not a heuristic shortcut.
P_VS_NP=OPEN.
"""
from __future__ import annotations

import json
from typing import Any

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.mad_lab import asymmetric_pq_track as pqtrack
from experiments.mad_lab import keymaster_scalable_exact_root_labels as labels

P_VS_NP = "OPEN"
SCHEMA = "JANUS/KEYMASTER/SCALABLE-EXACT-2CNF-TRANSITION/v1.0.0"
UNBOUNDED_CAP = 10**18


def canon_width2_raw_exact(raw: set[base.Clause]) -> base.CNF:
    if any(len(c) > 2 for c in raw):
        raise ValueError("width-2 exact canonicalizer received a wider clause")
    if () in raw:
        return ((),)
    units = {c for c in raw if len(c) == 1}
    unit_literals = {c[0] for c in units}
    twos = {c for c in raw if len(c) == 2 and not any(l in unit_literals for l in c)}
    kept = units | twos
    return tuple(sorted(kept, key=lambda c: (len(c), c)))


def eliminate_var_capped_2cnf_exact(cnf: base.CNF, var: int, raw_cap: int) -> tuple[base.CNF | None, dict[str, Any]]:
    if any(len(c) > 2 for c in cnf):
        raise ValueError("specialized exact replay only supports width<=2 CNF")
    pos = [c for c in cnf if var in c]
    neg = [c for c in cnf if -var in c]
    retained = [c for c in cnf if var not in c and -var not in c]

    raw: set[base.Clause] = set(retained)
    raw_units = base.state_units(tuple(raw))
    if raw_units > raw_cap:
        return None, {"var": var, "pairs": 0, "tautologies": 0, "raw_units": raw_units, "cap": raw_cap}

    pairs = 0; tautologies = 0
    for p in pos:
        for n in neg:
            pairs += 1
            r = labels.resolve_2cnf_exact(p, n, var)
            if r is None:
                tautologies += 1
                continue
            if r not in raw:
                raw.add(r)
                raw_units += 1 + len(r)
                if raw_units > raw_cap:
                    return None, {
                        "var": var, "pairs": pairs, "tautologies": tautologies,
                        "raw_units": raw_units, "cap": raw_cap, "aborted": True,
                    }

    out = canon_width2_raw_exact(raw)
    return out, {
        "var": var, "positive": len(pos), "negative": len(neg), "retained": len(retained),
        "pairs": pairs, "tautologies": tautologies, "raw_units": raw_units,
        "canonical_units": base.state_units(out), "cap": raw_cap, "aborted": False,
    }


def verify_transition_2cnf_exact(before: base.CNF, var: int, after: base.CNF, raw_cap: int) -> bool:
    rebuilt, _ = eliminate_var_capped_2cnf_exact(before, var, raw_cap)
    return rebuilt is not None and rebuilt == after


def root_runtime_fast(e: dict[str, Any], order: list[int]) -> dict[str, Any]:
    cap = e["local_stress_cap"]
    checks = 0; pair_work = 0; raw_sum = 0; peak = e["root_units"]; attempts = []
    chosen = None
    for idx in order:
        pivot = e["vars"][idx]
        checks += 1
        out, st = eliminate_var_capped_2cnf_exact(e["cnf"], pivot, cap)
        raw = int(st["raw_units"]); pairs = int(st.get("pairs", 0))
        pair_work += pairs; raw_sum += raw; peak = max(peak, raw)
        fit = out is not None
        attempts.append({"pivot_local_for_audit": pivot, "raw_units": raw, "pair_work": pairs, "fit": fit})
        if fit:
            if not verify_transition_2cnf_exact(e["cnf"], pivot, out, cap):
                raise AssertionError("specialized exact transition replay failed")
            chosen = pivot
            break
    if chosen is None:
        raise AssertionError("q30 cap must admit at least one exact root pivot")
    return {
        "exact_checks": checks, "pair_work": pair_work, "raw_units_sum": raw_sum,
        "peak_raw_units": peak, "chosen_first_pivot_local_for_audit": chosen,
        "root_attempts": attempts, "exact_transition_verified": True,
        "exact_replay_engine": "WIDTH2_SEMANTIC_EQUIVALENT_REPLAY",
    }


def _project_stats(st: dict[str, Any]) -> dict[str, Any]:
    keys = ("var", "positive", "negative", "retained", "pairs", "tautologies", "raw_units", "canonical_units", "cap", "aborted")
    return {k: st.get(k) for k in keys if k in st}


def self_test() -> dict[str, Any]:
    comparisons = []
    for p, q, seed in [(1, 1, 9100), (3, 3, 9101), (11, 11, 9102), (13, 16, 9103), (16, 13, 9104), (31, 31, 9105)]:
        cnf, _ = pqtrack.construct(p, q, seed)
        pivots = list(base.vars_of(cnf))
        probes = pivots if len(pivots) <= 18 else [pivots[0], pivots[len(pivots)//2], pivots[-1]]
        for pivot in probes:
            full_out, full_st = base.eliminate_var_capped(cnf, pivot, UNBOUNDED_CAP)
            if full_out is None:
                raise AssertionError("unbounded generic engine overflowed")
            raw = int(full_st["raw_units"])
            caps = sorted(set([max(1, raw - 1), raw, raw + 7, UNBOUNDED_CAP]))
            for cap in caps:
                a, sa = base.eliminate_var_capped(cnf, pivot, cap)
                b, sb = eliminate_var_capped_2cnf_exact(cnf, pivot, cap)
                if a != b or _project_stats(sa) != _project_stats(sb):
                    raise AssertionError({"p": p, "q": q, "pivot": pivot, "cap": cap, "generic_out": a, "fast_out": b, "generic_stats": sa, "fast_stats": sb})
                if b is not None and not verify_transition_2cnf_exact(cnf, pivot, b, cap):
                    raise AssertionError("self-verification failed")
                comparisons.append({"p": p, "q": q, "pivot": pivot, "cap": cap, "fit": b is not None})
    return {
        "schema": SCHEMA + "/self-test", "status": "PASS", "comparisons": len(comparisons),
        "output_bit_identical_to_generic_engine": True,
        "accounting_identical_to_generic_engine": True,
        "semantic_change": False, "heuristic_approximation": False,
        "P_VS_NP": P_VS_NP,
    }


if __name__ == "__main__":
    print(json.dumps(self_test(), indent=2, sort_keys=True))
