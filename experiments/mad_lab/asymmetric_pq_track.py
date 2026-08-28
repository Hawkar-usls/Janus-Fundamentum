#!/usr/bin/env python3
"""Exact asymmetric p:q UNSAT 2-CNF track for JANUS gauntlet.

For p,q >= 2, choose an even n with n-1 >= max(p,q). A 1-factorization of K_n
is partitioned into two edge-disjoint regular graphs:
  * min(p,q) matchings form the XOR parity core. Every XOR edge contributes
    exactly +1 and -1 occurrence to both endpoints.
  * abs(p-q) additional matchings receive one sign-biased clause per edge,
    adding only the missing sign.

The XOR core is first made consistent from latent bits, then one cycle edge is
flipped, giving an exact UNSAT parity contradiction without changing p:q.
All clauses are canonical and edge-disjoint between gadgets, so occurrence
counts are exact. The exact 2-SAT solver independently verifies UNSAT.

This is a benchmark generator, not a theorem about SAT complexity. P_VS_NP=OPEN.
"""
from __future__ import annotations

import argparse
import json
import random
from collections import Counter, deque
from pathlib import Path
from typing import Any

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base

P_VS_NP = "OPEN"
SCHEMA = "JANUS/MAD-LAB/ASYMMETRIC-PQ-TRACK/v1.0.0"


