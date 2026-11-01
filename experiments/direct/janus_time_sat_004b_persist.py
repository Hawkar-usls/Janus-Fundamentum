#!/usr/bin/env python3
"""004B: immutable first SCREENING evidence from exact original Actions bytes.

Keep BOTH raw JSON files intact. Add independently recomputed scientific
interpretation where SIGXCPU(-24) is UNKNOWN_CPU_LIMIT, never an algorithmic
error or UNSAT. Original downloaded benchmark bytes are NOT inside this
artifact, so published SHA are *first-party captured TLS download SHA*, not
a pre-published signed origin hash. GBD 32-hex ID != SHA256.
"""
from __future__ import annotations
from hashlib import sha256
import argparse
import json
from pathlib import Path
import shutil
import zipfile

ORIGINAL_SHA="13edc87fb7c5d6843ac3478e44ac404e9fcf048878cd697bfe0caf54af8f2638"
ORIGINAL_ARTIFACT_ID=13090195696
ORIGINAL_RUN=41322622378
ORIGINAL_RUN_HEAD="293a5f665938bb07b018833e9532668037d21b49"
PREREG_BLOB_SHA="dc658d57453813bb306aa20f45b3385571f1fe3d"
EXPECTED_LABELS={"sat":4,"unsat":4,"unknown":4}


def digest(x:bytes):return sha256(x).hexdigest()


