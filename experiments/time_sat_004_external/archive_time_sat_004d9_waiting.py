#!/usr/bin/env python3
"""Preserve exact original 004D9 GitHub preflight evidence, never fake Witness."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import zipfile

RUN=41364674100
HEAD="b13542563b960f5f9afa1752d6dd241cf1e35e09"
ARTIFACTS={
 "ubuntu22":{"id":13106507731,
             "sha256":"2c2f0071dd2d58c630dde0903eeef9e11e3a99ecd6a74a3f204b264a482450d0"},
 "ubuntu24":{"id":13106751122,
             "sha256":"1fbb9e33d9eca35e3da0d978c8f10943abf1562873513fbc1b0cb011e93f3a1e"}
}
EXPECTED={
"status":"WAITING_FOR_EXTERNAL_WITNESS",
"actual_external_SAT_cases_admitted":0,
"model_replay":"NOT_RUN",
"rank_experiment":"NOT_RUN",
"admin_independence":"NOT_ESTABLISHED",
"C023_main":"UNCHANGED"
}

def sha(raw):return sha256(raw).hexdigest()

def verify(path,host):
    raw=path.read_bytes()
    if sha(raw)!=ARTIFACTS[host]["sha256"]:
        raise AssertionError("Original GitHub Actions artifact ZIP sha changed")
    with zipfile.ZipFile(path) as z:
        if set(z.namelist())!={"preflight.json"}:
            raise AssertionError("Original artifact member list changed")
        payload=z.read("preflight.json")
    receipt=json.loads(payload)
    if any(receipt.get(k)!=v for k,v in EXPECTED.items()):
        raise AssertionError("Original preflight unexpectedly claimed real external witness")
    return payload

def run(z22,z24,out):
    a=verify(z22,"ubuntu22")
    b=verify(z24,"ubuntu24")
    if a!=b:
        raise AssertionError("Two hosts disagreed on external absence")
    out.mkdir(parents=True,exist_ok=True)
    for host,payload,z in (("ubuntu22",a,z22),("ubuntu24",b,z24)):
        shutil.copyfile(z,out/f"original-actions-{host}.zip")
        (out/f"original-{host}.json").write_bytes(payload)
    summary={
       "schema":"JANUS-TIME-SAT-004D9-EXACT-ORIGINAL-DUAL-UBUNTU-WAITING-EVIDENCE-V1",
       "scientific_status":"SIGNED_INTAKE_SYNTHETIC_CONTROLS_PASS_NO_REAL_EXTERNAL_CASES",
       "source_ci":RUN,"head_sha":HEAD,
       "original_artifacts":ARTIFACTS,
       "adversarial_signature_source_model_tests_per_host":11,
       "previous_sat_gate_tests_per_host":9,
       "original_C023_independent_verifier":"PASS_BOTH",
       "original_two_worker_preflight":EXPECTED,
       "synthetic_public_keys_did_NOT_create_external_Witness":True,
       "frozen_custodian_approved_public_key_count":0,
       "frozen_real_external_source_precommitted_count":0,
       "real_external_SAT_model_verified":0,
       "original_source_GF2_rank_computations":0,
       "performance_comparison":"NOT_RUN",
       "outside_GitHub_004C_Witness":"OPEN",
       "C023_main":"UNCHANGED",
       "original_files_sha256":{p.name:sha(p.read_bytes()) for p in out.iterdir() if p.is_file()}
    }
    (out/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("004D9_WAITING_ORIGINAL_ARCHIVE_PASS",
          json.dumps({"workers":2,"real_candidates":0,
                      "synthetic_signature_fixture_tests":22,
                      "independent_admin_witness":"OPEN"},sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--zip22",type=Path,required=True)
    ap.add_argument("--zip24",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    x=ap.parse_args();run(x.zip22,x.zip24,x.out)
