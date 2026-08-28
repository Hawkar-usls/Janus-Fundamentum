#!/usr/bin/env python3
"""JANUS MAD-LAB 50:50 multi-formula exact corpus.

Cycle-0 data generation for the Keymaster/JGPT/Pivot-Slime/PIPPI program.
This script deliberately does NOT claim learning gain. It builds several
independent canonical n=7 formulas with p=q=50 for every variable, verifies
them exactly, exhaustively enumerates all 7! pivot orders without a restrictive
cap, then chooses a per-formula static stress cap equal to the minimum exact
route peak. This yields an oracle route and a near-cap landscape for later
matched learning/holdout tests.

Construction: all clauses have width 5. A complement-sign pair on one support
contributes one positive and one negative occurrence for each variable in that
support. We select 70 such pairs. Supports are indexed by their omitted 2-set.
Every omitted pair has multiplicity 3, plus one 7-cycle whose omitted pairs have
multiplicity 4. Hence each variable is omitted 20 times and present 50 times;
therefore each variable has degree 100 and polarity 50:50.

P_VS_NP remains OPEN. Static stress caps are local experiment parameters, not
proved reachable JANUS roots.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import itertools
import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Any

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base

SCHEMA = "JANUS/MAD-LAB/JUXTAPOSE-50x50-MULTIFORMULA/v1"
P_VS_NP = "OPEN"
NVAR = 7
WIDTH = 5
TARGET_POS = 50
TARGET_NEG = 50
TARGET_DEGREE = 100
PAIR_COUNT = 70
MCLAUSE = 140
LITERAL_MASS = 700
PIVOTS = tuple(range(1, NVAR + 1))
ORDERS = math.factorial(NVAR)
UNBOUNDED_CAP = 10**9


def digest(obj: object) -> str:
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def cycle_edges(seed: int) -> set[tuple[int, int]]:
    rng = random.Random(0x50_50_50 ^ int(seed))
    ring = list(PIVOTS)
    rng.shuffle(ring)
    edges = set()
    for i, a in enumerate(ring):
        b = ring[(i + 1) % len(ring)]
        edges.add(tuple(sorted((a, b))))
    assert len(edges) == 7
    degree = Counter(v for e in edges for v in e)
    assert degree == Counter({v: 2 for v in PIVOTS})
    return edges


def pair_mask_clauses(support: tuple[int, ...], pair_index: int) -> tuple[base.Clause, base.Clause]:
    assert 0 <= pair_index < 16
    mask = int(pair_index)
    comp = mask ^ 31
    def clause(m: int) -> base.Clause:
        lits = []
        for i, v in enumerate(support):
            lits.append(v if ((m >> i) & 1) else -v)
        return tuple(lits)
    return clause(mask), clause(comp)


def construct(seed: int) -> base.CNF:
    cyc = cycle_edges(seed)
    clauses: set[base.Clause] = set()
    multiplicities: dict[tuple[int, int], int] = {}
    for edge_idx, omitted in enumerate(itertools.combinations(PIVOTS, 2)):
        omitted = tuple(sorted(omitted))
        mult = 4 if omitted in cyc else 3
        multiplicities[omitted] = mult
        support = tuple(v for v in PIVOTS if v not in omitted)
        assert len(support) == WIDTH
        rng = random.Random((seed + 1) * 1_000_003 + edge_idx * 97_409 + 50_050)
        chosen = sorted(rng.sample(range(16), mult))
        for idx in chosen:
            a, b = pair_mask_clauses(support, idx)
            clauses.add(a); clauses.add(b)
    assert sum(multiplicities.values()) == PAIR_COUNT
    assert len(clauses) == MCLAUSE
    cnf = base.canon_cnf(tuple(sorted(clauses)))
    assert len(cnf) == MCLAUSE
    return cnf


def stats(cnf: base.CNF) -> dict[str, Any]:
    pos = [sum(v in c for c in cnf) for v in PIVOTS]
    neg = [sum(-v in c for c in cnf) for v in PIVOTS]
    degree = [a + b for a, b in zip(pos, neg)]
    widths = [len(c) for c in cnf]
    out = {
        "n": len(base.vars_of(cnf)),
        "m": len(cnf),
        "L": sum(widths),
        "state_units": base.state_units(cnf),
        "width_histogram": {str(k): widths.count(k) for k in sorted(set(widths))},
        "positive": pos,
        "negative": neg,
        "degree": degree,
        "fingerprint": base.fingerprint(cnf),
    }
    assert out["n"] == NVAR and out["m"] == MCLAUSE and out["L"] == LITERAL_MASS
    assert out["width_histogram"] == {"5": MCLAUSE}
    assert pos == [TARGET_POS] * NVAR
    assert neg == [TARGET_NEG] * NVAR
    assert degree == [TARGET_DEGREE] * NVAR
    return out


def truth(cnf: base.CNF) -> dict[str, Any]:
    models = []
    for bits in itertools.product((0, 1), repeat=NVAR):
        assignment = {i + 1: bits[i] for i in range(NVAR)}
        if base.verify_total_assignment(cnf, assignment):
            models.append("".join("1" if b else "0" for b in bits))
    return {
        "assignments_checked": 1 << NVAR,
        "satisfying_count": len(models),
        "UNSAT": not models,
        "models_digest": digest(models),
    }


@functools.lru_cache(maxsize=None)
def transition(cnf: base.CNF, pivot: int, cap: int):
    """Compute and exact-verify a unique transition once, then cache its receipt.

    This does not weaken verification: the first request for a concrete
    (canonical_state, pivot, cap) is verified by the canonical verifier. Later
    routes reuse the already verified transition instead of rerunning the same
    verifier on identical bytes.
    """
    out, st = base.eliminate_var_capped(cnf, pivot, cap)
    if out is not None:
        assert base.verify_elimination_transition(cnf, pivot, out, cap)
    return out, st


def replay(root: base.CNF, order: tuple[int, ...], cap: int) -> dict[str, Any]:
    state = root
    peak = base.state_units(root)
    raw_sum = 0
    pair_sum = 0
    checks = 0
    terminal = None
    overflow = False
    for step, p in enumerate(order, 1):
        if state == ((),):
            terminal = terminal or (step - 1)
            break
        if p not in set(base.vars_of(state)):
            continue
        checks += 1
        out, st = transition(state, p, cap)
        raw = int(st["raw_units"])
        pairs = int(st.get("pairs", 0))
        peak = max(peak, raw)
        raw_sum += raw
        pair_sum += pairs
        if out is None:
            overflow = True
            break
        state = out
        if state == ((),) and terminal is None:
            terminal = step
    return {
        "order": list(order),
        "overflow": overflow,
        "terminal_unsat": state == ((),),
        "terminal_step": terminal,
        "exact_checks": checks,
        "peak_raw": peak,
        "sum_raw": raw_sum,
        "pair_work": pair_sum,
    }


def rank(r: dict[str, Any]):
    return (int(r["overflow"]), r["peak_raw"], r["sum_raw"], r["pair_work"], r["terminal_step"] or 99, tuple(r["order"]))


def analyze_formula(seed: int, cnf: base.CNF, split: str) -> dict[str, Any]:
    cache_before = transition.cache_info()
    unbounded = [replay(cnf, o, UNBOUNDED_CAP) for o in itertools.permutations(PIVOTS)]
    assert len(unbounded) == ORDERS
    assert all(not r["overflow"] for r in unbounded)
    assert all(r["terminal_unsat"] for r in unbounded)
    champion_u = min(unbounded, key=rank)
    min_peak = min(r["peak_raw"] for r in unbounded)
    max_peak = max(r["peak_raw"] for r in unbounded)
    stress_cap = min_peak

    stressed = [replay(cnf, o, stress_cap) for o in itertools.permutations(PIVOTS)]
    safe = [r for r in stressed if not r["overflow"]]
    over = [r for r in stressed if r["overflow"]]
    assert safe, "stress cap must retain at least one exact route"
    assert all(r["terminal_unsat"] for r in safe)
    champion_s = min(safe, key=rank)

    first_pivot = {}
    for p in PIVOTS:
        one = replay(cnf, (p,), UNBOUNDED_CAP)
        first_pivot[str(p)] = {
            "raw_units": one["peak_raw"],
            "pair_work": one["pair_work"],
        }

    exhaustive_checks = sum(r["exact_checks"] for r in stressed)
    exhaustive_pair_work = sum(r["pair_work"] for r in stressed)
    cache_after = transition.cache_info()
    cache_delta = {
        "hits": cache_after.hits - cache_before.hits,
        "misses_exact_verified": cache_after.misses - cache_before.misses,
        "currsize": cache_after.currsize,
    }
    return {
        "seed": seed,
        "split": split,
        "stats": stats(cnf),
        "truth": truth(cnf),
        "stress": {
            "cap": stress_cap,
            "min_unbounded_route_peak": min_peak,
            "max_unbounded_route_peak": max_peak,
            "orders": ORDERS,
            "safe_orders": len(safe),
            "overflow_orders": len(over),
            "exhaustive_exact_checks": exhaustive_checks,
            "exhaustive_pair_work": exhaustive_pair_work,
            "oracle_champion": champion_s,
            "unbounded_champion": champion_u,
            "first_pivot": first_pivot,
            "transition_cache": cache_delta,
        },
    }


def build_corpus(count: int, train_count: int, max_seed: int) -> dict[str, Any]:
    selected: list[tuple[int, base.CNF]] = []
    fingerprints = set()
    scanned = 0
    for seed in range(max_seed):
        scanned += 1
        cnf = construct(seed)
        t = truth(cnf)
        if not t["UNSAT"]:
            continue
        fp = base.fingerprint(cnf)
        if fp in fingerprints:
            continue
        fingerprints.add(fp)
        selected.append((seed, cnf))
        if len(selected) >= count:
            break
    if len(selected) < count:
        raise RuntimeError(f"only {len(selected)} UNSAT fingerprints found in {max_seed} seeds")

    formulas = []
    for i, (seed, cnf) in enumerate(selected):
        split = "TRAIN" if i < train_count else "HOLDOUT"
        formulas.append(analyze_formula(seed, cnf, split))

    assert len({f["stats"]["fingerprint"] for f in formulas}) == count
    return {
        "schema": SCHEMA,
        "status": "EXACT_CYCLE0_CORPUS_READY__NO_LEARNING_GAIN_CLAIM",
        "P_VS_NP": P_VS_NP,
        "construction": {
            "n": NVAR,
            "width": WIDTH,
            "clauses": MCLAUSE,
            "literal_mass": LITERAL_MASS,
            "polarity_each_variable": "50:50",
            "complement_sign_pairs": PAIR_COUNT,
            "omitted_pair_multiplicity": "3 everywhere +1 on one deterministic 7-cycle",
        },
        "selection": {
            "requested_formulas": count,
            "train_formulas": train_count,
            "holdout_formulas": count - train_count,
            "seeds_scanned": scanned,
            "selection_rule": "first distinct exact-UNSAT fingerprints in deterministic seed order",
        },
        "verification_cache_policy": {
            "rule": "Each unique (canonical_state,pivot,cap) transition is exact-verified once and then reused by identical route prefixes.",
            "proof_semantics_changed": False,
        },
        "formulas": formulas,
        "firewall": {
            "formula_fingerprint_split": True,
            "holdout_not_used_for_training": True,
            "static_stress_cap_not_reachability_claim": True,
            "oracle_is_for_scoring_not_runtime_authority": True,
            "learning_gain_measured": False,
            "P_VS_NP": P_VS_NP,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=8)
    ap.add_argument("--train-count", type=int, default=5)
    ap.add_argument("--max-seed", type=int, default=500)
    ap.add_argument("--json-out", type=Path, required=True)
    args = ap.parse_args()
    if not (1 <= args.train_count < args.count):
        raise SystemExit("require 1 <= train-count < count")
    out = build_corpus(args.count, args.train_count, args.max_seed)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    compact = {
        "status": out["status"],
        "formulas": len(out["formulas"]),
        "train": out["selection"]["train_formulas"],
        "holdout": out["selection"]["holdout_formulas"],
        "seeds_scanned": out["selection"]["seeds_scanned"],
        "caps": [f["stress"]["cap"] for f in out["formulas"]],
        "safe_orders": [f["stress"]["safe_orders"] for f in out["formulas"]],
        "exact_verified_transition_misses": [f["stress"]["transition_cache"]["misses_exact_verified"] for f in out["formulas"]],
        "P_VS_NP": P_VS_NP,
    }
    print(json.dumps(compact, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