def archive(original_zip:Path,out:Path,prereg:Path):
    blob=original_zip.read_bytes()
    if digest(blob)!=ORIGINAL_SHA:
        raise AssertionError("ORIGINAL_GITHUB_ACTIONS_ARTIFACT_DIGEST_MISMATCH")
    with zipfile.ZipFile(original_zip) as archive:
        if set(archive.namelist())!={"acquisition.json","screen.json"}:
            raise AssertionError("ORIGINAL_ARTIFACT_MISSING_OR_UNEXPECTED_MEMBERS")
        a_raw=archive.read("acquisition.json")
        s_raw=archive.read("screen.json")
    a=json.loads(a_raw);s=json.loads(s_raw)
    j=json.loads(prereg.read_text())
    if (a["registered_candidates"]!=12 or a["retrieved"]!=12 or
        len(a["results"])!=12 or len(s["per_candidate"])!=12 or
        s["candidate_count"]!=12):
        raise AssertionError("WRONG_CANDIDATE_OR_RETRIEVAL_COUNT")
    metas={x["hash"]:x for x in j["candidates"]}
    records=[]
    labels={"sat":0,"unsat":0,"unknown":0}
    valid=ready=cpu=unsat_only=skipped=0
    for original,trial in zip(a["results"],s["per_candidate"]):
        id=original["GBD_database_ID_NOT_SHA256"]
        if (id not in metas or trial["GBD_database_ID_NOT_SHA256"]!=id or
            original["family"]!=metas[id]["family"] or
            original["upstream_label_UNVERIFIED"]!=metas[id]["result"]):
            raise AssertionError("FROZEN_PREREG_OR_ORDER_MISMATCH")
        labels[metas[id]["result"]]+=1
        if original["status"]!="SOURCE_FETCHED_DIMACS_VALID":
            raise AssertionError("SOURCE_NOT_VALIDATED "+id)
        valid+=1
        if len(original["source_sha256"])!=64 or len(original["uncompressed_sha256"])!=64:
            raise AssertionError("SOURCE_HASHES_MISSING")
        if original["solver_status"]=="READY_FOR_STRICT_BASELINE":
            ready+=1
        else:skipped+=1
        engines={}
        for key in ("cadical195","glucose4"):
            v=trial["solver_results"].get(key)
            if original["solver_status"]!="READY_FOR_STRICT_BASELINE":
                if v is not None:raise AssertionError("SOLVER_SHOULD_SKIP "+id)
                engines[key]={"verdict":"NOT_RUN_SIZE_CAP"}
                continue
            if v is None:raise AssertionError("SOLVER_RESULT_MISSING "+id)
            if v["verdict"]=="ENGINE_ERROR_OR_RESOURCE_LIMIT" and v.get("return_code")==-24:
                verdict="UNKNOWN_CPU_LIMIT_SIGXCPU"
                cpu+=1
            elif v["verdict"]=="UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF":
                verdict=v["verdict"];unsat_only+=1
            elif v["verdict"]=="SAT_VERIFIED_ORIGINAL_CNF":
                if not v.get("original_model_checked"):
                    raise AssertionError("SAT_MODEL_NOT_VERIFIED")
                verdict=v["verdict"]
            else:verdict=v["verdict"]
            engines[key]={
                "scientific_verdict":verdict,
                "raw_verdict":v["verdict"],"raw_return_code":v.get("return_code"),
                "end_to_end_child_wall_seconds":v.get("end_to_end_child_wall_seconds"),
                "reported_native_CDCL_statistics":v.get("native_CDCL_statistics"),
                "portable_unsat_proof":"NOT_PRODUCED"
            }
        records.append({
          "GBD_hash_not_SHA256":id,
          "family":original["family"],"author":original["author"],
          "catalog_label_UNVERIFIED":original["upstream_label_UNVERIFIED"],
          "source_original_TLS_sha256":original["source_sha256"],
          "source_original_transfer_bytes":original["original_transfer_bytes"],
          "decoded_original_CNF_sha256":original["uncompressed_sha256"],
          "decoded_original_CNF_bytes":original["uncompressed_bytes"],
          "compressed_format":original["decoded_format"],
          "n_vars":original["n_variables"],"n_clauses":original["n_clauses"],
          "n_literal_occurrences":original["n_literal_occurrences"],
          "max_clause_width":original["max_clause_width"],
          "safe_parser_status":original["status"],
          "bounded_solver_admission":original["solver_status"],
          "engines":engines
        })
    if labels!=EXPECTED_LABELS or (valid,ready,skipped,cpu,unsat_only)!=(12,9,3,16,2):
        raise AssertionError("CROSS_CHECK_COUNTS_INCONSISTENT "+str((labels,valid,ready,skipped,cpu,unsat_only)))
    out.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(original_zip,out/"original-actions-artifact-13090195696.zip")
    (out/"acquisition.original.json").write_bytes(a_raw)
    (out/"screen.original.json").write_bytes(s_raw)
    science={
      "schema":"JANUS-TIME-SAT-004B-ORIGINAL-COMPETITION-SCREEN-INTERPRETED-V1",
      "date_utc":"2026-11-01",
      "source_run_id":ORIGINAL_RUN,"source_head_sha":ORIGINAL_RUN_HEAD,
      "source_artifact_id":ORIGINAL_ARTIFACT_ID,
      "source_artifact_SHA256":ORIGINAL_SHA,
      "preregister_git_blob_sha":PREREG_BLOB_SHA,
      "source_GBD_ID_is_not_SHA256":True,
      "source_sha256_provenance":"SHA of TLS-downloaded exact bytes first observed by JANUS; no source-published SHA256 available for cross-check",
      "public_not_blinded":True,
      "downloaded_originals_not_embedded_in_this_small_evidence_zip":True,
      "labels_from_catalog_not_independent_proof":True,
      "all_12_original_transfers_validated_against_strict_DIMACS":True,
      "counts":{"frozen_original":12,"downloaded_DIMACS":12,"admitted_to_raw_CDCL":9,
                "skipped_on_predeclared_solver_size_cap":3,
                "SIGXCPU_individual_solver_runs":16,
                "SIGXCPU_cases_both_engines":8,
                "UNSAT_solver_only_individual_runs":2,
                "UNSAT_solver_only_cases":1,
                "portable_UNSAT_certificates_produced":0},
      "cases":records,
      "cost_budget":{"rlimit_AS_bytes":2147483648,
                     "rlimit_CPU_seconds":16,
                     "subprocess_wall_seconds":18,
                     "max_transfer_bytes_per_case":52428800},
      "honest_verdict":"EXTERNAL_PUBLIC_SOURCE_BOUNDED_SCREEN_ONLY_NOT_HARDNESS_CALIBRATED_NO_SPEEDUP",
      "C023_production":"UNCHANGED","research_PR_578":"DRAFT",
      "external_hidden_exam":"NOT_PERFORMED","external_trusted_Witness":"NOT_PERFORMED"
    }
    result=json.dumps(science,sort_keys=True,indent=2)+"\n"
    (out/"scientific_interpretation.json").write_text(result)
    filehashes={p.name:digest(p.read_bytes()) for p in out.iterdir() if p.is_file()}
    (out/"manifest.json").write_text(json.dumps({
      "schema":"JANUS-TIME-SAT-004B-DURABLE-FIRST-EVIDENCE-MANIFEST-V1",
      "original_artifact_id":ORIGINAL_ARTIFACT_ID,
      "original_artifact_SHA256":ORIGINAL_SHA,
      "original_run_id":ORIGINAL_RUN,"first_repo_capture":True,
      "files_sha256":filehashes
    },sort_keys=True,indent=2)+"\n")
    print("ARCHIVE_SCREEN_PASS",json.dumps(science["counts"],sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--preregister",type=Path,required=True)
    a=p.parse_args()
    archive(a.original_zip,a.out,a.preregister)
