#!/usr/bin/env python3
"""Archive byte-exact original TIME-SAT-004D4D two-worker research evidence.

Source run/commit/artifact ids+API digests are frozen before retrieval. No
rerun or reinterpretation of raw results. Original competition CNFs are
SHA-pinned in parent 004D4B evidence. Research-only, not production.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import zipfile

RUN=41347280844
SOURCE_HEAD="28c486ae19f47b6978e03b1be2911eb9c667be88"
ARTIFACTS={
    "ubuntu22":{"id":13099787705,"sha256":"7e4ea05a5bf348295e4a3fcb91964699183c115065067844ec8a615efc506437"},
    "ubuntu24":{"id":13100130974,"sha256":"36457ebd6e0c4b7a550b21167df9e6c37bc97e7eddc28cb5b4dec0afa39db28d"},
}
FROZEN_BLOB="0cbf0eee23aa77b399ad2057f113ac1e48bd8405"
COHORT=Path("experiments/time_sat_004_external/PREREGISTERED_004D4B_PUBLIC_FOUR_MIXED_20261101.json")
PARENT=Path("experiments/time_sat_004_external/time_sat_004d4b_evidence")
KNOWN={"linear-equations":(0,21040,2,1040),
       "xor-shifting":(1643,1890,1,0),
       "minimum-disagreement-parity":(639,2237,1,0),
       "binary-tree-parity":(857,660,1,0)}

def digest(data):
    return sha256(data).hexdigest()

def parse_original(zip_path, worker):
    blob=zip_path.read_bytes()
    if digest(blob)!=ARTIFACTS[worker]["sha256"]:
        raise AssertionError("original artifact ZIP digest differs from GitHub upload "+worker)
    with zipfile.ZipFile(zip_path) as zipped:
        if set(zipped.namelist())!={"result.json"}:
            raise AssertionError("unexpected source artifact file list")
        content=zipped.read("result.json")
    data=json.loads(content)
    if (data.get("schema")!="JANUS-TIME-SAT-004D4D-SHA-PINNED-PAGED-FULL-SOURCE-SCAN-V1"
        or str(data.get("run_id"))!=str(RUN)
        or data.get("run_head")!=SOURCE_HEAD
        or data.get("frozen_manifest_git_blob")!=FROZEN_BLOB
        or data.get("all_supported_groups_scanned") is not True
        or len(data.get("cases",[]))!=4):
        raise AssertionError("original CI identity or proof boundary mismatch")
    if [c["family"] for c in data["cases"]]!=list(KNOWN):
        raise AssertionError("wrong original four source families")
    for c in data["cases"]:
        eq,res,pages,unindexed=KNOWN[c["family"]]
        if (c["complete_source_XOR_equations"]!=eq
            or c["original_residual_clauses_retained_unchanged"]!=res
            or len(c["page_stats"])!=pages
            or c["previously_unindexed_source_clause_rows"]!=unindexed
            or c["page_stats"][-1]["unindexed_rows_forwarded"]!=0
            or c["source_partition"]!="SOURCE_PARTITION_VERIFIED"
            or c["SAT_UNSAT_solver"]!="NOT_INVOKED"):
            raise AssertionError("incorrect original source-only result "+c["family"])
    return content,data

def archive(zip22, zip24, out):
    raw22,run22=parse_original(zip22,"ubuntu22")
    raw24,run24=parse_original(zip24,"ubuntu24")
    frozen=json.loads(COHORT.read_text())["candidates"]
    receipts=[]
    for one,two,prior in zip(run22["cases"],run24["cases"],frozen):
        for k in ("family","GBD_ID_NOT_SHA256","original_decoded_CNF_SHA256",
                  "original_dimensions","logical_source_SHA256",
                  "original_source_rows","page_stats","complete_source_XOR_equations",
                  "source_clauses_consumed_by_XOR",
                  "original_residual_clauses_retained_unchanged",
                  "xor_source_indices_SHA256","original_residual_indices_SHA256",
                  "source_partition"):
            if one[k]!=two[k]:
                raise AssertionError("dual worker divergent receipt "+k)
        if (one["GBD_ID_NOT_SHA256"]!=prior["GBD_id_NOT_SHA256"] or
            one["original_decoded_CNF_SHA256"]!=prior["decoded_CNF_SHA256"]):
            raise AssertionError("frozen original source identity mismatch")
        source=PARENT/(prior["GBD_id_NOT_SHA256"]+".original.cnf")
        if digest(source.read_bytes())!=prior["decoded_CNF_SHA256"]:
            raise AssertionError("archived original SATComp CNF SHA mismatch")
        receipts.append({
            "family":one["family"],
            "GBD_id_NOT_SHA256":one["GBD_ID_NOT_SHA256"],
            "original_CNF_SHA256":one["original_decoded_CNF_SHA256"],
            "original_clause_count":one["original_source_rows"],
            "paged_complete_XOR_equations":one["complete_source_XOR_equations"],
            "support_pages":len(one["page_stats"]),
            "previously_unindexed_source_clause_rows":one["previously_unindexed_source_clause_rows"],
            "current_unindexed_source_clause_rows":one["page_stats"][-1]["unindexed_rows_forwarded"],
            "original_residual_clause_count":one["original_residual_clauses_retained_unchanged"],
            "xor_indices_SHA256":one["xor_source_indices_SHA256"],
            "residual_indices_SHA256":one["original_residual_indices_SHA256"],
        })
    out.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(zip22,out/"original-actions-ubuntu22.zip")
    shutil.copyfile(zip24,out/"original-actions-ubuntu24.zip")
    (out/"original-ubuntu22.json").write_bytes(raw22)
    (out/"original-ubuntu24.json").write_bytes(raw24)
    summary={
        "schema":"JANUS-TIME-SAT-004D4D-ORIGINAL-TWO-WORKER-ARCHIVE-V1",
        "status":"BOTH_WORKERS_EXHAUSTIVE_SUPPORTED_SIGN_MASK_COVERAGE_ZERO_NEW_LINEAR_XOR",
        "source_CI":RUN,
        "original_head":SOURCE_HEAD,
        "original_artifact_sha256":ARTIFACTS,
        "source_CNF_archive":str(PARENT),
        "frozen_manifest_git_blob":FROZEN_BLOB,
        "original_two_worker_agreement":"PASS",
        "original_source_SHA_replay":"PASS",
        "case_receipts":receipts,
        "correct_scientific_scope":"No complete explicitly encoded source sign-mask XOR block of width <=6 in 21,040-clause linear-equations CNF. This does not rule out implicit XOR or other encodings.",
        "new_SAT_UNSAT_verdicts":"NONE",
        "benchmark_or_speedup":"NOT_PERFORMED",
        "external_witness":"OPEN",
        "production_C023":"UNCHANGED",
        "file_SHA256":{p.name:digest(p.read_bytes()) for p in out.iterdir() if p.is_file()},
    }
    (out/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("004D4D_DURABLE_ORIGINAL_PASS",json.dumps({
        "workers":2,"sources":4,"linear_clauses_checked":21040,
        "linear_eq_XOR_equations":0,"regressions":0,"no_solver":True},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--zip22",required=True,type=Path)
    p.add_argument("--zip24",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    archive(a.zip22,a.zip24,a.out)
