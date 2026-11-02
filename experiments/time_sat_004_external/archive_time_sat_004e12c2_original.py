#!/usr/bin/env python3
"""E12C2 exact 18 GitHub-hosted original ZIP SHA and 576-child proof archive.

Never call this a third-party witness or a champion; only preserves original
GitHub administration data and a fresh re-audit of full original SAT clauses.
"""
from __future__ import annotations
import argparse,json,os,subprocess,sys
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from urllib.request import Request,urlopen
from zipfile import ZipFile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from janus_time_sat_004e12c2_audit import audit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e12c2_cost_aware as m
REPO="Hawkar-usls/Janus-Fundamentum"
RUN=41493989350
HEAD="7113673e7a0def92fa1698c715977dfcf6a84e60"
LOCK="sat-e12c2-source-lock-before-workers"
AUDIT="sat-e12c2-original-research-audit"
def hash_bytes(raw):return sha256(raw).hexdigest()
def fetch(path):
    if not os.environ.get("GH_TOKEN"):raise AssertionError("Missing Actions token")
    q=Request("https://api.github.com"+path,headers={
        "Authorization":"Bearer "+os.environ["GH_TOKEN"],
        "Accept":"application/vnd.github+json",
        "X-GitHub-Api-Version":"1618-11-28"})
    with urlopen(q,timeout=35) as r:return json.load(r)

def archive(out):
    scientific=fetch("/repos/"+REPO+"/actions/runs/"+str(RUN))
    if (scientific["status"]!="completed" or scientific["conclusion"]!="success"
        or scientific["head_sha"]!=HEAD):
        raise AssertionError("Original SHA-locked E12C2 CI is not PASS")
    jobs=fetch("/repos/"+REPO+"/actions/runs/"+str(RUN)+"/jobs?per_page=100")
    jj=jobs["jobs"]
    if jobs["total_count"]!=18 or len(jj)!=18 or any(j["conclusion"]!="success" for j in jj):
        raise AssertionError("Original scientific run not 18/18 PASS")
    machines=[j for j in jj if j["name"].startswith("six-arm-original-cold-worker-matrix (")]
    runner_ids=[j.get("runner_id") for j in machines]
    if (len(machines)!=16 or len(set(runner_ids))!=16 or any(x is None for x in runner_ids)):
        raise AssertionError("Need 16 distinct actual hosted original worker VMs")
    events=[]
    for j in machines:
        a=datetime.fromisoformat(j["started_at"].replace("Z","+00:00")).timestamp()
        b=datetime.fromisoformat(j["completed_at"].replace("Z","+00:00")).timestamp()
        if b<=a:raise AssertionError("Invalid VM run time interval")
        events.extend([(a,+1),(b,-1)])
    peak=current=0
    for _,delta in sorted(events,key=lambda x:(x[0],x[1])):
        current+=delta;peak=max(peak,current)
    if peak>6:raise AssertionError("Simultaneous hosted VM exceeds frozen 8")
    artifacts=fetch("/repos/"+REPO+"/actions/runs/"+str(RUN)+"/artifacts?per_page=100")
    required={LOCK,AUDIT}|{"sat-e12c2-original-worker-"+os+"-"+case for os in m.HOSTS for case in m.IDS}
    if (artifacts["total_count"]!=18 or {x["name"] for x in artifacts["artifacts"]}!=required):
        raise AssertionError("Original 18 ZIP source evidence missing/unexpected")
    zipdir=out/"original-GitHub-18-ZIPs"
    source=out/"preworker-original-SAT-source-and-model-lock"
    workers=out/"original-16-worker-JSON"
    for p in (zipdir,source,workers):p.mkdir(parents=True,exist_ok=True)
    manifest={};original_audit=None
    for art in artifacts["artifacts"]:
        name=art["name"];dest=zipdir/(name+".zip")
        subprocess.run(["curl","--fail","--silent","--show-error","--retry","2",
            "--location","-H","Authorization: Bearer "+os.environ["GH_TOKEN"],
            "-H","Accept: application/vnd.github+json",
            "https://api.github.com/repos/"+REPO+"/actions/artifacts/"+str(art["id"])+"/zip",
            "-o",str(dest)],check=True)
        raw=dest.read_bytes()
        if art.get("digest")!="sha256:"+hash_bytes(raw):
            raise AssertionError("Original GitHub ZIP bytes do not match original GitHub digest")
        manifest[name]={"original_github_artifact_id":art["id"],"zip_sha256":hash_bytes(raw)}
        with ZipFile(dest) as z:
            names=z.namelist()
            if not names or any("/" in n or "\\" in n for n in names):
                raise AssertionError("Nested/traversal original ZIP member not accepted")
            data={n:z.read(n) for n in names}
        if name==LOCK:
            if set(data)!={"SOURCE_LOCK.json","SOURCE_LOCK.sha256"}:
                raise AssertionError("Frozen preworker lock ZIP missing source+model checksum")
            for n,buf in data.items():(source/n).write_bytes(buf)
        elif name==AUDIT:
            if set(data)!={"AUDIT.json"}:raise AssertionError("Missing original auditor JSON")
            original_audit=json.loads(data["AUDIT.json"])
            (out/"ORIGINAL_SAME_ADMIN_AUDIT.json").write_bytes(data["AUDIT.json"])
        else:
            if len(data)!=1 or not next(iter(data)).endswith(".json"):
                raise AssertionError("Original worker was not single source/model JSON receipt")
            n,buf=next(iter(data.items()))
            if (workers/n).exists():raise AssertionError("Duplicate source worker")
            (workers/n).write_bytes(buf)
    l,lock_sha=m.checked_lock(source/"SOURCE_LOCK.json")
    new_audit=audit(workers,source/"SOURCE_LOCK.json")
    if original_audit is None or new_audit!=original_audit:
        raise AssertionError("Independent replay of original science same-admin audit failed")
    if (new_audit["original_science_HEAD"]!=HEAD
        or new_audit["original_run_id"]!=str(RUN)
        or new_audit["original_cold_children"]!=576):
        raise AssertionError("Old archive refers to wrong original commit/run")
    summary={
       "schema":"JANUS-TIME-SAT-004E12C2-EXACT-18-ORIGINAL-ZIP-16-VM-576-COLD-ARCHIVE-V1",
       "status":"ORIGINAL_GITHUB_ZIP_SHA_AND_ALL_SOURCE_MODELS_FROZEN_576_CHILD_REAUDITED",
       "original_science_run_id":RUN,"original_science_HEAD":HEAD,
       "original_prereg_git_blob":m.BLOB,
       "source_precommitted_before_first_worker":True,
       "preworker_original_source_sha_and_model_lock_sha256":lock_sha,
       "actual_distinct_original_cloud_VM_runner_IDs":16,
       "observed_peak_concurrent_cloud_VMs":peak,
       "original_scientific_jobs":18,
       "original_github_ZIPs":18,
       "original_exact_GitHub_ZIP_SHA256":manifest,
       "original_same_admin_reaudited_science":new_audit,
       "external_independent_custodians":0,"C023_main":"UNCHANGED",
       "automatic_champion_promotion":False
    }
    (out/"SUMMARY.json").write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n")
    print("E12C2_SOURCE_SCIENCE_ORIGINAL_ARCHIVE_PASS",json.dumps({
        "VMs":16,"peak":peak,"ZIPs":18,"children":576,
        "outcomes":new_audit["original_outcomes"]},sort_keys=True))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True,type=Path)
    archive(p.parse_args().out)
