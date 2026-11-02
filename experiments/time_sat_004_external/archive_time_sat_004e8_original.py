#!/usr/bin/env python3
"""004E8 exact original Actions 16-worker/160-child immutable evidence archiver.

Source run id and tested scientific HEAD are hard pinned. GitHub Actions ZIP
digest must match official digest. Recompute audit from raw per-worker receipts
in independent same-GitHub-admin VM and compare exact original audit bytes.
"""
from __future__ import annotations
import argparse
from datetime import datetime
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.request import Request,urlopen
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parent))
from janus_time_sat_004e8_audit import audit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
from janus_time_sat_004e8_model_first import IDS,HOSTS

RUN=41454451078
TESTED_SHA="f58576a34f0f51bbeb99fd2d93e7bf160d2914f1"
AUDIT="sat-004e8-research-audit"
PREFIX="sat-004e8-"

def sha(b):return sha256(b).hexdigest()

def github(path):
    token=os.getenv("GH_TOKEN")
    if not token:raise AssertionError("Must use original GitHub Actions read-only token")
    req=Request("https://api.github.com"+path,
                headers={"Authorization":"Bearer "+token,
                         "Accept":"application/vnd.github+json",
                         "X-GitHub-Api-Version":"2022-11-28"})
    with urlopen(req,timeout=30) as response:return json.load(response)

def original_details():
    uri="/repos/Hawkar-usls/Janus-Fundamentum/actions/runs/"+str(RUN)
    r=github(uri)
    if r["head_sha"]!=TESTED_SHA or r["status"]!="completed" or r["conclusion"]!="success":
        raise AssertionError("Original fixed 004E8 science 16 VM CI not completed SUCCESS at declared head")
    j=github(uri+"/jobs?per_page=100")
    all_jobs=j["jobs"]
    if len(all_jobs)!=18 or j["total_count"]!=18 or any(x["conclusion"]!="success" for x in all_jobs):
        raise AssertionError("Original preflight + 16 worker + audit exact 18 SUCCESS jobs missing")
    workers=[x for x in all_jobs if x["name"].startswith("worker (")]
    if (len(workers)!=16 or len({x["runner_id"] for x in workers})!=16
        or any(not x["runner_id"] for x in workers)
        or len([x for x in all_jobs if x["name"]=="preflight"])!=1
        or len([x for x in all_jobs if x["name"]=="research-audit"])!=1):
        raise AssertionError("Not 16 unique scheduled hosted runner VM identifiers")
    times=[]
    for w in workers:
        start=datetime.fromisoformat(w["started_at"].replace("Z","+00:00")).timestamp()
        end=datetime.fromisoformat(w["completed_at"].replace("Z","+00:00")).timestamp()
        if start>=end:raise AssertionError("Original time interval corrupt")
        times.extend([(start,1),(end,-1)])
    peak=active=0
    for _,shift in sorted(times,key=lambda x:(x[0],x[1])):
        active+=shift;peak=max(active,peak)
    if not 1<=peak<=8:raise AssertionError("Exceeded frozen max-parallel=8 research cap")
    a=github(uri+"/artifacts?per_page=100")
    artifacts=a["artifacts"]
    expected={AUDIT}|{PREFIX+os+"-"+case for os in HOSTS for case in IDS}
    if a["total_count"]!=17 or len(artifacts)!=17 or {x["name"] for x in artifacts}!=expected:
        raise AssertionError("Original Actions 17 artifact ZIPs not complete or unexpected")
    return all_jobs,artifacts,peak

def download(a,folder):
    digest=a.get("digest","")
    if not digest.startswith("sha256:") or len(digest)!=71:
        raise AssertionError("No official GitHub original source ZIP digest")
    path=folder/(a["name"]+".zip")
    subprocess.run(["curl","--fail","--silent","--show-error","--retry","2","--location",
       "-H","Authorization: Bearer "+os.environ["GH_TOKEN"],
       "-H","Accept: application/vnd.github+json",
       "https://api.github.com/repos/Hawkar-usls/Janus-Fundamentum/actions/artifacts/"+str(a["id"])+"/zip",
       "-o",str(path)],check=True,stdout=subprocess.DEVNULL)
    data=path.read_bytes()
    if sha(data)!=digest.split(":",1)[1]:
        raise AssertionError("Original Actions ZIP byte digest mismatch "+a["name"])
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        if len(names)!=1 or "/" in names[0] or "\\" in names[0]:
            raise AssertionError("Original ZIP layout unexpected")
        raw=z.read(names[0])
    return raw,names[0],sha(data)

def archiver(out):
    jobs,artifacts,peak=original_details()
    zips=out/"original-github-ZIPs";receipts=out/"original-worker-JSON"
    zips.mkdir(parents=True,exist_ok=True)
    receipts.mkdir(parents=True,exist_ok=True)
    zipsha={};jsonsha={};oldaudit=None
    filenames={case+"__"+os+".json" for case in IDS for os in HOSTS}
    for a in sorted(artifacts,key=lambda x:x["name"]):
        data,name,h=download(a,zips)
        zipsha[a["name"]]={"id":a["id"],"official_original_ZIP_SHA256":h}
        if a["name"]==AUDIT:
            if name!="AUDIT.json":raise AssertionError("Original audit filename mismatch")
            oldaudit=json.loads(data)
            (out/"ORIGINAL_SAME_ADMIN_AUDIT.json").write_bytes(data)
        else:
            if name not in filenames or (receipts/name).exists():
                raise AssertionError("Unknown/duplicate original worker JSON")
            (receipts/name).write_bytes(data)
            jsonsha[name]=sha(data)
    observed=audit(receipts)
    if observed!=oldaudit:
        raise AssertionError("Independent same-admin re-audit differs from original Actions audit")
    if (observed["source_scientific_run_id"]!=str(RUN)
        or observed["source_scientific_head"]!=TESTED_SHA):
        raise AssertionError("Source receipts do not belong to locked experimental scientific run")
    summary={"schema":"JANUS-TIME-SAT-004E8-ORIGINAL-16-VM-160-SAT-CHILD-17-ZIP-ARCHIVE-V1",
      "original_science_run_id":RUN,"original_tested_SHA":TESTED_SHA,
      "source_GitHub_original_jobs_SUCCESS":18,"original_unique_worker_runner_IDs":16,
      "measured_peak_concurrent_workers":peak,"requested_max_parallel":8,
      "original_source_artifact_ZIPs":zipsha,"original_raw_worker_receipt_SHA256":jsonsha,
      "original_GitHub_jobs_JSON_SHA256":sha(json.dumps(jobs,sort_keys=True).encode()),
      "recomputed_audit":observed,"original_160_child_records_all_preserved":True,
      "count_of_original_SAT_sources":8,"public_preseen_sources":2,
      "synthetic_planted_sources":6,"outside_admin_hidden_source_count":0,
      "C023_main":"UNCHANGED","004F":"NOT_READY","global_champion":"NOT_ESTABLISHED"}
    (out/"SUMMARY.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("004E8_ARCHIVED_ALL_ORIGINALS",json.dumps({
        "runner_VMs":16,"peak":peak,"children":160,
        "SAT":observed["all_outcomes"].get("SAT_ORIGINAL_CNF_MODEL_VERIFIED",0),
        "original_complete_pairs":observed["completed_only_ratio_count"],
        "new_hidden":0},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    archiver(p.parse_args().out)
