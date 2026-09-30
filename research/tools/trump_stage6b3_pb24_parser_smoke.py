#!/usr/bin/env python3
"""Stage6B.3 PB24 parser smoke harness.

This run has NO scientific boundary authority. It exists only to prove that the
pinned RoundingSat binary accepts the repaired PB24 wire format and reaches
normal solving before the 13 authority-eligible boundary runs are launched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

PARSER_REJECTION_PATTERNS = [
    re.compile(r"invalid\s+opb\s+header", re.I),
    re.compile(r"invalid\s+opb", re.I),
    re.compile(r"opb.*parse", re.I),
    re.compile(r"parse.*opb", re.I),
    re.compile(r"unsupported.*opb", re.I),
    re.compile(r"unsupported.*format", re.I),
]
UNSAT_RE = re.compile(r"\bUNSAT(?:ISFIABLE)?\b", re.I)
SAT_RE = re.compile(r"\bSAT(?:ISFIABLE)?\b", re.I)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify(text: str) -> str:
    if UNSAT_RE.search(text):
        return "UNSAT"
    if SAT_RE.search(text):
        return "SAT"
    return "NO_FINAL_STATUS"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roundingsat")
    ap.add_argument("opb")
    ap.add_argument("outdir")
    ap.add_argument("--timeout-seconds", type=int, default=5)
    ns = ap.parse_args()

    binary = Path(ns.roundingsat)
    opb = Path(ns.opb)
    outdir = Path(ns.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stdoutp = outdir / "parser_smoke.stdout"
    stderrp = outdir / "parser_smoke.stderr"

    cmd = [str(binary), "--print-sol=0", "--lp=0", str(opb)]
    t0 = time.perf_counter()
    try:
        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=ns.timeout_seconds,
            check=False,
        )
        timed_out = False
        code = p.returncode
        out = p.stdout
        err = p.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        code = None
        out = exc.stdout or ""
        err = exc.stderr or ""
        if isinstance(out, bytes):
            out = out.decode(errors="replace")
        if isinstance(err, bytes):
            err = err.decode(errors="replace")

    runtime = time.perf_counter() - t0
    stdoutp.write_text(out, encoding="utf-8")
    stderrp.write_text(err, encoding="utf-8")
    combined = out + "\n" + err

    rejection_markers = [
        pattern.pattern
        for pattern in PARSER_REJECTION_PATTERNS
        if pattern.search(combined)
    ]
    final_status = classify(combined)

    parser_accepted = (
        not rejection_markers
        and (
            timed_out
            or final_status in ("SAT", "UNSAT")
            or code in (0, 10, 20)
        )
    )

    receipt = {
        "schema": "janus.trump.stage6b3.pb24_parser_smoke_receipt.v1",
        "authority": "FORMAT_SMOKE_ONLY__NO_SCIENTIFIC_BOUNDARY_AUTHORITY",
        "scientific_authority": False,
        "binary_sha256": sha(binary),
        "OPB_sha256": sha(opb),
        "execution_command": cmd,
        "runtime_limit_seconds": ns.timeout_seconds,
        "runtime_seconds": runtime,
        "exit_code": code,
        "timed_out": timed_out,
        "observed_final_status": final_status,
        "parser_rejection_markers": rejection_markers,
        "parser_accepted": parser_accepted,
        "normal_solving_entered": parser_accepted,
        "status": "PARSER_SMOKE_PASS" if parser_accepted else "INFRASTRUCTURE_ERROR",
        "stdout_sha256": sha(stdoutp),
        "stderr_sha256": sha(stderrp),
    }
    rp = outdir / "parser_smoke.receipt.json"
    rp.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": receipt["status"],
        "parser_accepted": parser_accepted,
        "timed_out": timed_out,
        "exit_code": code,
        "observed_final_status": final_status,
        "parser_rejection_markers": rejection_markers,
    }, sort_keys=True))
    if not parser_accepted:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
