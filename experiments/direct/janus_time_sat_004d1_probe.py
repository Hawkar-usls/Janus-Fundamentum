#!/usr/bin/env python3
"""004D1: bounded real-origin source-only GF(2) diagnostic, NO CDCL solves.

Fetches exactly the two previously SHA-frozen 004D0 public SATComp CNFs,
verifies original transfer/decoded SHA and DIMACS counts before inspection.
A full XOR cover yields an independently checked original-CNF SAT model or
a same-admin algebraic contradiction receipt; incomplete cover ABSTAINS.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import resource
import subprocess
from time import perf_counter

from janus_time_sat_004b_acquire import retrieve,unpack_bounded,scan_dimacs
from janus_time_sat_004b_baselines import read_cnf
from janus_time_sat_004d_pilot import FROZEN_SHA,EXPECTED_PREREG_GIT_BLOB
from janus_time_sat_004d1_xor import solve_if_exact_xor

def run(out:Path):
    resource.setrlimit(resource.RLIMIT_AS,(2_147_483_648,2_147_483_648))
    resource.setrlimit(resource.RLIMIT_CPU,(15,16))
    prereg=Path("experiments/time_sat_004_external/PREREGISTERED_SATCOMP2026_PILOT_20261101.json")
    checked=subprocess.run(["git","hash-object",str(prereg)],text=True,
                            capture_output=True,check=True).stdout.strip()
    if checked!=EXPECTED_PREREG_GIT_BLOB:
        raise AssertionError("preregistered source selection SHA mismatch")
    candidates=json.loads(prereg.read_text())["candidates"]
    out.mkdir(parents=True,exist_ok=True)
    cases=[]
    for candidate in candidates:
        lookup=FROZEN_SHA.get(candidate["hash"])
        if lookup is None:continue
        start=perf_counter()
        original,metadata=retrieve(candidate,out)
        if metadata["source_sha256"]!=lookup["original"]:
            raise AssertionError("original competition compressed SHA changed")
        decoded=out/(candidate["hash"]+".cnf")
        decoded_receipt=unpack_bounded(original,decoded)
        if decoded_receipt["uncompressed_sha256"]!=lookup["decoded"]:
            raise AssertionError("original competition decoded SHA changed")
        dimensions=scan_dimacs(decoded)
        if (dimensions["n_variables"],dimensions["n_clauses"])!=(
                lookup["n"],lookup["m"]):
            raise AssertionError("original source dimensions mismatch")
        source=read_cnf(decoded,lookup["n"],lookup["m"])
        before=perf_counter()
        exact=solve_if_exact_xor(source,lookup["n"])
        compute_s=perf_counter()-before
        if exact["verdict"]=="SAT_ORIGINAL_MODEL_VERIFIED":
            if len(exact["model"])!=lookup["n"]:
                raise AssertionError("SAT model missing variables")
        cases.append({
            "family":lookup["family"],"gbd_id_NOT_sha256":candidate["hash"],
            "original_transfer_sha256":metadata["source_sha256"],
            "original_decoded_sha256":decoded_receipt["uncompressed_sha256"],
            "dimensions":dimensions,
            "xor_certificate":exact,
            "structural_GF2_seconds_not_CDCL_comparable":compute_s,
            "download_parse_and_GF2_wall_seconds":perf_counter()-start,
            "whole_process_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        })
        print("TIME_SAT_004D1",lookup["family"],
              exact["coverage_status"],exact["verdict"],
              "groups",exact["group_count"],
              "seconds",round(compute_s,6),flush=True)
        original.unlink(missing_ok=True)
        decoded.unlink(missing_ok=True)
    if len(cases)!=2:
        raise AssertionError("frozen two-source cohort missing")
    payload={
       "schema":"JANUS-TIME-SAT-004D1-EXTERNAL-ORIGIN-XOR-PROOF-ONLY-V1",
       "study":"PUBLIC_COMPETITION_DEVELOPMENT_NOT_SEALED_HOLDOUT",
       "source_prior_004D0_CI":41326432087,
       "source_repeated_original_SHA_verification":True,
       "algorithms":"Exact full XOR-CNF cover + GF(2) Gaussian; ABSTAIN on mixed source",
       "strong_native_specialized_baseline":"NOT_YET_BENCHMARKED",
       "strong_generic_baseline_004D0":"ALL_32_CPU_CENSORED_AT_SIX_SECONDS",
       "source_administrator":"SAME_GITHUB_OWNER",
       "original_C023":"UNCHANGED",
       "production_promotion":"FORBIDDEN",
       "cases":cases,
    }
    out.joinpath("result.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print("TIME_SAT_004D1_SUMMARY",json.dumps({
       x["family"]:{
         "coverage":x["xor_certificate"]["coverage_status"],
         "verdict":x["xor_certificate"]["verdict"],
         "groups":x["xor_certificate"]["group_count"]
       } for x in cases},sort_keys=True),flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    run(parser.parse_args().out)
