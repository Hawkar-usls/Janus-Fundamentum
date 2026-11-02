#!/usr/bin/env python3
"""E12C4 INTERNAL DEVELOPMENT ONLY. No held-out timing or champion promotion.

Certified exact source masks are a correctness prerequisite; profit is an
empirical, fallible prediction. Missing development evidence => untouched RAW.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import sys
from collections import Counter
from hashlib import sha256
from pathlib import Path
from statistics import median

import janus_time_sat_004e12c1_cost_aware as c1

COVERAGES = (0.60, 0.67, 0.699, 0.701, 0.75, 0.80, 0.90)
ROOT = Path("experiments/time_sat_004_external")
VARIANTS = ("as_emitted", "global_shuffle", "renamed_polarity")
SCHEMA = "JANUS-TIME-SAT-004E12C4-INTERNAL-DEV-V1"
# New prospective originals, distinct from E12C3's already exposed eight.
# The held-out seeds must not be timed, profiled or used to fit the model.
FAMILIES = tuple(["coverage_%s" % str(x) for x in COVERAGES] +
                 ["mixed_partial", "width5", "width4", "planted3", "unsat_parity_guard"])
DEVELOPMENT = tuple((f, 202611040000 + i * 100 + j)
                    for i, f in enumerate(FAMILIES) for j in range(2))
HOLDOUT = tuple((f, 202611050000 + i * 100 + j)
                for i, f in enumerate(FAMILIES) for j in range(2))

def digest(payload: bytes) -> str:
    return sha256(payload).hexdigest()

def _dimacs(n, rows):
    return ("p cnf %d %d\n" % (n, len(rows)) +
            "".join(" ".join(map(str, row)) + " 0\n" for row in rows)).encode()

def _model_ok(rows, model):
    values = {abs(x): x > 0 for x in model}
    return all(any(values.get(abs(x)) == (x > 0) for x in row) for row in rows)

def _block(support, rhs):
    w = len(support)
    return [[v if b == 0 else -v for v, b in zip(support, mask)]
            for mask in itertools.product((0, 1), repeat=w)
            if sum(mask) % 2 != rhs]

def generate(family, seed):
    """Deterministic original CNF; never select a source based on solver timing."""
    if family not in FAMILIES or type(seed) is not int:
        raise ValueError("Unregistered internal source family/seed")
    rng = random.Random(seed)
    is_unsat = family == "unsat_parity_guard"
    n = 12 if is_unsat else 30
    truth = {i: bool(rng.getrandbits(1)) for i in range(1, n + 1)}
    model = [i if truth[i] else -i for i in range(1, n + 1)]
    rows = []
    complete = []
    partial = []
    if family != "planted3":
        width = 5 if family in ("width5", "unsat_parity_guard") else (4 if family == "width4" else 6)
        nfull = 1 if is_unsat else (8 if family == "mixed_partial" else 12)
        supports = set()
        if is_unsat:
            supports.add(tuple(range(1, 6)))
        while len(supports) < nfull + (4 if family == "mixed_partial" else 0) + (2 if is_unsat else 0):
            s = tuple(sorted(rng.sample(range(1, n + 1), width if not is_unsat or not supports else 6)))
            supports.add(s)
        keys = sorted(supports)
        if is_unsat:
            keys.remove(tuple(range(1, 6)))
            keys.insert(0, tuple(range(1, 6)))
        for i, support in enumerate(keys):
            rhs = sum(int(truth[v]) for v in support) % 2
            block = _block(support, rhs)
            rng.shuffle(block)
            if i >= nfull:
                # Missing sign masks are *never* a certified XOR.
                del block[0]
                partial.append(tuple(support))
            else:
                complete.append(tuple(support))
            rows.extend(block)
    if is_unsat:
        # Independent UNSAT witness: fix all five support bits to the *opposite*
        # parity of their certified full-width5 equation.
        forced = {v: truth[v] for v in range(1, 6)}
        forced[1] = not forced[1]
        rows.extend([[v if forced[v] else -v] for v in sorted(forced)])
    else:
        guard = 240 if family == "planted3" else (48 if family == "mixed_partial" else 0)
        if family.startswith("coverage_"):
            target = float(family.split("_")[1])
            covered = sum(2 ** (len(s) - 1) for s in complete)
            guard = max(0, round(covered / target - len(rows)))
        seen = {tuple(sorted(row)) for row in rows}
        attempts = 0
        while guard:
            attempts += 1
            if attempts > 100000:
                raise AssertionError("Cannot construct fresh planted guards")
            vs = rng.sample(range(1, n + 1), 3)
            clause = [v if rng.getrandbits(1) else -v for v in vs]
            key = tuple(sorted(clause))
            if key in seen or not any(truth[abs(v)] == (v > 0) for v in clause):
                continue
            rows.append(clause)
            seen.add(key)
            guard -= 1
    if family in ("mixed_partial", "unsat_parity_guard"):
        # Duplicates are not silently consumed by sign-mask certificates.
        rows.extend([list(rows[i]) for i in range(3)])
    rng.shuffle(rows)
    if not is_unsat and not _model_ok(rows, model):
        raise AssertionError("Planted SAT model invalid")
    payload = _dimacs(n, rows)
    return {"family": family, "seed": seed, "n": n, "rows": rows,
            "status_by_construction": "UNSAT" if is_unsat else "SAT",
            "model": None if is_unsat else model,
            "original_sha256": digest(payload),
            "model_sha256": None if is_unsat else digest(json.dumps(model).encode()),
            "complete_supports": complete, "partial_supports": partial,
            "cnf": payload}

def transform(source, variant):
    if variant not in VARIANTS:
        raise ValueError("Unregistered variant")
    rows = [list(row) for row in source["rows"]]
    model = None if source["model"] is None else list(source["model"])
    n = source["n"]
    if variant != "as_emitted":
        rng = random.Random(source["seed"] + 900001 * VARIANTS.index(variant))
        if variant == "global_shuffle":
            for row in rows:
                rng.shuffle(row)
            rng.shuffle(rows)
        else:
            dest = list(range(1, n + 1))
            rng.shuffle(dest)
            mapping = {i: dest[i-1] for i in range(1, n + 1)}
            flips = {i: bool(rng.getrandbits(1)) for i in range(1, n + 1)}
            rows = [[(1 if v > 0 else -1) * (-1 if flips[abs(v)] else 1) *
                     mapping[abs(v)] for v in row] for row in rows]
            if model is not None:
                new_model = [None] * n
                for v in model:
                    old = abs(v)
                    new = mapping[old]
                    sign = (v > 0) != flips[old]
                    new_model[new-1] = new if sign else -new
                model = new_model
    if model is not None and not _model_ok(rows, model):
        raise AssertionError("Renamed full original SAT model invalid")
    return {**source, "rows": rows, "model": model,
            "variant": variant, "variant_sha256": digest(_dimacs(n, rows))}

def _proof_and_residual(rows, n, equations):
    """Recheck full forbidden masks independently of C1's detected indices."""
    used = set()
    for eq in equations:
        support = tuple(eq["variables"])
        rhs = eq["rhs"]
        indices = eq["original_clause_indices"]
        w = len(support)
        if w not in (5, 6) or len(indices) != 2 ** (w - 1):
            raise AssertionError("Uncertified source width/count")
        if len(set(indices)) != len(indices) or any(i in used for i in indices):
            raise AssertionError("Reused source clause")
        expected = Counter(tuple(sorted(x)) for x in _block(support, rhs))
        actual = Counter(tuple(sorted(rows[i])) for i in indices
                         if type(i) is int and 0 <= i < len(rows))
        if actual != expected:
            raise AssertionError("Not exactly the full source forbidden masks")
        used.update(indices)
    residual = [row for i, row in enumerate(rows) if i not in used]
    if Counter(tuple(sorted(r)) for r in rows) != (
            Counter(tuple(sorted(rows[i])) for i in used) +
            Counter(tuple(sorted(r)) for r in residual)):
        raise AssertionError("Original source clause multiset not conserved")
    if residual != [row for i, row in enumerate(rows) if i not in used]:
        raise AssertionError("Residual order changed")
    return residual

