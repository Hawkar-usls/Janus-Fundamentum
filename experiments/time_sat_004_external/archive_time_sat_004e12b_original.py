#!/usr/bin/env python3
"""E12B strict original SHA-locked 22 GitHub Actions ZIP scientific archive."""
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
from zipfile import ZipFile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from janus_time_sat_004e12b_audit import audit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e12b_support_index as m

REPO="Hawkar-usls/Janus-Fundamentum"
SCIENTIFIC_RUN=41479552023
SCIENTIFIC_HEAD="5f09929a1bf715cfccdafce10755d85d4aa0cab1"
LOCK_NAME="sat-e12b-frozen-source-model-decisions-before-workers"
AUDIT_NAME="sat-e12b-original-independent-same-admin-audit"

def digest(raw):return sha256(raw).hexdigest()

def api(path):
    req=Request("https://api.github.com"+path,headers={
       "Authorization":"Bearer "+os.environ["GH_TOKEN"],
       "Accept":"application/vnd.github+json",
       "X-GitHub-Api-Version":"2022-11-28"})
    with urlopen(req,timeout=35) as r:return json.load(r)

def archive(output):
    run=api("/repos/"+REPO+"/actions/runs/"+str(SCIENTIFIC_RUN))
    if (run["head_sha"]!=SCIENTIFIC_HEAD or run["status"]!="completed"
        or run["conclusion"]!="success"):
        raise AssertionError("Original E12B source run/head not completed and successful")
    jobs=api("/repos/"+REPO+"/actions/runs/"+str(SCIENTIFIC_RUN)+"/jobs?per_page=100")
    j=jobs["jobs"]
    if jobs["total_count"]!=22 or len(j)!=22 or any(x["conclusion"]!="success" for x in j):
        raise AssertionError("Need 20 successful original VM jobs + preflight + independent auditor")
    workers=[x for x in j if x["name"].startswith("original-source-comparison-workers (")]
    if (len(workers)!=20 or len({x["runner_id"] for x in workers})!=20
        or any(x["runner_id"] is None for x in workers)):
        raise AssertionError("Actual 20 unique separately hosted GitHub VM runner IDs missing")
    concurrency=[]
    for job in workers:
        a=datetime.fromisoformat(job["started_at"].replace("Z","+00:00")).timestamp()
        b=datetime.fromisoformat(job["completed_at"].replace("Z","+00:00")).timestamp()
        if b<=a:raise AssertionError("Original source VM time interval invalid")
        concurrency.extend([(a,1),(b,-1)])
    cur=peak=0
    for _,delta in sorted(concurrency,key=lambda x:(x[0],x[1])):
        cur+=delta;peak=max(peak,cur)
    if not 1<=peak<=8:raise AssertionError("Original max concurrency exceeded preregistered 8")
    artifacts=api("/repos/"+REPO+"/actions/runs/"+str(SCIENTIFIC_RUN)+"/artifacts?per_page=100")
    expected={LOCK_NAME,AUDIT_NAME}|{
       "sat-e12b-worker-"+os+"-"+case for os in m.HOSTS for case in m.IDS}
    if (artifacts["total_count"]!=22 or
        {a["name"] for a in artifacts["artifacts"]}!=expected):
        raise AssertionError("Need 22 original GitHub ZIP artifacts including pre-worker source lock")
    zip_dir=output/"original-GitHub-22-ZIPs"
    source_dir=output/"original-preworker-model-source-lock"
    receipts_dir=output/"original-20-worker-JSON"
    for p in (zip_dir,source_dir,receipts_dir):p.mkdir(parents=True,exist_ok=True)
    zipper={};original_audit=None
    for x in artifacts["artifacts"]:
        name=x["name"];dest=zip_dir/(name+".zip")
        subprocess.run(["curl","--fail","--silent","--show-error","--retry","2",
             "--location","-H","Authorization: Bearer "+os.environ["GH_TOKEN"],
             "-H","Accept: application/vnd.github+json",
             "https://api.github.com/repos/"+REPO+"/actions/artifacts/"+str(x["id"])+"/zip",
             "-o",str(dest)],check=True)
        raw=dest.read_bytes()
        if x.get("digest")!="sha256:"+digest(raw):
            raise AssertionError("Original GitHub Actions ZIP digest mismatch")
        zipper[name]={"artifact_id":x["id"],"exact_original_zip_SHA256":digest(raw)}
        with ZipFile(dest) as z:
            names=z.namelist()
            if not names or any("/" in name or "\\" in name for name in names):
                raise AssertionError("Unexpected nested original ZIP directory")
            members={name:z.read(name) for name in names}
        if name==LOCK_NAME:
            if set(members)!={"SOURCE_LOCK.json","SOURCE_LOCK.sha256"}:
                raise AssertionError("Missing source-lock original full original SAT model files")
            for path,b in members.items():(source_dir/path).write_bytes(b)
        elif name==AUDIT_NAME:
            if set(members)!={"AUDIT.json"}:
                raise AssertionError("Original independent audit ZIP missing JSON")
            original_audit=json.loads(members["AUDIT.json"])
            (output/"ORIGINAL_SAME_ADMIN_AUDIT.json").write_bytes(members["AUDIT.json"])
        else:
            if len(members)!=1 or not next(iter(members)).endswith(".json"):
                raise AssertionError("Expected exactly one original 30-child worker JSON")
            p,b=next(iter(members.items()))
            if (receipts_dir/p).exists():raise AssertionError("Duplicated worker receipt")
            (receipts_dir/p).write_bytes(b)
    lock,locksha=m.checked_lock(source_dir/"SOURCE_LOCK.json")
    if original_audit is None:raise AssertionError("Missing original source scientific audit")
    independent=audit(receipts_dir,source_dir/"SOURCE_LOCK.json")
    if independent!=original_audit:
        raise AssertionError("Original same-admin audit not reproducible byte-for-byte")
    if (independent["original_run_id"]!=str(SCIENTIFIC_RUN)
        or independent["original_HEAD"]!=SCIENTIFIC_HEAD
        or independent["original_cold_children"]!=600):
        raise AssertionError("Original run/HEAD/600 child provenance mismatch")
    summary={
      "schema":"JANUS-TIME-SAT-004E12B-ORIGINAL-22-ZIP-20-VM-600-COLD-SHA-PROVENANCE-ARCHIVE-V1",
      "status":"SOURCE_SHA_MODEL_AND_FULL_E12B_600_ORIGINAL_CHILDREN_REPLAYED_FROM_22_GITHUB_ZIPS",
      "original_scientific_run":SCIENTIFIC_RUN,
      "original_scientific_HEAD":SCIENTIFIC_HEAD,
      "frozen_manifest_git_blob":m.PREREG_BLOB,
      "preworker_source_sha_and_original_complete_model_lock_SHA256":locksha,
      "original_GitHub_jobs":22,
      "original_worker_VM_ids":20,
      "observed_peak_VMs":peak,
      "original_GitHub_ZIP_count":22,
      "original_GitHub_ZIP_SHA256":zipper,
      "original_science_independent_same_admin_reaudited":independent,
      "external_independent_custodian_originals":0,
      "all_original_results_preserved_even_negative":True,
      "champion":"NOT_ADMITTED","C023_main":"UNCHANGED"
    }
    (output/"SUMMARY.json").write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n")
    print("E12B_ORIGINAL_ZIP_ARCHIVE_PASS",json.dumps({
       "workers":20,"max_concurrency":peak,"zip_count":22,
       "children":600,"verdicts":independent["outcomes"]},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True,type=Path)
    archive(p.parse_args().out)
