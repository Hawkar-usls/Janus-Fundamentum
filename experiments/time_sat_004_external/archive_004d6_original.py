#!/usr/bin/env python3
"""Preserve SHA-exact original TIME-SAT-004D6 dual-host source-only receipts.

Run SHA and GitHub Actions artifact IDs/digests are pinned before retrieval.
Replays the full resolution proof DAG against each original SATComp CNF again;
keeps the original unaltered JSON and ZIP, including zero-yield and caps.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
from janus_time_sat_004b_acquire import scan_dimacs
from janus_time_sat_004b_baselines import read_cnf
from janus_time_sat_004d6_replay import replay_all

RUN=41355380127
HEAD="f191948ae9c0b5bf20420d57afdbcfdc35b72592"
ARTIFACT={
 "ubuntu22":{"id":13102619807,"sha256":"a26df26b3183c8809f382188a5f6177b46e5908041032e1a460953f825d9762a"},
 "ubuntu24":{"id":13102338561,"sha256":"58e418d1532b318b9f8ce8eb0d8cd43f00fca18100cb3e38c88f9404ddf522c9"}
}
FROZEN_SOURCE="0cbf0eee23aa77b399ad2057f113ac1e48bd8405"
FROZEN_THIS="150d16f6cc90551afba81e964adc09ad0fe7c032"
ORIGINAL=Path("experiments/time_sat_004_external/time_sat_004d4b_evidence")
REG=Path("experiments/time_sat_004_external/PREREGISTERED_004D4B_PUBLIC_FOUR_MIXED_20261101.json")
EXPECTED={
 "linear-equations":(0,0,False),
 "xor-shifting":(2000,169,True),
 "minimum-disagreement-parity":(60,0,False),
 "binary-tree-parity":(2000,164,True)
}

def digest(blob):
    return sha256(blob).hexdigest()

def original(path,host):
    if digest(path.read_bytes())!=ARTIFACT[host]["sha256"]:
        raise AssertionError("original artifact ZIP SHA changed "+host)
    with zipfile.ZipFile(path) as fd:
        if set(fd.namelist())!={"result.json"}:
            raise AssertionError("unexpected artifact ZIP files "+host)
        b=fd.read("result.json")
    data=json.loads(b)
    if (data.get("schema")!="JANUS-TIME-SAT-004D6-FOUR-ORIGINAL-BOUNDED-RESOLUTION-V1"
        or str(data.get("run_id"))!=str(RUN)
        or data.get("run_head")!=HEAD
        or data.get("registration_git_blob")!=FROZEN_THIS
        or data.get("original_source_manifest_git_blob")!=FROZEN_SOURCE
        or data.get("no_solver_or_benchmark") is not True
        or len(data.get("cases",[]))!=4):
        raise AssertionError("source CI identity/protocol mismatch")
    for c in data["cases"]:
        if c["family"] not in EXPECTED:
            raise AssertionError("not a registered source case")
        derived,new,cap=EXPECTED[c["family"]]
        if (c["new_resolvents"]!=derived or
            c["new_complete_XOR_equations_beyond_explicit_source"]!=new or
            c["truncated_by_total_resolvent_budget"] is not cap or
            c["proof_validation"]!="ALL_RESOLUTION_STEPS_AND_ALL_NEW_PARITY_MASKS_SOURCE_REPLAY_PASS"):
            raise AssertionError("original source result changed "+c["family"])
    return b,data

def archive(a,b,out):
    raw22,run22=original(a,"ubuntu22")
    raw24,run24=original(b,"ubuntu24")
    source_meta=json.loads(REG.read_text())["candidates"]
    if [x["family"] for x in source_meta]!=list(EXPECTED):
        raise AssertionError("frozen original source order changed")
    cases=[]
    for x,y,pre in zip(run22["cases"],run24["cases"],source_meta):
        for key in ("family","GBD_ID_NOT_SHA256","original_decoded_CNF_SHA256",
                    "original_dimensions","new_resolvents",
                    "new_complete_XOR_equations_beyond_explicit_source",
                    "truncated_by_total_resolvent_budget","round_stats",
                    "evidence"):
            if x[key]!=y[key]:
                raise AssertionError("two hosted workers produced divergent evidence "+key)
        if (x["GBD_ID_NOT_SHA256"]!=pre["GBD_id_NOT_SHA256"] or
            x["original_decoded_CNF_SHA256"]!=pre["decoded_CNF_SHA256"]):
            raise AssertionError("original source identity mismatch")
        src=ORIGINAL/(pre["GBD_id_NOT_SHA256"]+".original.cnf")
        if digest(src.read_bytes())!=pre["decoded_CNF_SHA256"]:
            raise AssertionError("frozen original CNF SHA mismatch")
        shape=scan_dimacs(src)
        if shape!=pre["original_shape"]:
            raise AssertionError("frozen original CNF shape mismatch")
        rows=read_cnf(src,shape["n_variables"],shape["n_clauses"],max_literals=120000)
        if not replay_all(rows,shape["n_variables"],x["evidence"]):
            raise AssertionError("archived original source resolution witness invalid")
        cases.append({
          "family":x["family"],
          "original_CNF_SHA256":pre["decoded_CNF_SHA256"],
          "original_clauses":len(rows),
          "derived_resolvents":x["new_resolvents"],
          "new_complete_XOR_representations":x["new_complete_XOR_equations_beyond_explicit_source"],
          "truncated_by_2000_resolvent_limit":x["truncated_by_total_resolvent_budget"],
          "witnesses_sampled":len(x["evidence"]["new_witness_examples"]),
          "source_replay":"PASS_ON_BOTH_GITHUB_WORKERS_AND_ARCHIVE",
          "original_CNF_kept_unchanged":True
        })
    out.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(a,out/"original-actions-ubuntu22.zip")
    shutil.copyfile(b,out/"original-actions-ubuntu24.zip")
    (out/"original-ubuntu22.json").write_bytes(raw22)
    (out/"original-ubuntu24.json").write_bytes(raw24)
    manifest={
      "schema":"JANUS-TIME-SAT-004D6-ORIGINAL-TWO-WORKER-RESOLUTION-ARCHIVE-V1",
      "status":"BOTH_WORKERS_EXACT_ORIGINAL_RESOLUTION_REPLAY_333_ADDITIONAL_REPRESENTATIONS",
      "source_ci_run":RUN,"original_HEAD":HEAD,
      "original_artifact_zip_SHA256":ARTIFACT,
      "source_manifest_git_blob":FROZEN_SOURCE,
      "resolution_preregistration_git_blob":FROZEN_THIS,
      "source_CNF_provenance":str(ORIGINAL),
      "source_replay_again_during_archive":"PASS",
      "two_worker_result_agreement":"PASS",
      "case_receipts":cases,
      "complete_additional_parity_representations":333,
      "independent_GF2_rank_or_new_information":"NOT_EVALUATED",
      "new_SAT_UNSAT_verdict":"NONE",
      "benchmark_or_speedup":"NOT_EVALUATED",
      "independent_external_admin_Witness":"OPEN",
      "production_C023":"UNCHANGED",
      "files_SHA256":{p.name:digest(p.read_bytes()) for p in out.iterdir() if p.is_file()}
    }
    (out/"summary.json").write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    print("004D6_DURABLE_ORIGINAL_ARCHIVE_PASS",json.dumps({
      "hosts":2,"sources":4,"new_XOR_representations":333,
      "source_proofs_replayed":True,"two_budget_saturations":2,
      "no_solvers":True},sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--zip22",required=True,type=Path)
    ap.add_argument("--zip24",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    archive(args.zip22,args.zip24,args.out)
