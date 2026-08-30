#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRODUCER = HERE / "mk_bceg_r4_producer.py"
VERIFIER = HERE / "mk_bceg_r4_replay_verifier.py"


def load(path):
    return json.loads(Path(path).read_text())


def run(cmd):
    p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        raise RuntimeError(f"command failed: {cmd}\n{p.stdout}\n{p.stderr}")
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    d = Path(args.dir)
    d.mkdir(parents=True, exist_ok=True)
    run([sys.executable, str(PRODUCER), "seed", "--pairs", "4", "--backend-version", "storm-0", "--output", str(d / "package_0.json")])
    run([sys.executable, str(VERIFIER), "verify-package", "--package", str(d / "package_0.json"), "--output", str(d / "receipt_0.json"), "--verifier-release", "storm-verifier-1"])
    p0 = load(d / "package_0.json")
    semantic = p0["semantics_ref"]["semantic_hash"]
    root_anchor = p0["authority_lineage"]["root_anchor_hash"]
    rows = [{
        "step": 0,
        "operation": "SEED_COMPILE",
        "language": p0["language"],
        "package_hash": p0["package_hash"],
        "producer_work_units": p0["paid_costs"]["current_producer_work_units"],
        "verification_work_units": load(d / "receipt_0.json")["verification_work_units"],
        "lineage_depth": 0,
    }]
    previous_language = p0["language"]
    for i in range(1, 7):
        op = "ROBDD_TO_D_DNNF" if i % 2 else "D_DNNF_TO_ROBDD_EXACT_RECOMPILE"
        run([
            sys.executable, str(PRODUCER), "transition",
            "--input", str(d / f"package_{i-1}.json"),
            "--receipt", str(d / f"receipt_{i-1}.json"),
            "--operation", op,
            "--backend-version", f"storm-{i}",
            "--output", str(d / f"package_{i}.json"),
            "--certificate", str(d / f"cert_{i}.json"),
        ])
        run([
            sys.executable, str(VERIFIER), "verify-transition",
            "--input", str(d / f"package_{i-1}.json"),
            "--parent-receipt", str(d / f"receipt_{i-1}.json"),
            "--output-package", str(d / f"package_{i}.json"),
            "--certificate", str(d / f"cert_{i}.json"),
            "--receipt", str(d / f"receipt_{i}.json"),
            "--verifier-release", "storm-verifier-1",
        ])
        pkg = load(d / f"package_{i}.json")
        rec = load(d / f"receipt_{i}.json")
        if pkg["semantics_ref"]["semantic_hash"] != semantic:
            raise RuntimeError(f"switch storm semantic hash drift at step {i}")
        if pkg["authority_lineage"]["root_anchor_hash"] != root_anchor:
            raise RuntimeError(f"switch storm root anchor drift at step {i}")
        if pkg["authority_lineage"]["lineage_depth"] != i:
            raise RuntimeError(f"switch storm lineage depth drift at step {i}")
        if rec["verdict"] != "PASS":
            raise RuntimeError(f"switch storm receipt not PASS at step {i}")
        rows.append({
            "step": i,
            "operation": op,
            "language": pkg["language"],
            "package_hash": pkg["package_hash"],
            "producer_backend_version": pkg["backend"]["release_version"],
            "producer_work_units": pkg["paid_costs"]["current_producer_work_units"],
            "verification_work_units": rec["verification_work_units"],
            "lineage_depth": pkg["authority_lineage"]["lineage_depth"],
            "parent_package_hash": pkg["authority_lineage"]["parent_package_hash"],
            "parent_acceptance_receipt_hash": pkg["authority_lineage"]["parent_acceptance_receipt_hash"],
        })
        previous_language = pkg["language"]
    total_p = sum(int(r["producer_work_units"]) for r in rows)
    total_v = sum(int(r["verification_work_units"]) for r in rows)
    result = {
        "schema": "JANUS/MK_BCEG/R4/SWITCH_STORM_RESULT/v1.0",
        "status": "COMPLETE",
        "verdict": "FINITE_SWITCH_STORM_SURVIVOR_NOT_THEOREM",
        "steps": 6,
        "packages": 7,
        "rows": rows,
        "semantic_hash_constant": semantic,
        "root_anchor_hash_constant": root_anchor,
        "total_switch_producer_work_units_including_seed": total_p,
        "total_independent_verification_work_units_including_seed": total_v,
        "total_paid_work_units": total_p + total_v,
        "all_lineage_depths_exact": all(r["lineage_depth"] == r["step"] for r in rows),
        "all_switches_receipt_gated": True,
        "note":"D_DNNF_TO_ROBDD_EXACT_RECOMPILE is intentionally charged as recompilation from embedded exact CNF semantics, not misreported as a free direct representation translation.",
        "universal_polynomial_switching_proved": False,
        "P_VS_NP": "OPEN",
    }
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": result["verdict"], "total_producer": total_p, "total_verifier": total_v, "total_paid": total_p + total_v}, indent=2))


if __name__ == "__main__":
    main()
