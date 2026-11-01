#!/usr/bin/env python3
"""TIME-SAT-004D8: immutable original two-host SAT models / proof archive.

Never generate fake CI receipts. Fetch original GH Actions ZIPs by ID and
validate GitHub-reported SHA256, original CI run/head, exact original DIMACS
and full signed models on both workers; replay all resolution and GF2 rank.
Persist original JSON + ZIP and original lights-out CNF + transfer SHA.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
from janus_time_sat_004b_acquire import retrieve,unpack_bounded,scan_dimacs
from janus_time_sat_004b_baselines import read_cnf
from janus_time_sat_004d8_sat_gate import certified_model,gate_rank_for_sat
from janus_time_sat_004d7_rank_gate import source_rank_experiment

ROOT=Path("experiments/time_sat_004_external")
FROZEN=ROOT/"PREREGISTERED_004D8_VERIFIED_SAT_MODEL_FIRST_20261102.json"
TREE=ROOT/"time_sat_004d4b_evidence"
RUN=41363901306
HEAD="f592bf67f539c37937bbd23753168b3d77f77a99"
SOURCE_BLOB="d4a9f9aede966e2caf057da843a9183edfacf2af"
ZIPS={
  "ubuntu22":{"id":13105359637,"sha256":"3c40b08fc9f27f0d07fa2333d4d2f48c4374cecc466dfe9da36a847ac67d62f2"},
  "ubuntu24":{"id":13106606147,"sha256":"feaf536e5402b20db7dd49c6cc9259f1fc05b773e46af6ca1db2e05b1ad64d91"}
}
FAMILIES=["binary-tree-parity","lights-out"]


def digest(data):
    return sha256(data).hexdigest()


def zip_read(path,host):
    raw=path.read_bytes()
    if digest(raw)!=ZIPS[host]["sha256"]:
        raise AssertionError("original ZIP sha changed "+host)
    results={}
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            short=Path(name).name
            if short in ("summary.json",*[c+".result.json" for c in FAMILIES]):
                if short in results:raise AssertionError("duplicate original ZIP path")
                results[short]=archive.read(name)
        if set(results)!={"summary.json",*[c+".result.json" for c in FAMILIES]}:
            raise AssertionError("incomplete original artifact")
    summary=json.loads(results["summary.json"])
    if (summary["schema"]!="JANUS-TIME-SAT-004D8-MODEL-FIRST-FROZEN-ORIGINAL-TWO-CASE-V1"
         or summary["registration_git_blob"]!=SOURCE_BLOB
         or str(summary["run_id"])!=str(RUN)
         or summary["run_head"]!=HEAD
         or len(summary["cases"])!=2):
        raise AssertionError("wrong original CI identity, HEAD or frozen source")
    for c in FAMILIES:
        d=json.loads(results[c+".result.json"])
        if (d["family"]!=c or d["status"]!="SAT_MODEL_AND_SOURCE_PROOF_VERIFIED"
            or d["original_SAT_certification"]["status"]!="SAT_VERIFIED_EVERY_ORIGINAL_CLAUSE"
            or d["all_derived_XOR_checked_against_SAT_model"] is not True):
            raise AssertionError("original model not source certified "+c)
    return results


def archive(zip22,zip24,out):
    two={"ubuntu22":zip_read(zip22,"ubuntu22"),
         "ubuntu24":zip_read(zip24,"ubuntu24")}
    cases=json.loads(FROZEN.read_text())["registered_cases"]
    out.mkdir(parents=True,exist_ok=True)
    light_meta=cases[1]
    src_download,info=retrieve(
        {"hash":light_meta["GBD_ID_NOT_SHA256"],
         "official_uri":"http://benchmark-database.de/file/"+light_meta["GBD_ID_NOT_SHA256"]},
        out)
    if info["source_sha256"]!=light_meta["source_transfer_SHA256"]:
        raise AssertionError("archiving HTTPS source transfer differs from frozen prior")
    light=out/"lights-out.original.cnf"
    data=unpack_bounded(src_download,light)
    if data["uncompressed_sha256"]!=light_meta["original_decoded_CNF_SHA256"]:
        raise AssertionError("original decoded lights-out source SHA mismatch")
    src_download.rename(out/"lights-out.original.download")
    original_sources={
       "binary-tree-parity":TREE/(cases[0]["GBD_ID_NOT_SHA256"]+".original.cnf"),
       "lights-out":light
    }
    receipts=[]
    for case in cases:
        family=case["family"]
        source=original_sources[family]
        if digest(source.read_bytes())!=case["original_decoded_CNF_SHA256"]:
            raise AssertionError("exact original SHA mismatch "+family)
        dims=scan_dimacs(source)
        for key,expect in (("n_variables",case["n"]),("n_clauses",case["m"]),
                           ("n_literal_occurrences",case["literals"])):
            if dims[key]!=expect:raise AssertionError("original source dimensions changed")
        rows=read_cnf(source,case["n"],case["m"],max_literals=120000)
        left=json.loads(two["ubuntu22"][family+".result.json"])
        right=json.loads(two["ubuntu24"][family+".result.json"])
        for v in (left,right):
            cert=certified_model(rows,case["n"],v["signed_model"])
            if cert["status"]!="SAT_VERIFIED_EVERY_ORIGINAL_CLAUSE":
                raise AssertionError("original persisted model violates CNF "+family)
            if cert["signed_model_SHA256"]!=v["original_SAT_certification"]["signed_model_SHA256"]:
                raise AssertionError("original claimed model digest mismatch")
            rerank=source_rank_experiment(rows,case["n"])
            if rerank["status"]!="SOURCE_PROOF_REPLAY_AND_EXACT_GF2_RANK_PASS":
                raise AssertionError("resolution proof invalid")
            for name in ("original_complete_mask_XOR_count","source_derived_new_syntactic_XOR_count"):
                if rerank[name]!=v["rank_analysis"][name]:
                    raise AssertionError("original structural result changed")
            if rerank["independent_rank_analysis"]!=v["rank_analysis"]["independent_rank_analysis"]:
                raise AssertionError("GF2 independence records changed")
            for eq in v["rank_analysis"]["additional_parity_keys"]:
                assignment={abs(i):i>0 for i in v["signed_model"]}
                if sum(int(assignment[i]) for i in eq["variables"])%2!=eq["rhs"]:
                    raise AssertionError("derived original source XOR violates SAT model")
        if left["signed_model"]!=right["signed_model"]:
            raise AssertionError("original workers have divergent signed model")
        if left["rank_gate"]!=right["rank_gate"]:
            raise AssertionError("original workers have divergent rank gates")
        if left["rank_analysis"]["resolution_evidence"]!=right["rank_analysis"]["resolution_evidence"]:
            raise AssertionError("original workers have divergent resolution DAG")
        receipts.append({
            "family":family,"source_CNF_SHA256":case["original_decoded_CNF_SHA256"],
            "original_SAT_certified_full_clauses":len(rows),
            "SAT_model_SHA256":left["original_SAT_certification"]["signed_model_SHA256"],
            "two_host_identical_model_and_DAG":True,
            "original_verified_SAT":True,
            "new_XOR_forms":left["rank_analysis"]["source_derived_new_syntactic_XOR_count"],
            "additional_GF2_coefficient_rank":left["rank_analysis"]["independent_rank_analysis"]["independent_new_coefficient_rank"],
            "additional_GF2_augmented_rank":left["rank_analysis"]["independent_rank_analysis"]["independent_new_augmented_rank"],
            "rank_gate":left["rank_gate"],
            "source_replay_at_archive":"PASS"
        })
    for host,path in (("ubuntu22",zip22),("ubuntu24",zip24)):
        shutil.copyfile(path,out/("original-actions-"+host+".zip"))
        for name,raw in two[host].items():
            (out/("original-"+host+"-"+name)).write_bytes(raw)
    summary={
       "schema":"JANUS-TIME-SAT-004D8-EXACT-SAT-MODEL-ORIGINAL-TWO-HOST-ARCHIVE-V1",
       "status":"TWO_ORIGINAL_SAT_MODELS_SOURCE_VERIFIED_ZERO_NEW_INDEPENDENT_GF2_RANK",
       "original_CI":RUN,"original_HEAD":HEAD,
       "source_preregistration_git_blob":SOURCE_BLOB,
       "original_two_workers":"PASS",
       "exact_original_actions_ZIP_SHA256":ZIPS,
       "original_SAT_model_CNF_replay":"PASS_ON_BOTH_WORKERS_AND_ARCHIVER",
       "independent_resolution_DAG_replay":"PASS_SAME_ADMIN",
       "SAT_verified_count":2,
       "positive_incremental_GF2_rank_count":0,
       "case_receipts":receipts,
       "source_only_no_CDCL_benchmark":True,
       "external_independent_Witness":"OPEN",
       "production_C023":"UNCHANGED",
       "file_SHA256":{p.name:digest(p.read_bytes()) for p in out.iterdir() if p.is_file()}
    }
    (out/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("004D8_DURABLE_SAT_ARCHIVE_PASS",json.dumps({
       "hosts":2,"verified_sat_originals":2,
       "rank_positive":0,
       "external_witness":False,"source_only":True},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--zip22",type=Path,required=True)
    p.add_argument("--zip24",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    archive(a.zip22,a.zip24,a.out)
