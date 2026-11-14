#!/usr/bin/env python3
"""Conservative cross-runner UFR promotion gate; never edits production code.

Intentionally exits nonzero when improvement has NOT been demonstrated.
All checks are tied to the same PR merge SHA and at least two distinct
GitHub-hosted Linux images, with independent fresh subprocess measurements.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import statistics
import sys


def evaluate(files: list[Path]) -> dict:
    failures: list[str] = []
    evidence: list[dict] = []
    for file in files:
        try:
            row = json.loads(file.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            failures.append(f"{file}: invalid evidence {error}")
            continue
        evidence.append(row)
    if len(evidence) != 2:
        failures.append("require exactly two independent runner evidence files")
    labels = [row.get("source", {}).get("os_label") for row in evidence]
    shas = [row.get("source", {}).get("head_sha") for row in evidence]
    if len(set(labels)) != 2 or any(not label for label in labels):
        failures.append("runner OS labels must be distinct, e.g. ubuntu-22.04/24.04")
    if len(set(shas)) != 1 or any(not sha for sha in shas):
        failures.append("both machines must test the same exact commit")
    for row in evidence:
        machine = row.get("source", {}).get("os_label")
        if row.get("schema") != "JANUS-UFR-PAIRED-RSS-V2":
            failures.append(f"{machine}: unexpected evidence schema")
            continue
        rounds = row.get("repetitions", 0)
        pairs = row.get("pairs", [])
        main = [x for x in pairs if x.get("fixture") == "MAJ3_K4"]
        controls = [x for x in pairs if x.get("fixture") != "MAJ3_K4"]
        if rounds < 3 or len(main) != rounds or len(controls) != 4:
            failures.append(f"{machine}: insufficient preregistered repetitions/controls")
            continue
        for item in pairs:
            name = item["fixture"]
            original, ufr = item["baseline"], item["ufr"]
            if original["status"] != "PASS_REPLAY" or ufr["status"] != "PASS_REPLAY":
                failures.append(f"{machine}/{name}: certificate replay not passed")
            if (original.get("certificate_accounting") != "BOTH_SERIALIZED_INDEPENDENT_REPLAY"
                    or ufr.get("certificate_accounting") != "BOTH_SERIALIZED_INDEPENDENT_REPLAY"):
                failures.append(f"{machine}/{name}: asymmetric proof-accounting methodology")
            if original["answer"] != ufr["answer"] or type(ufr["answer"]) is not bool:
                failures.append(f"{machine}/{name}: Boolean result mismatch")
            if name == "MAJ3_K4" and (
                ufr["isomorphic_cache_hits"] < 165 or
                ufr["unique_states"] > 2354 or original["unique_states"] != 2427
            ):
                failures.append(f"{machine}: MAJ3 state/165-hit regression")
            ratios = (item.get("solve_ratio"), item.get("end_to_end_ratio"),
                      item.get("rss_ratio"))
            if any(type(value) not in (int, float) or not math.isfinite(value)
                   or value <= 0 for value in ratios):
                failures.append(f"{machine}/{name}: nonfinite or invalid ratio")
                continue
            if ufr["peak_rss_bytes"] <= 0 or original["peak_rss_bytes"] <= 0:
                failures.append(f"{machine}/{name}: invalid RSS")
        if len(main) == rounds:
            solve = statistics.median(x["solve_ratio"] for x in main)
            total = statistics.median(x["end_to_end_ratio"] for x in main)
            rss = statistics.median(x["rss_ratio"] for x in main)
            # Conservative repeatability and resource requirements.
            if solve > 0.97:
                failures.append(f"{machine}: MAJ3 median solver time ratio {solve:.4f} > 0.97")
            if total > 0.97:
                failures.append(f"{machine}: MAJ3 median solve+proof ratio {total:.4f} > 0.97")
            if rss > 1.00:
                failures.append(f"{machine}: MAJ3 median peak RSS ratio {rss:.4f} > 1.00")
            if max(x["solve_ratio"] for x in main) > 1.05:
                failures.append(f"{machine}: at least one MAJ3 replicate >5% slower")
            if max(x["rss_ratio"] for x in main) > 1.05:
                failures.append(f"{machine}: at least one MAJ3 replicate >5% more RSS")
        # Short (<20ms) cases are noisy; allow only small absolute regressions.
        for x in controls:
            a, b = x["baseline"]["wall_seconds"], x["ufr"]["wall_seconds"]
            if b > a * 1.15 + 0.010:
                failures.append(f"{machine}/{x['fixture']}: control regression {a:.4f}->{b:.4f}")
    return {
        "schema": "JANUS-UFR-PROMOTION-GATE-001",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "READY_FOR_HUMAN_REVIEW" if not failures else "NOT_READY",
        "promotion_authorized_automatically": False,
        "runner_images": labels,
        "tested_shas": shas,
        "failures": failures,
        "summary": {str(row.get("source", {}).get("os_label")): row.get("summary")
                    for row in evidence},
        "caveat": "Necessary evidence gate, not asymptotic theorem or permission to bypass protected-branch review. Production C023 remains unchanged.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, default=Path("ufr-promotion-gate.json"))
    args = parser.parse_args()
    verdict = evaluate(args.files)
    args.out.write_text(json.dumps(verdict, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(verdict, indent=2))
    md = ["## JANUS-UFR-001 independent promotion gate",
          f"**Decision:** {verdict['decision']}",
          f"**Runner images:** {', '.join(map(str, verdict['runner_images']))}",
          f"**Test SHA:** {verdict['tested_shas']}",
          "Production C023 untouched. No automatic merge."]
    md += [f"- {item}" for item in verdict["failures"]]
    Path("ufr-gate-summary.md").write_text("\n\n".join(md) + "\n", encoding="utf-8")
    if verdict["decision"] != "READY_FOR_HUMAN_REVIEW":
        sys.exit(1)


if __name__ == "__main__":
    main()
