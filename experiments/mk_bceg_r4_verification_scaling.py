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
    root = Path(args.dir)
    root.mkdir(parents=True, exist_ok=True)
    rows = []
    for pairs in [2, 3, 4, 5, 6, 7, 8]:
        d = root / f"pairs_{pairs}"
        d.mkdir(parents=True, exist_ok=True)
        pkg = d / "package.json"
        receipt = d / "receipt.json"
        run([sys.executable, str(PRODUCER), "seed", "--pairs", str(pairs), "--backend-version", "scale-1.0", "--output", str(pkg)])
        run([sys.executable, str(VERIFIER), "verify-package", "--package", str(pkg), "--output", str(receipt), "--verifier-release", "scale-1.0"])
        p = load(pkg)
        r = load(receipt)
        n = 2 * pairs
        expected = 1 << n
        if r["semantic_assignments_checked"] != expected:
            raise RuntimeError(f"scale rung {pairs}: expected {expected} exact assignments, got {r['semantic_assignments_checked']}")
        producer = int(p["paid_costs"]["current_producer_work_units"])
        verifier = int(r["verification_work_units"])
        rows.append({
            "pairs": pairs,
            "variables": n,
            "producer_work_units": producer,
            "verification_work_units": verifier,
            "semantic_assignments_checked": expected,
            "verification_to_producer_ratio": {"numerator": verifier, "denominator": producer},
            "package_bytes": pkg.stat().st_size,
            "receipt_bytes": receipt.stat().st_size,
        })
    exact_enumeration = all(row["semantic_assignments_checked"] == (1 << row["variables"]) for row in rows)
    result = {
        "schema": "JANUS/MK_BCEG/R4/VERIFICATION_SCALING_RESULT/v1.0",
        "status": "COMPLETE",
        "verdict": "BACKEND_VERIFICATION_COMPLEXITY_BARRIER" if exact_enumeration else "SCALING_MEASUREMENT_INCONSISTENT",
        "rows": rows,
        "backend_algorithm_fact": "The frozen R4 exact-fallback verifier explicitly enumerates every assignment of active variables; therefore this verifier performs 2^n semantic assignment checks by construction. This is a backend-algorithm complexity statement, not a lower bound for all possible verifiers or a theorem about the representation language.",
        "finite_measurements_are_language_theorem": False,
        "producer_polynomial_from_rows_proved": False,
        "portable_polynomial_verification_proved": False,
        "P_VS_NP": "OPEN",
    }
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": result["verdict"], "rows": [{"n":r["variables"], "P":r["producer_work_units"], "V":r["verification_work_units"], "checked":r["semantic_assignments_checked"]} for r in rows]}, indent=2))
    if not exact_enumeration:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
