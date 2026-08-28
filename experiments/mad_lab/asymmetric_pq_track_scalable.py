#!/usr/bin/env python3
"""Scalable exact construction for the frozen asymmetric p:q track.

The general `canon_cnf` performs arbitrary-width subsumption. Every non-formation
clause emitted by `asymmetric_pq_track` is already a canonical width-2 clause.
For a uniform width-2 family, A subseteq B implies A==B, so exact canonical CNF
is simply deduplication followed by the same canonical sort. This module changes
no formula semantics; a self-test requires bit-identical CNF/fingerprint equality
with the general canonicalizer on representative smaller p:q instances.

P_VS_NP=OPEN.
"""
from __future__ import annotations

import json
import random
from typing import Any

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.mad_lab import asymmetric_pq_track as slow

P_VS_NP = "OPEN"
SCHEMA = "JANUS/MAD-LAB/ASYMMETRIC-PQ-TRACK-SCALABLE-CANON/v1.0.1"


def canon_uniform_width2_exact(clauses: list[base.Clause]) -> base.CNF:
    if any(c is None or len(c) != 2 for c in clauses):
        raise ValueError("uniform width-2 exact canonicalizer requires canonical width-2 clauses")
    # Every input clause already passed base.canon_clause in the frozen generator.
    # Same-length proper subsumption is impossible; equality is handled by set.
    return tuple(sorted(set(clauses), key=lambda c: (len(c), c)))


def construct_fast(p: int, q: int, seed: int, n: int | None = None) -> tuple[base.CNF, dict[str, Any]]:
    if p == q == 1:
        # Keep the formation special-case local. This avoids alias recursion when
        # a harness intentionally monkeypatches slow.construct = construct_fast.
        var = 20_000_000 + seed
        cnf = base.canon_cnf(((var,), (-var,)))
        return cnf, {"p": 1, "q": 1, "n": 1, "mode": "UNIT_FORMATION", "xor_unsat": True,
                     "fingerprint": base.fingerprint(cnf), "exact_2sat_unsat": True,
                     "canonicalizer": "GENERIC_UNIT_FORMATION"}
    if min(p, q) < 2:
        raise ValueError("general asymmetric track requires min(p,q)>=2; 1:1 is the only formation special case")
    if n is None:
        n = slow.minimum_even_n(p, q)
    if n % 2 or n - 1 < max(p, q):
        raise ValueError(f"chosen n={n} cannot support edge-disjoint generator for p:q={p}:{q}")

    rounds = slow.one_factorization(n)
    d = min(p, q); extra = abs(p - q)
    core = slow.graph_from_matchings(rounds, 0, d)
    biased = slow.graph_from_matchings(rounds, d, extra)
    if core & biased:
        raise AssertionError("core/biased graphs are not edge-disjoint")

    rng = random.Random(0xA57A5EED ^ seed ^ (p << 18) ^ (q << 5) ^ n)
    latent = {v: rng.randrange(2) for v in range(1, n + 1)}
    rhs = {e: latent[e[0]] ^ latent[e[1]] for e in core}

    flip = None
    comps = slow.components(set(range(1, n + 1)), core)
    for comp in sorted(comps, key=lambda c: (-len(c), c)):
        cset = set(comp)
        local = {e for e in core if e[0] in cset and e[1] in cset}
        for e in sorted(local):
            if slow.connected_after_removal(comp, local, e):
                flip = e; break
        if flip is not None:
            break
    if flip is None:
        raise AssertionError("no cycle edge in XOR core")
    rhs[flip] ^= 1
    if not slow.parity_unsat(core, rhs):
        raise AssertionError("failed to create parity contradiction")

    clauses: list[base.Clause] = []
    for u, v in sorted(core):
        a, b = slow.xor_clauses(u, v, rhs[(u, v)])
        if a is None or b is None:
            raise AssertionError("invalid XOR clause")
        clauses.extend((a, b))
    sign = 1 if p > q else -1
    for u, v in sorted(biased):
        c = base.canon_clause((sign * u, sign * v))
        if c is None:
            raise AssertionError("invalid biased clause")
        clauses.append(c)

    cnf = canon_uniform_width2_exact(clauses)
    if len(cnf) != len(clauses):
        raise AssertionError("unexpected canonical collision")

    vs = base.vars_of(cnf)
    # Count occurrences linearly instead of repeatedly scanning the whole CNF.
    pos = {v: 0 for v in vs}; neg = {v: 0 for v in vs}
    for c in cnf:
        for lit in c:
            (pos if lit > 0 else neg)[abs(lit)] += 1
    if any(pos[v] != p or neg[v] != q for v in vs) or len(vs) != n:
        raise AssertionError((p, q, n, list(pos.items())[:8], list(neg.items())[:8]))
    sat2 = base.solve_2sat_exact(cnf)
    if sat2 is None or sat2[0] is not False:
        raise AssertionError("independent exact 2-SAT verifier did not confirm UNSAT")
    return cnf, {
        "p": p, "q": q, "n": n, "m": len(cnf), "L": sum(map(len, cnf)),
        "core_degree": d, "biased_degree": extra,
        "biased_sign": "POSITIVE" if p > q else ("NEGATIVE" if q > p else "NONE"),
        "core_edges": len(core), "biased_edges": len(biased), "flipped_edge": list(flip),
        "components": [len(c) for c in comps], "xor_unsat": True,
        "fingerprint": base.fingerprint(cnf), "exact_2sat_unsat": True,
        "canonicalizer": "UNIFORM_WIDTH2_EXACT_DEDUP_SORT",
    }


def self_test() -> dict[str, Any]:
    rows = []
    for p, q, seed in [(1, 1, 8100), (3, 3, 8101), (11, 11, 8102), (13, 16, 8103), (16, 13, 8104), (31, 31, 8105)]:
        a, am = slow.construct(p, q, seed)
        b, bm = construct_fast(p, q, seed)
        if a != b or base.fingerprint(a) != base.fingerprint(b):
            raise AssertionError((p, q, base.fingerprint(a), base.fingerprint(b)))
        rows.append({"p": p, "q": q, "n": bm["n"], "m": len(b), "fingerprint": base.fingerprint(b), "bit_identical": True})
    return {
        "schema": SCHEMA + "/self-test", "status": "PASS", "cases": rows,
        "formula_semantics_changed": False, "canonical_cnf_bit_identical": True,
        "formation_special_case_local": True,
        "P_VS_NP": P_VS_NP,
    }


if __name__ == "__main__":
    print(json.dumps(self_test(), indent=2, sort_keys=True))
