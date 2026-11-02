#!/usr/bin/env python3
"""Preserve exact ORIGINAL E11 16 VM, source/model lock and 224 source-paired outputs.

Fails on a lost/mismatched GitHub Actions ZIP SHA, missing VM, absent new
SAT-model source lock, altered original HEAD or any original audit mismatch.
Research branch only, not C023/main or an external independent witness.
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
from zipfile import ZipFile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from janus_time_sat_004e11_audit import audit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e11_parity_probe as m

REPO="Hawkar-usls/Janus-Fundamentum"
RUN=41472124484
HEAD="d2e7b4c63675cd80831b3de06ce479dfa8ff12e1"
LOCK_NAME="sat-e11-original-source-lock-before-validation"
AUDIT_NAME="sat-e11-original-audit"

def sha(data):return sha256(data).hexdigest()

def github_api(path):
    token=os.environ.get("GH_TOKEN")
    if not token:raise AssertionError("GH_TOKEN in research archive Actions missing")
    req=Request("https://api.github.com"+path,headers={
        "Authorization":"Bearer "+token,
        "Accept":"application/vnd.github+json",
        "X-GitHub-Api-Version":"2022-11-28"})
    with urlopen(req,timeout=30) as f:return json.load(f)

def archive(target):
    run=github_api("/repos/"+REPO+"/actions/runs/"+str(RUN))
    if (run["head_sha"]!=HEAD or run["status"]!="completed"
        or run["conclusion"]!="success"):
        raise AssertionError("Original E11 18-job source experiment not fully PASS on tested HEAD")
    jobs=github_api("/repos/"+REPO+"/actions/runs/"+str(RUN)+"/jobs?per_page=100")
    j=jobs["jobs"]
    if jobs["total_count"]!=18 or len(j)!=18 or any(x["conclusion"]!="success" for x in j):
        raise AssertionError("Expected preflight, 16 actual original VM jobs, independent auditor PASS")
    workers=[x for x in j if x["name"].startswith("compare-previous-and-new-gates (")]
    if len(workers)!=16 or len({x["runner_id"] for x in workers})!=16 or any(
       not x.get("runner_id") for x in workers):
        raise AssertionError("Source platform is not 16 independently identifiable VMs")
    events=[]
    for x in workers:
        start=datetime.fromisoformat(x["started_at"].replace("Z","+00:00")).timestamp()
        stop=datetime.fromisoformat(x["completed_at"].replace("Z","+00:00")).timestamp()
        if stop<=start:raise AssertionError("Bad source VM start/stop interval")
        events.extend([(start,1),(stop,-1)])
    current=peak=0
    for _,delta in sorted(events,key=lambda x:(x[0],x[1])):
        current+=delta;peak=max(peak,current)
    if not 1<=peak<=8:raise AssertionError("Peak original simultaneous workers out of frozen range")
    items=github_api("/repos/"+REPO+"/actions/runs/"+str(RUN)+"/artifacts?per_page=100")
    expected={LOCK_NAME,AUDIT_NAME}|{
      "sat-e11-original-worker-"+os+"-"+case for os in m.HOSTS for case in m.IDS}
    if (items["total_count"]!=18 or
        {x["name"] for x in items["artifacts"]}!=expected):
        raise AssertionError("Missing original E11 preworker source SHA/model ZIP or 16 VM ZIPs or audit ZIP")
    target.mkdir(parents=True,exist_ok=True)
    zipdir=target/"original-GitHub-18-ZIPs"
    receipts=target/"original-16-worker-JSON"
    locks=target/"original-SAT-source-lock"
    for f in (zipdir,receipts,locks):f.mkdir(exist_ok=True)
    original_sha={}
    original_audit=None
    for a in items["artifacts"]:
        name=a["name"];dest=zipdir/(name+".zip")
        subprocess.run(["curl","--fail","--silent","--show-error","--retry","2",
            "--location","-H","Authorization: Bearer "+os.environ["GH_TOKEN"],
            "-H","Accept: application/vnd.github+json",
            "https://api.github.com/repos/"+REPO+"/actions/artifacts/"+str(a["id"])+"/zip",
            "-o",str(dest)],check=True)
        raw=dest.read_bytes()
        if a.get("digest")!="sha256:"+sha(raw):
            raise AssertionError("GitHub original artifact ZIP SHA failed")
        original_sha[name]={"id":a["id"],"original_ZIP_sha256":sha(raw)}
        with ZipFile(dest) as z:
            names=z.namelist()
            if not names or any("/" in n or "\\" in n for n in names):
                raise AssertionError("Original artifact contains unexpected nested file path")
            members={n:z.read(n) for n in names}
        if name==LOCK_NAME:
            if set(members)!={"SOURCE_LOCK.json","SOURCE_LOCK.sha256"}:
                raise AssertionError("No precommitted source and original SAT model SHA lock")
            for p,data in members.items():(locks/p).write_bytes(data)
        elif name==AUDIT_NAME:
            if set(members)!={"AUDIT.json"}:
                raise AssertionError("Original science audit artifact shape wrong")
            original_audit=json.loads(members["AUDIT.json"])
            (target/"ORIGINAL_SAME_ADMIN_AUDIT.json").write_bytes(members["AUDIT.json"])
        else:
            if len(members)!=1 or not next(iter(members)).endswith(".json"):
                raise AssertionError("Not one original worker JSON per source ZIP")
            p,data=next(iter(members.items()))
            if (receipts/p).exists():raise AssertionError("Original worker receipt duplicated")
            (receipts/p).write_bytes(data)
    lock,locksha=m.checked_lock(locks/"SOURCE_LOCK.json")
    if original_audit is None:raise AssertionError("Missing original independent auditor")
    rechecked=audit(receipts,locks/"SOURCE_LOCK.json")
    if rechecked!=original_audit:
        raise AssertionError("Independent original source audit not replayable byte-for-byte")
    if (rechecked["original_source_run_id"]!=str(RUN)
        or rechecked["original_source_HEAD"]!=HEAD
        or rechecked["original_cold_children"]!=224):
        raise AssertionError("Original audited source run HEAD or child count mismatch")
    summary={
      "schema":"JANUS-TIME-SAT-004E11-EXACT-ORIGINAL-18-ZIP-16-VM-224-COLD-SOURCE-LOCKED-ARCHIVE-V1",
      "status":"ORIGINAL_GITHUB_ALL_18_JOBS_AND_224_SOURCE_MODEL_VERIFIED",
      "original_scientific_CI_run":RUN,"original_tested_HEAD":HEAD,
      "original_Worker_VM_runner_ids":16,
      "observed_peak_VM_concurrency":peak,
      "original_GitHub_jobs":18,"original_GitHub_artifact_ZIPs":18,
      "original_artifacts":original_sha,
      "preworker_exact_SAT_source_lock_SHA256":locksha,
      "frozen_policy_Git_blob":m.PLAN_BLOB,
      "original_independent_same_admin_science_audit":rechecked,
      "independent_external_hidden_source_count":0,
      "new_internal_3_parity_generators_six_originals":True,
      "preseen_exact_source_negative_controls":2,
      "C023_main":"UNCHANGED","autonomous_champion_promotion":False
    }
    (target/"SUMMARY.json").write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n")
    print("004E11_ARCHIVE_SOURCE_LOCK_PASS",json.dumps({
       "VMs":16,"peak":peak,"original_ZIPs":18,"children":224,
       "status":rechecked["all_outcomes"]},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    archive(p.parse_args().out)
