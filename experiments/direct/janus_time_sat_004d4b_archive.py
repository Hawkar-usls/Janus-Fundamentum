#!/usr/bin/env python3
"""TIME-SAT-004D4B research archive of ORIGINAL exact 2 GitHub Actions ZIPs.

Preserves original raw ZIP/JSON receipts; re-acquires all 4 exact SHA-pinned
competition sources and obtains separately verified original-source SAT model
for the new mixed XOR+CNF binary-tree-parity case. Not a hidden or outside-
admin witness. No CDCL rerun or production modifications.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import resource
import shutil
import statistics
import tempfile
import zipfile

from janus_time_sat_004d4b_real_pilot import frozen_sources,check_original,original_model_replay
from janus_time_sat_004b_acquire import retrieve,unpack_bounded
from janus_time_sat_004b_baselines import read_cnf
from janus_time_sat_004d4_mixed_xor import extract_mixed_xor

RUN=41340944813
TESTED_SHA="d41c11fb7120119d58d34d8d38b866a2238a5080"
ZIPS={
 "ubuntu22":{"id":13097550060,
    "sha256":"c39c219e9964977a4619f6dfaec26af2ac3bb36a746f9c519bfff9f9ca8d8f40"},
 "ubuntu24":{"id":13096979436,
    "sha256":"adecbeedcfbe5d42e13a62bf7d2ddd97505f646a7653a8f7c54fe832ede7c4b5"}
}
EXPECTED_STATUS={
 "linear-equations":("ABSTAIN_GROUP_BUDGET",False,0),
 "xor-shifting":("SOURCE_PARTITION_VERIFIED",True,1643),
 "minimum-disagreement-parity":("SOURCE_PARTITION_VERIFIED",True,639),
 "binary-tree-parity":("SOURCE_PARTITION_VERIFIED",True,857)
}
ARMS=("janus_mixed_native_xor","cryptominisat_original_cnf","cadical195_original_cnf")

def sha(b):return sha256(b).hexdigest()

def read_zip(path,host,candidates):
    zraw=path.read_bytes()
    if sha(zraw)!=ZIPS[host]["sha256"]:
        raise AssertionError("Original GitHub Actions ZIP byte SHA mismatch")
    with zipfile.ZipFile(path) as z:
        if set(z.namelist())!={"result.json"}:
            raise AssertionError("Original result ZIP unexpected names")
        data=z.read("result.json")
    report=json.loads(data)
    if (report.get("schema")!="JANUS-TIME-SAT-004D4B-REAL-FOUR-PUBLIC-SOURCE-MIXED-XOR-CNF-V1"
        or report.get("Github_run_id")!=str(RUN)
        or report.get("Github_HEAD")!=TESTED_SHA
        or len(report.get("cases",[]))!=4):
        raise AssertionError("Original CI/source identity mismatch")
    summary={}
    for old,candidate in zip(report["cases"],candidates):
        family=candidate["family"]
        expected=EXPECTED_STATUS[family]
        if (old["family"]!=family
            or old["GBD_id_NOT_SHA256"]!=candidate["GBD_id_NOT_SHA256"]
            or old["source_status"]!="ORIGINAL_SHA_AND_DIMACS_VERIFIED"
            or old["frozen_original_CNF_SHA256"]!=candidate["decoded_CNF_SHA256"]
            or old["frozen_transfer_SHA256"]!=candidate["original_transfer_SHA256"]
            or old["structural"]["status"]!=expected[0]
            or old["structural"]["benchmark_admitted"]!=expected[1]):
            raise AssertionError("Frozen source or structural result changed")
        if expected[1]:
            if (old["structural"]["xor_equations"]!=expected[2]
                or old["structural"]["xor_source_clauses"]+
                   old["structural"]["residual_original_clauses"]!=candidate["original_shape"]["n_clauses"]):
                raise AssertionError("Original mixed source XOR partition mismatch")
            bench=old["benchmark"]
            if len(bench)!=6:
                raise AssertionError("Original 2x3 arm grid incomplete")
            outcomes={}
            for arm in ARMS:
                rec=[r for r in bench if r["arm"]==arm]
                if len(rec)!=2 or sorted(r["repeat"] for r in rec)!=[0,1]:
                    raise AssertionError("Missing original arm pairing")
                verdicts=[r["result"]["verdict"] for r in rec]
                desired=("SAT_ORIGINAL_CNF_VERIFIED" if
                         (family=="binary-tree-parity" and arm=="janus_mixed_native_xor")
                         else "UNKNOWN_CPU_LIMIT_SIGXCPU")
                if any(v!=desired for v in verdicts):
                    raise AssertionError("Original verdict unexpectedly different: "+family+" "+arm)
                stats={"verdict":desired,"count":len(rec)}
                if desired=="SAT_ORIGINAL_CNF_VERIFIED":
                    if any(r["result"].get("original_decoded_SHA256")!=candidate["decoded_CNF_SHA256"]
                           for r in rec):
                        raise AssertionError("Successful SAT child not bound to source SHA")
                    stats["median_complete_child_wall_seconds"]=statistics.median(
                        r["full_cold_child_wall_seconds"] for r in rec)
                    stats["max_success_peak_RSS_kib"]=max(
                        r["result"]["successful_child_peak_RSS_KiB"] for r in rec)
                else:stats["finite_speedup_ratio"]="UNDEFINED_CPU_CENSORED"
                outcomes[arm]=stats
        else:
            if old["benchmark"]:
                raise AssertionError("Failed extraction incorrectly launched solver")
            outcomes={}
        summary[family]={
            "original_SHA256":candidate["decoded_CNF_SHA256"],
            "original_GBD":candidate["GBD_id_NOT_SHA256"],
            "structure":old["structural"],
            "outcomes":outcomes}
    return data,summary

def independently_obtain_mixed_sat_model(path,candidate):
    resource.setrlimit(resource.RLIMIT_AS,(2_147_483_648,2_147_483_648))
    resource.setrlimit(resource.RLIMIT_CPU,(8,9))
    import pycryptosat
    shape=check_original(path,candidate)
    rows=read_cnf(path,shape["n_variables"],shape["n_clauses"],max_literals=120000)
    x=extract_mixed_xor(rows,shape["n_variables"])
    if (x["status"]!="SOURCE_PARTITION_VERIFIED" or
        x["complete_xor_equation_count"]!=857 or
        x["source_residual_clauses"]!=660):
        raise AssertionError("Archived source does not have expected mixed XOR cover")
    solver=pycryptosat.Solver(threads=1)
    for eq in x["equations"]:
        solver.add_xor_clause(eq["variables"],bool(eq["rhs"]))
    for clause in x["residual_clauses"]:solver.add_clause(clause)
    sat,sol=solver.solve()
    n=shape["n_variables"]
    if sat is not True or sol is None or len(sol)<=n:
        raise AssertionError("Recomputed mixed SAT model missing")
    assignment=[i if bool(sol[i]) else -i for i in range(1,n+1)]
    if not original_model_replay(rows,n,assignment):
        raise AssertionError("Recomputed SAT model fails original unchanged CNF")
    return {
        "GBD_id_NOT_SHA256":candidate["GBD_id_NOT_SHA256"],
        "original_CNF_SHA256":candidate["decoded_CNF_SHA256"],
        "source_variables":n,"source_clauses":shape["n_clauses"],
        "extracted_XOR_equations":857,"original_residual_clauses":660,
        "signed_model":assignment,
        "verified_every_original_clause":True,
        "portable_UNSAT_proof":"NOT_APPLICABLE_SAT",
        "administrative_independence":"NOT_OUTSIDE_GITHUB"
    }

def archive(z22,z24,out):
    candidates=frozen_sources()
    first,stats1=read_zip(z22,"ubuntu22",candidates)
    second,stats2=read_zip(z24,"ubuntu24",candidates)
    for fam in EXPECTED_STATUS:
        for key in ("status","xor_equations","xor_source_clauses","residual_original_clauses"):
            if stats1[fam]["structure"].get(key)!=stats2[fam]["structure"].get(key):
                raise AssertionError("Two original workers disagreed "+fam+" "+key)
    out.mkdir(parents=True,exist_ok=True)
    for host,zraw,original in (("ubuntu22",z22,first),("ubuntu24",z24,second)):
        shutil.copyfile(zraw,out/("original-actions-"+host+".zip"))
        (out/("original-"+host+".json")).write_bytes(original)
    archived_sources=[]
    with tempfile.TemporaryDirectory() as root:
        temp=Path(root)
        for c in candidates:
            gbd=c["GBD_id_NOT_SHA256"]
            source,meta=retrieve({"hash":gbd,"official_uri":c["official_URI"]},temp)
            if meta["source_sha256"]!=c["original_transfer_SHA256"]:
                raise AssertionError("Compressed original SHA changed: "+c["family"])
            cnf=temp/(gbd+".cnf")
            extracted=unpack_bounded(source,cnf)
            if extracted["uncompressed_sha256"]!=c["decoded_CNF_SHA256"]:
                raise AssertionError("Uncompressed original SHA changed: "+c["family"])
            check_original(cnf,c)
            compressed=out/(gbd+".original.download")
            raw=out/(gbd+".original.cnf")
            shutil.copyfile(source,compressed)
            shutil.copyfile(cnf,raw)
            archived_sources.append({"family":c["family"],"GBD_id":gbd,
                "original_download_sha256":meta["source_sha256"],
                "original_CNF_sha256":extracted["uncompressed_sha256"]})
            if c["family"]=="binary-tree-parity":
                cert=independently_obtain_mixed_sat_model(cnf,c)
                (out/"binary-tree-parity-SAT-original-model.json").write_text(
                    json.dumps(cert,indent=2,sort_keys=True)+"\n")
            source.unlink(missing_ok=True);cnf.unlink(missing_ok=True)
    result={
      "schema":"JANUS-TIME-SAT-004D4B-FOUR-PUBLIC-CNF-EXACT-ORIGINAL-ARCHIVE-V1",
      "status":"ORIGINAL_TWO_WORKER_SHA_PASS_THREE_PARTIAL_XOR_ONE_SAT_TWO_UNKNOWN_ONE_ABSTAIN",
      "original_run":RUN,"original_tested_head":TESTED_SHA,
      "original_workers":{"ubuntu22":stats1,"ubuntu24":stats2},
      "original_zip_ids_and_SHA":ZIPS,
      "four_complete_original_downloads_and_CNFs":archived_sources,
      "original_source_SAT_model_recomputed_and_independently_replayed":"PASS_SAME_GITHUB_ADMIN",
      "original_readonly_C023":"UNCHANGED",
      "cross_family_result":"BINARY_TREE_PARITY_SAT_ONLY_OTHER_TWO_CPU_CENSORED",
      "outside_Github_Witness":"OPEN",
      "public_preseen_not_blind":True,
      "finite_speedup_from_CPU_timeout":"NOT_DEFINED",
      "source_record_file_SHA256":{p.name:sha(p.read_bytes()) for p in out.iterdir() if p.is_file()}
    }
    (out/"summary.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("004D4B_DURABLE_ORIGINAL_PASS",json.dumps({
       "original_source_count":4,"raw_worker_ZIPs":2,
       "n_trials":36,"new_source_verified_SAT":"binary-tree-parity",
       "other_two_mixed":"ALL_CPU_CENSORED",
       "linear_equations":"ABSTAIN_GROUP_BUDGET",
    },sort_keys=True),flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--zip22",required=True,type=Path)
    ap.add_argument("--zip24",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    archive(args.zip22,args.zip24,args.out)
