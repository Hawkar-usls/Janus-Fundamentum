#!/usr/bin/env python3
"""004D7 archive exact ORIGINAL cloud artifacts and check P-center UNSAT gate.

New linear rank on UNSAT CNF is not actionable evidence of added useful
information: inconsistent CNF entails all equations. The old source DRUP
is independently replayed again, not trusted merely by name or label.
No SAT engine or production changes. Original CI ZIP bytes preserved.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path,PurePosixPath
import shutil
import sys
import zipfile

HERE=Path(__file__).resolve().parents[1]/"direct"
sys.path.insert(0,str(HERE))
from janus_time_sat_004b_baselines import read_cnf
from janus_time_sat_003_drup_witness import verify_drup

RUN=41360542574
HEAD="df9732cfff128cb0e3a94558445fc73abbe30c80"
ZIPS={
 "ubuntu22":{"id":13104893052,
             "sha256":"795b3b4dfcfd7a83a205289b6b350c8afdc656874ff096c21b3986bf3a4ca3a1"},
 "ubuntu24":{"id":13105021725,
             "sha256":"00dcca234ff38dee39f16fe50a30d435df75148e096eaf9fb9c6ca12bebf9554"}
}
ROOT=Path("experiments/time_sat_004_external")
FROZEN=ROOT/"PREREGISTERED_004D7_NEW_SOURCE_RANK_GATE_20261102.json"
OLD=ROOT/"pcenter_011984fd82_verified"
EXPECTED_RANK={"or_randxor":0,"greentao":0,"p-center":2}
EXPECTED_SOURCES={"or_randxor":(0,0,16),
                  "greentao":(0,0,0),
                  "p-center":(2,2,2000)}

def sha(b):return sha256(b).hexdigest()

def member(z,name):
    candidates=[p for p in z.namelist() if PurePosixPath(p).name==name]
    if len(candidates)!=1:raise AssertionError("missing/ambiguous exact original artifact "+name)
    return z.read(candidates[0])

def verify_original_zip(path,worker,original_candidates):
    if sha(path.read_bytes())!=ZIPS[worker]["sha256"]:
        raise AssertionError("ORIGINAL_GITHUB_ACTIONS_ZIP_SHA_MISMATCH")
    with zipfile.ZipFile(path) as z:
        report_raw=member(z,"summary.json")
        report=json.loads(report_raw)
        if (report["schema"]!="JANUS-TIME-SAT-004D7-THREE-SHA-FROZEN-NEW-TO-RESOLUTION-PUBLIC-SOURCES-V1"
            or report["n_completed"]!=3 or str(report["run_id"])!=str(RUN)
            or report["head_sha"]!=HEAD or len(report["cases"])!=3):
            raise AssertionError("ORIGINAL_RUN_OR_HEAD_SOURCE_IDENTITY_MISMATCH")
        facts={}
        for c,selected in zip(report["cases"],original_candidates):
            family=c["family"]
            if (family!=selected["family"] or
                c["declared_original_SHA256"]!=selected["original_decoded_CNF_sha256"]
                or c["status"]!="SOURCE_PROOF_AND_GF2_RANK_PASS"):
                raise AssertionError("ORIGINAL_REPORT_DIFFERENT_COHORT")
            verdict=c["result"]
            rank=EXPECTED_SOURCES[family]
            if (verdict.get("rank_increment_coeff")!=rank[0]
                or verdict.get("rank_increment_augmented")!=rank[1]
                or verdict.get("resolvents")!=rank[2]):
                raise AssertionError("ORIGINAL_GITHUB_COMPARISON_DIFFERENT")
            raw_cnf=member(z,selected["GBD_id_NOT_SHA256"]+".original.cnf")
            original_transfer=member(z,selected["GBD_id_NOT_SHA256"]+".download")
            if (sha(raw_cnf)!=selected["original_decoded_CNF_sha256"] or
                sha(original_transfer)!=selected["original_transfer_sha256"]):
                raise AssertionError("ORIGINAL_COMPETITION_SOURCE_CHANGED")
            detail=member(z,family+"-exact-rank.json")
            if sha(detail)!=verdict["source_proof_file_sha256"]:
                raise AssertionError("ORIGINAL_RESOLUTION_PROOF_SHA_MISMATCH")
            j=json.loads(detail)
            if (j["family"]!=family or j["original_SHA256"]!=selected["original_decoded_CNF_sha256"]
                or j["rank_diagnostic"]["verification"]!="EXACT_ORIGINAL_SOURCE_CLAUSE_DAG_REPLAY_PASS"
                or j["rank_diagnostic"]["independent_rank_analysis"]["independent_new_augmented_rank"]!=rank[1]):
                raise AssertionError("ORIGINAL_DETAIL_NOT_SOURCE_BOUND")
            facts[family]={
               "source_GBD":selected["GBD_id_NOT_SHA256"],
               "source_CNF_SHA256":sha(raw_cnf),"original_transfer_SHA256":sha(original_transfer),
               "resolution_DAG_detail_SHA256":sha(detail),
               "new_GF2_coefficient_rank":rank[0],
               "new_GF2_augmented_rank":rank[1],
               "raw_original_resolvents":rank[2],
               "verified_original_source_and_DAG":True
            }
        return report_raw,facts

def proven_unsat_original_pcenter():
    m=json.loads((OLD/"manifest.json").read_text())
    if (m["independent_RUP_replay"]!="PASS"
        or m["empty_clause_verified"] is not True):
        raise AssertionError("Original older P-center has no verified proof claim")
    cnf=(OLD/"original.cnf").read_bytes()
    proof=(OLD/"original.drup").read_bytes()
    if (sha(cnf)!=m["files_SHA256"]["original.cnf"] or
        sha(proof)!=m["files_SHA256"]["original.drup"] or
        sha(cnf)!=m["original_uncompressed_CNF_SHA256"]):
        raise AssertionError("P-center old proof or original CNF changed")
    rows=read_cnf(OLD/"original.cnf",m["source_cnf_n"],m["source_cnf_clauses"])
    check=verify_drup(rows,proof.decode("ascii").splitlines(),
                      timeout_seconds=30,max_steps=10000,max_resident_clauses=30000)
    if (check.status!="INDEPENDENT_RUP_REPLAY_PASS"
        or check.complete_empty_clause is not True
        or check.additions_checked!=7):
        raise AssertionError("NO_VERIFIED_ORIGINAL_PCENTER_UNSAT")
    return {"original_CNF_SHA256":sha(cnf),
            "original_DRUP_SHA256":sha(proof),
            "original_source_GBD_ID":m["original_gbd_id_NOT_sha256"],
            "independent_UCP_additions":check.additions_checked,
            "deletions_ignored":check.deletions_ignored,
            "final_empty_clause_replayed":True,
            "same_GitHub_administrator":True}

def gate_for_performance(*,new_rank,verified_original_sat_model,verified_original_unsat):
    if verified_original_unsat:
        return "BLOCK_UNSAT_ORIGINAL_ENTAILS_EVERY_GF2_EQUATION"
    if not verified_original_sat_model:
        return "BLOCK_NO_VERIFIED_SAT_SOURCE_ORIGINAL_MODEL"
    if new_rank<=0:
        return "BLOCK_NO_NEW_INDEPENDENT_GF2_RANK"
    return "POTENTIAL_FUTURE_BENCHMARK_ONLY_AFTER_EXTERNAL_WITNESS_AND_PREREG"

def archive(z22,z24,out):
    original_cases=json.loads(FROZEN.read_text())["original_cases"]
    raw22,left=verify_original_zip(z22,"ubuntu22",original_cases)
    raw24,right=verify_original_zip(z24,"ubuntu24",original_cases)
    if left!=right:
        raise AssertionError("Original two workers disagree on source witnesses or rank")
    unsat=proven_unsat_original_pcenter()
    pcenter=next(c for c in original_cases if c["family"]=="p-center")
    if unsat["original_CNF_SHA256"]!=pcenter["original_decoded_CNF_sha256"]:
        raise AssertionError("P-center UNSAT proof belongs to DIFFERENT source")
    classifications={
        "p-center":gate_for_performance(new_rank=2,
            verified_original_sat_model=False,verified_original_unsat=True),
        "or_randxor":gate_for_performance(new_rank=0,
            verified_original_sat_model=False,verified_original_unsat=False),
        "greentao":gate_for_performance(new_rank=0,
            verified_original_sat_model=False,verified_original_unsat=False)
    }
    if classifications["p-center"]!="BLOCK_UNSAT_ORIGINAL_ENTAILS_EVERY_GF2_EQUATION":
        raise AssertionError("meaningless GF2 rank incorrectly admitted")
    out.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(z22,out/"original-actions-ubuntu22.zip")
    shutil.copyfile(z24,out/"original-actions-ubuntu24.zip")
    (out/"original-ubuntu22.json").write_bytes(raw22)
    (out/"original-ubuntu24.json").write_bytes(raw24)
    d={
        "schema":"JANUS-TIME-SAT-004D7-EXACT-ORIGINAL-WORKERS-AND-PCENTER-UNSAT-CONSISTENCY-V1",
        "status":"ORIGINAL_DUAL_HOST_PROOF_RANK_PASS_TWO_GF2_UNIT_CONSEQUENCES_NOT_ACTIONABLE_CERTIFIED_UNSAT",
        "original_run":RUN,"original_tested_HEAD":HEAD,
        "original_CI_ZIP_SHA256":ZIPS,
        "three_original_sources_and_replayed_proof_DAGs":left,
        "same_admin_original_Pcenter_UNSAT_DRUP_rechecked_again":unsat,
        "true_new_rank_relative_to_original_EXPLICIT_XOR_at_pcenter":2,
        "usable_new_rank_on_original_verified_SAT_tasks":0,
        "critical_logic":"Since the original P-center CNF has a verified UNSAT proof, it entails ALL equations; two independent GF2 unit expressions cannot prove useful algorithmic progress on a satisfiable problem.",
        "prospective_speed_benchmark_eligibility":classifications,
        "non_Pcenter_catalog_UNSAT_labels":"UNVERIFIED_CATALOG_ONLY_NO_SAT_UNSAT_CLAIM",
        "proof_of_original_pcenter_UNSAT_external_admin":"NOT_DONE",
        "solver_benchmark_run":"NO",
        "C023_main":"UNCHANGED",
        "original_files_SHA256":{p.name:sha(p.read_bytes()) for p in out.iterdir() if p.is_file()}
    }
    (out/"summary.json").write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print("004D7_PROOF_AWARE_ARCHIVE_PASS",json.dumps({
       "original_workers":2,"new_rank_on_pcenter":2,
       "verified_pcenter_UNSAT":True,
       "admissible_new_GF2_on_verified_SAT":0,
       "new_benchmark_started":False},sort_keys=True))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--zip22",required=True,type=Path)
    parser.add_argument("--zip24",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    archive(args.zip22,args.zip24,args.out)
