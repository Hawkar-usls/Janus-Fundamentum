#!/usr/bin/env python3
"""TIME-SAT-004E2: preserve EXACT two-host original research CI artifacts.

Archive all successes, CPU-censored, solver-only UNSAT and negative controls.
Never reinterpret timeouts as UNSAT or compute finite speed ratios on
censored trials. Cannot establish holdout, outside-admin or generalized profit.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import shutil
import zipfile

SOURCE_CI=41419535647
TESTED_HEAD="78094eb08680916ac27f1e6bbe50a8ff44fab29c"
FROZEN_BLOB="09563db338939cb19b0bb6aab7ce56dce3eda5f2"
FAMILIES=("linear-equations","xor-shifting","minimum-disagreement-parity","binary-tree-parity")
ARMS=("adaptive_cms","noop_scan_cms","cms_original","cadical195_original","glucose4_original")
SHA={
    "linear-equations":"dd2e52c12cafa012316052c6c2ac06ea48ccf1c999a5ae57a25c5f208e1cb9bc",
    "xor-shifting":"03bae774557f351990c0348c7b11933d8760f4d7a8cf60455f1d4754fe9739c0",
    "minimum-disagreement-parity":"6e054967f4c71d900b2bba2508fea2054ac13de78fa0b0b6a94753f66e9e95fc",
    "binary-tree-parity":"8d94924bef8978b28a2bf95472556b280bef5d98b6833c6db33554098f52d2d8"
}
STATUS_OK={"SAT_ORIGINAL_CNF_MODEL_VERIFIED","UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF",
           "UNKNOWN_CPU_LIMIT_SIGXCPU","UNKNOWN_NO_ANSWER"}
N=40

def original_artifact(path,expected_sha,host):
    raw=path.read_bytes()
    actual=sha256(raw).hexdigest()
    if actual!=expected_sha:raise AssertionError("Original Actions ZIP SHA mismatch: "+host)
    with zipfile.ZipFile(path) as f:
        names=f.namelist()
        if len(names)!=1 or Path(names[0]).name!="comparison.json":
            raise AssertionError("Unexpected original Actions ZIP members")
        body=f.read(names[0])
    x=json.loads(body)
    if (x.get("schema")!="JANUS-TIME-SAT-004E2-PRESEEN-MULTIFAMILY-FULL-COST-SAFE-GATE-2026-11-02-V1"
        or x.get("frozen_policy_blob")!=FROZEN_BLOB
        or str(x.get("github_run_id"))!=str(SOURCE_CI)
        or x.get("github_head")!=TESTED_HEAD
        or x.get("total_expected_trials_per_host")!=N
        or x.get("repeats")!=2 or x.get("declared_gate_threshold_fraction")!=0.8
        or x.get("cpu_limit_seconds")!=6 or x.get("wall_limit_seconds")!=10
        or x.get("zero_hidden_instances") is not True
        or x.get("production_C023")!="UNCHANGED"
        or x.get("external_independent_004C_Witness")!="OPEN"):
        raise AssertionError("Source CI policy/head/resource/claim drift: "+host)
    if tuple(x.get("arms",[]))!=ARMS or len(x.get("records",[]))!=N:
        raise AssertionError("Original source arms or trial count changed")
    found=set();counts={}
    for r in x["records"]:
        family=r["family"];arm=r["arm"];rep=r["repeat"]
        if (family not in FAMILIES or arm not in ARMS or rep not in (0,1)
            or (family,rep,arm) in found):
            raise AssertionError("Missing/duplicate/unregistered source arm")
        found.add((family,rep,arm))
        result=r["outcome"]
        state=result.get("status",result.get("verdict","MISSING"))
        if state not in STATUS_OK:
            raise AssertionError("Unreported broken child/abstention: "+str(state))
        if result.get("source_sha256",SHA[family])!=SHA[family]:
            raise AssertionError("Original CNF SHA mismatch in worker result")
        if state=="SAT_ORIGINAL_CNF_MODEL_VERIFIED":
            if result.get("all_SAT_models_checked_on_original_CNF") is not True:
                raise AssertionError("Original SAT model replay unverified")
        if family=="binary-tree-parity" and state=="UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF":
            raise AssertionError("Unverified UNSAT contradicts archived true SAT")
        cell=counts.setdefault(family,{}).setdefault(arm,Counter())
        cell[state]+=1
        if arm in ("adaptive_cms","noop_scan_cms") and state in ("SAT_ORIGINAL_CNF_MODEL_VERIFIED","UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF"):
            d=result["gate"]
            wanted="native_xor_CMS" if family=="binary-tree-parity" and arm=="adaptive_cms" else "raw_CMS"
            if d.get("choose")!=wanted:
                raise AssertionError("Frozen coverage-only decision drift")
        if state=="SAT_ORIGINAL_CNF_MODEL_VERIFIED" and arm not in ("adaptive_cms","noop_scan_cms"):
            # Raw arms do not claim they ran an XOR extraction.
            if result.get("source_scan_and_extraction_wall_seconds")!=0:
                raise AssertionError("Raw arm unexpectedly preprocessed source")
    if len(found)!=N:raise AssertionError("Original CI missing trials")
    per_family={}
    for family in FAMILIES:
        per_family[family]={}
        for arm in ARMS:
            per_family[family][arm]=dict(counts.get(family,{}).get(arm,Counter()))
            if sum(per_family[family][arm].values())!=2:
                raise AssertionError("One original trial missing in specific arm")
    return body,per_family

def main(zip22,sha22,id22,zip24,sha24,id24,out):
    b22,m22=original_artifact(zip22,sha22,"ubuntu22")
    b24,m24=original_artifact(zip24,sha24,"ubuntu24")
    out.mkdir(parents=True,exist_ok=True)
    for name,binary in (
        ("original-actions-ubuntu22.zip",zip22.read_bytes()),
        ("original-actions-ubuntu24.zip",zip24.read_bytes()),
        ("original-ubuntu22.json",b22),("original-ubuntu24.json",b24)):
        (out/name).write_bytes(binary)
    source={
      "schema":"JANUS-TIME-SAT-004E2-ORIGINAL-COLD-COST-CENSORED-DUAL-UBUNTU-ARCHIVE-V1",
      "status":"PERFORMANCE_CALIBRATION_ON_FOUR_PRESEEN_PUBLIC_FAMILIES_NO_EXTERNAL_HOLDOUT",
      "scientific_head_tested":TESTED_HEAD,
      "source_original_CI":SOURCE_CI,
      "source_CI_original_artifact_ids":{"ubuntu22":id22,"ubuntu24":id24},
      "source_CI_original_artifact_SHA256":{"ubuntu22":sha22,"ubuntu24":sha24},
      "original_file_SHA256":{f.name:sha256(f.read_bytes()).hexdigest() for f in out.iterdir() if f.is_file()},
      "frozen_policy_blob":FROZEN_BLOB,
      "cases":list(FAMILIES),
      "five_controls":list(ARMS),
      "total_two_runner_trials":2*N,
      "two_host_outcomes":{"ubuntu22":m22,"ubuntu24":m24},
      "CPU_timeouts_are_unknown_not_UNSAT":True,
      "finite_speedup_ratio_if_any_comparator_censored":"NOT_DEFINED",
      "no_holdout_or_population_predictive_claim":True,
      "adaptive_gate_training_leak":"KNOWN_PRESEEN_BINARY_TREE_DEVELOPMENT_ONLY",
      "new_external_SAT_evidence":0,
      "external_004C_Witness":"OPEN",
      "independent_004E2_admission":"NOT_ESTABLISHED",
      "production_C023_main":"UNCHANGED",
      "paid_Rowan":"NONE",
      "interpretation":"Do not cherry-pick binary-tree; compare all four family raw/scan+raw/adaptive outcomes and retain negative and timeout rows. Gate is an engineering prototype NOT proven net-profit prediction."
    }
    (out/"summary.json").write_text(json.dumps(source,sort_keys=True,indent=2)+"\n")
    print("004E2_EXACT_ORIGINAL_ARCHIVE_PASS",json.dumps({
        "two_hosts":2,"original_trials":2*N,"external_witness":0,
        "production_C023":"UNCHANGED"},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for name in ("zip22","sha22","id22","zip24","sha24","id24","out"):
        p.add_argument("--"+name,required=True,type=Path if name in ("zip22","zip24","out") else int if name.startswith("id") else str)
    x=p.parse_args()
    main(x.zip22,x.sha22,x.id22,x.zip24,x.sha24,x.id24,x.out)