def edge(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def one_factorization(n: int) -> list[list[tuple[int, int]]]:
    """Round-robin 1-factorization of K_n for even n."""
    if n < 2 or n % 2:
        raise ValueError("n must be positive even")
    arr = list(range(1, n + 1))
    seen: set[tuple[int, int]] = set()
    rounds: list[list[tuple[int, int]]] = []
    for _ in range(n - 1):
        matching = []
        for i in range(n // 2):
            e = edge(arr[i], arr[-1 - i])
            if e in seen:
                raise AssertionError("1-factorization duplicate edge")
            seen.add(e)
            matching.append(e)
        rounds.append(matching)
        arr = [arr[0], arr[-1], *arr[1:-1]]
    if len(seen) != n * (n - 1) // 2:
        raise AssertionError("1-factorization incomplete")
    return rounds


def minimum_even_n(p: int, q: int) -> int:
    if p < 1 or q < 1:
        raise ValueError("p,q must be >=1")
    n = max(p, q) + 1
    if n % 2:
        n += 1
    return max(4, n)


def graph_from_matchings(rounds: list[list[tuple[int, int]]], start: int, count: int) -> set[tuple[int, int]]:
    out: set[tuple[int, int]] = set()
    for r in rounds[start:start + count]:
        out.update(r)
    return out


def components(vertices: set[int], edges: set[tuple[int, int]]) -> list[list[int]]:
    adj = {v: set() for v in vertices}
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    seen = set(); out = []
    for s in sorted(vertices):
        if s in seen:
            continue
        q = deque([s]); seen.add(s); comp = []
        while q:
            u = q.popleft(); comp.append(u)
            for w in sorted(adj[u]):
                if w not in seen:
                    seen.add(w); q.append(w)
        out.append(comp)
    return out


def connected_after_removal(comp: list[int], edges: set[tuple[int, int]], removed: tuple[int, int]) -> bool:
    vv = set(comp)
    if len(vv) <= 1:
        return True
    adj = {v: set() for v in vv}
    for a, b in edges:
        if (a, b) == removed or a not in vv or b not in vv:
            continue
        adj[a].add(b); adj[b].add(a)
    start = min(vv); seen = {start}; q = deque([start])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if w not in seen:
                seen.add(w); q.append(w)
    return seen == vv


def xor_clauses(u: int, v: int, rhs: int) -> tuple[base.Clause, base.Clause]:
    if rhs == 0:
        return base.canon_clause((u, -v)), base.canon_clause((-u, v))
    return base.canon_clause((u, v)), base.canon_clause((-u, -v))


def parity_unsat(edges: set[tuple[int, int]], rhs: dict[tuple[int, int], int]) -> bool:
    adj: dict[int, list[tuple[int, int]]] = {}
    for a, b in edges:
        adj.setdefault(a, []).append((b, rhs[(a, b)]))
        adj.setdefault(b, []).append((a, rhs[(a, b)]))
    val: dict[int, int] = {}
    for s in sorted(adj):
        if s in val:
            continue
        val[s] = 0; q = deque([s])
        while q:
            u = q.popleft()
            for v, bit in adj[u]:
                want = val[u] ^ bit
                if v in val:
                    if val[v] != want:
                        return True
                else:
                    val[v] = want; q.append(v)
    return False


def construct(p: int, q: int, seed: int, n: int | None = None) -> tuple[base.CNF, dict[str, Any]]:
    if p == q == 1:
        var = 20_000_000 + seed
        cnf = base.canon_cnf(((var,), (-var,)))
        return cnf, {"p": 1, "q": 1, "n": 1, "mode": "UNIT_FORMATION", "xor_unsat": True}
    if min(p, q) < 2:
        raise ValueError("general asymmetric track requires min(p,q)>=2; 1:1 is the only formation special case")
    if n is None:
        n = minimum_even_n(p, q)
    if n % 2 or n - 1 < max(p, q):
        raise ValueError(f"chosen n={n} cannot support edge-disjoint generator for p:q={p}:{q}")

    rounds = one_factorization(n)
    d = min(p, q); extra = abs(p - q)
    core = graph_from_matchings(rounds, 0, d)
    biased = graph_from_matchings(rounds, d, extra)
    if core & biased:
        raise AssertionError("core/biased graphs are not edge-disjoint")

    rng = random.Random(0xA57A5EED ^ seed ^ (p << 18) ^ (q << 5) ^ n)
    latent = {v: rng.randrange(2) for v in range(1, n + 1)}
    rhs = {e: latent[e[0]] ^ latent[e[1]] for e in core}

    flip = None
    comps = components(set(range(1, n + 1)), core)
    for comp in sorted(comps, key=lambda c: (-len(c), c)):
        local = {e for e in core if e[0] in set(comp) and e[1] in set(comp)}
        for e in sorted(local):
            if connected_after_removal(comp, local, e):
                flip = e; break
        if flip is not None:
            break
    if flip is None:
        raise AssertionError("no cycle edge in XOR core")
    rhs[flip] ^= 1
    if not parity_unsat(core, rhs):
        raise AssertionError("failed to create parity contradiction")

    clauses: list[base.Clause] = []
    for u, v in sorted(core):
        a, b = xor_clauses(u, v, rhs[(u, v)])
        if a is None or b is None:
            raise AssertionError("invalid XOR clause")
        clauses.extend((a, b))
    sign = 1 if p > q else -1
    for u, v in sorted(biased):
        c = base.canon_clause((sign * u, sign * v))
        if c is None:
            raise AssertionError("invalid biased clause")
        clauses.append(c)
    cnf = base.canon_cnf(clauses)
    if len(cnf) != len(clauses):
        raise AssertionError("unexpected canonical collision")

    vs = base.vars_of(cnf)
    pos = [sum(v in c for c in cnf) for v in vs]
    neg = [sum(-v in c for c in cnf) for v in vs]
    if pos != [p] * n or neg != [q] * n:
        raise AssertionError((p, q, pos[:8], neg[:8]))
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
    }


def fixed_width2_feasibility(p: int, q: int, n: int, allow_units: bool = False) -> dict[str, Any]:
    """Necessary signed-occurrence capacity certificate for canonical width-2 CNF.

    For a fixed variable x_i and every other variable x_j, there are exactly two
    non-tautological width-2 clauses containing +x_i and two containing -x_i.
    Thus each sign has capacity 2(n-1); a unit clause would add at most one more.
    """
    cap = 2 * (n - 1) + (1 if allow_units else 0)
    possible_by_capacity = p <= cap and q <= cap
    return {
        "schema": "JANUS/MAD-LAB/FIXED-WIDTH2-FEASIBILITY-CERT/v1.0.0",
        "p": p, "q": q, "n": n, "allow_units": allow_units,
        "per_sign_occurrence_capacity": cap,
        "possible_by_capacity": possible_by_capacity,
        "status": "CAPACITY_NOT_REFUTED" if possible_by_capacity else "TRACK_CONSTRUCTION_IMPOSSIBLE_BY_SIGNED_OCCURRENCE_CAPACITY",
        "proof": f"canonical non-tautological width-2 gives at most 2*(n-1){'+1 unit' if allow_units else ''} occurrences per literal sign",
        "P_VS_NP": P_VS_NP,
    }


def self_test() -> dict[str, Any]:
    rows = []
    for p, q in [(1, 1), (11, 11), (13, 16), (16, 13)]:
        cnf, meta = construct(p, q, 12345 + p * 101 + q)
        rows.append({"p": p, "q": q, "n": meta["n"], "m": len(cnf), "fingerprint": base.fingerprint(cnf)})
    imp = fixed_width2_feasibility(251, 251, 126, allow_units=False)
    if imp["possible_by_capacity"]:
        raise AssertionError("251:251 should violate fixed n=126 width-2 no-unit sign capacity")
    return {"schema": SCHEMA + "/self-test", "status": "PASS", "cases": rows, "impossibility_probe": imp, "P_VS_NP": P_VS_NP}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--p", type=int)
    ap.add_argument("--q", type=int)
    ap.add_argument("--seed", type=int, default=20260828)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    if args.self_test:
        obj = self_test()
    else:
        if args.p is None or args.q is None:
            ap.error("--p and --q required unless --self-test")
        cnf, meta = construct(args.p, args.q, args.seed)
        obj = {"schema": SCHEMA, "status": "PASS", "meta": meta, "state_units": base.state_units(cnf), "P_VS_NP": P_VS_NP}
    text = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True); args.out.write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
