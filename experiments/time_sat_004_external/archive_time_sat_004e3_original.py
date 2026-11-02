#!/usr/bin/env python3
"""004E3 permanent source-run audit, 25 original GitHub ZIPs and peak concurrency.

Read-only original GitHub Actions source; write only research branch archive.
A completed 24-job matrix is different from peak concurrent VMs; use actual
GitHub runner IDs + start/end times to measure peak. No auto-promotion.
"""
from __future__ import annotations
import argparse
from datetime import datetime
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from janus_time_sat_004e3_independent_audit import scan
ROOT=Path("experiments/time_sat_004_external")
RUN=41422441073
HEAD="510fcd520d5cdaa4ac5a29abac966b31f811b203"
PREFIX="sat-004e3-"
AUDIT_ARTIFACT="sat-004e3-aggregate-audit"

def sha(raw):return sha256(raw).hexdigest()

def github_get(relative):
    token=os.environ.get("GH_TOKEN")
    if not token:raise AssertionError("Read-only GitHub Actions token required")
    import urllib.request
    req=urllib.request.Request("https://api.github.com"+relative,
        headers={"Authorization":"Bearer "+token,
                 "Accept":"application/vnd.github+json",
                 "X-GitHub-Api-Version":"2022-11-28"})
    with urllib.request.urlopen(req,timeout=30) as resp:
        return json.load(resp)

def orig_run_jobs_and_artifacts():
    run=github_get("/repos/Hawkar-usls/Janus-Fundamentum/actions/runs/"+str(RUN))
    if run["head_sha"]!=HEAD or run["status"]!="completed" or run["conclusion"]!="success":
        raise AssertionError("Not source-locked successful original 004E3 workflow")
    data=github_get("/repos/Hawkar-usls/Janus-Fundamentum/actions/runs/"+str(RUN)+"/jobs?per_page=100")
    jobs=data["jobs"]
    if data["total_count"]!=25 or len(jobs)!=25:
        raise AssertionError("Original expected 24 worker + 1 independent auditor missing")
    workers=[x for x in jobs if x["name"].startswith("challenger (")]
    audit=[x for x in jobs if x["name"]=="independent-research-audit"]
    if len(workers)!=24 or len(audit)!=1 or any(x["conclusion"]!="success" for x in jobs):
        raise AssertionError("Missing or unsuccessful original matrix job or independent auditor")
    vm_ids=[x["runner_id"] for x in workers]
    if any(not i for i in vm_ids) or len(set(vm_ids))!=24:
        raise AssertionError("Original worker IDs must identify 24 distinct GitHub-hosted VMs")
    times=[]
    for job in workers:
        if not job["started_at"] or not job["completed_at"]:
            raise AssertionError("No source truth for actual VM concurrency")
        t0=datetime.fromisoformat(job["started_at"].replace("Z","+00:00")).timestamp()
        t1=datetime.fromisoformat(job["completed_at"].replace("Z","+00:00")).timestamp()
        if t1<=t0:raise AssertionError("Corrupt VM interval")
        times.extend([(t0,1),(t1,-1)])
    times.sort(key=lambda x:(x[0],x[1]))
    active=peak=0
    for _,d in times:
        active+=d
        peak=max(peak,active)
    if not (1<=peak<=20):
        raise AssertionError("Observed parallelism exceeds frozen matrix safety cap")
    data=github_get("/repos/Hawkar-usls/Janus-Fundamentum/actions/runs/"+str(RUN)+"/artifacts?per_page=100")
    artifacts=data["artifacts"]
    if data["total_count"]!=25 or len(artifacts)!=25:
        raise AssertionError("All 24 worker ZIPs plus original independent audit artifact required")
    if len({a["name"] for a in artifacts})!=25:
        raise AssertionError("Original artifact names not unique")
    return jobs,artifacts,peak

def download_artifact(a,out):
    expect=a.get("digest","")
    if not expect.startswith("sha256:") or len(expect)!=71:
        raise AssertionError("Original Actions ZIP digest not authoritative")
    path=out/(a["name"]+".zip")
    token=os.environ["GH_TOKEN"]
    command=["curl","--fail","--silent","--show-error","--retry","2",
             "--location","-H","Authorization: Bearer "+token,
             "-H","Accept: application/vnd.github+json",
             "https://api.github.com/repos/Hawkar-usls/Janus-Fundamentum/actions/artifacts/"+str(a["id"])+"/zip",
             "-o",str(path)]
    subprocess.run(command,check=True,stdout=subprocess.DEVNULL)
    actual=sha(path.read_bytes())
    if actual!=expect.split(":",1)[1]:
        raise AssertionError("Original artifact ZIP exact source digest mismatch: "+a["name"])
    return path,actual

