#!/usr/bin/env python3
"""Archive exact original GitHub CI original-byte evidence for 004D4C.

No algorithm reruns, no generated fake CI receipt. Compare original dual host
source-bound structural results; permanently retain original ZIP, original
JSON and SHA-checked manifest in research Git. Original CNFs are already
permanently archived by 004D4B; SHA verify them again.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import zipfile

RUN=41345939700
SOURCE_HEAD="183587248c31096fb6830ad36f445406486f2100"
ARTIFACTS={
 "ubuntu22":{"id":13099526547,"sha256":"915bf14bac09763367b774c2a093906e66d13cfa43cc1137ad05a42abc8f34bb"},
 "ubuntu24":{"id":13099081811,"sha256":"e2edd5a55b516747c233f79cd6dea75face090d228815e1ca7e4d60ef6a96c2f"}
}
EXPECTED={
 "linear-equations":("ABSTAIN_GROUP_BUDGET",0,21040,1040),
 "xor-shifting":("SOURCE_PARTITION_VERIFIED",1643,1890,0),
 "minimum-disagreement-parity":("SOURCE_PARTITION_VERIFIED",639,2237,0),
 "binary-tree-parity":("SOURCE_PARTITION_VERIFIED",857,660,0)
}
PARENT=Path("experiments/time_sat_004_external/time_sat_004d4b_evidence")
COHORT=Path("experiments/time_sat_004_external/PREREGISTERED_004D4B_PUBLIC_FOUR_MIXED_20261101.json")

def digest(b):return sha256(b).hexdigest()

def read_original(path,os):
    source=path.read_bytes()
    if digest(source)!=ARTIFACTS[os]["sha256"]:
        raise AssertionError("CI ZIP byte SHA mismatch")
    with zipfile.ZipFile(path) as z:
        if set(z.namelist())!={"result.json"}:
            raise AssertionError("unexpected original artifact entries")
        payload=z.read("result.json")
    data=json.loads(payload)
    if (data.get("schema")!="JANUS-TIME-SAT-004D4C-REAL-ORIGINAL-SUPPORT-INDEX-SAFETY-PILOT-V1"
        or str(data.get("run_id"))!=str(RUN)
        or data.get("run_head")!=SOURCE_HEAD
        or data.get("no_solver_invocations") is not True
        or data.get("frozen_registration_git_blob")!="0cbf0eee23aa77b399ad2057f113ac1e48bd8405"
        or len(data.get("cases",[]))!=4):
        raise AssertionError("original 004D4C CI receipt identity mismatch")
    for c in data["cases"]:
        family=c["family"]
        old,eq,res,skipped=EXPECTED[family]
        if (c["old_status"]!=old
            or c["new_status"]!="SOURCE_PARTITION_VERIFIED"
            or c["xor_equations"]!=eq
            or c["unaltered_residual_source_clauses"]!=res
            or c["unindexed_original_clause_rows_kept"]!=skipped
            or c["source_clause_partition_exact"]!="PASS"
            or c["SAT_or_UNSAT"]!="NOT_ATTEMPTED"):
            raise AssertionError("original structural receipt disagreement "+family)
    return payload,data

def archive(one,two,out):
    source_manifest=json.loads(COHORT.read_text())
    cohort=source_manifest["candidates"]
    a,A=read_original(one,"ubuntu22")
    b,B=read_original(two,"ubuntu24")
    independent=[]
    for left,right,pre in zip(A["cases"],B["cases"],cohort):
        for field in ("GBD_ID_NOT_SHA256","exact_original_CNF_SHA256","source_n",
                      "source_original_clauses","old_status","new_status",
                      "xor_equations","xor_source_clauses",
                      "unaltered_residual_source_clauses",
                      "unindexed_original_clause_rows_kept","index_exhausted"):
            if left[field]!=right[field]:
                raise AssertionError("two worker source results differ on "+field)
        if left["GBD_ID_NOT_SHA256"]!=pre["GBD_id_NOT_SHA256"]:
            raise AssertionError("previous frozen source ID mismatch")
        orig=PARENT/(pre["GBD_id_NOT_SHA256"]+".original.cnf")
        if digest(orig.read_bytes())!=pre["decoded_CNF_SHA256"]:
            raise AssertionError("permanently archived original CNF SHA mismatch")
        independent.append({
            "family":left["family"],
            "source_GBD_id":left["GBD_ID_NOT_SHA256"],
            "source_decoded_sha256":left["exact_original_CNF_SHA256"],
            "old_extractor":left["old_status"],
            "new_extractor":left["new_status"],
            "equations":left["xor_equations"],
            "original_unaltered_residual_clause_count":left["unaltered_residual_source_clauses"],
            "previously_unindexed_source_clause_count":left["unindexed_original_clause_rows_kept"],
            "source_original_clauses_sha_again_checked":True
        })
    out.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(one,out/"original-actions-ubuntu22.zip")
    shutil.copyfile(two,out/"original-actions-ubuntu24.zip")
    (out/"original-ubuntu22.json").write_bytes(a)
    (out/"original-ubuntu24.json").write_bytes(b)
    manifest={
        "schema":"JANUS-TIME-SAT-004D4C-EXACT-ORIGINAL-TWO-WORKER-ARCHIVE-V1",
        "status":"BOTH_WORKER_ORIGINAL_BYTES_PASS_ONE_ABSTAIN_REMOVED_ZERO_NEW_XOR_AND_3_REGRESSIONS_PASS",
        "source_CI":RUN,"original_head":SOURCE_HEAD,
        "original_exact_zip_SHA256":ARTIFACTS,
        "original_source_CNF_provenance":str(PARENT),
        "source_only_no_solver_run":True,
        "source_verified_case_receipts":independent,
        "correct_scientific_claim":"linear-equations first 20000 supports had ZERO complete XOR equations; remaining 1040 original clauses are retained unindexed and might include separate parity groups",
        "real_performance_benchmark":"NONE",
        "independent_external_witness":"NOT_DONE",
        "production_C023":"UNCHANGED",
        "files_SHA256":{p.name:digest(p.read_bytes()) for p in out.iterdir() if p.is_file()},
    }
    (out/"summary.json").write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    print("004D4C_DURABLE_ORIGINAL_PASS",
          json.dumps({"hosts":2,"cases":4,"regressions":0,
                      "linear_new_equations":0,"source_only":True},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--zip22",type=Path,required=True)
    p.add_argument("--zip24",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    opts=p.parse_args();archive(opts.zip22,opts.zip24,opts.out)
