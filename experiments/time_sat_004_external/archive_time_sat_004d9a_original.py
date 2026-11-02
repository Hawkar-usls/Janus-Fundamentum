#!/usr/bin/env python3
"""TIME-SAT-004D9A preserve original dual-host synthetic-only CI preflight.

This is a *negative* evidentiary archive: zero external custodians/cases.
No ephemeral private keys, CNFs, models or trust roots are archived.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import zipfile

RUN_ID=41407180555
CI_HEAD="1f95d76fd925b0b69dac157d186333caa42e4ced"
ZIPS={
 "ubuntu22":{"id":13123179951,"sha256":"9b763fc05caba6e4a3377dcc9bbf558e9e150896c989181e5661df33b960f992"},
 "ubuntu24":{"id":13123323558,"sha256":"9b763fc05caba6e4a3377dcc9bbf558e9e150896c989181e5661df33b960f992"}
}
WAITING="WAITING_FOR_EXTERNAL_WITNESS"


def read_original(path,host):
    binary=path.read_bytes()
    if sha256(binary).hexdigest()!=ZIPS[host]["sha256"]:
        raise AssertionError("Original CI ZIP digest mismatch "+host)
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        if len(names)!=1 or Path(names[0]).name!="preflight.json":
            raise AssertionError("Unexpected artifact contents including potential secrets")
        raw=z.read(names[0])
    x=json.loads(raw)
    if (x.get("status")!=WAITING or
        x.get("actual_external_SAT_cases_admitted")!=0 or
        x.get("admin_independence")!="NOT_ESTABLISHED" or
        x.get("model_replay")!="NOT_RUN" or
        x.get("rank_experiment")!="NOT_RUN" or
        x.get("C023_main")!="UNCHANGED"):
        raise AssertionError("Original CI wrongly claimed real independent data")
    return raw


def archive(z22,z24,out):
    raw22=read_original(z22,"ubuntu22")
    raw24=read_original(z24,"ubuntu24")
    if raw22!=raw24:
        raise AssertionError("Original two worker preflight results diverged")
    out.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(z22,out/"original-actions-ubuntu22.zip")
    shutil.copyfile(z24,out/"original-actions-ubuntu24.zip")
    (out/"original-ubuntu22.json").write_bytes(raw22)
    (out/"original-ubuntu24.json").write_bytes(raw24)
    payload={
      "schema":"JANUS-TIME-SAT-004D9A-ORIGINAL-DUAL-HOST-OFFLINE-KIT-SYNTHETIC-PREFLIGHT-V1",
      "status":"SYNTHETIC_OFFLINE_FIXTURES_PASS_NO_REAL_EXTERNAL_WITNESS",
      "original_test_CI":RUN_ID,"original_tested_head":CI_HEAD,
      "original_artifact_zip_ids_and_sha256":ZIPS,
      "original_two_host_results_identical":True,
      "new_synthetic_protocol_tests_each_host":10,
      "previous_004D9_intake_tests_each_host":11,
      "previous_004D8_model_gate_tests_each_host":9,
      "old_C023_serialized_verifier":"PASS_BOTH",
      "real_approved_external_custodians":0,
      "real_external_data_sources":0,
      "real_verified_external_SAT_models":0,
      "witness_admin_independence":"NOT_ESTABLISHED",
      "SINCE_NO_EXTERNAL_DATA_NO_GF2_RANK_WAS_RUN":True,
      "original_parent_policy_modified":False,
      "production_C023_main":"UNCHANGED",
      "raw_artifact_SHA256":{
        "original-ubuntu22.json":sha256(raw22).hexdigest(),
        "original-ubuntu24.json":sha256(raw24).hexdigest()},
      "scientific_boundary":"Working offline signing protocol only; synthetic tests cannot be presented as independent evaluations, hidden SAT benchmarks or portable 004C proof attestations."
    }
    (out/"summary.json").write_text(json.dumps(payload,sort_keys=True,indent=2)+"\n")
    print("004D9A_ORIGINAL_DUAL_HOST_ARCHIVE_PASS",json.dumps({
       "original_hosts":2,"synthetic_tests_total":20,
       "real_custodians":0,"external_SAT_sources":0,
       "witness":"OPEN","C023":"UNCHANGED"},sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--zip22",type=Path,required=True)
    p.add_argument("--zip24",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    archive(a.zip22,a.zip24,a.out)
