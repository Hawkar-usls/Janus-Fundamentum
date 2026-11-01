#!/usr/bin/env python3
"""Permanent original 004D3 dual-worker evidence + both new public Lights-out.

Only accepts original GitHub Actions ZIP bytes with GitHub-provided SHA-256.
Re-downloads both new original competition sources under pinned SHA from TWO
independent first-run receipts; independently verifies SAT model and original-
source GF2 UNSAT combination. Never regenerates or edits original receipts.
This certificate remains SAME-ADMIN, not portable DRUP/LRAT and not external.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import resource
import shutil
import sys
import tempfile
import zipfile

from janus_time_sat_004b_acquire import retrieve,unpack_bounded,scan_dimacs
from janus_time_sat_004b_baselines import read_cnf
from janus_time_sat_004d1_xor import (
  solve_if_exact_xor,independently_replay_unsat_combination,check_original_cnf,
)
from janus_time_sat_004d3_probe import verify_frozen_manifest,FROZEN_GIT_BLOB

SOURCE_RUN=41332411998
SOURCE_HEAD="e8440bd5aa272f058cccc70a8204f4e32c7456c6"
ARTIFACTS={
  "ubuntu-22.04":{
      "id":13093662320,
      "sha256":"444d63b2a082a11102d5b96bb40a3f055b8473ad47ac69dbc46fbda7e263d5f3"},
  "ubuntu-24.04":{
      "id":13093028948,
      "sha256":"46fb0f78b1330dedef3666864ecdbd21c66b5dfb609aef059830f79dd3550f1a"},
}
FROZEN_IDS=(
 "28dcc4119e1bbb5fbd3fdd8f4140f28d",
 "0efcbd10294eb001b16b4d126923372f"
)

def digest(b:bytes):
    return sha256(b).hexdigest()

def extract_exact_worker(archive_path,worker):
    artifact=ARTIFACTS[worker]
    b=archive_path.read_bytes()
    if digest(b)!=artifact["sha256"]:
        raise AssertionError("UNEXPECTED_EXACT_GITHUB_ARTIFACT_ZIP_SHA")
    with zipfile.ZipFile(archive_path) as archive:
        if set(archive.namelist())!={"result.json"}:
            raise AssertionError("UNEXPECTED_ORIGINAL_GITHUB_ZIP_MEMBERS")
        original=archive.read("result.json")
    j=json.loads(original)
    if (j.get("schema")!="JANUS-TIME-SAT-004D3-PUBLIC-MULTIFAMILY-SOURCE-ONLY-PILOT-V1"
        or j.get("run_id")!=str(SOURCE_RUN)
        or j.get("run_head_SHA")!=SOURCE_HEAD
        or j.get("frozen_manifest_git_blob")!=FROZEN_GIT_BLOB
        or len(j.get("results",[]))!=9):
        raise AssertionError("SOURCE_RUN_AND_9_CASE_RECEIPTS_NOT_MATCHED")
    return j,{"original_zip_SHA256":artifact["sha256"],
              "original_zip_artifact_id":artifact["id"],
              "original_receipt_json_SHA256":digest(original),
              "job":worker}

def validate_across_hosts(left,right):
    if [x["GBD_id_NOT_SHA256"] for x in left] != [
        x["GBD_id_NOT_SHA256"] for x in right]:
        raise AssertionError("FROZEN_WORKER_ORDER_DIFFERS")
    expected=verify_frozen_manifest()
    if [x["GBD_id_NOT_SHA256"] for x in left] != [
        x["GBD_database_id_NOT_SHA256"] for x in expected]:
        raise AssertionError("ORIGINAL_RESULTS_NOT_IN_PREREGISTRATION_ORDER")
    cross=[]
    for a,b in zip(left,right):
        for field in ("source_status","original_bytes_sha256","decoded_CNF_sha256",
                      "dimensions","structural_status","verdict"):
            if a.get(field)!=b.get(field):
                raise AssertionError("INDEPENDENT_TWO_WORKER_MISMATCH "+field+" "+a["family"])
        if a["source_status"]!="STRICT_DIMACS_ORIGINAL_PASS":
            raise AssertionError("ORIGINAL_9_CNF_INTEGRITY_MISSING")
        if a["original_bytes_sha256"] is None or a["decoded_CNF_sha256"] is None:
            raise AssertionError("ORIGINAL_SOURCE_SHA_MISSING")
        cross.append({
          "family":a["family"],"source_GBD_id":a["GBD_id_NOT_SHA256"],
          "source_download_sha256":a["original_bytes_sha256"],
          "decoded_CNF_sha256":a["decoded_CNF_sha256"],
          "dimensions":a["dimensions"],
          "structural_status":a["structural_status"],"verdict":a["verdict"],
        })
    for j,target in enumerate(FROZEN_IDS):
        first=left[j];second=right[j]
        if first["GBD_id_NOT_SHA256"]!=target:
            raise AssertionError("FIRST_TWO_ARE_NOT_FROZEN_LIGHTSOUT")
        if (first["structural_status"]!="EXACT_XOR_COVER_PASS" or
            second["structural_status"]!="EXACT_XOR_COVER_PASS"):
            raise AssertionError("EXPECTED_TWO_FULL_GF2_COVERS_MISSING")
        aa=first["structural_result"];bb=second["structural_result"]
        expected_verdict=("SAT_ORIGINAL_MODEL_VERIFIED" if j==0
             else "GF2_UNSAT_SAME_ADMIN_REPLAY_ONLY")
        if first["verdict"]!=expected_verdict or bb["verdict"]!=expected_verdict:
            raise AssertionError("UNEXPECTED_GF2_SAT_UNSAT_VERDICT")
        key="model" if j==0 else "xor_contradiction_equation_indices"
        if aa[key]!=bb[key]:
            raise AssertionError("TWO_HOST_SOURCE_BOUND_MODEL_OR_COMBINATION_DIFFERS")
    return cross

def archive(z22:Path,z24:Path,out:Path):
    resource.setrlimit(resource.RLIMIT_AS,(2_147_483_648,2_147_483_648))
    resource.setrlimit(resource.RLIMIT_CPU,(35,37))
    one,a=extract_exact_worker(z22,"ubuntu-22.04")
    two,b=extract_exact_worker(z24,"ubuntu-24.04")
    cross=validate_across_hosts(one["results"],two["results"])
    freeze=verify_frozen_manifest()
    out.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(z22,out/"original-actions-ubuntu22.zip")
    shutil.copyfile(z24,out/"original-actions-ubuntu24.zip")
    (out/"original-ubuntu22.json").write_text(json.dumps(one,sort_keys=True,indent=2)+"\n")
    (out/"original-ubuntu24.json").write_text(json.dumps(two,sort_keys=True,indent=2)+"\n")
    source_evidence=[]
    with tempfile.TemporaryDirectory() as d:
        tmp=Path(d)
        for index in range(2):
            candidate=freeze[index]
            id=candidate["GBD_database_id_NOT_SHA256"]
            original,info=retrieve({
              "hash":id,"official_uri":candidate["official_uri"]},tmp)
            proof=one["results"][index]
            if info["source_sha256"]!=proof["original_bytes_sha256"]:
                raise AssertionError("REACQUIRED_ORIGINAL_COMPRESSED_SHA_CHANGED")
            decoded=tmp/(id+".cnf")
            info_dec=unpack_bounded(original,decoded)
            if info_dec["uncompressed_sha256"]!=proof["decoded_CNF_sha256"]:
                raise AssertionError("REACQUIRED_ORIGINAL_DIMACS_SHA_CHANGED")
            shape=scan_dimacs(decoded)
            if shape!=proof["dimensions"]:
                raise AssertionError("REACQUIRED_DIMACS_SHAPE_CHANGED")
            rows=read_cnf(decoded,shape["n_variables"],shape["n_clauses"],
                         max_literals=120000)
            actual=solve_if_exact_xor(rows,shape["n_variables"])
            previous=proof["structural_result"]
            if actual["verdict"]!=previous["verdict"] or (
               actual["group_count"]!=previous["group_count"]):
                raise AssertionError("DIFFERENT_GF2_SOURCE_SOLVING_REPLAY")
            if index==0:
                if list(actual["model"])!=previous["model"]:
                    raise AssertionError("REPLAYED_SAT_MODEL_DIFFERENCE")
                bits=sum(1<<(abs(l)-1) for l in previous["model"] if l>0)
                if not check_original_cnf(rows,shape["n_variables"],bits):
                    raise AssertionError("SAT_MODEL_BAD_ON_ORIGINAL_CNF")
                (out/"new-lightsout-SAT-model.json").write_text(
                    json.dumps({"source_id":id,"model":previous["model"],
                    "valid_every_original_CNF_clause":True},sort_keys=True,indent=2)+"\n")
            else:
                combo=previous["xor_contradiction_equation_indices"]
                if actual["xor_contradiction_equation_indices"]!=combo:
                    raise AssertionError("REPLAYED_UNSAT_COMBINATION_DIFFERENCE")
                if not independently_replay_unsat_combination(
                   rows,shape["n_variables"],combo):
                    raise AssertionError("UNSAT_GF2_ZERO_EQUALS_ONE_REPLAY_FAILED")
                (out/"new-lightsout-UNSAT-GF2.json").write_text(
                    json.dumps({"source_id":id,
                    "source_bound_XOR_equation_indices":combo,
                    "zero_equals_one_replayed":True,
                    "portable_DRUP_LRAT":"NOT_PRODUCED",
                    "outside_GitHub_Witness":"NOT_VERIFIED"},
                    sort_keys=True,indent=2)+"\n")
            shutil.copyfile(original,out/("lightsout-"+str(index+1)+".original.download"))
            shutil.copyfile(decoded,out/("lightsout-"+str(index+1)+".original.cnf"))
            source_evidence.append({
                "GBD_id_NOT_SHA256":id,
                "original_transfer_SHA256":info["source_sha256"],
                "original_CNF_SHA256":info_dec["uncompressed_sha256"],
                "variable_count":shape["n_variables"],
                "clause_count":shape["n_clauses"],
                "XOR_equations":actual["equation_count"],
                "verdict":actual["verdict"]})
            original.unlink(missing_ok=True)
            decoded.unlink(missing_ok=True)
    saved={p.name:digest(p.read_bytes()) for p in out.iterdir() if p.is_file()}
    manifest={
      "schema":"JANUS-TIME-SAT-004D3-EXACT-ORIGINAL-9-SOURCE-2-XOR-ARCHIVE-V1",
      "status":"9_OF_9_SOURCE_SHA_CROSS_RUNNER_PASS_2_EXACT_PARITY_VERDICTS_REPLAYED",
      "original_run_id":SOURCE_RUN,
      "original_tested_HEAD":SOURCE_HEAD,
      "original_Github_artifacts":{"ubuntu22":a,"ubuntu24":b},
      "source_public_not_externally_blinded":True,
      "all_nine_source_sha256_cross_host_equality":True,
      "cross_host_case_receipts":cross,
      "exact_source_bytes_preserved_for_two_lightsout":source_evidence,
      "SAT_model_source_exact_every_original_clause":"PASS",
      "UNSAT_GF2_combination_original_source_replay":"PASS_SAME_ADMIN_NOT_DRUP",
      "any_measured_solve_time_speedup":"NOT_YET_COMPARED",
      "independent_outside_Github_witness":"OPEN",
      "production_C023":"UNCHANGED",
      "files_SHA256":saved}
    (out/"manifest.json").write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    print("004D3_ORIGINAL_DURABLE_PASS",json.dumps({
       "nine_sha_match":len(cross),"two_original_CNF":len(source_evidence),
       "model_SAT":True,"GF2_UNSAT_receipt":True,
       "original_zip_SHA_checked":2},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--zip22",required=True,type=Path)
    p.add_argument("--zip24",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    archive(args.zip22,args.zip24,args.out)
