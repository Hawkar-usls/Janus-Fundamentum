#!/usr/bin/env python3
"""Keymaster M2R-PM persistent calibration memory.

Consumes exact KEYMASTER pivot microscope JSON and turns it into:
  * immutable deduplicated pivot episodes;
  * recomputable Welford-style context aggregates;
  * Pivot-Slime training JSONL;
  * TOPA SPIDER seed JSONL.

This is an advisory memory/routing subsystem.  It cannot change exact JANUS
proof verdicts.  P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "JANUS/KEYMASTER/M2R-PM/v1.0.0"
P_VS_NP = "OPEN"


def stable_hash(obj: object) -> str:
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def structural_vector(case: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    cheap = row["cheap_cooccurrence_features"]
    d, p, q = row["signature"]
    return {
        "case_n": len(row.get("cheap_cooccurrence_features", {}).get("per_other_variable", [])) + 1,
        "root_units": case["root_units"],
        "cap": case["reference_cap"],
        "degree_d": d,
        "positive_p": p,
        "negative_q": q,
        "balance_ratio": min(p, q) / max(1, max(p, q)),
        "parent_pairs": row["parent_pairs"],
        "positive_parent_mean_width": row["positive_parent_mean_width"],
        "negative_parent_mean_width": row["negative_parent_mean_width"],
        "retained_clause_count": row["retained_clause_count"],
        "retained_units": row["retained_units"],
        "single_conflict_mass_per_pair": cheap["single_conflict_mass_per_pair"],
        "same_sign_mass_per_pair": cheap["same_sign_mass_per_pair"],
        "support_overlap_mass_per_pair": cheap["support_overlap_mass_per_pair"],
    }


def coarse_bucket(features: dict[str, Any]) -> str:
    # Numeric pivot id is deliberately absent.  Coarse rounding lets online
    # memory gather structurally similar cases while preserving raw episodes.
    bucket = {
        "n": features["case_n"],
        "d": features["degree_d"],
        "p": features["positive_p"],
        "q": features["negative_q"],
        "pw": round(features["positive_parent_mean_width"], 2),
        "nw": round(features["negative_parent_mean_width"], 2),
        "retained": features["retained_clause_count"],
        "conflict": round(features["single_conflict_mass_per_pair"], 3),
        "aligned": round(features["same_sign_mass_per_pair"], 3),
        "overlap": round(features["support_overlap_mass_per_pair"], 3),
    }
    return stable_hash(bucket)[:24]


def episode_from_row(case: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    features = structural_vector(case, row)
    exact = row["exact_outcome"]
    pairs = row["parent_pairs"]
    before = row["before_units"]
    after = exact["canonical_units"]
    delta = max(0, before - after)
    target = {
        "raw_units": exact["raw_units"],
        "canonical_units": after,
        "tautology_rate": row["exact_pair_structure"]["tautology_rate"],
        "collision_rate_non_taut": row["exact_pair_structure"]["collision_rate_among_non_taut"],
        "subsumed_raw_clauses": exact["subsumed_raw_clauses"],
        "fit_under_reference_cap": exact["fit_under_reference_cap"],
        "rank_by_exact_raw_local": row["rank_by_exact_raw_local"],
        "m2r": {
            "state_reduction_fraction": delta / max(1, before),
            "raw_efficiency": delta / max(1, exact["raw_units"]),
            "pair_efficiency": delta / max(1, pairs),
            "cap_margin_fraction": exact["cap_margin_reference"] / max(1, case["reference_cap"]),
        },
    }
    provenance = {
        "case_id": case["case_id"],
        "root_fingerprint": case["root_fingerprint"],
        "pivot_id_local": row["pivot_id_local"],
        "microscope_sha": None,
    }
    episode_id = stable_hash({"provenance": provenance, "features": features, "target": target})
    return {
        "episode_id": episode_id,
        "context_bucket": coarse_bucket(features),
        "provenance": provenance,
        "features": features,
        "target": target,
    }


def aggregate(episodes: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for e in episodes:
        groups.setdefault(e["context_bucket"], []).append(e)
    out = {}
    metrics = [
        ("raw_units", lambda e: float(e["target"]["raw_units"])),
        ("canonical_units", lambda e: float(e["target"]["canonical_units"])),
        ("tautology_rate", lambda e: float(e["target"]["tautology_rate"])),
        ("collision_rate_non_taut", lambda e: float(e["target"]["collision_rate_non_taut"])),
        ("state_reduction_fraction", lambda e: float(e["target"]["m2r"]["state_reduction_fraction"])),
        ("raw_efficiency", lambda e: float(e["target"]["m2r"]["raw_efficiency"])),
        ("pair_efficiency", lambda e: float(e["target"]["m2r"]["pair_efficiency"])),
        ("cap_margin_fraction", lambda e: float(e["target"]["m2r"]["cap_margin_fraction"])),
    ]
    for key, rows in sorted(groups.items()):
        stats = {"count": len(rows), "metrics": {}}
        for name, fn in metrics:
            n = 0
            mean = 0.0
            M2 = 0.0
            for e in rows:
                x = fn(e)
                n += 1
                d = x - mean
                mean += d / n
                M2 += d * (x - mean)
            stats["metrics"][name] = {
                "count": n,
                "mean": mean,
                "M2": M2,
                "sample_variance": M2 / (n - 1) if n > 1 else 0.0,
            }
        stats["representative_features"] = rows[0]["features"]
        out[key] = stats
    return out


def topa_record(e: dict[str, Any]) -> dict[str, Any]:
    f = e["features"]
    t = e["target"]
    status = "SAFE" if t["fit_under_reference_cap"] else "OVERFLOW"
    tags = [
        "KEYMASTER_PIVOT",
        "EXACT_RECEIPT",
        status,
        f"N{f['case_n']}",
        f"D{f['degree_d']}",
        f"P{f['positive_p']}",
        f"Q{f['negative_q']}",
        "HIGH_COMPRESSION" if t["raw_units"] / max(1, t["canonical_units"]) >= 5 else "LOWER_COMPRESSION",
        "HIGH_TAUTOLOGY" if t["tautology_rate"] >= 0.6 else "MODERATE_TAUTOLOGY",
    ]
    text = (
        f"Exact Keymaster pivot episode. n={f['case_n']} d={f['degree_d']} p={f['positive_p']} q={f['negative_q']} "
        f"pairs={f['parent_pairs']} raw={t['raw_units']} canonical={t['canonical_units']} "
        f"tautology_rate={t['tautology_rate']:.6f} collision_rate={t['collision_rate_non_taut']:.6f} "
        f"conflict_mass_per_pair={f['single_conflict_mass_per_pair']:.6f} "
        f"same_sign_mass_per_pair={f['same_sign_mass_per_pair']:.6f} "
        f"support_overlap_mass_per_pair={f['support_overlap_mass_per_pair']:.6f} "
        f"cap={f['cap']} fit={status} rank={t['rank_by_exact_raw_local']}."
    )
    return {
        "provider": "TOPA_REPO",
        "archive_id": "keymaster-" + e["episode_id"][:20],
        "title": f"Keymaster pivot calibration {e['provenance']['case_id']} local-pivot-{e['provenance']['pivot_id_local']}",
        "text": text,
        "source_url": "repo://Janus-Fundamentum/data/keymaster",
        "relation_tags": tags,
        "exact_episode_id": e["episode_id"],
        "context_bucket": e["context_bucket"],
    }


def load_state(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {
            "schema": SCHEMA,
            "P_VS_NP": P_VS_NP,
            "status": "ADVISORY_MEMORY__EXACT_RECEIPTS_ONLY",
            "episodes": {},
            "aggregates": {},
            "laws": [
                "PIVOT_ID_IS_LOCAL_PROVENANCE_ONLY",
                "MODEL_MEMORY_CANNOT_CHANGE_EXACT_VERDICT",
                "TOPA_RELATIONS_ARE_HYPOTHESES",
                "P_VS_NP_IS_OPEN",
            ],
        }
    return json.loads(path.read_text(encoding="utf-8"))


def update_state(microscope: dict[str, Any], old: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    assert microscope["P_VS_NP"] == "OPEN"
    episodes_by_id = dict(old.get("episodes") or {})
    new_rows = []
    micro_sha = microscope.get("sha256")
    for case in microscope["cases"]:
        for row in case["rows"]:
            e = episode_from_row(case, row)
            e["provenance"]["microscope_sha"] = micro_sha
            # Recompute id including stable provenance sha.
            e["episode_id"] = stable_hash({
                "provenance": e["provenance"],
                "features": e["features"],
                "target": e["target"],
            })
            if e["episode_id"] not in episodes_by_id:
                episodes_by_id[e["episode_id"]] = e
                new_rows.append(e)
    episodes = [episodes_by_id[k] for k in sorted(episodes_by_id)]
    state = {
        "schema": SCHEMA,
        "P_VS_NP": P_VS_NP,
        "status": "ADVISORY_MEMORY__EXACT_RECEIPTS_ONLY",
        "episodes": {e["episode_id"]: e for e in episodes},
        "episode_count": len(episodes),
        "aggregates": aggregate(episodes),
        "laws": old.get("laws") or [
            "PIVOT_ID_IS_LOCAL_PROVENANCE_ONLY",
            "MODEL_MEMORY_CANNOT_CHANGE_EXACT_VERDICT",
            "TOPA_RELATIONS_ARE_HYPOTHESES",
            "P_VS_NP_IS_OPEN",
        ],
    }
    state["state_sha256"] = stable_hash({k: v for k, v in state.items() if k != "state_sha256"})
    return state, new_rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for r in rows), encoding="utf-8")


def self_test() -> None:
    fake = {
        "P_VS_NP": "OPEN",
        "sha256": "fake",
        "cases": [{
            "case_id": "test",
            "root_fingerprint": "root",
            "reference_cap": 100,
            "root_units": 20,
            "rows": [{
                "pivot_id_local": 7,
                "signature": [4, 2, 2],
                "before_units": 20,
                "parent_pairs": 4,
                "positive_parent_mean_width": 3.0,
                "negative_parent_mean_width": 3.0,
                "retained_clause_count": 2,
                "retained_units": 7,
                "cheap_cooccurrence_features": {
                    "single_conflict_mass_per_pair": 0.5,
                    "same_sign_mass_per_pair": 0.25,
                    "support_overlap_mass_per_pair": 0.75,
                },
                "exact_pair_structure": {"tautology_rate": 0.5, "collision_rate_among_non_taut": 0.5},
                "exact_outcome": {
                    "raw_units": 12,
                    "canonical_units": 8,
                    "subsumed_raw_clauses": 1,
                    "fit_under_reference_cap": True,
                    "cap_margin_reference": 88,
                },
                "rank_by_exact_raw_local": 1,
            }],
        }],
    }
    state, new = update_state(fake, load_state(None))
    assert state["episode_count"] == 1 and len(new) == 1
    state2, new2 = update_state(fake, state)
    assert state2["episode_count"] == 1 and len(new2) == 0
    e = next(iter(state["episodes"].values()))
    assert "pivot_id_local" not in e["features"]
    assert topa_record(e)["provider"] == "TOPA_REPO"


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--microscope", type=Path)
    ap.add_argument("--state-in", type=Path)
    ap.add_argument("--state-out", type=Path)
    ap.add_argument("--training-out", type=Path)
    ap.add_argument("--topa-out", type=Path)
    args = ap.parse_args(list(argv) if argv is not None else None)
    if args.self_test:
        self_test()
        print(json.dumps({"status": "PASS", "P_VS_NP": P_VS_NP}))
        return 0
    if not args.microscope or not args.state_out or not args.training_out or not args.topa_out:
        ap.error("--microscope --state-out --training-out --topa-out are required")
    microscope = json.loads(args.microscope.read_text(encoding="utf-8"))
    old = load_state(args.state_in)
    state, new_rows = update_state(microscope, old)
    args.state_out.parent.mkdir(parents=True, exist_ok=True)
    args.state_out.write_text(json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    all_rows = [state["episodes"][k] for k in sorted(state["episodes"])]
    write_jsonl(args.training_out, all_rows)
    write_jsonl(args.topa_out, [topa_record(e) for e in all_rows])
    print(json.dumps({
        "status": "PASS",
        "episodes_total": state["episode_count"],
        "episodes_added": len(new_rows),
        "context_buckets": len(state["aggregates"]),
        "P_VS_NP": P_VS_NP,
        "state_sha256": state["state_sha256"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
