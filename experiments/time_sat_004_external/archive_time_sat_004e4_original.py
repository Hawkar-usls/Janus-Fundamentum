#!/usr/bin/env python3
"""004E4: one-shot exact original 24-worker Actions ZIP archive, 96 child review.

Recomputes independent (same GitHub administration) research audit and actual
GitHub scheduler concurrency from original job timestamps. No production
activation or external blind proof; fail closed on any mismatch.
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
import zipfile
from urllib.request import Request,urlopen

sys.path.insert(0,str(Path(__file__).resolve().parent))
from janus_time_sat_004e4_research_audit import audit
from janus_time_sat_004e4_research_audit import HOSTS
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
from janus_time_sat_004e4_transfer import CASES,VARIANTS

RUN=41436259878
HEAD="02ec539dfab47583a1674d3022daf0a42144ea02"
PREFIX="sat-004e4-"
AUDIT_ARTIFACT="sat-004e4-research-audit"

def digest(b):return sha256(b).hexdigest()

def gh(relative):
    token=os.environ.get("GH_TOKEN")
    if not token:raise AssertionError("Missing read-only GitHub Actions token")
    request=Request("https://api.github.com"+relative,
        headers={"Authorization":"Bearer "+token,
                 "Accept":"application/vnd.github+json",
                 "X-GitHub-Api-Version":"2022-11-28"})
    with urlopen(request,timeout=30) as f:
        return json.load(f)

def run_jobs_and_artifacts():
    uri="/repos/Hawkar-usls/Janus-Fundamentum/actions/runs/"+str(RUN)
    parent=gh(uri)
    if (parent["head_sha"]!=HEAD or parent["status"]!="completed"
        or parent["conclusion"]!="success"):
        raise AssertionError("Original E4 scientific CI not completed successfully at frozen HEAD")
    j=gh(uri+"/jobs?per_page=100")
    jobs=j["jobs"]
    if j["total_count"]!=25 or len(jobs)!=25:
        raise AssertionError("Expected exactly 24 VM jobs and one audit job")
    workers=[x for x in jobs if x["name"].startswith("challenger (")]
    checker=[x for x in jobs if x["name"]=="research-audit"]
    if len(workers)!=24 or len(checker)!=1 or any(x["conclusion"]!="success" for x in jobs):
        raise AssertionError("All source original jobs must succeed")
    runner_ids=[x["runner_id"] for x in workers]
    if not all(runner_ids) or len(set(runner_ids))!=24:
        raise AssertionError("Original workers do not identify 24 distinct GitHub VM runner IDs")
    event=[]
    for x in workers:
        start=datetime.fromisoformat(x["started_at"].replace("Z","+00:00")).timestamp()
        end=datetime.fromisoformat(x["completed_at"].replace("Z","+00:00")).timestamp()
        if start>=end:raise AssertionError("Original runner scheduler timestamp invalid")
        event.extend([(start,1),(end,-1)])
    event.sort(key=lambda x:(x[0],x[1]))
    peak=active=0
    for _,sign in event:
        active+=sign
        peak=max(peak,active)
    if not 1<=peak<=20:raise AssertionError("Observed peak outside declared max-parallel 20")
    a=gh(uri+"/artifacts?per_page=100")
    artifacts=a["artifacts"]
    if a["total_count"]!=25 or len(artifacts)!=25:
        raise AssertionError("Missing 25 original unmodified Actions artifact ZIPs")
    wanted={AUDIT_ARTIFACT}|{
        PREFIX+host+"-"+family+"-"+variant
        for host in HOSTS for family in CASES for variant in VARIANTS}
    if {x["name"] for x in artifacts}!=wanted:
        raise AssertionError("Original E4 25 artifact names missing or extra")
    return jobs,artifacts,peak

def download_one(a,folder):
    expected=a.get("digest","")
    if not expected.startswith("sha256:") or len(expected)!=71:
        raise AssertionError("No verified GitHub Actions original ZIP digest")
    target=folder/(a["name"]+".zip")
    subprocess.run([
        "curl","--fail","--silent","--show-error","--retry","2","--location",
        "-H","Authorization: Bearer "+os.environ["GH_TOKEN"],
        "-H","Accept: application/vnd.github+json",
        "https://api.github.com/repos/Hawkar-usls/Janus-Fundamentum/actions/artifacts/"+str(a["id"])+"/zip",
        "-o",str(target)],check=True,stdout=subprocess.DEVNULL)
    binary=target.read_bytes()
    if digest(binary)!=expected.split(":",1)[1]:
        raise AssertionError("Original ZIP SHA-256 changed "+a["name"])
    with zipfile.ZipFile(target) as z:
        names=z.namelist()
        if len(names)!=1 or "/" in names[0] or "\\" in names[0]:
            raise AssertionError("Unexpected original JSON ZIP layout")
        raw=z.read(names[0])
    return raw,names[0],expected.split(":",1)[1]

def archive(out):
    jobs,artifacts,peak=run_jobs_and_artifacts()
    originals=out/"original-github-zips"
    receipts=out/"original-per-worker-json"
    originals.mkdir(parents=True,exist_ok=True)
    receipts.mkdir(parents=True,exist_ok=True)
    listing={}
    originals_sha={}
    original_audit=None
    for a in sorted(artifacts,key=lambda x:x["name"]):
        body,member,got=download_one(a,originals)
        listing[a["name"]]={"GitHub_artifact_id":a["id"],"original_ZIP_SHA256":got}
        if a["name"]==AUDIT_ARTIFACT:
            if member!="AUDIT.json":
                raise AssertionError("Original separate-auditor artifact name changed")
            original_audit=json.loads(body)
            (out/"ORIGINAL_RESEARCH_AUDIT.json").write_bytes(body)
        else:
            if member not in {
                family+"__"+variant+"__"+host+".json"
                for host in HOSTS for family in CASES for variant in VARIANTS
            }:
                raise AssertionError("Original archived worker JSON file invalid: "+member)
            dest=receipts/member
            if dest.exists():raise AssertionError("Duplicate original worker receipt")
            dest.write_bytes(body)
            originals_sha[member]=digest(body)
    checked=audit(receipts)
    if original_audit!=checked:
        raise AssertionError("Separate original audit differs from independently recomputed audit")
    if checked["original_CI_run_id"]!=str(RUN) or checked["original_source_head"]!=HEAD:
        raise AssertionError("Original worker CI run/head mutated")
    result={
        "schema":"JANUS-TIME-SAT-004E4-ORIGINAL-CROSS-COHORT-24-VM-96-CHILD-ARCHIVE-V1",
        "source_run":RUN,"source_head":HEAD,
        "original_matrix_workers":24,
        "original_unique_runner_IDs":24,
        "actual_maximum_simultaneous_worker_jobs":peak,
        "requested_maximum_simultaneous_workers":20,
        "original_cold_child_results":96,
        "original_source_job_JSON_SHA256":digest(json.dumps(jobs,sort_keys=True).encode()),
        "original_actions_artifact_zip_SHA256_and_ID":listing,
        "original_worker_JSON_SHA256":originals_sha,
        "recomputed_original_same_admin_independent_audit":checked,
        "exact_zip_count":25,"archive_status":"SOURCE_ORIGINAL_25_ZIPS_24_VMS_96_CHILDREN_REPLAY_PASS",
        "external_hidden_holdout":False,
        "four_source_families_previously_seen_in_OTHER_JANUS_experiments":True,
        "new_hidden_sources":0,"new_external_Witness":0,
        "winner":"NOT_ADMITTED","original_C023_main":"UNCHANGED"
    }
    (out/"SUMMARY.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("004E4_ORIGINAL_EVIDENCE_ARCHIVED",json.dumps({
      "distinct_worker_VMs":24,"real_peak_concurrent":peak,
      "original_children":96,
      "verified_SAT":checked["original_verified_SAT"],
      "unknown_CPU_or_wall":checked["CPU_or_wall_unknown"],
      "uncertified_UNSAT":checked["solver_only_UNSAT_not_proven"],
      "hidden_external_holdout":False},sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    archive(p.parse_args().out)
