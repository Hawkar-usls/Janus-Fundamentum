#!/usr/bin/env python3
"""Source-pin E9 original 16 GitHub VMs, 160 subprocesses, precommitted E8 model.

Verify all SHA256 of ORIGINAL Actions ZIPs, reproduce independent audit
without copying test outcomes into training, then archive on research only.
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
from janus_time_sat_004e9_audit import audit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e9_cost_to_observe as m

RUN=41460961558
HEAD="c4974f14f63e82b5d0c70f53d6ed5cc2e2eea7b3"
REPO="Hawkar-usls/Janus-Fundamentum"
PREFLIGHT="sat-e9-frozen-before-validation-model"
AUDIT="sat-e9-original-science-audit"

def sha(data):return sha256(data).hexdigest()

def get(url):
    request=Request("https://api.github.com"+url,headers={
        "Authorization":"Bearer "+os.environ["GH_TOKEN"],
        "Accept":"application/vnd.github+json",
        "X-GitHub-Api-Version":"2022-11-28"})
    with urlopen(request,timeout=30) as handle:return json.load(handle)

def run_archive(output):
    report=get("/repos/"+REPO+"/actions/runs/"+str(RUN))
    if (report["head_sha"]!=HEAD or report["status"]!="completed"
        or report["conclusion"]!="success"):
        raise AssertionError("004E9 original scientific run not complete with same tested SHA")
    jobs=get("/repos/"+REPO+"/actions/runs/"+str(RUN)+"/jobs?per_page=100")
    j=jobs["jobs"]
    if jobs["total_count"]!=18 or len(j)!=18 or any(x["conclusion"]!="success" for x in j):
        raise AssertionError("Expected one E8-only frozen calibration + 16 source VMs + one auditor")
    workers=[x for x in j if x["name"].startswith("candidate-and-original-controls (")]
    if len(workers)!=16 or len({x["runner_id"] for x in workers})!=16 or any(
        not x.get("runner_id") for x in workers):
        raise AssertionError("16 actual distinct GitHub hosted challenger VMs required")
    events=[]
    for x in workers:
        if not x["started_at"] or not x["completed_at"]:
            raise AssertionError("Missing original GitHub VM execution timestamps")
        s=datetime.fromisoformat(x["started_at"].replace("Z","+00:00")).timestamp()
        e=datetime.fromisoformat(x["completed_at"].replace("Z","+00:00")).timestamp()
        if e<=s:raise AssertionError("Invalid actual GitHub job interval")
        events.extend([(s,1),(e,-1)])
    cur=peak=0
    for _,change in sorted(events,key=lambda x:(x[0],x[1])):
        cur+=change;peak=max(cur,peak)
    if not 1<=peak<=8:raise AssertionError("Runner scheduling peak outside preregistered bounds")
    out=get("/repos/"+REPO+"/actions/runs/"+str(RUN)+"/artifacts?per_page=100")
    artifacts=out["artifacts"]
    names={a["name"] for a in artifacts}
    expected={PREFLIGHT,AUDIT}|{
        "sat-e9-worker-"+host+"-"+case
        for host in m.HOSTS for case in m.IDS}
    if (names!=expected or len(artifacts)!=18 or out["total_count"]!=18):
        raise AssertionError("Original model preflight, 16 workers, auditor ZIPs required")
    output.mkdir(parents=True,exist_ok=True)
    zip_folder=output/"original-github-Actions-ZIPs"
    proof_dir=output/"original-16-worker-JSON"
    model_dir=output/"original-frozen-E8-model"
    for p in (zip_folder,proof_dir,model_dir):p.mkdir(exist_ok=True)
    file_zips={}
    original_audit=None
    for a in artifacts:
        name=a["name"]
        dest=zip_folder/(name+".zip")
        subprocess.run(["curl","--fail","--silent","--show-error","--retry","2",
            "--location","-H","Authorization: Bearer "+os.environ["GH_TOKEN"],
            "-H","Accept: application/vnd.github+json",
            "https://api.github.com/repos/"+REPO+"/actions/artifacts/"+str(a["id"])+"/zip",
            "-o",str(dest)],check=True,stdout=subprocess.DEVNULL)
        raw=dest.read_bytes()
        if a.get("digest")!="sha256:"+sha(raw):
            raise AssertionError("Actual original GitHub Actions ZIP digest mismatch")
        file_zips[name]={"id":a["id"],"zip_sha256":sha(raw)}
        with ZipFile(dest) as z:
            paths=z.namelist()
            if not paths or any("/" in p or "\\" in p for p in paths):
                raise AssertionError("No nested original ZIP contents permitted")
            members={p:z.read(p) for p in paths}
        if name==PREFLIGHT:
            if set(members)!={"MODEL.json","MODEL.sha256"}:
                raise AssertionError("Original model + SHA file both required before validation")
            for p,data in members.items():(model_dir/p).write_bytes(data)
        elif name==AUDIT:
            if set(members)!={"AUDIT.json"}:
                raise AssertionError("Original independent audit ZIP unexpected")
            original_audit=json.loads(members["AUDIT.json"])
            (output/"ORIGINAL_SCIENCE_AUDIT.json").write_bytes(members["AUDIT.json"])
        else:
            if len(members)!=1 or not next(iter(members)).endswith(".json"):
                raise AssertionError("Not exactly one original worker receipt in ZIP")
            p,data=next(iter(members.items()))
            if (proof_dir/p).exists():raise AssertionError("Duplicate original worker JSON")
            (proof_dir/p).write_bytes(data)
    model,modelsha=m.checked_model(model_dir/"MODEL.json")
    if original_audit is None:raise AssertionError("Source auditor JSON missing")
    reread=audit(proof_dir,model_dir/"MODEL.json")
    if reread!=original_audit:
        raise AssertionError("Original independent audit not reproducible from original ZIP JSON")
    if (reread["original_source_run"]!=str(RUN)
        or reread["original_source_scientific_HEAD"]!=HEAD
        or reread["original_cold_child_outcomes"]!=160):
        raise AssertionError("Wrong tested original source identity")
    final={
      "schema":"JANUS-TIME-SAT-004E9-SHA-VERIFIED-ORIGINAL-E8-TRAIN-16-VM-VALIDATION-ARCHIVE-V1",
      "status":"EXACT_ORIGINAL_18_ACTIONS_ZIPS_16_VMS_160_CHILDREN_MODEL_BEFORE_TEST_VERIFIED",
      "original_scientific_run":RUN,"original_tested_HEAD":HEAD,
      "original_E8_training_run":41454451078,"frozen_protocol_git_blob":m.PLAN_BLOB,
      "model_SHA256":modelsha,"trained_model_groups":8,
      "same_generator_new_seed_validation_cases":6,
      "training_overlap_public_regression_cases":2,
      "observed_real_GitHub_VM_IDs":16,
      "observed_peak_simultaneous_VMs":peak,
      "original_total_GitHub_jobs":18,
      "original_artifact_ZIP_count":18,
      "all_original_artifact_ZIP_digests":file_zips,
      "original_audit_recomputed":reread,
      "scientific_limit":"Only six NEW SEEDS under SAME INTERNAL planted SAT generators, two already E8-trained public CNFs; not external independent unknown source test",
      "automatic_champion_promotion":"FORBIDDEN",
      "C023_main":"UNCHANGED"
    }
    (output/"SUMMARY.json").write_text(json.dumps(final,sort_keys=True,indent=2)+"\n")
    print("004E9_ORIGINAL_SOURCE_ARCHIVE_PASS",json.dumps({
       "original_workers":16,"peak":peak,"children":160,"zips":18,
       "SAT":reread["all_verdicts"].get(m.SAT,0)},sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    run_archive(ap.parse_args().out)