def archive(out):
    jobs,artifacts,peak=orig_run_jobs_and_artifacts()
    out.mkdir(parents=True,exist_ok=True)
    raw=out/"original-github-zips"
    evidence=out/"original-per-worker-json"
    raw.mkdir(exist_ok=True)
    evidence.mkdir(exist_ok=True)
    byname={}
    receipts={}
    for a in artifacts:
        name=a["name"]
        if not (name.startswith(PREFIX)):
            raise AssertionError("Unknown original artifact type "+name)
        expected=frozenset({AUDIT_ARTIFACT} |
           {PREFIX+f+"-"+v for f in (
            "linear-equations","xor-shifting",
            "minimum-disagreement-parity","binary-tree-parity") for v in (
            "raw_cms","scan_noop_cms","native_all",
            "native_width2_only","native_width3plus_only","adaptive_80")})
        if name not in expected:
            raise AssertionError("Original artifact not predeclared")
        archive_zip,got=download_artifact(a,raw)
        byname[name]={"GitHub_artifact_id":a["id"],"original_ZIP_SHA256":got}
        with zipfile.ZipFile(archive_zip) as z:
            members=z.namelist()
            if len(members)!=1 or "/" in members[0] or "\\" in members[0]:
                raise AssertionError("Exactly one root-level JSON expected in original ZIP")
            content=z.read(members[0])
        if name==AUDIT_ARTIFACT:
            if members[0]!="AUDIT.json":
                raise AssertionError("Wrong original auditor filename")
            original_audit=json.loads(content)
            (out/"ORIGINAL_INDEPENDENT_AUDIT.json").write_bytes(content)
        else:
            if not members[0].endswith(".json"):
                raise AssertionError("Wrong original evidence file type")
            filename=members[0]
            if (evidence/filename).exists():
                raise AssertionError("Duplicate worker original receipt")
            (evidence/filename).write_bytes(content)
            receipts[name]=sha(content)
    if len(receipts)!=24:
        raise AssertionError("24 distinct original worker JSON expected")
    verified=scan(evidence)
    if original_audit!=verified:
        raise AssertionError("Source original audit differs from independently recomputed 24-worker audit")
    if (verified["original_GitHub_run_id"]!=str(RUN)
        or verified["original_head_SHA"]!=HEAD
        or verified["verified_cold_child_trials"]!=96):
        raise AssertionError("Unexpected original 96 child source receipt")
    result={
        "schema":"JANUS-TIME-SAT-004E3-SOURCE-LOCKED-PERMANENT-24-VM-AUDIT-V1",
        "status":"ALL_24_SEPARATE_VM_JOBS_96_COLD_CHILD_TRIALS_ORIGINAL_SOURCE_AUDIT_PASS",
        "original_source_run":RUN,"original_source_HEAD":HEAD,
        "original_GitHub_matrix_jobs":24,
        "distinct_original_runner_ids":len(set(x["runner_id"] for x in jobs if x["name"].startswith("challenger ("))),
        "source_observed_max_concurrent_worker_jobs":peak,
        "requested_max_parallel":20,
        "independent_audit_job":"SUCCESS",
        "original_GitHub_jobs_SHA256":sha(json.dumps(jobs,sort_keys=True).encode()),
        "original_worker_json_receipt_SHA256":receipts,
        "original_GitHub_artifact_ZIP_SHA256_and_ID":byname,
        "recomputed_model_and_challenger_audit":verified,
        "original_CNF_sources_preseen_public":True,
        "real_external_admin_Witness":"OPEN",
        "experimental_best_variant_across_unknown_families":"NOT_ESTABLISHED",
        "production_C023_main":"UNCHANGED",
        "permanent_original_zip_count":25
    }
    (out/"SUMMARY.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("004E3_ORIGINAL_VM_ARCHIVE_PASS",json.dumps({
        "worker_vm_count":24,"peak_concurrent_workers":peak,
        "cold_child_trials":96,"original_actions_zip_count":25,
        "independent_hidden_SAT_proof":False,
        "production_promotion":False},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    archive(p.parse_args().out)
