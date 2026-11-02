#!/usr/bin/env python3
"""004E5 exact original Actions 24-VM proof/data archive, no data rewriting."""
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
from urllib.request import Request,urlopen
from zipfile import ZipFile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from janus_time_sat_004e5_audit import verify
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e5_metamorphic as m

RUN=41439466935
HEAD="c7df96852d168305a9c74d6347fd8371758c132c"
REPO="Hawkar-usls/Janus-Fundamentum"
PREFIX="sat-004e5-"
AUDIT_NAME="sat-004e5-audit"

def github_json(path):
    token=os.environ["GH_TOKEN"]
    request=Request("https://api.github.com"+path,headers={
        "Authorization":"Bearer "+token,
        "Accept":"application/vnd.github+json",
        "X-GitHub-Api-Version":"2022-11-28"})
    with urlopen(request,timeout=30) as r:return json.load(r)

def sha(raw):return sha256(raw).hexdigest()

def go(out):
    r=github_json("/repos/"+REPO+"/actions/runs/"+str(RUN))
    if (r["head_sha"]!=HEAD or r["status"]!="completed" or
        r["conclusion"]!="success"):
        raise AssertionError("Wrong original source Actions CI or no SUCCESS")
    jobs=github_json("/repos/"+REPO+"/actions/runs/"+str(RUN)+"/jobs?per_page=100")
    if jobs["total_count"]!=26 or len(jobs["jobs"])!=26:
        raise AssertionError("Preflight+24 VMs+final auditor is exactly 26 Github jobs")
    challengers=[x for x in jobs["jobs"] if x["name"].startswith("challenger (")]
    if len(challengers)!=24 or any(x["conclusion"]!="success" for x in jobs["jobs"]):
        raise AssertionError("Not 24 successful GitHub-hosted execution jobs")
    ids=[x.get("runner_id") for x in challengers]
    if any(not i for i in ids) or len(set(ids))!=24:
        raise AssertionError("24 distinct real runner IDs not confirmed")
    events=[]
    for job in challengers:
        for moment,weight in ((job["started_at"],1),(job["completed_at"],-1)):
            if not moment:raise AssertionError("Missing source GitHub runner timestamp")
            events.append((datetime.fromisoformat(moment.replace("Z","+00:00")).timestamp(),weight))
    current=peak=0
    for _,delta in sorted(events,key=lambda x:(x[0],x[1])):
        current+=delta
        peak=max(current,peak)
    if not 1<=peak<=20:raise AssertionError("Invalid original GitHub requested 20 concurrency ceiling")
    artifacts=github_json("/repos/"+REPO+"/actions/runs/"+str(RUN)+"/artifacts?per_page=100")
    if artifacts["total_count"]!=25 or len(artifacts["artifacts"])!=25:
        raise AssertionError("Expected exactly 24 matrix archives + one original audit")
    known={PREFIX+os+"-"+family+"-pad"+str(p)+"-"+v
           for os in ("ubuntu-22.04","ubuntu-24.04")
           for family in m.FAMILIES for p in m.PADS for v in m.VARIANTS}
    known.add(AUDIT_NAME)
    if {x["name"] for x in artifacts["artifacts"]}!=known:
        raise AssertionError("Original artifact names not in frozen manifest")
    out.mkdir(parents=True,exist_ok=True)
    zipdir=out/"original-github-zips"
    jsondir=out/"original-per-worker-json"
    zipdir.mkdir(exist_ok=True)
    jsondir.mkdir(exist_ok=True)
    zips={}
    audit_bytes=None
    for artifact in artifacts["artifacts"]:
        name=artifact["name"]
        dest=zipdir/(name+".zip")
        subprocess.run(["curl","--fail","--silent","--show-error","--retry","2",
            "--location","-H","Authorization: Bearer "+os.environ["GH_TOKEN"],
            "-H","Accept: application/vnd.github+json",
            "https://api.github.com/repos/"+REPO+"/actions/artifacts/"+str(artifact["id"])+"/zip",
            "-o",str(dest)],check=True,stdout=subprocess.DEVNULL)
        original=dest.read_bytes()
        if artifact.get("digest")!="sha256:"+sha(original):
            raise AssertionError("Exact original ZIP GitHub Actions digest mismatch")
        zips[name]={"artifact_id":artifact["id"],"original_SHA256":sha(original)}
        with ZipFile(dest) as z:
            files=z.namelist()
            if len(files)!=1 or "/" in files[0] or "\\" in files[0]:
                raise AssertionError("Unexpected original GitHub artifact shape")
            raw=z.read(files[0])
        if name==AUDIT_NAME:
            if files[0]!="AUDIT.json":raise AssertionError("Auditor filename changed")
            audit_bytes=raw
            (out/"ORIGINAL_INDEPENDENT_AUDIT.json").write_bytes(raw)
        else:
            if not files[0].endswith(".json") or (jsondir/files[0]).exists():
                raise AssertionError("Duplicate or non-JSON original worker output")
            (jsondir/files[0]).write_bytes(raw)
    if audit_bytes is None:raise AssertionError("Original independent audit lost")
    audited=verify(jsondir)
    if json.loads(audit_bytes)!=audited:
        raise AssertionError("Independent reviewer did not recreate original internal audit")
    if (audited["source_job_run_id"]!=str(RUN) or
        audited["original_git_head"]!=HEAD or
        audited["verified_cold_child_outcomes"]!=96):
        raise AssertionError("Wrong original CI SHA or child counts")
    result={
        "schema":"JANUS-TIME-SAT-004E5-PERMANENT-24-VM-METAMORPHIC-SHA-ARCHIVE-V1",
        "status":"ORIGINAL_GITHUB_26_JOBS_AND_96_CHILDREN_STRICT_SHA_REPLAY_PASS",
        "original_workflow_run":RUN,"tested_original_HEAD":HEAD,
        "original_challenger_VM_count":24,"original_verified_distinct_runner_ids":24,
        "original_observed_max_simultaneous_VMs":peak,
        "original_GitHub_26_jobs":26,"original_worker_artifact_ZIP_count":25,
        "original_zip_artifact_sha256":zips,
        "original_semantic_audit":audited,
        "new_independently_selected_SAT_cases":0,
        "source_truth":"TWO_PREVIOUSLY_SEEN_CERTIFIED_SAT_ORIGINALS",
        "meta_scientific_status":"METAMORPHIC_DIAGNOSTIC_NOT_BLIND_ACCELERATION",
        "main_C023":"UNCHANGED"
    }
    (out/"SUMMARY.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("004E5_ARCHIVE_VERIFIED_PASS",json.dumps({
        "unique_VM":24,"peak_concurrent":peak,"total_child":96,
        "original_git_zip_count":25,"external_cases":0},sort_keys=True))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    go(parser.parse_args().out)
