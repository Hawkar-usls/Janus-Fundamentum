#!/usr/bin/env python3
"""JANUS E12C4: bounded, state-driven INTERNAL DEVELOPMENT (never held-out).

A scheduled main-branch dispatcher launches this on public GitHub ephemeral
workers only. Every cycle derives a fresh development original from a monotonic
cycle number, benchmarks all registered controls cold, and emits immutable
receipts. It NEVER benchmarks fixed E12C4 HOLDOUT seeds, auto-merges or promotes.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import resource
import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from time import perf_counter, process_time

import janus_time_sat_004e12c4_profit_aware_dev as e

ARMS = ("raw_cms", "certified_native", "selected_dev", "cadical195")
MAX_CYCLES = 500
CPU_LIMIT = 12
WALL_LIMIT = 18
MEM_LIMIT = 2147483648
SOURCE_STATE_SCHEMA = "JANUS-E12C4-AUTOPILOT-STATE-V1"
RECEIPT_SCHEMA = "JANUS-E12C4-AUTOPILOT-CYCLE-V1"
SAT = "SAT_VERIFIED"
UNSAT = "UNSAT_INTERNAL_EXHAUSTIVE_ONLY"
UNKNOWN = {"UNKNOWN_CPU_LIMIT", "UNKNOWN_WALL_LIMIT", "UNKNOWN_NO_ANSWER"}

def sha(data):
    return sha256(data).hexdigest()

def encoded(v):
    return (json.dumps(v, sort_keys=True, separators=(",", ":")) + "\n").encode()

def source_for_cycle(index):
    if type(index) is not int or not (0 <= index < MAX_CYCLES):
        raise ValueError("Outside explicitly bounded development cycles")
    if index < len(e.DEVELOPMENT):
        family, seed = e.DEVELOPMENT[index]
    else:
        family = e.FAMILIES[index % len(e.FAMILIES)]
        seed = 202611070000 + index * 1009
    if (family, seed) in e.HOLDOUT:
        raise AssertionError("Attempted held-out source")
    return family, seed

def trained_from_past(state):
    base = e.fit_archived_e12c3()
    past = []
    for record in state["history"]:
        if record.get("cycle_status") != "COMPLETE":
            continue
        if len(record.get("paired_full_cold", [])) != len(e.VARIANTS):
            raise AssertionError("Incomplete old development source pairs")
        past.append({"original_sha256": record["original_sha256"],
                     "features": record["features"],
                     "paired_full_cold": record["paired_full_cold"]})
    if past:
        new = e.fit_development(past, forbidden_source_shas={
            e.generate(f, s)["original_sha256"] for f, s in e.HOLDOUT})
        known = {p["original_sha256"] for p in base["profiles"]}
        for p in new["profiles"]:
            if p["original_sha256"] in known:
                raise AssertionError("Archived C3 training duplicates new original")
            known.add(p["original_sha256"])
            base["profiles"].append(p)
    if len(base["profiles"]) != len(set(p["original_sha256"] for p in base["profiles"])):
        raise AssertionError("Training original SHA not independent")
    return base

def cold_child(args):
    # Linux hosted ephemeral runner, never run on local owner machines.
    resource.setrlimit(resource.RLIMIT_AS, (MEM_LIMIT, MEM_LIMIT))
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_LIMIT, CPU_LIMIT + 1))
    start = perf_counter()
    cpu_start = process_time()
    src = e.generate(args.family, args.seed)
    s = e.transform(src, args.variant)
    if (src["original_sha256"] != args.original_sha or
        s["variant_sha256"] != args.variant_sha):
        raise AssertionError("Frozen original/variant CNF SHA mismatch")
    if s["status_by_construction"] == "SAT":
        if not e._model_ok(s["rows"], s["model"]):
            raise AssertionError("Bad original model")
    else:
        if e.independent_truth_table(s["rows"], s["n"]) != "INTERNAL_EXHAUSTIVE_UNSAT_VERIFIED":
            raise AssertionError("UNSAT source not independently exhaustive")
    fit = json.loads(Path(args.fit_path).read_text())
    if sha(encoded(fit)) != args.fit_sha or fit["schema"] != e.SCHEMA + "-DEV-FIT":
        raise AssertionError("Development model SHA mismatch")

    t = perf_counter()
    if args.arm == "certified_native":
        idx = e.c1.source_index_all_widths(s["rows"], s["n"])
        selected = [x for x in idx["equations"] if x["width"] in (5, 6)]
        residual = e._proof_and_residual(s["rows"], s["n"], selected)
        decision = "CERTIFIED_SOURCE_NATIVE"
    elif args.arm == "selected_dev":
        decision_result = e.choose(s["rows"], s["n"], fitted=fit)
        selected = decision_result["equations"]
        residual = decision_result["cnf_clauses"]
        decision = decision_result["decision"]
    else:
        selected, residual, decision = [], s["rows"], "RAW_ORIGINAL"
    analysis_s = perf_counter() - t
    if selected:
        # Defense in depth: a second exact-source proof before native solver.
        assert residual == e._proof_and_residual(s["rows"], s["n"], selected)
    t = perf_counter()
    if args.arm == "cadical195":
        from pysat.solvers import Solver
        solver = Solver(name="cadical195", bootstrap_with=s["rows"])
        setup_s = perf_counter() - t
        with solver:
            t = perf_counter()
            solved = solver.solve()
            solver_s = perf_counter() - t
            model = solver.get_model() if solved is True else None
    else:
        import pycryptosat
        solver = pycryptosat.Solver(threads=1)
        for eq in selected:
            solver.add_xor_clause(eq["variables"], bool(eq["rhs"]))
        for row in residual:
            solver.add_clause(row)
        setup_s = perf_counter() - t
        t = perf_counter()
        solved, assignment = solver.solve()
        solver_s = perf_counter() - t
        model = ([i if bool(assignment[i]) else -i for i in range(1, s["n"] + 1)]
                 if solved is True and assignment is not None else None)
    t = perf_counter()
    if solved is True:
        if not model or not e._model_ok(s["rows"], model) or s["status_by_construction"] != "SAT":
            raise AssertionError("False SAT output on original CNF")
        status = SAT
    elif solved is False:
        if s["status_by_construction"] != "UNSAT" or e.independent_truth_table(
                s["rows"], s["n"]) != "INTERNAL_EXHAUSTIVE_UNSAT_VERIFIED":
            raise AssertionError("UNSAT on satisfiable original source or no independent truth-table")
        status = UNSAT  # NOT a general independently checked portable UNSAT proof.
    else:
        status = "UNKNOWN_NO_ANSWER"
    replay_s = perf_counter() - t
    result = {"status": status, "variant": args.variant, "arm": args.arm,
              "original_sha256": src["original_sha256"],
              "variant_sha256": s["variant_sha256"], "fit_sha256": args.fit_sha,
              "decision": decision, "native_equations": len(selected),
              "analysis_wall_s": analysis_s, "setup_wall_s": setup_s,
              "solver_wall_s": solver_s, "original_replay_wall_s": replay_s,
              "inner_full_cold_wall_s": perf_counter() - start,
              "cpu_s": process_time() - cpu_start,
              "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    print(json.dumps(result, sort_keys=True))

def loop(args):
    source_state_bytes = Path(args.state).read_bytes()
    state = json.loads(source_state_bytes)
    if state.get("schema") != SOURCE_STATE_SCHEMA:
        raise AssertionError("Wrong persistent state schema")
    run_id = str(os.environ.get("GITHUB_RUN_ID", "LOCAL_" + str(os.getpid())))
    stamp = {"schema": RECEIPT_SCHEMA, "run_id": run_id,
             "previous_state_sha256": sha(source_state_bytes),
             "cycle_index": state["next_cycle"],
             "cycle_status": "INTERNAL_ERROR",
             "main_C023": "UNCHANGED", "promotion": "PROHIBITED",
             "heldout_sources_timed": 0,
             "external_proof_verifier": False,
             "worker": "GITHUB_HOSTED_PUBLIC_ONLY",
             "cpu_child_limit_s": CPU_LIMIT, "wall_child_limit_s": WALL_LIMIT,
             "address_space_bytes": MEM_LIMIT}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    report = out / "REPORT.json"
    if run_id in state.get("completed_run_ids", []):
        stamp["cycle_status"] = "SKIPPED_DUPLICATE_RUN"
    elif state.get("mode") != "DEVELOPMENT_ONLY":
        stamp["cycle_status"] = "SKIPPED_PAUSED"
    elif state["next_cycle"] >= MAX_CYCLES:
        stamp["cycle_status"] = "PAUSED_BUDGET_LIMIT"
    else:
        i = state["next_cycle"]
        family, seed = source_for_cycle(i)
        src = e.generate(family, seed)
        if src["original_sha256"] in {z["original_sha256"] for z in state["history"]}:
            raise AssertionError("Duplicate development original SHA")
        holdout_shas = {e.generate(f, s)["original_sha256"] for f, s in e.HOLDOUT}
        if src["original_sha256"] in holdout_shas:
            raise AssertionError("Frozen held-out original SHA must not be benchmarked")
        model = trained_from_past(state)
        model_file = out / "FIT.json"
        model_file.write_bytes(encoded(model))
        fit_sha = sha(model_file.read_bytes())
        stamp.update({"family": family, "seed": seed, "n": src["n"],
            "m": len(src["rows"]), "original_sha256": src["original_sha256"],
            "original_model_sha256": src["model_sha256"], "fit_sha256": fit_sha,
            "features": e.features(src["rows"], src["n"], [
                x for x in e.c1.source_index_all_widths(src["rows"], src["n"])["equations"]
                if x["width"] in (5, 6)]),
            "source_code_sha": os.environ.get("E12C4_RESEARCH_SHA", "LOCAL"),
            "original_status_by_construction": src["status_by_construction"]})
        records = []
        for variant in e.VARIANTS:
            transformed = e.transform(src, variant)
            for arm in ARMS:
                command = [sys.executable, str(Path(__file__).resolve()),
                    "--child", "--family", family, "--seed", str(seed),
                    "--variant", variant, "--arm", arm,
                    "--original-sha", src["original_sha256"],
                    "--variant-sha", transformed["variant_sha256"],
                    "--fit-sha", fit_sha, "--fit-path", str(model_file.resolve())]
                started = perf_counter()
                try:
                    proc = subprocess.run(command, capture_output=True, text=True,
                                          timeout=WALL_LIMIT, check=False)
                    if proc.returncode == 0:
                        outcome = json.loads(proc.stdout)
                        if (outcome["original_sha256"] != src["original_sha256"] or
                            outcome["variant_sha256"] != transformed["variant_sha256"] or
                            outcome["arm"] != arm):
                            raise AssertionError("Cold solver receipt source/arm drift")
                    elif proc.returncode < 0 and -proc.returncode in (24, 9):
                        outcome = {"status": "UNKNOWN_CPU_LIMIT", "signal": -proc.returncode}
                    else:
                        outcome = {"status": "ERROR_CHILD",
                                   "exit_code": proc.returncode,
                                   "stderr_tail": proc.stderr[-1000:]}
                except subprocess.TimeoutExpired:
                    outcome = {"status": "UNKNOWN_WALL_LIMIT"}
                except Exception as exc:
                    outcome = {"status": "ERROR_CHILD", "error": str(exc)[:400]}
                records.append({"variant": variant, "arm": arm,
                    "full_cold_child_wall_s": perf_counter() - started, "outcome": outcome})
        stamp["records"] = records
        choices = {r["outcome"].get("decision") for r in records
                   if r["arm"] == "selected_dev"}
        failures = [r for r in records if r["outcome"]["status"] not in
                    {SAT, UNSAT, *UNKNOWN}]
        if failures or len(choices) > 1:
            stamp["cycle_status"] = "PAUSED_SAFETY_FAILURE"
            stamp["safety_failures"] = len(failures)
            stamp["decision_isomorphism_flip"] = len(choices) > 1
        else:
            pairs = []
            for variant in e.VARIANTS:
                pair = {r["arm"]: r for r in records if r["variant"] == variant}
                a, b = pair["raw_cms"], pair["certified_native"]
                pairs.append({
                    "raw_status": "VERIFIED" if a["outcome"]["status"] == SAT else "UNKNOWN",
                    "xor_status": "VERIFIED" if b["outcome"]["status"] == SAT else "UNKNOWN",
                    "raw_s": a["full_cold_child_wall_s"],
                    "xor_s": b["full_cold_child_wall_s"]})
            stamp["paired_full_cold"] = pairs
            stamp["cycle_status"] = "COMPLETE"
    report.write_bytes((json.dumps(stamp, indent=2, sort_keys=True) + "\n").encode())
    print("JANUS_E12C4_CYCLE", stamp["cycle_index"], stamp["cycle_status"],
          "sha256", sha(report.read_bytes()), flush=True)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--state", type=Path)
    p.add_argument("--out", type=Path)
    p.add_argument("--child", action="store_true")
    p.add_argument("--family")
    p.add_argument("--seed", type=int)
    p.add_argument("--variant", choices=e.VARIANTS)
    p.add_argument("--arm", choices=ARMS)
    p.add_argument("--original-sha")
    p.add_argument("--variant-sha")
    p.add_argument("--fit-sha")
    p.add_argument("--fit-path")
    q = p.parse_args()
    if q.child:
        cold_child(q)
    else:
        if not q.state or not q.out:
            p.error("--state and --out are required")
        loop(q)
