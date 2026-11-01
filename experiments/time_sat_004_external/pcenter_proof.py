#!/usr/bin/env python3
"""Probe original SAT Competition 2026 P-center UNSAT under independent DRUP.

Pinned original GBD download SHA256 is from FIRST exact TLS acquisition, not
a SHA signed by GBD. This proves an externally originated public formula
UNSAT only if Glucose DRUP checks against original unchanged CNF. The producer
and the independent Boolean checker are still under SAME JANUS GitHub trust.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import resource
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"direct"))
from janus_time_sat_004b_acquire import retrieve,unpack_bounded,scan_dimacs
from janus_time_sat_004b_baselines import read_cnf
from janus_time_sat_003_drup_witness import produce_and_check

CANDIDATE={
 "hash":"011984fd82d62d609e776fbf5de75440",
 "official_uri":"http://benchmark-database.de/file/011984fd82d62d609e776fbf5de75440"
}
PINNED_ORIGINAL="fa3549a5f3dd4fbd31a2ac6ccecd6a72f5a6bb5f71212d15257d3f00ab7c8d23"
PINNED_DECODED="0542d88497b5a7ef610e30a570e8be9088bdb343e4b54d31561b5ae47bfa906b"


def main():
    out=Path("evidence/time_sat_004b_pcenter");out.mkdir(parents=True,exist_ok=True)
    resource.setrlimit(resource.RLIMIT_AS,(2_147_483_648,2_147_483_648))
    fetched,source=retrieve(CANDIDATE,out)
    if source["source_sha256"]!=PINNED_ORIGINAL:
        raise AssertionError("GBD ORIGINAL SHA256 differs from preregistered first observation")
    decoded=out/"011984fd82d62d609e776fbf5de75440.original.cnf"
    unpack=unpack_bounded(fetched,decoded)
    if unpack["uncompressed_sha256"]!=PINNED_DECODED:
        raise AssertionError("decoded CNF SHA differs from first original acquisition")
    structure=scan_dimacs(decoded)
    if (structure["n_variables"],structure["n_clauses"])!=(2320,8620):
        raise AssertionError("source DIMACS bounds do not match original baseline")
    clauses=read_cnf(decoded,2320,8620)
    start=time.monotonic()
    outcome=produce_and_check(clauses,timeout_seconds=12)
    status=outcome.get("proof_status","UNKNOWN")
    records={
        "schema":"JANUS-TIME-SAT-004B-PCENTER-ORIGINAL-CNF-DRUP-REPLAY-V1",
        "source_id":CANDIDATE["hash"],
        "source_original_TLSSHA256":PINNED_ORIGINAL,
        "source_decoded_CNF_SHA256":PINNED_DECODED,
        "source_label_organizer":"unknown",
        "source_sha_matches_first_pilot":True,
        "source_cnf":structure,
        "drup_checker_status":status,
        "solver_result":outcome.get("solver_status"),
        "elapsed_total_proof_seconds":time.monotonic()-start,
        "separate_verifier": "janus_time_sat_003_drup_witness.py; no solver API while replaying",
        "external_admin_independence":"NOT_ESTABLISHED_SAME_GITHUB",
        "actual_proof_lines":outcome.get("raw_drup_lines"),
        "source_and_proof_digest":outcome.get("certificate_sha256"),
        "research_only":True,
        "original_C023_main":"UNCHANGED"
    }
    (out/"pcenter_replay.json").write_text(json.dumps(records,indent=2,sort_keys=True)+"\n")
    print("PCENTER_RESULT",json.dumps({k:records[k] for k in (
        "drup_checker_status","solver_result","source_and_proof_digest",
        "elapsed_total_proof_seconds","external_admin_independence"
    )},sort_keys=True),flush=True)
    if status!="INDEPENDENT_RUP_REPLAY_PASS":
        raise AssertionError("P-center UNSAT remains unverified: "+str(outcome))


if __name__=="__main__":main()
