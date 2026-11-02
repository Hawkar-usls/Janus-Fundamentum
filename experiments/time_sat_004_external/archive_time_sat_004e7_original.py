#!/usr/bin/env python3
"""Archival of exact original 004E7 GitHub Actions, 20 VM, 200 children, 21 ZIPs.

Archive never modifies the original scientific tested HEAD or frozen protocol.
It fails closed on missing resource-censored outcomes, mismatched SHAs or jobs.
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
from janus_time_sat_004e7_audit import audit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e7_transfer as m

ORIGINAL_RUN=41444587786
ORIGINAL_TESTED_HEAD="f7b9bef8d39f469b5bfa594b9948a03217c46693"
REPO="Hawkar-usls/Janus-Fundamentum"
AUDIT_ZIP="sat-004e7-independent-source-audit"

def digest(raw):return sha256(raw).hexdigest()
def get_json(path):
    token=os.environ.get("GH_TOKEN")
    if not token:raise AssertionError("GitHub Actions read-only API token absent")
    req=Request("https://api.github.com"+path,headers={
        "Authorization":"Bearer "+token,
        "Accept":"application/vnd.github+json",
        "X-GitHub-Api-Version":"2022-11-28"})
    with urlopen(req,timeout=30) as response:
        return json.load(response)

def do_archive(directory):
    run=get_json("/repos/"+REPO+"/actions/runs/"+str(ORIGINAL_RUN))
    if (run["head_sha"]!=ORIGINAL_TESTED_HEAD or
        run["status"]!="completed" or run["conclusion"]!="success"):
        raise AssertionError("Original 004E7 scientific matrix not SUCCESS on pinned original commit")
    jobs=get_json("/repos/"+REPO+"/actions/runs/"+str(ORIGINAL_RUN)+"/jobs?per_page=100")
    j=jobs["jobs"]
    if jobs["total_count"]!=22 or len(j)!=22 or any(row["conclusion"]!="success" for row in j):
        raise AssertionError("Expected 20 workers plus successful preflight & auditor, no missing jobs")
    workers=[x for x in j if x["name"].startswith("challenger (")]
    if len(workers)!=20 or len({x["runner_id"] for x in workers})!=20 or any(
        not x.get("runner_id") for x in workers):
        raise AssertionError("Not 20 original distinct GitHub ephemeral VM IDs")
    events=[]
    for job in workers:
        if not job["started_at"] or not job["completed_at"]:
            raise AssertionError("Missing source start/end VM interval")
        start=datetime.fromisoformat(job["started_at"].replace("Z","+00:00")).timestamp()
        end=datetime.fromisoformat(job["completed_at"].replace("Z","+00:00")).timestamp()
        if end<=start:raise AssertionError("Original source job impossible timing")
        events.extend([(start,1),(end,-1)])
    concurrent=peak=0
    for _,amount in sorted(events,key=lambda x:(x[0],x[1])):
        concurrent+=amount
        peak=max(peak,concurrent)
    if not 1<=peak<=20:
        raise AssertionError("Observed actual GitHub concurrency violates original limit")
    artifacts=get_json("/repos/"+REPO+"/actions/runs/"+str(ORIGINAL_RUN)+"/artifacts?per_page=100")
    if artifacts["total_count"]!=21 or len(artifacts["artifacts"])!=21:
        raise AssertionError("Original source 20 worker artifacts and one auditor ZIP missing")
    expected={"sat-004e7-"+host+"-"+fam+"-"+state
              for host in m.HOSTS for fam in m.FAMILIES for state in m.STATES}
    expected.add(AUDIT_ZIP)
    if {a["name"] for a in artifacts["artifacts"]}!=expected:
        raise AssertionError("Unexpected or missing GitHub Actions original artifact identity")
    directory.mkdir(parents=True,exist_ok=True)
    zips=directory/"original-source-github-ZIPs"
    receipts=directory/"original-20-worker-JSON"
    zips.mkdir(exist_ok=True);receipts.mkdir(exist_ok=True)
    original_archive={}
    original_audit=None
    for a in artifacts["artifacts"]:
        name=a["name"]
        dest=zips/(name+".zip")
        subprocess.run(["curl","--fail","--silent","--show-error","--retry","2",
            "--location",
            "-H","Authorization: Bearer "+os.environ["GH_TOKEN"],
            "-H","Accept: application/vnd.github+json",
            "https://api.github.com/repos/"+REPO+"/actions/artifacts/"+str(a["id"])+"/zip",
            "-o",str(dest)],check=True,stdout=subprocess.DEVNULL)
        raw=dest.read_bytes()
        if a.get("digest")!="sha256:"+digest(raw):
            raise AssertionError("Original Actions ZIP digest does not match GitHub artifact API")
        original_archive[name]={"id":a["id"],"ZIP_SHA256":digest(raw)}
        with ZipFile(dest) as file:
            paths=file.namelist()
            if len(paths)!=1 or "/" in paths[0] or "\\" in paths[0]:
                raise AssertionError("Original artifact ZIP not a single top-level JSON")
            data=file.read(paths[0])
        if name==AUDIT_ZIP:
            if paths[0]!="AUDIT.json":raise AssertionError("Unrecognized source auditor")
            original_audit=json.loads(data)
            (directory/"ORIGINAL_SOURCE_AUDIT.json").write_bytes(data)
        else:
            if not paths[0].endswith(".json") or (receipts/paths[0]).exists():
                raise AssertionError("Wrong original worker JSON path or duplicate worker artifact")
            (receipts/paths[0]).write_bytes(data)
    if original_audit is None:raise AssertionError("Original auditor artifact missing")
    reread=audit(receipts)
    if reread!=original_audit:
        raise AssertionError("Independent fresh archive replay differs from original 20-worker audit")
    if (reread["original_GitHub_run"]!=str(ORIGINAL_RUN) or
        reread["original_GitHub_HEAD"]!=ORIGINAL_TESTED_HEAD or
        reread["original_full_cold_children"]!=200):
        raise AssertionError("Source run/head or frozen child total mismatch")
    summary={
      "schema":"JANUS-TIME-SAT-004E7-25-COMPARISON-SOURCE-ARCHIVED-20-VM-V1",
      "archive_status":"ORIGINAL_GITHUB_SOURCE_LOCKED_20_VM_200_CHILD_AUDIT_PASS",
      "original_GitHub_run":ORIGINAL_RUN,"original_GitHub_head":ORIGINAL_TESTED_HEAD,
      "original_total_workflow_jobs":22,
      "unique_original_challenger_VM_runner_IDs":20,
      "observed_max_simultaneous_VM_jobs":peak,
      "original_ZIP_artifacts":original_archive,
      "original_ZIP_count":21,
      "original_sources_are_preseen_public":True,
      "independent_external_hidden_SAT_CNF":0,
      "scientific_outcome":reread,
      "C023_main":"UNCHANGED","no_production_promotion":True
    }
    (directory/"SUMMARY.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("004E7_ARCHIVE_ORIGINAL_SOURCE_PASS",json.dumps({
       "VMs":20,"peak":peak,"trials":200,"ZIPs":21,
       "status_counts":reread["verdict_counts"]},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    do_archive(p.parse_args().out)