def features(rows, n, equations):
    covered = sum(len(eq["original_clause_indices"]) for eq in equations)
    return {"n": n, "m": len(rows), "lits": sum(map(len, rows)),
            "eq": len(equations), "width6": sum(eq["width"] == 6 for eq in equations),
            "coverage": round(covered / len(rows), 6) if rows else 0.0,
            "residual": len(rows) - covered}

def fit_development(receipts, forbidden_source_shas=()):
    """Group by original SHA; no variant/repeat may count as a new independent source.

    Each input is a source-aggregated verified full-cold paired receipt; a single
    CPU/wall UNKNOWN disqualifies the source from positive training evidence.
    """
    forbidden = set(forbidden_source_shas)
    seen = set()
    profiles = []
    for r in receipts:
        sha = r["original_sha256"]
        if sha in seen or sha in forbidden or len(sha) != 64:
            raise AssertionError("Duplicate/held-out or invalid development original SHA")
        seen.add(sha)
        pairs = r["paired_full_cold"]
        if not pairs:
            raise AssertionError("Missing development pairs")
        censored = any(p["raw_status"] != "VERIFIED" or
                       p["xor_status"] != "VERIFIED" for p in pairs)
        if censored:
            profiles.append({"original_sha256": sha, "features": r["features"],
                             "censored": True, "gain": None})
            continue
        ratios = []
        for p in pairs:
            a, b = float(p["raw_s"]), float(p["xor_s"])
            if not (math.isfinite(a) and math.isfinite(b) and a > 0 and b > 0):
                raise AssertionError("Non-finite or partial full-cold pair")
            ratios.append(a / b)
        profiles.append({"original_sha256": sha, "features": r["features"],
                         "censored": False, "gain": median(ratios)})
    return {"schema": SCHEMA + "-DEV-FIT", "profiles": profiles,
            "min_gain": 1.5, "min_matching_originals": 2,
            "training_only": True, "promotion": "PROHIBITED"}

