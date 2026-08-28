#!/usr/bin/env python3
"""JANUS adaptive XOR race-track shakedown.

Builds an exact family of balanced UNSAT 2-CNFs labelled d:d.
For d>=2, the variable graph is d-regular. Every graph edge is one XOR equation
x_u xor x_v = b, encoded as two width-2 CNF clauses; therefore every incident
edge contributes exactly one positive and one negative occurrence to each
endpoint, giving p=q=d for every variable.

We first build a consistent XOR system from latent bits, then flip one non-bridge
edge in one connected component. The parity system becomes inconsistent, hence
the CNF is UNSAT. The canonical JANUS engine remains the authority for every
elimination transition. d=1 uses the exact unit contradiction (x)&(~x).

This file is only a track shakedown: it measures root-pivot landscape diversity
before the full PIPPI/JGPT/Slime/Spider/Keymaster adaptive ladder is allowed to
run. P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
from collections import Counter, deque
from pathlib import Path
from typing import Any

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base

P_VS_NP = "OPEN"
UNBOUNDED_CAP = 10**12
SCHEMA = "JANUS/MAD-LAB/ADAPTIVE-XOR-TRACK-PROBE/v1.0.0"


def edge(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def degree_map(n: int, edges: set[tuple[int, int]]) -> dict[int, int]:
    c = Counter()
    for a, b in edges:
        c[a] += 1; c[b] += 1
    return {v: c[v] for v in range(1, n + 1)}


def components(n: int, edges: set[tuple[int, int]]) -> list[list[int]]:
    adj = {v: set() for v in range(1, n + 1)}
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    seen = set(); out = []
    for s in range(1, n + 1):
        if s in seen: continue
        q = deque([s]); seen.add(s); comp = []
        while q:
            u = q.popleft(); comp.append(u)
            for w in sorted(adj[u]):
                if w not in seen:
                    seen.add(w); q.append(w)
        out.append(sorted(comp))
    return out


def connected_after_removal(vertices: list[int], edges: set[tuple[int, int]], removed: tuple[int, int]) -> bool:
    vv = set(vertices)
    if len(vv) <= 1: return True
    adj = {v: set() for v in vv}
    for a, b in edges:
        if (a, b) == removed or a not in vv or b not in vv: continue
        adj[a].add(b); adj[b].add(a)
    start = min(vv); seen = {start}; q = deque([start])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if w not in seen:
                seen.add(w); q.append(w)
    return seen == vv


def base_missing_4_regular(n: int) -> set[tuple[int, int]]:
    assert n >= 7
    e = set()
    for u0 in range(n):
        for delta in (1, 2):
            v0 = (u0 + delta) % n
            e.add(edge(u0 + 1, v0 + 1))
    assert all(x == 4 for x in degree_map(n, e).values())
    return e


def switched_missing_graph(n: int, seed: int) -> set[tuple[int, int]]:
    """Degree-preserving 2-switches on a 4-regular missing-edge graph."""
    rng = random.Random(0xA11CE ^ seed ^ (n << 16))
    e = base_missing_4_regular(n)
    attempts = 8 * n
    done = 0
    for _ in range(attempts * 8):
        if done >= attempts: break
        a_b, c_d = rng.sample(sorted(e), 2)
        a, b = a_b; c, d = c_d
        if len({a, b, c, d}) < 4: continue
        if rng.random() < 0.5:
            x, y = edge(a, c), edge(b, d)
        else:
            x, y = edge(a, d), edge(b, c)
        if x == y or x in e or y in e: continue
        e.remove(a_b); e.remove(c_d); e.add(x); e.add(y); done += 1
    assert all(x == 4 for x in degree_map(n, e).values())
    return e


def regular_formula_graph(d: int, seed: int) -> tuple[int, set[tuple[int, int]]]:
    assert d >= 2
    # n=d+5 means complementing a 4-regular graph gives degree d exactly.
    n = d + 5
    all_edges = {edge(a, b) for a, b in itertools.combinations(range(1, n + 1), 2)}
    missing = switched_missing_graph(n, seed)
    g = all_edges - missing
    deg = degree_map(n, g)
    assert deg == {v: d for v in range(1, n + 1)}
    return n, g


def xor_clauses(u: int, v: int, rhs: int) -> tuple[base.Clause, base.Clause]:
    # rhs=0 => equality; rhs=1 => inequality.
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
        if s in val: continue
        val[s] = 0; q = deque([s])
        while q:
            u = q.popleft()
            for v, bit in adj[u]:
                want = val[u] ^ bit
                if v in val:
                    if val[v] != want: return True
                else:
                    val[v] = want; q.append(v)
    return False


def construct(d: int, seed: int) -> tuple[base.CNF, dict[str, Any]]:
    if d == 1:
        var = 10_000 + seed
        cnf = base.canon_cnf(((var,), (-var,)))
        return cnf, {"n": 1, "graph_edges": 0, "flipped_edge": None, "xor_unsat": True}

    n, g = regular_formula_graph(d, seed)
    rng = random.Random(0x515151 ^ seed ^ (d << 20))
    latent = {v: rng.randrange(2) for v in range(1, n + 1)}
    rhs = {e: latent[e[0]] ^ latent[e[1]] for e in g}

    # Pick an edge lying on a cycle inside one component. Flipping it makes the
    # component inconsistent while preserving the exact d:d occurrence counts.
    comps = components(n, g)
    flip = None
    for comp in sorted(comps, key=lambda c: (-len(c), c)):
        local_edges = {e for e in g if e[0] in set(comp) and e[1] in set(comp)}
        for e in sorted(local_edges):
            if connected_after_removal(comp, local_edges, e):
                flip = e; break
        if flip is not None: break
    if flip is None:
        raise AssertionError("no non-bridge edge available for XOR contradiction")
    rhs[flip] ^= 1
    assert parity_unsat(g, rhs)

    clauses = []
    for u, v in sorted(g):
        a, b = xor_clauses(u, v, rhs[(u, v)])
        assert a is not None and b is not None
        clauses.extend((a, b))
    cnf = base.canon_cnf(clauses)
    assert len(cnf) == 2 * len(g)
    return cnf, {"n": n, "graph_edges": len(g), "components": [len(x) for x in comps], "flipped_edge": list(flip), "xor_unsat": True}


def exact_stats(cnf: base.CNF, d: int) -> dict[str, Any]:
    vs = base.vars_of(cnf)
    pos = [sum(v in c for c in cnf) for v in vs]
    neg = [sum(-v in c for c in cnf) for v in vs]
    if d == 1:
        assert pos == [1] and neg == [1]
    else:
        assert pos == [d] * len(vs), (d, pos[:10])
        assert neg == [d] * len(vs), (d, neg[:10])
        assert all(len(c) == 2 for c in cnf)
    sat2 = base.solve_2sat_exact(cnf)
    assert sat2 is not None and sat2[0] is False
    return {
        "n": len(vs), "m": len(cnf), "L": sum(len(c) for c in cnf),
        "state_units": base.state_units(cnf), "positive": pos, "negative": neg,
        "fingerprint": base.fingerprint(cnf), "exact_2sat_unsat": True,
    }


def root_landscape(cnf: base.CNF) -> dict[str, Any]:
    root_units = base.state_units(cnf)
    rows = []
    for p in base.vars_of(cnf):
        out, st = base.eliminate_var_capped(cnf, p, UNBOUNDED_CAP)
        assert out is not None
        assert base.verify_elimination_transition(cnf, p, out, UNBOUNDED_CAP)
        rows.append({
            "pivot": p,
            "raw_units": int(st["raw_units"]),
            "pair_work": int(st.get("pairs", 0)),
            "after_units": base.state_units(out),
            "tautologies": int(st.get("tautologies", 0)),
        })
    raws = [r["raw_units"] for r in rows]
    pairs = [r["pair_work"] for r in rows]
    afters = [r["after_units"] for r in rows]
    q = max(0, min(len(rows) - 1, int(0.30 * (len(rows) - 1))))
    cap = max(root_units, sorted(raws)[q])
    safe = sum(r["raw_units"] <= cap for r in rows)
    return {
        "root_units": root_units,
        "raw_min": min(raws), "raw_max": max(raws), "raw_span": max(raws)-min(raws),
        "pair_min": min(pairs), "pair_max": max(pairs), "pair_span": max(pairs)-min(pairs),
        "after_min": min(afters), "after_max": max(afters), "after_span": max(afters)-min(afters),
        "distinct_raw": len(set(raws)), "distinct_after": len(set(afters)),
        "local_stress_cap_q30": cap, "safe_pivots": safe, "pivots": len(rows),
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-d", type=int, default=12)
    ap.add_argument("--seeds-per-level", type=int, default=4)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    levels = []
    all_fp = set()
    for d in range(1, args.max_d + 1):
        formulas = []
        for j in range(args.seeds_per_level):
            seed = d * 100_003 + j * 997 + 17
            cnf, meta = construct(d, seed)
            st = exact_stats(cnf, d)
            if st["fingerprint"] in all_fp:
                raise AssertionError("duplicate fingerprint in track probe")
            all_fp.add(st["fingerprint"])
            land = root_landscape(cnf)
            formulas.append({"seed": seed, "meta": meta, "stats": st, "landscape": land})
        levels.append({
            "difficulty": f"{d}:{d}", "d": d, "formulas": formulas,
            "formulas_with_root_raw_diversity": sum(f["landscape"]["distinct_raw"] > 1 for f in formulas),
            "mean_raw_span": sum(f["landscape"]["raw_span"] for f in formulas) / len(formulas),
            "mean_safe_fraction_q30": sum(f["landscape"]["safe_pivots"] / f["landscape"]["pivots"] for f in formulas) / len(formulas),
        })
        print(json.dumps({
            "d": d,
            "n": [f["stats"]["n"] for f in formulas],
            "raw_distinct": [f["landscape"]["distinct_raw"] for f in formulas],
            "raw_span": [f["landscape"]["raw_span"] for f in formulas],
            "safe": [f["landscape"]["safe_pivots"] for f in formulas],
        }, sort_keys=True))
    out = {
        "schema": SCHEMA,
        "status": "TRACK_SHAKEDOWN_COMPLETE__NO_LEARNING_GAIN_CLAIM",
        "P_VS_NP": P_VS_NP,
        "levels": levels,
        "firewall": {
            "d_d_counts_exactly_verified": True,
            "2SAT_unsat_exactly_verified": True,
            "every_elimination_transition_exactly_verified": True,
            "local_stress_caps_are_scoring_parameters_not_reachability_claims": True,
            "learning_gain_measured": False,
            "P_VS_NP": P_VS_NP,
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
