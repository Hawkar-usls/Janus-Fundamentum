#!/usr/bin/env python3
"""Emit PACE incidence graphs and summarize externally generated tree decompositions.

This harness contains no treewidth algorithm. It only:
  * converts frozen CNF residuals into incidence graphs (.gr),
  * parses PACE .td headers,
  * records external validator results,
  * emits a source-bound JSON receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def canonical_hash(obj):
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def emit(input_json: Path, out_dir: Path):
    data = json.loads(input_json.read_text(encoding="utf-8"))
    rows = data["residuals"]
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for i, row in enumerate(rows):
        clauses = row["residual_formula"]
        variables = sorted({abs(lit) for clause in clauses for lit in clause})
        vmap = {v: j + 1 for j, v in enumerate(variables)}
        nv = len(variables)
        edges = []
        for ci, clause in enumerate(clauses, start=1):
            cnode = nv + ci
            for v in sorted({abs(lit) for lit in clause}):
                edges.append((vmap[v], cnode))
        graph_path = out_dir / f"r50g25x_{i:02d}.gr"
        with graph_path.open("w", encoding="ascii") as f:
            f.write(f"c R50G25X index {i} residual {row['residual_hash']}\n")
            f.write(f"p tw {nv + len(clauses)} {len(edges)}\n")
            for a, b in edges:
                f.write(f"{a} {b}\n")
        manifest.append({
            "index": i,
            "family": row["family"],
            "residual_hash": row["residual_hash"],
            "CLV": row["residual_CLV"],
            "formula_canonical_sha256": canonical_hash(clauses),
            "original_variable_ids": variables,
            "graph_file": graph_path.name,
            "incidence_vertices": nv + len(clauses),
            "incidence_edges": len(edges),
            "variable_vertices": nv,
            "clause_vertices": len(clauses),
        })
    mpath = out_dir / "manifest.json"
    mpath.write_text(json.dumps({
        "schema": "janus.trump.r50g25x.pace_incidence_manifest.v1",
        "source_artifact_id": 9992845123,
        "source_run_id": 34044941068,
        "rows": manifest,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_td(path: Path):
    if not path.exists() or path.stat().st_size == 0:
        return None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("c"):
            continue
        parts = line.split()
        if len(parts) >= 5 and parts[0] == "s" and parts[1] == "td":
            nbags = int(parts[2])
            max_bag_size = int(parts[3])
            graph_n = int(parts[4])
            return {
                "nbags": nbags,
                "max_bag_size": max_bag_size,
                "width": max_bag_size - 1,
                "graph_n": graph_n,
            }
    return None


def summarize(graph_dir: Path, td_dir: Path, validation_dir: Path, output: Path,
              flow_commit: str, validator_commit: str):
    manifest = json.loads((graph_dir / "manifest.json").read_text(encoding="utf-8"))
    rows = []
    for row in manifest["rows"]:
        i = row["index"]
        td_path = td_dir / f"r50g25x_{i:02d}.td"
        status_path = validation_dir / f"r50g25x_{i:02d}.status"
        log_path = validation_dir / f"r50g25x_{i:02d}.log"
        parsed = parse_td(td_path)
        validation_status = status_path.read_text().strip() if status_path.exists() else "MISSING"
        rows.append({
            **row,
            "td_file": td_path.name,
            "td_sha256": hashlib.sha256(td_path.read_bytes()).hexdigest() if td_path.exists() else None,
            "td_header": parsed,
            "external_td_validate": validation_status,
            "validator_log": log_path.read_text(encoding="utf-8", errors="replace")[-4000:] if log_path.exists() else "",
        })
    valid = [r for r in rows if r["external_td_validate"] == "PASS" and r["td_header"]]
    output.write_text(json.dumps({
        "schema": "janus.trump.r50g25x.external_incidence_treewidth_flowcutter.v1",
        "authority": "EXTERNAL_PUBLIC_TD_FINDER_PLUS_EXTERNAL_PUBLIC_VALIDATOR__FINITE_CORPUS_ONLY",
        "source_artifact_id": 9992845123,
        "source_run_id": 34044941068,
        "external_tools": {
            "flowcutter_repo": "kit-algo/flow-cutter-pace17",
            "flowcutter_commit": flow_commit,
            "td_validate_repo": "holgerdell/td-validate",
            "td_validate_commit": validator_commit,
        },
        "rows": rows,
        "validated_count": len(valid),
        "validated_widths": [r["td_header"]["width"] for r in valid],
        "claim_ceiling": {
            "minimum_treewidth": "NOT_CLAIMED",
            "asymptotic_O_log_n_bound": "NOT_ESTABLISHED",
            "general_sat_in_p": "NOT_PROVED",
            "p_vs_np": "OPEN",
        },
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("emit")
    a.add_argument("input")
    a.add_argument("out_dir")
    b = sub.add_parser("summarize")
    b.add_argument("graph_dir")
    b.add_argument("td_dir")
    b.add_argument("validation_dir")
    b.add_argument("output")
    b.add_argument("--flow-commit", required=True)
    b.add_argument("--validator-commit", required=True)
    ns = ap.parse_args()
    if ns.cmd == "emit":
        emit(Path(ns.input), Path(ns.out_dir))
    else:
        summarize(Path(ns.graph_dir), Path(ns.td_dir), Path(ns.validation_dir),
                  Path(ns.output), ns.flow_commit, ns.validator_commit)


if __name__ == "__main__":
    main()