def choose(rows, n, fitted=None):
    """Certified XOR if and ONLY if full proof and conservative development neighbors.

    No oracle ground-truth SAT/UNSAT labels or solver timing enters choice.
    An unknown/degraded/censored neighborhood => exact RAW (not residual-only).
    """
    raw = {"equations": [], "cnf_clauses": rows, "decision": "RAW"}
    try:
        index = c1.source_index_all_widths(rows, n)
        certified = [eq for eq in index["equations"] if eq["width"] in (5, 6)]
        proof_residual = _proof_and_residual(rows, n, certified)
        f = features(rows, n, certified)
    except (AssertionError, IndexError, KeyError, MemoryError, TypeError, ValueError):
        return {**raw, "reason": "INVALID_OR_UNPROVEN_SOURCE_FAIL_CLOSED"}
    if not certified or not fitted or fitted.get("schema") != SCHEMA + "-DEV-FIT":
        return {**raw, "reason": "NO_CERTIFICATE_OR_FROZEN_DEV_MODEL", "features": f}
    neighbors = []
    for p in fitted["profiles"]:
        q = p["features"]
        if (q["eq"] >= 4 and f["eq"] >= 4 and
            q["width6"] == f["width6"] and
            abs(q["coverage"] - f["coverage"]) <= 0.06 and
            0.7 <= q["n"] / f["n"] <= 1.43):
            neighbors.append(p)
    if (len({p["original_sha256"] for p in neighbors}) <
            fitted["min_matching_originals"] or
        any(p["censored"] or p["gain"] is None or
            p["gain"] < fitted["min_gain"] for p in neighbors)):
        return {**raw, "reason": "LOW_CONFIDENCE_OR_CENSORED_DEV", "features": f}
    return {"decision": "XOR_INTERNAL_DEVELOPMENT", "reason": "DEV_NEIGHBORS_ONLY",
            "equations": certified, "cnf_clauses": proof_residual, "features": f}

def independent_truth_table(rows, n, bound=12):
    """Small original CNF exhaustive verification, no SAT solver or XOR index.

    Same administration, but independent checking algorithm. Above bound we
    return UNVERIFIED, never transform solver-reported UNSAT into proof.
    """
    if n > bound:
        return "UNVERIFIED_TOO_LARGE"
    for bits in itertools.product((False, True), repeat=n):
        if all(any(bits[abs(v)-1] == (v > 0) for v in clause)
               for clause in rows):
            return "SAT_HAS_MODEL"
    return "INTERNAL_EXHAUSTIVE_UNSAT_VERIFIED"

def pair_result(raw, candidate):
    if raw["status"] not in ("SAT_VERIFIED", "UNSAT_PROOF_VERIFIED") or (
        candidate["status"] not in ("SAT_VERIFIED", "UNSAT_PROOF_VERIFIED")):
        return {"regret": "INDETERMINATE", "reason": "CENSORED_OR_UNVERIFIED"}
    if raw["status"] != candidate["status"]:
        return {"regret": "INVALID_RESULT_MISMATCH"}
    a, b = raw["full_cold_s"], candidate["full_cold_s"]
    if not (0 < a and 0 < b and math.isfinite(a) and math.isfinite(b)):
        return {"regret": "INVALID_TIMING"}
    return {"raw_over_candidate": a / b, "regret": "FINITE_PAIR"}

def cohort_manifest():
    catalog = {}
    all_shas = set()
    for split, specs in (("development", DEVELOPMENT), ("heldout_internal", HOLDOUT)):
        arr = []
        for family, seed in specs:
            src = generate(family, seed)
            if src["original_sha256"] in all_shas:
                raise AssertionError("Source SHA overlaps splits")
            all_shas.add(src["original_sha256"])
            entry = {"family": family, "seed": seed,
                     "original_sha256": src["original_sha256"],
                     "model_sha256": src["model_sha256"],
                     "n": src["n"], "m": len(src["rows"]),
                     "intended_status": src["status_by_construction"],
                     "variants": {v: transform(src, v)["variant_sha256"] for v in VARIANTS}}
            arr.append(entry)
        catalog[split] = arr
    return {"schema": SCHEMA + "-COHORT-LOCK", "catalog": catalog,
            "holdout_external": False, "holdout_timed": False,
            "main_C023": "UNCHANGED",
            "three_gates": ["SOUNDNESS", "RESULT_VERIFICATION", "NET_PROFIT"],
            "promotion": "PROHIBITED"}

