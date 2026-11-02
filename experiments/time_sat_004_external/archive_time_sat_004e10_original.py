#!/usr/bin/env python3
"""TIME-SAT-004E10: preserve exact 14 GitHub original artifact ZIPs.

No external witness is implied by same-GitHub-admin independent recomputation.
All original runner IDs, SHA and 144 outcomes must match the original CI.
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
from janus_time_sat_004e10_audit import audit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
from janus_time_sat_004e10_ood import IDS,HOSTS,MODEL_SHA

RUN=41468961992
HEAD="ca903714c8c26a9a8f322abbe6e3865236f8b544"
PREFIX="sat-e10-worker-"
PRE="sat-e10-before-workers-source-lock"
AUD="sat-e10-original-research-audit"

def digest(a):return sha256(a).hexdigest()
def github(url):
    token=os.getenv("GH_TOKEN")
    if not token:raise AssertionError("Need read-only original GitHub Actions token")
    req=Request("https://api.github.com"+url,headers={
        "Authorization":"Bearer "+token,
        "Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
    with urlopen(req,timeout=30) as f:return json.load(f)

def details():
    uri="/repos/Hawkar-usls/Janus-Fundamentum/actions/runs/"+str(RUN)
    r=github(uri)
    if r["head_sha"]!=HEAD or r["status"]!="completed" or r["conclusion"]!="success":
        raise AssertionError("Original experimental run HEAD/status not the pinned SUCCESS run")
    js=github(uri+"/jobs?per_page=100")
    jobs=js["jobs"]
    if js["total_count"]!=14 or len(jobs)!=14 or any(x["conclusion"]!="success" for x in jobs):
        raise AssertionError("Need original 14/14 jobs PASS")
    wrk=[x for x in jobs if x["name"].startswith("worker (")]
    if (len(wrk)!=12 or len({x["runner_id"] for x in wrk})!=12
        or not all(x["runner_id"] for x in wrk)
        or len([x for x in jobs if x["name"]=="freeze-new-original-sources"])!=1
        or len([x for x in jobs if x["name"]=="original-research-audit"])!=1):
        raise AssertionError("Did not get 12 real distinct GitHub runner VMs")
    event=[]
    for item in wrk:
        start=datetime.fromisoformat(item["started_at"].replace("Z","+00:00")).timestamp()
        end=datetime.fromisoformat(item["completed_at"].replace("Z","+00:00")).timestamp()
        if start>=end:raise AssertionError("Incorrect GitHub original VM wall timestamps")
        event.extend([(start,1),(end,-1)])
    peak=live=0
    for _,d in sorted(event,key=lambda x:(x[0],x[1])):
        live+=d;peak=max(live,peak)
    if not 1<=peak<=6:raise AssertionError("Exceeded frozen max 6 concurrent real VMs")
    arts=github(uri+"/artifacts?per_page=100")
    expected={PRE,AUD}|{PREFIX+os+"-"+case for os in HOSTS for case in IDS}
    if arts["total_count"]!=14 or {x["name"] for x in arts["artifacts"]}!=expected:
        raise AssertionError("Original artifact count/IDs drifted from exactly 14")
    return jobs,arts["artifacts"],peak

def download(a,out):
    want=a.get("digest","")
    if not want.startswith("sha256:") or len(want)!=71:
        raise AssertionError("No official GitHub original Actions ZIP SHA256 digest")
    filename=out/(a["name"]+".zip")
    subprocess.run(["curl","--fail","--silent","--show-error","--retry","2","--location",
        "-H","Authorization: Bearer "+os.environ["GH_TOKEN"],
        "-H","Accept: application/vnd.github+json",
        "https://api.github.com/repos/Hawkar-usls/Janus-Fundamentum/actions/artifacts/"+str(a["id"])+"/zip",
        "-o",str(filename)],check=True,stdout=subprocess.DEVNULL)
    raw=filename.read_bytes()
    if digest(raw)!=want.split(":",1)[1]:
        raise AssertionError("Raw source original SHA mismatch: "+a["name"])
    with ZipFile(filename) as z:
        members=z.namelist()
        if not members or any("/" in name or "\\" in name for name in members):
            raise AssertionError("Not a flat original source artifact ZIP")
        contents={key:z.read(key) for key in members}
    return contents,digest(raw)

def archive(out):
    jobs,arts,peak=details()
    z=out/"original-GitHub-14-ZIPs"
    workers=out/"original-12-worker-JSON"
    pre=out/"original-source-lock"
    for path in (z,workers,pre):path.mkdir(parents=True,exist_ok=True)
    original_audit=None;zinfo={};rinfo={}
    valid={case+"__"+os+".json" for case in IDS for os in HOSTS}
    for a in sorted(arts,key=lambda x:x["name"]):
        contents,zipsha=download(a,z)
        zinfo[a["name"]]={"official_source_GitHub_artifact_id":a["id"],
                          "official_source_ZIP_SHA256":zipsha}
        if a["name"]==PRE:
            if set(contents)!={"SOURCE_LOCK.json","SOURCE_LOCK.sha256"}:
                raise AssertionError("Missing original presolve source SHA manifest")
            for n,b in contents.items():(pre/n).write_bytes(b)
        elif a["name"]==AUD:
            if set(contents)!={"AUDIT.json"}:raise AssertionError("Source original audit member invalid")
            original_audit=json.loads(contents["AUDIT.json"])
            (out/"ORIGINAL_SAME_ADMIN_AUDIT.json").write_bytes(contents["AUDIT.json"])
        else:
            if len(contents)!=1:raise AssertionError("Unexpected source worker artifact members")
            name=next(iter(contents))
            if name not in valid or (workers/name).exists():
                raise AssertionError("Original worker artifact filename collision or foreign item")
            (workers/name).write_bytes(contents[name])
            rinfo[name]=digest(contents[name])
    checked=audit(workers,pre/"SOURCE_LOCK.json")
    if (checked!=original_audit
        or checked["original_run"]!=str(RUN)
        or checked["original_head"]!=HEAD
        or checked["original_pretrained_E9_MODEL_SHA256"]!=MODEL_SHA):
        raise AssertionError("Original source audit/protocol or independently recomputed audit mismatch")
    final={"schema":"JANUS-TIME-SAT-004E10-ORIGINAL-3-GENERATOR-12VM-144-SAT-CHILD-ARCHIVE-V1",
      "source_original_science_run":RUN,"source_tested_SHA":HEAD,
      "original_14_jobs_SUCCESS":True,"distinct_worker_VM_ids":12,
      "measured_peak_concurrent_VMs":peak,
      "original_source_ZIP_sha256_and_id":zinfo,
      "original_12_worker_JSON_SHA256":rinfo,
      "original_jobs_response_SHA256":digest(json.dumps(jobs,sort_keys=True).encode()),
      "original_recomputed_same_admin_audit":checked,
      "original_144_child_full_results_archived":True,
      "new_external_blind_originals":0,"published_synthetic_family_count":3,
      "C023_main":"UNCHANGED","global_champion":"NOT_ADMITTED"}
    (out/"SUMMARY.json").write_text(json.dumps(final,sort_keys=True,indent=2)+"\n")
    print("004E10_ARCHIVE_PASS",json.dumps({
      "original_worker_VM":12,"original_peak":peak,
      "original_children":144,"outcomes":checked["original_all_outcomes"],
      "independent_external_witness":"NONE"},sort_keys=True))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    archive(p.parse_args().out)
