#!/usr/bin/env python3
"""ROOSTERS multi-epoch structural-lambda stability gate.

This executable is bound to the preregistration committed before the spectra:
research/C025_STRUCTURAL_LAMBDA_ROOSTERS_MULTI_EPOCH_PREREGISTRATION_2026-08-29.json

It runs seven genuinely different CNF construction geometries under one fixed
search/scoring/spectral pipeline.  The historical selector-product trace is a
nonvoting anchor.  This is a structural search-dynamics experiment, not a
physical wavelength measurement, theorem proof, or complexity-class result.
P_VS_NP remains OPEN.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from copy import deepcopy
from pathlib import Path
from typing import Callable, Iterable

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base

P_VS_NP = "OPEN"
PREREG_PATH = Path("research/C025_STRUCTURAL_LAMBDA_ROOSTERS_MULTI_EPOCH_PREREGISTRATION_2026-08-29.json")
OUT_PATH = Path("c025-structural-lambda-roosters-multi-epoch-result.json")

Clause = base.Clause
CNF = base.CNF


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def random_clause(rng: random.Random, variables: list[int], width: int) -> Clause:
    support = sorted(rng.sample(variables, width))
    return base.canon_clause([v if rng.getrandbits(1) else -v for v in support])  # type: ignore[return-value]


def random_unique_clauses(rng: random.Random, variables: list[int], count: int, width: int, predicate=None) -> list[Clause]:
    rows: set[Clause] = set()
    tries = 0
    while len(rows) < count:
        tries += 1
        if tries > 200000:
            raise RuntimeError("CLAUSE_GENERATION_EXHAUSTED")
        c = random_clause(rng, variables, width)
        if predicate is not None and not predicate(c):
            continue
        rows.add(c)
    return sorted(rows, key=lambda c: (len(c), c))


def raw_elimination_units(cnf: CNF, pivot: int) -> int:
    pos = [c for c in cnf if pivot in c]
    neg = [c for c in cnf if -pivot in c]
    raw: set[Clause] = {c for c in cnf if pivot not in c and -pivot not in c}
    for p in pos:
        for n in neg:
            r = base.resolve_on_var(p, n, pivot)
            if r is not None:
                raw.add(r)
    return 1 + len(raw) + sum(len(c) for c in raw)


def exact_delta(cnf: CNF, cap: int) -> tuple[int, list[dict]]:
    pivots = list(base.vars_of(cnf))
    if not pivots:
        raise ValueError("NO_LIVE_VARIABLES")
    rows = []
    for v in pivots:
        u = raw_elimination_units(cnf, v)
        rows.append({"pivot": int(v), "raw_units": int(u), "margin": int(u - cap)})
    return min(row["margin"] for row in rows), rows


def make_random_3cnf(spec: dict) -> dict:
    rng = random.Random(int(spec["seed"]))
    variables = list(range(1, int(spec["nvars"]) + 1))
    rows = random_unique_clauses(rng, variables, int(spec["budget"]), 3)
    return {"kind": spec["constructor"], "rows": rows, "variables": variables}


def mutate_random_3cnf(state: dict, rng: random.Random) -> dict:
    rows = list(state["rows"])
    current = set(rows)
    idx = rng.randrange(len(rows))
    for _ in range(2000):
        c = random_clause(rng, state["variables"], 3)
        if c not in current:
            rows[idx] = c
            cnf = base.canon_cnf(rows)
            if len(cnf) == len(rows):
                return {**state, "rows": list(cnf)}
    raise RuntimeError("RANDOM_3CNF_MUTATION_EXHAUSTED")


def make_balanced_4cnf(spec: dict) -> dict:
    rng = random.Random(int(spec["seed"]))
    n = int(spec["nvars"])
    m = int(spec["budget"])
    variables = list(range(1, n + 1))
    # Degree-balanced support schedule; signs alternate by occurrence, then rows are shuffled.
    occurrence = {v: 0 for v in variables}
    rows: set[Clause] = set()
    cursor = 0
    tries = 0
    while len(rows) < m:
        tries += 1
        if tries > 200000:
            raise RuntimeError("BALANCED_INIT_EXHAUSTED")
        support = sorted({1 + ((cursor + j * 3) % n) for j in range(4)})
        cursor += 1
        if len(support) < 4:
            support = sorted(rng.sample(variables, 4))
        lits = []
        for v in support:
            occurrence[v] += 1
            sign = 1 if occurrence[v] % 2 else -1
            lits.append(sign * v)
        c = base.canon_clause(lits)
        if c is not None:
            rows.add(c)
    return {"kind": spec["constructor"], "rows": sorted(rows, key=lambda c: (len(c), c)), "variables": variables}


def mutate_balanced_4cnf(state: dict, rng: random.Random) -> dict:
    rows = [list(c) for c in state["rows"]]
    for _ in range(4000):
        i, j = rng.sample(range(len(rows)), 2)
        a, b = rng.randrange(4), rng.randrange(4)
        la, lb = rows[i][a], rows[j][b]
        # Swap complete signed literals: global signed degree multiset is invariant.
        ni, nj = list(rows[i]), list(rows[j])
        ni[a], nj[b] = lb, la
        if len({abs(x) for x in ni}) != 4 or len({abs(x) for x in nj}) != 4:
            continue
        ci, cj = base.canon_clause(ni), base.canon_clause(nj)
        if ci is None or cj is None:
            continue
        candidate = list(state["rows"])
        candidate[i], candidate[j] = ci, cj
        cnf = base.canon_cnf(candidate)
        if len(cnf) == len(candidate) and all(len(c) == 4 for c in cnf):
            return {**state, "rows": list(cnf)}
    raise RuntimeError("BALANCED_4CNF_MUTATION_EXHAUSTED")


def make_planted_3sat(spec: dict) -> dict:
    rng = random.Random(int(spec["seed"]))
    variables = list(range(1, int(spec["nvars"]) + 1))
    plant = {v: rng.getrandbits(1) for v in variables}
    def sat(c: Clause) -> bool:
        return any(plant[abs(l)] == int(l > 0) for l in c)
    rows = random_unique_clauses(rng, variables, int(spec["budget"]), 3, sat)
    return {"kind": spec["constructor"], "rows": rows, "variables": variables, "plant": plant}


def mutate_planted_3sat(state: dict, rng: random.Random) -> dict:
    rows = list(state["rows"])
    current = set(rows)
    idx = rng.randrange(len(rows))
    plant = state["plant"]
    for _ in range(4000):
        c = random_clause(rng, state["variables"], 3)
        if c in current:
            continue
        if not any(plant[abs(l)] == int(l > 0) for l in c):
            continue
        rows[idx] = c
        cnf = base.canon_cnf(rows)
        if len(cnf) == len(rows):
            return {**state, "rows": list(cnf)}
    raise RuntimeError("PLANTED_MUTATION_EXHAUSTED")


def encode_xor3(equations: list[tuple[tuple[int, int, int], int]]) -> CNF:
    rows = []
    for support, rhs in equations:
        for mask in range(8):
            parity = mask.bit_count() & 1
            if parity == rhs:
                continue
            clause = []
            for j, v in enumerate(support):
                bit = (mask >> j) & 1
                clause.append(v if bit == 0 else -v)
            rows.append(clause)
    return base.canon_cnf(rows)


def make_xor3(spec: dict) -> dict:
    rng = random.Random(int(spec["seed"]))
    variables = list(range(1, int(spec["nvars"]) + 1))
    equations = []
    seen = set()
    while len(equations) < int(spec["budget"]):
        support = tuple(sorted(rng.sample(variables, 3)))
        rhs = rng.getrandbits(1)
        key = (support, rhs)
        if key not in seen:
            seen.add(key)
            equations.append(key)
    return {"kind": spec["constructor"], "equations": equations, "rows": list(encode_xor3(equations)), "variables": variables}


def mutate_xor3(state: dict, rng: random.Random) -> dict:
    equations = list(state["equations"])
    idx = rng.randrange(len(equations))
    existing = set(equations)
    for _ in range(2000):
        support = tuple(sorted(rng.sample(state["variables"], 3)))
        rhs = rng.getrandbits(1)
        eq = (support, rhs)
        if eq in existing:
            continue
        trial = list(equations)
        trial[idx] = eq
        cnf = encode_xor3(trial)
        if len(cnf) >= 4 * len(trial) - 4:
            return {**state, "equations": trial, "rows": list(cnf)}
    raise RuntimeError("XOR_MUTATION_EXHAUSTED")


def php_core(pigeons: int, holes: int) -> list[list[int]]:
    def var(p: int, h: int) -> int:
        return 1 + p * holes + h
    rows: list[list[int]] = []
    for p in range(pigeons):
        rows.append([var(p, h) for h in range(holes)])
        for h1 in range(holes):
            for h2 in range(h1 + 1, holes):
                rows.append([-var(p, h1), -var(p, h2)])
    for h in range(holes):
        for p1 in range(pigeons):
            for p2 in range(p1 + 1, pigeons):
                rows.append([-var(p1, h), -var(p2, h)])
    return rows


def make_php_noise(spec: dict) -> dict:
    rng = random.Random(int(spec["seed"]))
    p, h = int(spec["pigeons"]), int(spec["holes"])
    core_rows = php_core(p, h)
    start = p * h + 1
    noise_vars = list(range(start, start + 9))
    noise = random_unique_clauses(rng, noise_vars, int(spec["noise_clauses"]), 3)
    cnf = base.canon_cnf(core_rows + [list(c) for c in noise])
    return {"kind": spec["constructor"], "core_rows": core_rows, "noise": noise, "rows": list(cnf), "noise_vars": noise_vars}


def mutate_php_noise(state: dict, rng: random.Random) -> dict:
    noise = list(state["noise"])
    current = set(noise)
    idx = rng.randrange(len(noise))
    for _ in range(2000):
        c = random_clause(rng, state["noise_vars"], 3)
        if c in current:
            continue
        trial = list(noise); trial[idx] = c
        cnf = base.canon_cnf(state["core_rows"] + [list(x) for x in trial])
        # The immutable PHP core must remain exactly represented.
        if all(base.canon_clause(r) in cnf for r in state["core_rows"]):
            return {**state, "noise": trial, "rows": list(cnf)}
    raise RuntimeError("PHP_NOISE_MUTATION_EXHAUSTED")


def encode_graph3(vertices: int, edges: list[tuple[int, int]]) -> CNF:
    def var(v: int, c: int) -> int:
        return 1 + v * 3 + c
    rows = []
    for v in range(vertices):
        rows.append([var(v, c) for c in range(3)])
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                rows.append([-var(v, c1), -var(v, c2)])
    for u, v in edges:
        for c in range(3):
            rows.append([-var(u, c), -var(v, c)])
    return base.canon_cnf(rows)


def make_graph3(spec: dict) -> dict:
    rng = random.Random(int(spec["seed"]))
    n, m = int(spec["vertices"]), int(spec["edges"])
    universe = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = sorted(rng.sample(universe, m))
    return {"kind": spec["constructor"], "vertices": n, "edges": edges, "rows": list(encode_graph3(n, edges))}


def mutate_graph3(state: dict, rng: random.Random) -> dict:
    edges = set(state["edges"])
    universe = [(u, v) for u in range(state["vertices"]) for v in range(u + 1, state["vertices"])]
    remove = rng.choice(sorted(edges))
    available = [e for e in universe if e not in edges]
    add = rng.choice(available)
    edges.remove(remove); edges.add(add)
    edges2 = sorted(edges)
    return {**state, "edges": edges2, "rows": list(encode_graph3(state["vertices"], edges2))}


def contradictory_xor_core() -> list[list[int]]:
    equations = []
    for support in ((1,2,3), (4,5,6), (7,8,9)):
        equations.append((support, 0)); equations.append((support, 1))
    return [list(c) for c in encode_xor3(equations)]


def make_contradictory_noise(spec: dict) -> dict:
    rng = random.Random(int(spec["seed"]))
    n = int(spec["nvars"])
    variables = list(range(1, n + 1))
    core_rows = contradictory_xor_core()
    core_set = set(base.canon_cnf(core_rows))
    noise = random_unique_clauses(rng, variables, int(spec["noise_clauses"]), 3, lambda c: c not in core_set)
    cnf = base.canon_cnf(core_rows + [list(c) for c in noise])
    return {"kind": spec["constructor"], "core_rows": core_rows, "noise": noise, "variables": variables, "rows": list(cnf)}


def mutate_contradictory_noise(state: dict, rng: random.Random) -> dict:
    noise = list(state["noise"])
    current = set(noise)
    core_set = set(base.canon_cnf(state["core_rows"]))
    idx = rng.randrange(len(noise))
    for _ in range(3000):
        c = random_clause(rng, state["variables"], 3)
        if c in current or c in core_set:
            continue
        trial = list(noise); trial[idx] = c
        cnf = base.canon_cnf(state["core_rows"] + [list(x) for x in trial])
        if core_set.issubset(set(cnf)):
            return {**state, "noise": trial, "rows": list(cnf)}
    raise RuntimeError("CONTRADICTORY_NOISE_MUTATION_EXHAUSTED")


BUILDERS: dict[str, Callable[[dict], dict]] = {
    "RANDOM_3CNF": make_random_3cnf,
    "BALANCED_4CNF": make_balanced_4cnf,
    "PLANTED_3SAT": make_planted_3sat,
    "XOR3_SYSTEM": make_xor3,
    "PHP_CORE_PLUS_NOISE": make_php_noise,
    "GRAPH_3COLOR": make_graph3,
    "CONTRADICTORY_CORE_PLUS_NOISE": make_contradictory_noise,
}
MUTATORS: dict[str, Callable[[dict, random.Random], dict]] = {
    "RANDOM_3CNF": mutate_random_3cnf,
    "BALANCED_4CNF": mutate_balanced_4cnf,
    "PLANTED_3SAT": mutate_planted_3sat,
    "XOR3_SYSTEM": mutate_xor3,
    "PHP_CORE_PLUS_NOISE": mutate_php_noise,
    "GRAPH_3COLOR": mutate_graph3,
    "CONTRADICTORY_CORE_PLUS_NOISE": mutate_contradictory_noise,
}


def solve3(a: list[list[float]], b: list[float]) -> list[float]:
    m = [list(row) + [rhs] for row, rhs in zip(a, b)]
    for col in range(3):
        pivot = max(range(col, 3), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-15:
            raise ValueError("SINGULAR_TREND_FIT")
        m[col], m[pivot] = m[pivot], m[col]
        q = m[col][col]
        m[col] = [x / q for x in m[col]]
        for r in range(3):
            if r == col:
                continue
            q = m[r][col]
            m[r] = [m[r][j] - q * m[col][j] for j in range(4)]
    return [m[i][3] for i in range(3)]


def quadratic_detrend(values: list[float]) -> tuple[list[float], list[float]]:
    n = len(values)
    xs = [float(i) for i in range(n)]
    s0 = float(n); s1 = sum(xs); s2 = sum(x*x for x in xs)
    s3 = sum(x**3 for x in xs); s4 = sum(x**4 for x in xs)
    sy = sum(values); sxy = sum(x*y for x,y in zip(xs, values)); sx2y = sum(x*x*y for x,y in zip(xs, values))
    c0, c1, c2 = solve3([[s0,s1,s2],[s1,s2,s3],[s2,s3,s4]],[sy,sxy,sx2y])
    trend = [c0 + c1*x + c2*x*x for x in xs]
    return [y-t for y,t in zip(values, trend)], [c0,c1,c2]


def dft_power(values: list[float]) -> list[dict]:
    n = len(values)
    out = []
    for k in range(1, n//2 + 1):
        re = 0.0; im = 0.0
        for t, y in enumerate(values):
            ang = -2.0 * math.pi * k * t / n
            re += y * math.cos(ang); im += y * math.sin(ang)
        p = re*re + im*im
        out.append({"k": k, "frequency": k/n, "wavelength_generations": n/k, "power": p})
    total = sum(row["power"] for row in out)
    for row in out:
        row["power_fraction_non_dc"] = row["power"] / total if total else 0.0
    return out


def classify_spectrum(spectrum: list[dict], long_window: list[float], band: list[float], ambiguity_ratio: float) -> dict:
    lo, hi = long_window
    eligible = [r for r in spectrum if lo <= r["wavelength_generations"] <= hi]
    if len(eligible) < 2 or sum(r["power"] for r in eligible) <= 0:
        return {"valid": False, "reason": "NO_NONZERO_LONG_PERIOD_SPECTRUM"}
    ranked = sorted(eligible, key=lambda r: (-r["power"], r["k"]))
    first, second = ranked[0], ranked[1]
    ratio = float("inf") if second["power"] == 0 else first["power"] / second["power"]
    inside = lambda r: band[0] <= r["wavelength_generations"] <= band[1]
    strict = inside(first)
    broad = (not strict) and ratio < ambiguity_ratio and (inside(first) or inside(second))
    label = "STRICT_SUPPORT" if strict else ("BROAD_SUPPORT" if broad else "OUTSIDE")
    return {
        "valid": True,
        "label": label,
        "primary": first,
        "secondary": second,
        "top_to_second_power_ratio": ratio,
        "top_long_modes": ranked[:5],
    }


def public_state_fingerprint(state: dict) -> str:
    return base.fingerprint(base.canon_cnf(state["rows"]))


def run_epoch(spec: dict, prereg: dict) -> dict:
    kind = spec["constructor"]
    state = BUILDERS[kind](spec)
    initial_cnf = base.canon_cnf(state["rows"])
    N = base.input_size_units(initial_cnf)
    cap = N * N
    rng = random.Random(int(spec["seed"]) ^ 0x5A17C025)
    samples = int(prereg["trace_protocol"]["samples_per_epoch"])
    candidates_per_generation = int(prereg["trace_protocol"]["candidates_per_generation"])
    trace = []

    def record(g: int, st: dict) -> tuple[int, dict]:
        cnf = base.canon_cnf(st["rows"])
        delta, pivot_rows = exact_delta(cnf, cap)
        return delta, {
            "generation": g,
            "Delta": int(delta),
            "fingerprint": base.fingerprint(cnf),
            "state_units": int(base.state_units(cnf)),
            "clauses": len(cnf),
            "live_variables": len(base.vars_of(cnf)),
            "min_pivot": min(pivot_rows, key=lambda r: (r["margin"], r["pivot"])),
        }

    delta, row = record(0, state); trace.append(row)
    for g in range(1, samples):
        candidates = []
        for candidate_index in range(candidates_per_generation):
            cand = MUTATORS[kind](deepcopy(state), rng)
            d, rr = record(g, cand)
            candidates.append((d, rr["fingerprint"], candidate_index, cand, rr))
        # deterministic max Delta, then lexicographically smallest fingerprint.
        best_delta = max(x[0] for x in candidates)
        tied = [x for x in candidates if x[0] == best_delta]
        chosen = min(tied, key=lambda x: (x[1], x[2]))
        state = chosen[3]
        trace.append(chosen[4])

    values = [float(r["Delta"]) for r in trace]
    residual, coeff = quadratic_detrend(values)
    spectrum = dft_power(residual)
    cls = classify_spectrum(
        spectrum,
        prereg["spectral_pipeline"]["long_period_window_generations"],
        prereg["spectral_pipeline"]["candidate_band_generations"],
        float(prereg["spectral_pipeline"]["top_to_second_ambiguity_ratio"]),
    )
    return {
        "epoch_id": spec["id"],
        "constructor": kind,
        "seed": spec["seed"],
        "initial_fingerprint": base.fingerprint(initial_cnf),
        "final_fingerprint": trace[-1]["fingerprint"],
        "N": N,
        "cap": cap,
        "samples": samples,
        "trace": trace,
        "quadratic_trend_coefficients": coeff,
        "full_spectrum": spectrum,
        "classification": cls,
    }


def selftests() -> dict:
    tiny = base.canon_cnf([[1,2,3],[-1,2,4],[1,-3,4],[-1,3,-4]])
    raw_checks = 0
    for v in base.vars_of(tiny):
        _, stats = base.eliminate_var_capped(tiny, v, 10**9)
        assert raw_elimination_units(tiny, v) == int(stats["raw_units"])
        raw_checks += 1
    # Known period-16 sinusoid sampled 64 times must peak at k=4 after detrending.
    signal = [math.sin(2.0 * math.pi * t / 16.0) for t in range(64)]
    residual, _ = quadratic_detrend(signal)
    spectrum = dft_power(residual)
    peak = max(spectrum, key=lambda r: r["power"])
    assert peak["k"] == 4 and abs(peak["wavelength_generations"] - 16.0) < 1e-12
    return {"raw_elimination_equivalence_checks": raw_checks, "known_period_16_dft_peak": "PASS"}


def main() -> int:
    prereg = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
    if prereg["status"] != "FROZEN_BEFORE_MULTI_EPOCH_SPECTRA":
        raise ValueError("PREREG_NOT_FROZEN")
    tests = selftests()
    epochs = []
    errors = []
    initial_fps = set()
    constructors = set()
    for spec in prereg["voting_epochs"]:
        try:
            result = run_epoch(spec, prereg)
            if result["initial_fingerprint"] in initial_fps:
                raise ValueError("DUPLICATE_INITIAL_FINGERPRINT")
            if result["constructor"] in constructors:
                raise ValueError("DUPLICATE_CONSTRUCTOR_GEOMETRY")
            initial_fps.add(result["initial_fingerprint"])
            constructors.add(result["constructor"])
            epochs.append(result)
            c = result["classification"]
            print(f"{result['epoch_id']} {c.get('label')} lambda={c.get('primary',{}).get('wavelength_generations')} ratio={c.get('top_to_second_power_ratio')}")
        except Exception as exc:
            errors.append({"epoch_id": spec["id"], "constructor": spec["constructor"], "error": f"{type(exc).__name__}: {exc}"})
            print(f"{spec['id']} ERROR {type(exc).__name__}: {exc}")

    valid = [e for e in epochs if e["classification"].get("valid")]
    strict = sum(e["classification"].get("label") == "STRICT_SUPPORT" for e in valid)
    broad = sum(e["classification"].get("label") == "BROAD_SUPPORT" for e in valid)
    outside = sum(e["classification"].get("label") == "OUTSIDE" for e in valid)
    if len(valid) < 7:
        verdict = "UNKNOWN_INSUFFICIENT_INDEPENDENT_EVIDENCE"
    elif strict >= 4 and strict + broad >= 5:
        verdict = "REPLICATED_CANDIDATE_SCALE"
    else:
        verdict = "REFUTED_OR_GEOMETRY_SPECIFIC"

    report = {
        "schema": "JANUS/C025/STRUCTURAL-LAMBDA/ROOSTERS-MULTI-EPOCH-RESULT/v1",
        "status": verdict,
        "preregistration": str(PREREG_PATH),
        "preregistration_sha256": file_sha256(PREREG_PATH),
        "selftests": tests,
        "aggregate": {
            "required_independent_epochs": 7,
            "valid_independent_epochs": len(valid),
            "strict_support": strict,
            "broad_support": broad,
            "outside": outside,
            "errors": errors,
        },
        "candidate_band_generations": prereg["spectral_pipeline"]["candidate_band_generations"],
        "epochs": epochs,
        "historical_selector_product": prereg["nonvoting_historical_anchor"],
        "scientific_boundary": {
            "historical_anchor_did_not_vote": True,
            "seven_different_constructors_required": True,
            "structural_not_physical": True,
            "finite_replication_not_universal_constant": True,
            "spectral_result_not_theorem_authority": True,
            "P_VS_NP": "OPEN",
        },
        "P_VS_NP": "OPEN",
    }
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": verdict, **report["aggregate"], "P_VS_NP": "OPEN"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
