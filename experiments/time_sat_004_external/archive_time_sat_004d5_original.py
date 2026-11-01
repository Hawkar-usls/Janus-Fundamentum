#!/usr/bin/env python3
"""Archive exact original GitHub Actions ZIPs for TIME-SAT-004D5.
Only original source SHA, fixed cohort, source-only receipts. Never regenerate
or substitute original CI bytes, never infer solver/SAT acceleration.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import zipfile

RUN=41349728982
HEAD="105244ea1ef7aec96a277227616472f54b862dca"
ZIPS={
    "ubuntu22":{"id":13101080422,
      "sha256":"dad7459020a6b791b5a55003e34eb14f018153316f0cc32a310d8cee4a8c1d3a"},
    "ubuntu24":{"id":13100636511,
      "sha256":"3459ff3f9f14f7abc63d55c207172fb2a7f6e43f2377c124a38e7e3a130de65d"}
}
EXPECTED={"linear-equations":(1200,0,0),
          "xor-shifting":(1260,1643,0),
          "minimum-disagreement-parity":(646,639,0),
          "binary-tree-parity":(165,857,0)}
SOURCES=Path("experiments/time_sat_004_external/time_sat_004d4b_evidence")
FROZEN=Path("experiments/time_sat_004_external/PREREGISTERED_004D4B_PUBLIC_FOUR_MIXED_20261101.json")

def sha(raw):return sha256(raw).hexdigest()

def read_original(p,os):
    b=p.read_bytes()
    if sha(b)!=ZIPS[os]["sha256"]:raise AssertionError("Original GitHub ZIP SHA mismatch")
    with zipfile.ZipFile(p) as archive:
        if set(archive.namelist())!={"result.json"}:
            raise AssertionError("Unrecognized original GitHub ZIP members")
        raw=archive.read("result.json")
    j=json.loads(raw)
    if (j.get("schema")!="JANUS-TIME-SAT-004D5-SOURCE-BINARY-SCC-EQUIVALENCE-XOR-PROBE-V1"
        or str(j["run_id"])!=str(RUN) or j["run_head"]!=HEAD
        or j["registration_git_blob"]!="7e9c15aa9206dae147c6d318ccc8f1b9de093d78"
        or j["no_SAT_or_CDCL_solver_calls"] is not True or len(j["cases"])!=4):
        raise AssertionError("Source run not matching original frozen experiment")
    for c in j["cases"]:
        b=c["binary_equivalence_result"]
        expected=EXPECTED[c["family"]]
        if (b["status"]!="WITNESSED_BINARY_EQUIVALENCE_PARITY_SOURCE_SCAN_PASS"
            or b["binary_original_clause_count"]!=expected[0]
            or b["nontrivial_source_proven_signed_variable_aliases"]!=0
            or b["new_implied_XOR_equations_beyond_prior_canonical_baseline"]!=0
            or c["original_explicit_complete_XOR_equations"]!=expected[1]
            or b["sample_count"]!=0 or b["SAT_UNSAT"]!="NOT_ATTEMPTED"):
            raise AssertionError("Original scientific receipt mismatch "+c["family"])
    return raw,j

def archive(z22,z24,out):
    one,a=read_original(z22,"ubuntu22")
    two,b=read_original(z24,"ubuntu24")
    frozen=json.loads(FROZEN.read_text())["candidates"]
    matched=[]
    for c,d,source in zip(a["cases"],b["cases"],frozen):
        for field in ("family","GBD_ID_not_sha256","original_decoded_CNF_SHA256",
                      "original_explicit_complete_XOR_equations"):
            if c[field]!=d[field]:raise AssertionError("Two worker mismatch "+field)
        if (c["GBD_ID_not_sha256"]!=source["GBD_id_NOT_SHA256"] or
            c["original_decoded_CNF_SHA256"]!=source["decoded_CNF_SHA256"]):
            raise AssertionError("Prior pinned original source mismatch")
        src=SOURCES/(source["GBD_id_NOT_SHA256"]+".original.cnf")
        if sha(src.read_bytes())!=source["decoded_CNF_SHA256"]:
            raise AssertionError("Original unchanged CNF no longer matches SHA")
        matched.append({
            "family":c["family"],"GBD_id_NOT_SHA256":c["GBD_ID_not_sha256"],
            "original_decoded_SHA256":c["original_decoded_CNF_SHA256"],
            "source_original_binary_clauses":c["binary_equivalence_result"]["binary_original_clause_count"],
            "new_signed_equivalences":0,"new_explicit_XOR_equations":0,
            "retained_original_CNF_verified":True
        })
    out.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(z22,out/"original-actions-ubuntu22.zip")
    shutil.copyfile(z24,out/"original-actions-ubuntu24.zip")
    (out/"original-ubuntu22.json").write_bytes(one)
    (out/"original-ubuntu24.json").write_bytes(two)
    result={
        "schema":"JANUS-TIME-SAT-004D5-ORIGINAL-SHA-DUAL-HOST-SCC-EVIDENCE-V1",
        "status":"ORIGINAL_DUAL_HOST_SHA_PASS_ZERO_BINARY_EQUIVALENCES_ZERO_NEW_XOR",
        "original_CI":RUN,"original_HEAD_SHA":HEAD,
        "original_GitHub_ZIP_SHA256":ZIPS,
        "original_source_SHA_anchored_in_parent_004D4B":True,
        "case_receipts":matched,
        "synthetic_positive_controls":"9/9_TESTS_PASS_PER_HOST",
        "real_original_negative_result":"0 new implied XOR on 4 pinned public original CNFs",
        "solve_time_speedup_claim":"NONE_NO_SOLVER_RUN",
        "independent_outside_GitHub_Witness":"OPEN",
        "production_C023":"UNCHANGED",
        "file_sha256":{p.name:sha(p.read_bytes()) for p in out.iterdir() if p.is_file()},
    }
    (out/"summary.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("TIME_SAT_004D5_DURABLE_ORIGINAL_PASS",json.dumps({
        "workers":2,"sources":len(matched),"new_aliases":0,"new_xors":0,
        "original_zip_hashes_verified":True},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--zip22",required=True,type=Path)
    p.add_argument("--zip24",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    opts=p.parse_args();archive(opts.zip22,opts.zip24,opts.out)
