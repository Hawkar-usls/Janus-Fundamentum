#!/usr/bin/env python3
"""PIPPI Spider chunker + end-of-cycle mirror.

PIPPI is the canonical learning/resource journal name.  The historical KLGJ
engine/file format remains valid provenance, but all new reports use PIPPI.

This tool:
1. reads append-only journal events;
2. creates deterministic provenance chunks for TOPA DETECTIVE SPIDER;
3. extracts relation targets without turning correlation into truth;
4. emits PIPPI MIRROR for Pivot-Slime and Keymaster to read before the next
   cycle.

The mirror is advisory. Exact JANUS replay remains authority. P_VS_NP=OPEN.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

P_VS_NP = "OPEN"
SCHEMA = "JANUS/PIPPI/SPIDER-MIRROR/v1.0.0"


def stable_hash(obj: object) -> str:
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for r in rows), encoding="utf-8")


def boundary(prev: dict[str, Any] | None, cur: dict[str, Any], current_len: int, max_events: int) -> bool:
    if prev is None or current_len >= max_events:
        return True
    keys = ("formula_fingerprint", "configuration_id", "resource_cap")
    if any(prev.get(k) != cur.get(k) for k in keys):
        return True
    if prev.get("model_checkpoint_id") != cur.get("model_checkpoint_id"):
        return True
    p_prev = prev.get("holdout", {}).get("plateau_status")
    p_cur = cur.get("holdout", {}).get("plateau_status")
    if p_prev != p_cur and (p_prev is not None or p_cur is not None):
        return True
    if cur.get("event_type") in {"REGRESSION", "MATCHED_ABLATION"}:
        return True
    return False


def chunk_events(events: list[dict[str, Any]], max_events: int = 32) -> list[dict[str, Any]]:
    groups: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    prev = None
    for e in events:
        if current and boundary(prev, e, len(current), max_events):
            groups.append(current)
            current = []
        current.append(e)
        prev = e
    if current:
        groups.append(current)

    out: list[dict[str, Any]] = []
    for g in groups:
        seqs = [int(e["sequence_no"]) for e in g]
        event_ids = [e["event_id"] for e in g]
        metrics = [e.get("metrics", {}) for e in g]
        derived = [e.get("derived_vs_baseline", {}) for e in g]
        chunk = {
            "schema": "JANUS/PIPPI/SPIDER-CHUNK/v1.0.0",
            "sequence_start": min(seqs),
            "sequence_end": max(seqs),
            "event_ids": event_ids,
            "formula_fingerprints": sorted({str(e.get("formula_fingerprint")) for e in g}),
            "configuration_ids": sorted({str(e.get("configuration_id")) for e in g}),
            "model_checkpoint_ids": sorted({str(e.get("model_checkpoint_id")) for e in g if e.get("model_checkpoint_id") is not None}),
            "resource_caps": sorted({str(e.get("resource_cap")) for e in g}),
            "event_types": [e.get("event_type") for e in g],
            "raw_metrics": metrics,
            "derived_gain_metrics": derived,
            "training_cost": [e.get("training_cost", {}) for e in g],
            "regressions": [e["event_id"] for e in g if e.get("event_type") == "REGRESSION"],
            "provenance": {
                "source": "PIPPI_APPEND_ONLY_JOURNAL",
                "event_sha256": [e.get("event_sha256") for e in g],
            },
            "P_VS_NP": P_VS_NP,
        }
        chunk["chunk_id"] = stable_hash({k: v for k, v in chunk.items() if k != "chunk_id"})[:32]
        out.append(chunk)
    return out


def observed_relation_targets(events: list[dict[str, Any]], summary: dict[str, Any]) -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    for e in events:
        d = e.get("derived_vs_baseline", {})
        if d.get("comparable_for_search_gain"):
            signals = {}
            for k in ("exact_checks_attempted", "pair_work", "raw_units_sum", "peak_raw_units", "terminal_depth"):
                if isinstance(d.get(k), dict):
                    signals[k] = d[k].get("saved_fraction")
            targets.append({
                "relation_class": "RESOURCE_COST_TO_GAIN",
                "status": "OBSERVED_EDGE",
                "event_id": e["event_id"],
                "signals": signals,
                "training_cost": e.get("training_cost", {}),
                "instruction": "Test whether the apparent gain survives matched ablation / holdout and is not explained by formula, cap or hardware differences.",
            })
        if e.get("matched_ablation", {}).get("comparable"):
            targets.append({
                "relation_class": "MODEL_OR_MODULE_CHANGE_TO_GAIN",
                "status": "OBSERVED_EDGE",
                "event_id": e["event_id"],
                "changed_axis": e.get("changed_axis"),
                "deltas": e.get("matched_ablation", {}).get("deltas", {}),
                "instruction": "Attempt falsification for confounding and interaction effects before attribution.",
            })
    plateau = summary.get("plateau_watch", {})
    if plateau.get("status") not in {None, "INSUFFICIENT_HISTORY", "LEARNING_ACTIVE"}:
        targets.append({
            "relation_class": "PLATEAU_OR_REGRESSION_PRECURSOR",
            "status": "OBSERVED_EDGE",
            "plateau_watch": plateau,
            "instruction": "Search preceding chunks for repeated context/model/resource changes associated with slowing, while preserving non-causal status.",
        })
    if not targets:
        targets.append({
            "relation_class": "UNEXPLAINED_DELTA",
            "status": "INSUFFICIENT_COMPARABLE_GAIN_HISTORY",
            "instruction": "Do not invent a relation. Accumulate matched comparable checkpoints first.",
        })
    return targets


def mirror(events: list[dict[str, Any]], summary: dict[str, Any], chunks: list[dict[str, Any]], targets: list[dict[str, Any]]) -> dict[str, Any]:
    latest = events[-1] if events else None
    improved: list[dict[str, Any]] = []
    regressed: list[dict[str, Any]] = []
    if latest:
        d = latest.get("derived_vs_baseline", {})
        if d.get("comparable_for_search_gain"):
            for name in ("exact_checks_attempted", "pair_work", "raw_units_sum", "peak_raw_units", "terminal_depth"):
                x = d.get(name)
                if isinstance(x, dict):
                    item = {"metric": name, "saved": x.get("saved"), "saved_fraction": x.get("saved_fraction"), "capacity_multiplier": x.get("capacity_multiplier")}
                    if float(x.get("saved", 0)) >= 0:
                        improved.append(item)
                    else:
                        regressed.append(item)

    account = summary.get("accounting", {})
    plateau = summary.get("plateau_watch", {})
    lessons = []
    if improved:
        lessons.append("Some matched metrics improved; keep them as measured observations, not universal pivot rules.")
    if regressed:
        lessons.append("Regression exists; preserve it in M2R-PM/PIPPI and prioritize counterexample-oriented review.")
    if not improved and not regressed:
        lessons.append("No matched gain delta is available yet; mirror must not claim learning speedup.")

    out = {
        "schema": "JANUS/PIPPI/MIRROR/v1.0.0",
        "status": "READY",
        "P_VS_NP": P_VS_NP,
        "latest_event_id": latest.get("event_id") if latest else None,
        "latest_sequence_no": latest.get("sequence_no") if latest else None,
        "journal_event_count": len(events),
        "spider_chunk_count": len(chunks),
        "what_improved": improved,
        "what_regressed": regressed,
        "resource_balance": account,
        "plateau_or_slowing_status": plateau,
        "newly_supported_navigation_lessons": lessons,
        "lessons_rejected_by_TOPA": [],
        "unexplained_deltas": targets,
        "next_cycle_questions": [
            "Which exact matched metric improved or regressed after the last checkpoint?",
            "Did the improvement survive formula-fingerprint holdout and matched ablation?",
            "Which Spider relation should TOPA CORE try hardest to falsify next?",
            "Is effective capacity improving faster than training/calibration cost is accumulating?",
            "Is marginal gain slowing, and if so in which subsystem/context?",
        ],
        "slime_advisory_context": {
            "use": "Read before next cycle as context for route proposal/training prioritization.",
            "do_not_use_as_proof_label": True,
            "prefer": ["exact-receipt-backed targets", "documented regressions", "counterexample-rich near-cap cases"],
        },
        "keymaster_advisory_context": {
            "use": "Read before next cycle to order exact checks and diversify routes.",
            "do_not_change_truth_semantics": True,
            "avoid": ["repeating documented waste without exploration reason", "treating Spider edge density as evidence", "using unmatched speedup claims"],
        },
        "scientific_firewall": {
            "PIPPI_MIRROR_IS_NOT_PROOF": True,
            "SPIDER_EDGE_IS_NOT_CAUSATION": True,
            "TOPA_FALSIFICATION_REQUIRED_FOR_RELATION_PROMOTION": True,
            "EXACT_JANUS_REPLAY_REMAINS_AUTHORITY": True,
        },
    }
    out["mirror_checkpoint_id"] = stable_hash({k: v for k, v in out.items() if k != "mirror_checkpoint_id"})[:32]
    return out


def self_test() -> None:
    events = [
        {"sequence_no":1,"event_id":"a","event_sha256":"sa","event_type":"BASE","formula_fingerprint":"F","configuration_id":"A","resource_cap":10,"metrics":{},"derived_vs_baseline":{"status":"NO_BASELINE_LINKED"}},
        {"sequence_no":2,"event_id":"b","event_sha256":"sb","event_type":"LEARNING_CHECKPOINT","formula_fingerprint":"F","configuration_id":"B","resource_cap":10,"metrics":{"pair_work":5},"training_cost":{"pair_work":1},"derived_vs_baseline":{"comparable_for_search_gain":True,"pair_work":{"saved":5,"saved_fraction":0.5,"capacity_multiplier":2.0}}},
    ]
    summary={"accounting":{"cumulative_pair_work_saved_where_comparable":5,"cumulative_additional_training_pair_work_recorded":1,"net_pair_work_savings_after_recorded_training_cost":4,"resource_positive_on_recorded_pair_work_horizon":True,"physical_resource_created":False},"plateau_watch":{"status":"INSUFFICIENT_HISTORY"}}
    chunks=chunk_events(events)
    targets=observed_relation_targets(events,summary)
    m=mirror(events,summary,chunks,targets)
    assert len(chunks)==2
    assert m["what_improved"][0]["metric"]=="pair_work"
    assert m["scientific_firewall"]["PIPPI_MIRROR_IS_NOT_PROOF"] is True
    assert m["P_VS_NP"]=="OPEN"


def main() -> int:
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="cmd",required=True)
    sub.add_parser("self-test")
    p=sub.add_parser("build")
    p.add_argument("--journal",type=Path,required=True)
    p.add_argument("--summary",type=Path,required=True)
    p.add_argument("--chunks-out",type=Path,required=True)
    p.add_argument("--relations-out",type=Path,required=True)
    p.add_argument("--mirror-out",type=Path,required=True)
    p.add_argument("--max-events-per-chunk",type=int,default=32)
    a=ap.parse_args()
    if a.cmd=="self-test":
        self_test(); print(json.dumps({"status":"PASS","P_VS_NP":P_VS_NP})); return 0
    events=read_jsonl(a.journal)
    summary=json.loads(a.summary.read_text(encoding="utf-8"))
    chunks=chunk_events(events,a.max_events_per_chunk)
    targets=observed_relation_targets(events,summary)
    mir=mirror(events,summary,chunks,targets)
    write_jsonl(a.chunks_out,chunks)
    a.relations_out.parent.mkdir(parents=True,exist_ok=True)
    a.relations_out.write_text(json.dumps({"schema":"JANUS/PIPPI/SPIDER-RELATION-QUEUE/v1.0.0","status":"ADVISORY","P_VS_NP":P_VS_NP,"targets":targets},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    a.mirror_out.parent.mkdir(parents=True,exist_ok=True)
    a.mirror_out.write_text(json.dumps(mir,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","events":len(events),"chunks":len(chunks),"relations":len(targets),"mirror_checkpoint_id":mir["mirror_checkpoint_id"],"P_VS_NP":P_VS_NP},indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
