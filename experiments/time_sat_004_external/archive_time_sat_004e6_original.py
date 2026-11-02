#!/usr/bin/env python3
"""004E6 one-shot 13 original GitHub Actions ZIPs archive, 12 VMs/96 trials.

Never replace original data, never call separate GitHub audit externally
independent. Verify original exact GitHub run+HEAD and ZIP SHA256 before writing.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile
from urllib.request import Request,urlopen

sys.path.insert(0,str(Path(__file__).resolve().parent))
from janus_time_sat_004e6_audit import audit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
from janus_time_sat_004e6_semantic_selector import FAMILIES,STATES,HOSTS

RUN=41441179716
HEAD="f00da47e46c665e388defe1be89c484bf8f7541e"
PREFIX="sat-004e6-"
AUDIT="sat-004e6-research-audit"

def d(b):return sha256(b).hexdigest()

def get(path):
    token=os.environ.get("GH_TOKEN")
    if not token:raise AssertionError("Original GitHub Actions read-only token required")
    r=Request("https://api.github.com"+path,
              headers={"Authorization":"Bearer "+token,
                       "Accept":"application/vnd.github+json",
                       "X-GitHub-Api-Version":"2022-11-28"})
    with urlopen(r,timeout=30) as f:return json.load(f)

def source():
    uri="/repos/Hawkar-usls/Janus-Fundamentum/actions/runs/"+str(RUN)
    r=get(uri)
    if r["head_sha"]!=HEAD or r["status"]!="completed" or r["conclusion"]!="success":
        raise AssertionError("Original science CI not SUCCESS at exact pinned scientific head")
    jobs=get(uri+"/jobs?per_page=100")
    j=jobs["jobs"]
    if jobs["total_count"]!=14 or len(j)!=14 or any(x["conclusion"]!="success" for x in j):
        raise AssertionError("Need 12 worker, preflight and auditor all success")
    workers=[x for x in j if x["name"].startswith("challenger (")]
    if (len(workers)!=12 or len([x for x in j if x["name"]=="preflight"])!=1
        or len([x for x in j if x["name"]=="research-audit"])!=1
        or len(set(x["runner_id"] for x in workers))!=12):
        raise AssertionError("Not 12 distinct original GitHub-hosted VM job identifiers")
    times=[]
    for w in workers:
        if not w.get("started_at") or not w.get("completed_at"):
            raise AssertionError("No original job runtime timestamp")
        a=datetime.fromisoformat(w["started_at"].replace("Z","+00:00")).timestamp()
        b=datetime.fromisoformat(w["completed_at"].replace("Z","+00:00")).timestamp()
        if a>=b:raise AssertionError("Corrupt original GitHub job interval")
        times.extend([(a,1),(b,-1)])
    count=peak=0
    for t,s in sorted(times,key=lambda x:(x[0],x[1])):
        count+=s;peak=max(count,peak)
    if not 1<=peak<=12:raise AssertionError("Unexpected more concurrent VMs than frozen cap")
    a=get(uri+"/artifacts?per_page=100")
    artifacts=a["artifacts"]
    expected={AUDIT}|{PREFIX+os+"-"+family+"-"+state
          for os in HOSTS for family in FAMILIES for state in STATES}
    if a["total_count"]!=13 or {x["name"] for x in artifacts}!=expected:
        raise AssertionError("Required exact 13 ORIGINAL Actions artifact ZIPs")
    return j,artifacts,peak

def download(a,folder):
    expected=a.get("digest","")
    if not expected.startswith("sha256:") or len(expected)!=71:
        raise AssertionError("Missing authoritative GitHub Action ZIP SHA-256")
    path=folder/(a["name"]+".zip")
    subprocess.run(["curl","--fail","--silent","--show-error","--retry","2",
                    "--location","-H","Authorization: Bearer "+os.environ["GH_TOKEN"],
                    "-H","Accept: application/vnd.github+json",
                    "https://api.github.com/repos/Hawkar-usls/Janus-Fundamentum/actions/artifacts/"+str(a["id"])+"/zip",
                    "-o",str(path)],check=True,stdout=subprocess.DEVNULL)
    binary=path.read_bytes()
    if d(binary)!=expected.removeprefix("sha256:"):
        raise AssertionError("Original ZIP byte SHA-256 changed: "+a["name"])
    with zipfile.ZipFile(path) as z:
        files=z.namelist()
        if len(files)!=1 or "/" in files[0] or "\\" in files[0]:
            raise AssertionError("Unexpected original ZIP member layout")
        raw=z.read(files[0])
    return raw,files[0],d(binary)

def archive(out):
    jobs,artifacts,peak=source()
    zipdir=out/"original-actions-ZIPs"
    receipts=out/"original-worker-JSON"
    zipdir.mkdir(parents=True,exist_ok=True)
    receipts.mkdir(parents=True,exist_ok=True)
    zip_info={};raw_sha={};source_audit=None
    for a in sorted(artifacts,key=lambda x:x["name"]):
        raw,member,digest=download(a,zipdir)
        zip_info[a["name"]]={"original_GitHub_artifact_id":a["id"],
                             "original_GitHub_ZIP_SHA256":digest}
        if a["name"]==AUDIT:
            if member!="AUDIT.json":raise AssertionError("Original audit member missing")
            source_audit=json.loads(raw)
            (out/"ORIGINAL_AUDIT.json").write_bytes(raw)
        else:
            expected={family+"__"+state+"__"+os+".json"
                      for os in HOSTS for family in FAMILIES for state in STATES}
            if member not in expected or (receipts/member).exists():
                raise AssertionError("Unrecognized/duplicate original worker receipt")
            (receipts/member).write_bytes(raw)
            raw_sha[member]=d(raw)
    anew=audit(receipts)
    if anew!=source_audit or anew["original_run_id"]!=str(RUN) or anew["original_head"]!=HEAD:
        raise AssertionError("Original independent same-admin audit mismatches recomputed evidence")
    summary={
      "schema":"JANUS-TIME-SAT-004E6-ORIGINAL-12-VM-96-CHILD-13-ZIP-ARCHIVE-V1",
      "status":"ORIGINAL_SHA_VERIFIED_ALL_SOURCE_DATA_AND_AUDIT_PASS",
      "original_scientific_CI":RUN,"original_scientific_HEAD":HEAD,
      "original_14_jobs_SUCCESS":True,"original_worker_VM_count":12,
      "original_worker_unique_GitHub_runner_IDs":12,
      "observed_max_original_concurrent_worker_jobs":peak,
      "original_cold_child_count":96,
      "original_artifact_ZIPs_SHA_and_ID":zip_info,
      "original_receipt_SHA256":raw_sha,
      "original_jobs_JSON_SHA256":d(json.dumps(jobs,sort_keys=True).encode()),
      "recomputed_verification":anew,
      "new_external_independent_CNF":0,
      "same_admin_not_independent_external_Witness":True,
      "true_hidden_holdout":False,
      "source_C023_main":"UNCHANGED",
      "candidate_global_champion":"NOT_ESTABLISHED"}
    (out/"SUMMARY.json").write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n")
    print("004E6_ARCHIVE_PASS",json.dumps({
      "original_runner_VM":12,"peak_concurrent":peak,"original_cold_children":96,
      "SAT":anew["all_original_outcomes"].get("SAT_ORIGINAL_CNF_MODEL_VERIFIED",0),
      "external_custodian":0},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    archive(a.out)
