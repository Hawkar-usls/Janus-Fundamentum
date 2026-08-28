#!/usr/bin/env python3
"""Isomorphic random relabelling for the exact asymmetric p:q track.

The v2.3 diagnostic exposed a benchmark-control artifact: the frozen generator
chooses a lexicographically early parity-flip edge, while STATIC baseline tries
numeric pivot IDs in ascending order. This module leaves the unlabeled CNF and
all p:q/UNSAT structure unchanged, but applies a deterministic seed-derived
uniform permutation of variable labels. Therefore numeric order is decorrelated
from the distinguished graph roles without giving any adviser a new feature.

The relabelled CNF is exactly isomorphic to the base CNF. P_VS_NP=OPEN.
"""
from __future__ import annotations

import hashlib
import json
import random
from typing import Any

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.mad_lab import asymmetric_pq_track_scalable as scalable

P_VS_NP = "OPEN"
SCHEMA = "JANUS/MAD-LAB/ASYMMETRIC-PQ-TRACK-RELABELLED/v1.0.0"


def _perm_hash(perm: dict[int, int]) -> str:
    payload = json.dumps(sorted(perm.items()), separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def construct_relabelled(p: int, q: int, seed: int, n: int | None = None) -> tuple[base.CNF, dict[str, Any]]:
    cnf, meta = scalable.construct_fast(p, q, seed, n)
    if p == q == 1:
        # One variable has no nontrivial relabelling; preserve formation exactly.
        return cnf, {**meta, "relabelled": False, "relabel_reason": "SINGLE_VARIABLE_FORMATION"}

    vs = list(base.vars_of(cnf))
    shuffled = list(vs)
    rng = random.Random(0xB055C0DE ^ seed ^ (p << 21) ^ (q << 7) ^ len(vs))
    rng.shuffle(shuffled)
    perm = dict(zip(vs, shuffled))
    mapped: list[base.Clause] = []
    for c in cnf:
        cc = base.canon_clause((perm[abs(l)] if l > 0 else -perm[abs(l)] for l in c))
        if cc is None or len(cc) != len(c):
            raise AssertionError("relabel changed clause validity")
        mapped.append(cc)
    out = scalable.canon_uniform_width2_exact(mapped)
    if len(out) != len(cnf):
        raise AssertionError("isomorphic relabel changed clause count")

    ovs = base.vars_of(out)
    pos = {v: 0 for v in ovs}; neg = {v: 0 for v in ovs}
    for c in out:
        for lit in c:
            (pos if lit > 0 else neg)[abs(lit)] += 1
    if any(pos[v] != p or neg[v] != q for v in ovs):
        raise AssertionError("p:q occurrence invariant broken by relabel")
    sat2 = base.solve_2sat_exact(out)
    if sat2 is None or sat2[0] is not False:
        raise AssertionError("relabelled CNF lost exact UNSAT verdict")

    return out, {
        **meta,
        "fingerprint_before_relabel": base.fingerprint(cnf),
        "fingerprint": base.fingerprint(out),
        "relabelled": True,
        "permutation_sha256": _perm_hash(perm),
        "isomorphic_structure_preserved": True,
        "numeric_baseline_role_correlation_intentionally_broken": True,
    }


def self_test() -> dict[str, Any]:
    rows = []
    for p, q, seed in [(3, 3, 10101), (11, 11, 10102), (13, 16, 10103), (31, 31, 10104)]:
        a, am = scalable.construct_fast(p, q, seed)
        b, bm = construct_relabelled(p, q, seed)
        if len(a) != len(b) or len(base.vars_of(a)) != len(base.vars_of(b)):
            raise AssertionError("isomorphism size mismatch")
        if base.fingerprint(a) == base.fingerprint(b):
            # A random permutation could mathematically be an automorphism, but these
            # frozen test seeds are chosen so the serialized CNF changes.
            raise AssertionError("test permutation did not change serialized fingerprint")
        sat_a = base.solve_2sat_exact(a); sat_b = base.solve_2sat_exact(b)
        if sat_a is None or sat_b is None or sat_a[0] is not False or sat_b[0] is not False:
            raise AssertionError("UNSAT invariance failed")
        rows.append({"p": p, "q": q, "n": len(base.vars_of(b)), "m": len(b), "before": base.fingerprint(a), "after": base.fingerprint(b), "perm": bm["permutation_sha256"]})
    return {
        "schema": SCHEMA + "/self-test", "status": "PASS", "cases": rows,
        "logical_isomorphism_only": True, "p_q_preserved": True, "exact_unsat_preserved": True,
        "numeric_pivot_id_added_as_feature": False, "P_VS_NP": P_VS_NP,
    }


if __name__ == "__main__":
    print(json.dumps(self_test(), indent=2, sort_keys=True))
