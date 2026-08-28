#!/usr/bin/env python3
"""JANUS PIPPI v3.2 — warm-history cold-start with cost-aware eyes.

Controlled successor to the frozen v3.1 balanced-accounting checkpoint.
The v3.1 negative result diagnosed an implementation/spec mismatch:
HOT_PREDICTIVE still launched 20-25% of the root field as a batch, so even
high-confidence familiar geometry paid a JUXTAPOSE tax.

Only the field-coverage scheduler changes here:
- COLD: preserve the instinct exactly — one full-field exact JUXTAPOSE wave.
- WARM: start with a small confidence-dependent exact wave (8-30% of field),
  then expand geometrically only if no exact-safe pivot is found.
- HOT: true predictive mode — test exactly one ranked pivot at a time; expand
  sequentially only after exact failure.

JGPT, Pivot-Slime, M2R, Spider, adviser governance, exact semantics, warm-history
curriculum and the 60/40 compute/latency accounting are unchanged.

Evaluation hygiene: v3.2 uses a NEW deterministic seed namespace, disjoint from
both historical lessons and the v3.1 holdout. The v3.1 holdout is NOT imported
as training data. This is therefore a fresh post-diagnosis evaluation rather
than tuning on the same exam.

Every clone/probe is exact. P_VS_NP remains OPEN.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

from experiments.mad_lab import adaptive_pippi_juxtapose_coldstart_v3 as v31
from experiments.mad_lab import adaptive_pippi_gauntlet_v2 as v2
from experiments.mad_lab import adaptive_pippi_pitstop_ladder as v1
from experiments.mad_lab import asymmetric_pq_track_relabelled as relabel
from experiments.mad_lab import keymaster_scalable_exact_2cnf_transition as st

P_VS_NP = "OPEN"
SCHEMA = "JANUS/PIPPI/JUXTAPOSE-COLDSTART-GAUNTLET/v3.2.0"
FRESH_V32_BASE = 4_900_000_000


def make_pq_stage_v32(p: int, q: int, stage_serial: int, count: int, used: set[str], source: str = "RUTHLESS_PQ_TRACK"):
    out = []; j = 0; metas = []
    import time
    t0 = time.perf_counter()
    while len(out) < count:
        seed = FRESH_V32_BASE + stage_serial * 100_003 + p * 1019 + q * 1031 + j * 43
        cnf, meta = relabel.construct_relabelled(p, q, seed)
        e = v2.exact_pq_episode(cnf, p, q, seed, source, stage_serial)
        j += 1
        if e["fingerprint"] in used:
            continue
        used.add(e["fingerprint"]); out.append(e); metas.append(meta)
    return out, {"generation_wall_seconds": time.perf_counter() - t0, "metas": metas, "seed_namespace": FRESH_V32_BASE}


def _run_wave(e: dict[str, Any], indices: list[int], wave_id: int) -> dict[str, Any]:
    cap = int(e["local_stress_cap"])
    rows = []; safe = []
    for idx in indices:
        pivot = e["vars"][idx]
        out, stats = st.eliminate_var_capped_2cnf_exact(e["cnf"], pivot, cap)
        raw = int(stats["raw_units"]); pairs = int(stats.get("pairs", 0)); fit = out is not None
        if fit:
            if not st.verify_transition_2cnf_exact(e["cnf"], pivot, out, cap):
                raise AssertionError("v3.2 exact transition replay failed")
            safe.append((raw, v1.stable_hash(e["tokens"][idx]), idx, pivot))
        rows.append({"wave": wave_id, "pivot_local_for_audit": pivot, "candidate_index": idx, "raw_units": raw, "pair_work": pairs, "fit": fit})
    chosen = min(safe)[2] if safe else None
    return {
        "rows": rows, "chosen_index": chosen,
        "checks": len(rows),
        "pairs": sum(r["pair_work"] for r in rows),
        "raw": sum(r["raw_units"] for r in rows),
        "lat_pairs": max((r["pair_work"] for r in rows), default=0),
        "lat_raw": max((r["raw_units"] for r in rows), default=0),
    }


def coverage_runtime_v32(e: dict[str, Any], learned_order: list[int], policy: dict[str, Any]) -> dict[str, Any]:
    n = len(learned_order); mode = policy["mode"]; confidence = float(policy["confidence"])
    if n == 0:
        raise AssertionError("empty root field")

    if mode == "COLD_JUXTAPOSE":
        wave_sizes = [n]
    elif mode == "HOT_PREDICTIVE":
        # True HOT: no batch tax. One exact ranked candidate per wave.
        wave_sizes = [1] * n
    elif mode == "WARM_JUXTAPOSE":
        # Confidence 0.45 -> 30%; confidence 0.70 -> 8%.
        t = max(0.0, min(1.0, (0.70 - confidence) / 0.25))
        frac = 0.08 + 0.22 * t
        first = max(2, min(n, math.ceil(n * frac)))
        wave_sizes = []
        remaining = n; size = first
        while remaining > 0:
            take = min(remaining, size)
            wave_sizes.append(take); remaining -= take; size = max(size + 1, size * 2)
    else:
        raise AssertionError(("unknown coverage mode", mode))

    cursor = 0; attempts = []; chosen_index = None; total_checks = total_pairs = total_raw = 0
    lat_pairs = lat_raw = 0; waves_used = 0
    for wave_id, size in enumerate(wave_sizes, 1):
        if cursor >= n:
            break
        indices = learned_order[cursor:cursor + size]; cursor += len(indices)
        w = _run_wave(e, indices, wave_id); waves_used += 1
        attempts.extend(w["rows"]); total_checks += w["checks"]; total_pairs += w["pairs"]; total_raw += w["raw"]
        lat_pairs += w["lat_pairs"]; lat_raw += w["lat_raw"]
        if w["chosen_index"] is not None:
            chosen_index = w["chosen_index"]
            break
    if chosen_index is None:
        raise AssertionError("v3.2 exhausted root field without exact-safe pivot")

    chosen = e["vars"][chosen_index]
    return {
        "exact_checks": total_checks,
        "pair_work": total_pairs,
        "raw_units_sum": total_raw,
        "peak_raw_units": max([e["root_units"]] + [r["raw_units"] for r in attempts]),
        "chosen_first_pivot_local_for_audit": chosen,
        "chosen_candidate_index": chosen_index,
        "root_attempts": attempts,
        "exact_transition_verified": True,
        "coverage_mode": mode,
        "coverage_ratio": total_checks / n,
        "initial_coverage_ratio": wave_sizes[0] / n,
        "clone_count": total_checks,
        "available_pivots": n,
        "waves_used": waves_used,
        "parallel_pair_work_latency_proxy": lat_pairs,
        "parallel_raw_units_latency_proxy": lat_raw,
        "parallel_exact_wave_latency_proxy": waves_used,
        "total_compute_is_not_free": True,
        "parallel_latency_is_proxy_not_walltime": True,
        "scheduler_v32": {
            "HOT": "SEQUENTIAL_TOP1_EXPANSION",
            "WARM": "CONFIDENCE_DEPENDENT_8_TO_30_PERCENT_THEN_GEOMETRIC_EXPANSION",
            "COLD": "FULL_FIELD_ONE_WAVE"
        }
    }


def _out_dir() -> Path:
    if "--out-dir" not in sys.argv:
        raise AssertionError("--out-dir required")
    return Path(sys.argv[sys.argv.index("--out-dir") + 1])


def main() -> int:
    # Controlled scheduler + fresh namespace only.
    v31.coverage_runtime = coverage_runtime_v32
    v2.make_pq_stage = make_pq_stage_v32
    rc = v31.main()
    if rc != 0:
        return rc

    path = _out_dir() / "gauntlet-result.json"
    result = json.loads(path.read_text(encoding="utf-8"))
    result["schema"] = SCHEMA
    result["controlled_change_v3_2"] = {
        "scheduler_only": True,
        "JGPT_changed": False,
        "SLIME_changed": False,
        "M2R_changed": False,
        "SPIDER_changed": False,
        "adviser_governance_changed": False,
        "warm_history_changed": False,
        "accounting_changed": False,
        "HOT": "sequential top-1 exact expansion",
        "WARM": "8-30% confidence-dependent first wave, geometric expansion only after exact failure",
        "COLD": "full-field exact JUXTAPOSE retained unchanged",
        "fresh_seed_namespace": FRESH_V32_BASE,
        "v3_1_holdout_imported_as_training": False,
        "P_VS_NP": P_VS_NP,
    }
    result["scientific_firewall"]["V3_2_FRESH_NAMESPACE_DISJOINT_FROM_V3_1_BY_CONSTRUCTION"] = True
    result["scientific_firewall"]["HOT_BATCH_TAX_REMOVED"] = True
    result["scientific_firewall"]["COLD_FULL_FIELD_REFLEX_PRESERVED"] = True
    result["scientific_firewall"]["P_VS_NP"] = P_VS_NP
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "V3_2_POSTPROCESS": "PASS",
        "frontier": result.get("official_frontier"),
        "stop_reason": result.get("stop_reason"),
        "boss_score": result.get("boss_250x250", {}).get("score"),
        "P_VS_NP": P_VS_NP,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