def fit_archived_e12c3():
    """Consume *all* C3 source-group RAW/C2 pairs (exposed development evidence).

    Only original SHA groups are samples. Every OS/representation/repeat counts
    toward censoring but never becomes an additional independent observation.
    Uses archived original receipts, not generated E12C4 holdout performance.
    """
    import janus_time_sat_004e12c3_partial_mask_falsification as c3
    folder = ROOT / "time_sat_004e12c3_evidence" / "original-16-worker-JSON"
    files = sorted(folder.glob("*.json"))
    if len(files) != 16:
        raise AssertionError("All 16 archived C3 VMs are required")
    grouped = {}
    for path in files:
        j = json.loads(path.read_text())
        if (j.get("prereg_Git_blob") != c3.BLOB or
            j.get("original_os") not in c3.HOSTS or
            j.get("original_CNF_SHA256") != c3.original(j["case"])["sha"]):
            raise AssertionError("Untrusted C3 archive/source SHA mismatch")
        key = (j["case"], j["original_os"])
        if key in grouped:
            raise AssertionError("Duplicate archived C3 VM")
        pairs = {}
        for record in j["records"]:
            k = (record["variant"], record["repeat"])
            if record["arm"] in ("raw_cms", "e12c2_certified_width5_6_no_probe"):
                pairs.setdefault(k, {})[record["arm"]] = record
        if len(pairs) != 8 or any(set(p) !=
           {"raw_cms", "e12c2_certified_width5_6_no_probe"} for p in pairs.values()):
            raise AssertionError("Missing C3 matched original source pairs")
        grouped[key] = (j, pairs)
    if set(grouped) != set(itertools.product(c3.IDS, c3.HOSTS)):
        raise AssertionError("Original source or OS archive not exhaustive")
    training = []
    for case in c3.IDS:
        source = c3.original(case)
        idx = c1.source_index_all_widths(source["rows"], source["n"])
        certified = [eq for eq in idx["equations"] if eq["width"] in (5, 6)]
        f = features(source["rows"], source["n"], certified)
        paired = []
        for host in c3.HOSTS:
            j, pairs = grouped[(case, host)]
            if j["original_complete_model_SHA256"] != source["model_sha"]:
                raise AssertionError("Original C3 model SHA drift")
            for k in sorted(pairs):
                raw = pairs[k]["raw_cms"]
                xor = pairs[k]["e12c2_certified_width5_6_no_probe"]
                def verified(x):
                    o = x["outcome"]
                    return (o["status"] == c3.SAT and
                            o.get("full_original_CNF_complete_model_replay") == "PASS")
                paired.append({
                    "raw_status": "VERIFIED" if verified(raw) else "UNKNOWN",
                    "xor_status": "VERIFIED" if verified(xor) else "UNKNOWN",
                    "raw_s": raw["full_cold_child_wall_s"],
                    "xor_s": xor["full_cold_child_wall_s"]})
        training.append({"original_sha256": source["sha"],
                         "features": f, "paired_full_cold": paired})
    # No E12C4 new source appears in the old E12C3 experiment.
    forbidden = {generate(f, s)["original_sha256"] for f, s in HOLDOUT}
    return fit_development(training, forbidden_source_shas=forbidden)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-cohort-lock", type=Path)
    ap.add_argument("--write-development-fit", type=Path)
    args = ap.parse_args()
    if args.write_cohort_lock is not None:
        o = cohort_manifest()
        path = args.write_cohort_lock
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = (json.dumps(o, indent=2, sort_keys=True) + "\n").encode()
        path.write_bytes(payload)
        path.with_suffix(".sha256").write_text(digest(payload) + "  " + path.name + "\n")
        print("E12C4_INTERNAL_COHORT_GENERATED_NOT_TIMED", digest(payload))
    elif args.write_development_fit is not None:
        fitted = fit_archived_e12c3()
        path = args.write_development_fit
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = (json.dumps(fitted, indent=2, sort_keys=True) + "\\n").encode()
        path.write_bytes(payload)
        path.with_suffix(".sha256").write_text(digest(payload) + "  " + path.name + "\\n")
        print("E12C4_EXPOSED_C3_DEV_FIT_NOT_HOLDOUT", digest(payload))
    else:
        ap.error("Choose a development-only output, not a timed holdout")

if __name__ == "__main__":
    main()
