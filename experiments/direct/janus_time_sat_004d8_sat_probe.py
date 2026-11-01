#!/usr/bin/env python3
"""TIME-SAT-004D8: two preregistered original SAT candidates with model-first gate.

Original exact transfer/decoded SHA and DIMACS shape are checked BEFORE any
rank analysis. Known tree SAT model is independently replayed. Lights-out
public catalog SAT label is NOT trusted: try exact-XOR GF(2) original model,
then replay every original clause. If it fails/abstains, skip rank completely.
All source-only resolution/rank certificates replayed before any claim.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
from time import perf_counter

from janus_time_sat_004b_acquire import retrieve,unpack_bounded,scan_dimacs
from janus_time_sat_004b_baselines import read_cnf,classify_nonzero_exit
from janus_time_sat_004d1_xor import solve_if_exact_xor
from janus_time_sat_004d7_rank_gate import source_rank_experiment
from janus_time_sat_004d8_sat_gate import certified_model,gate_rank_for_sat

ROOT=Path("experiments/time_sat_004_external")
REG=ROOT/"PREREGISTERED_004D8_VERIFIED_SAT_MODEL_FIRST_20261102.json"
REG_SHA="d4a9f9aede966e2caf057da843a9183edfacf2af"
MODEL=ROOT/"time_sat_004d4b_evidence"/"binary-tree-parity-SAT-original-model.json"
ORIGINAL=ROOT/"time_sat_004d4b_evidence"
FROZEN_FAMILIES=("binary-tree-parity","lights-out")
CPU=18
WALL=24
AS_BYTES=2_147_483_648


def digest(path):
    h=sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(65536),b""):
            h.update(chunk)
    return h.hexdigest()


def source_check(original,c):
    if digest(original)!=c["original_decoded_CNF_SHA256"]:
        raise AssertionError("source-original SHA256 mismatch "+c["family"])
    shape=scan_dimacs(original)
    for key,expected in (("n_variables",c["n"]),("n_clauses",c["m"]),
                         ("n_literal_occurrences",c["literals"])):
        if shape[key]!=expected:
            raise AssertionError("original strict DIMACS shape differs "+key)
    if not (1<=shape["n_variables"]<=5000 and shape["n_clauses"]<=30000
            and shape["n_literal_occurrences"]<=120000):
        raise AssertionError("original source outside frozen research cap")
    return shape


def verify_prereg():
    found=subprocess.run(["git","hash-object",str(REG)],text=True,
                         capture_output=True,check=True).stdout.strip()
    if found!=REG_SHA:
        raise AssertionError("registered protocol changed after freezing")
    j=json.loads(REG.read_text())
    cases=j["registered_cases"]
    if [x["family"] for x in cases]!=list(FROZEN_FAMILIES):
        raise AssertionError("original case selection changed")
    return cases


def child(input_path,case_index,out):
    resource.setrlimit(resource.RLIMIT_AS,(AS_BYTES,AS_BYTES))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    c=verify_prereg()[case_index]
    source_check(input_path,c)
    rows=read_cnf(input_path,c["n"],c["m"],max_literals=120000)
    began=perf_counter()
    if c["family"]=="binary-tree-parity":
        if digest(MODEL)!="649c39123a5562a26bdf8aadb27d9bcef2d4ee993a92b0ebc2defa7761b066b3":
            raise AssertionError("known original SAT model archive checksum mismatch")
        archived=json.loads(MODEL.read_text())
        if (archived["original_CNF_SHA256"]!=c["original_decoded_CNF_SHA256"]
             or archived["source_variables"]!=c["n"] or archived["source_clauses"]!=c["m"]
             or archived["verified_every_original_clause"] is not True):
            raise AssertionError("model archive mismatched source identity")
        signed=archived["signed_model"]
        method="PREVIOUSLY_ARCHIVED_MIXED_NATIVE_XOR_MODEL"
    elif c["family"]=="lights-out":
        algebra=solve_if_exact_xor(rows,c["n"])
        if algebra.get("verdict")!="SAT_ORIGINAL_MODEL_VERIFIED":
            result={
                "schema":"JANUS-TIME-SAT-004D8-SAT-MODEL-FIRST-CANDIDATE-V1",
                "family":c["family"],
                "original_CNF_SHA256":c["original_decoded_CNF_SHA256"],
                "status":"BLOCK_NO_VERIFIED_SAT_MODEL",
                "SAT_model_method":"EXACT_XOR_GAUSSIAN_ONLY_NO_CDCL",
                "exact_XOR_SAT_model_status":algebra.get("verdict"),
                "algebra_reason":algebra.get("reason"),
                "rank_analysis":"NOT_RUN",
                "C023_main":"UNCHANGED",
            }
            out.parent.mkdir(parents=True,exist_ok=True)
            out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
            print("004D8_CHILD",c["family"],result["status"],flush=True)
            return
        signed=algebra["model"]
        method="FULL_EXACT_XOR_GAUSS_MODEL_ORIGINAL_CNF_REPLAYED"
    else:
        raise AssertionError("unregistered case")
    model=certified_model(rows,c["n"],signed)
    if model["status"]!="SAT_VERIFIED_EVERY_ORIGINAL_CLAUSE":
        raise AssertionError("certified SAT model FAILED exact original CNF")
    rank=source_rank_experiment(rows,c["n"])
    verdict=gate_rank_for_sat(model,rank)
    if rank["status"]!="SOURCE_PROOF_REPLAY_AND_EXACT_GF2_RANK_PASS":
        raise AssertionError("proof/recomputed GF2 rank not verified")
    vals={abs(x):x>0 for x in signed}
    for item in rank["additional_parity_keys"]:
        if sum(int(vals[v]) for v in item["variables"])%2 != item["rhs"]:
            raise AssertionError("source-entailed XOR violated verified original SAT MODEL")
    if rank["independent_rank_analysis"]["source_plus_derived_GF2_inconsistent"]:
        raise AssertionError("verified SAT source yielded GF2 contradictory constraints")
    result={
        "schema":"JANUS-TIME-SAT-004D8-SAT-MODEL-FIRST-CANDIDATE-V1",
        "family":c["family"],
        "original_CNF_SHA256":c["original_decoded_CNF_SHA256"],
        "original_source_n":c["n"],"original_source_m":c["m"],
        "status":"SAT_MODEL_AND_SOURCE_PROOF_VERIFIED",
        "signed_model":list(signed),
        "SAT_model_method":method,
        "original_SAT_certification":model,
        "rank_gate":verdict,
        "rank_analysis":rank,
        "all_derived_XOR_checked_against_SAT_model":True,
        "child_source_model_rank_seconds_NOT_BENCHMARK":perf_counter()-began,
        "child_peak_RSS_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "external_independently_administered_witness":"OPEN",
        "C023_main":"UNCHANGED",
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("004D8_CHILD",c["family"],"SAT_VERIFIED", "new_coeff_rank",
          rank["independent_rank_analysis"]["independent_new_coefficient_rank"],
          "new_aug_rank",rank["independent_rank_analysis"]["independent_new_augmented_rank"],
          "rank_gate",verdict,flush=True)


def main(out):
    cases=verify_prereg()
    out.mkdir(parents=True,exist_ok=True)
    collected=[]
    for i,c in enumerate(cases):
        row={"family":c["family"],"GBD_ID_NOT_SHA256":c["GBD_ID_NOT_SHA256"],
             "original_decoded_CNF_SHA256":c["original_decoded_CNF_SHA256"],
             "model_status":"NOT_ATTEMPTED",
             "result":None}
        original=None
        transfer=None
        try:
            if c["family"]=="binary-tree-parity":
                original=ORIGINAL/(c["GBD_ID_NOT_SHA256"]+".original.cnf")
                raw=ORIGINAL/(c["GBD_ID_NOT_SHA256"]+".original.download")
                if digest(raw)!=c["source_transfer_SHA256"]:
                    raise AssertionError("archived original transfer SHA mismatch")
                row["original_source_acquisition"]="PRIOR_TWO_WORKER_GIT_ARCHIVE_REVALIDATED"
            else:
                transfer,info=retrieve({
                    "hash":c["GBD_ID_NOT_SHA256"],
                    "official_uri":"http://benchmark-database.de/file/"+c["GBD_ID_NOT_SHA256"]
                },out)
                if info["source_sha256"]!=c["source_transfer_SHA256"]:
                    raise AssertionError("new HTTPS response differs from original frozen transfer")
                original=out/(c["GBD_ID_NOT_SHA256"]+".cnf")
                info2=unpack_bounded(transfer,original)
                if info2["uncompressed_sha256"]!=c["original_decoded_CNF_SHA256"]:
                    raise AssertionError("original source decompression SHA mismatch")
                row["original_source_acquisition"]="HTTPS_ORIGINAL_TRANSFER_AND_DECODE_SHA_PASS"
            source_check(original,c)
            row["source_identity"]="EXACT_BYTES_SHA_AND_STRICT_DIMACS_PASS"
            receipt=out/(c["family"]+".result.json")
            command=[sys.executable,str(Path(__file__).resolve()),
                     "--child",str(original),"--index",str(i),"--child-out",str(receipt)]
            start=perf_counter()
            try:
                p=subprocess.run(command,text=True,capture_output=True,
                                 check=False,timeout=WALL)
                if p.returncode:
                    row["model_status"]="ABSTAIN_CHILD_ERROR"
                    row["error"]=classify_nonzero_exit(p.returncode)
                    row["stderr_tail"]=p.stderr[-1000:]
                else:
                    if not receipt.is_file():
                        raise AssertionError("child did not write original model receipt")
                    data=json.loads(receipt.read_text())
                    if data["original_CNF_SHA256"]!=c["original_decoded_CNF_SHA256"]:
                        raise AssertionError("wrong original source bound to receipt")
                    row["model_status"]=data["status"]
                    if row["model_status"]=="SAT_MODEL_AND_SOURCE_PROOF_VERIFIED":
                        model=data["original_SAT_certification"]
                        if model["status"]!="SAT_VERIFIED_EVERY_ORIGINAL_CLAUSE":
                            raise AssertionError("child model status not independently certified")
                        row["result"]={
                            "rank_gate":data["rank_gate"],
                            "new_XOR_forms":data["rank_analysis"]["source_derived_new_syntactic_XOR_count"],
                            "new_coefficient_rank":data["rank_analysis"]["independent_rank_analysis"]["independent_new_coefficient_rank"],
                            "new_augmented_rank":data["rank_analysis"]["independent_rank_analysis"]["independent_new_augmented_rank"],
                            "source_model_SHA256":model["signed_model_SHA256"],
                            "source_resolution_DAG_SHA256":sha256(json.dumps(
                                data["rank_analysis"]["resolution_evidence"],
                                sort_keys=True,separators=(",",":")).encode("ascii")).hexdigest(),
                            "source_original_model_and_all_derivations":"FULL_REPLAY_PASS",
                            "receipt_sha256":digest(receipt),
                        }
                    else:
                        row["result"]={"rank_analysis":"SKIPPED_NO_SAT_MODEL",
                                       "receipt_sha256":digest(receipt)}
            except subprocess.TimeoutExpired:
                row["model_status"]="ABSTAIN_WALL_TIMEOUT_NO_SAT_CERTIFICATE"
            row["child_elapsed_seconds_NOT_PERFORMANCE_BENCHMARK"]=perf_counter()-start
        except Exception as e:
            row["model_status"]="ABSTAIN_SOURCE_OR_AUTHENTICITY_FAILURE"
            row["error_class"]=type(e).__name__
            row["error_message"]=str(e)[:250]
        finally:
            if c["family"]=="lights-out":
                if transfer is not None:transfer.unlink(missing_ok=True)
                if original is not None:original.unlink(missing_ok=True)
        collected.append(row)
        print("004D8_SOURCE",c["family"],row["model_status"],row.get("result"),flush=True)
    data={
        "schema":"JANUS-TIME-SAT-004D8-MODEL-FIRST-FROZEN-ORIGINAL-TWO-CASE-V1",
        "registration_git_blob":REG_SHA,
        "run_id":os.environ.get("GITHUB_RUN_ID","LOCAL"),
        "run_head":os.environ.get("GITHUB_SHA","LOCAL"),
        "source_public_previously_seen_NOT_HIDDEN":True,
        "frozen_model_first_gate":"ORIGINAL_MODEL_VERIFIED_BEFORE_ANY_RANK",
        "no_SAT_CDCL_benchmark":True,
        "independent_external_admin_witness":"OPEN",
        "production_C023_main":"UNCHANGED",
        "cases":collected
    }
    (out/"summary.json").write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    print("004D8_SUMMARY",json.dumps({
        "frozen_candidates":len(cases),
        "SAT_model_verified":sum(x["model_status"]=="SAT_MODEL_AND_SOURCE_PROOF_VERIFIED" for x in collected),
        "positive_rank_eligible":sum(x.get("result") is not None and
            x["result"].get("new_coefficient_rank",0)>0 for x in collected),
        "SAT_solver_calls":0
    },sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--child",type=Path)
    p.add_argument("--index",type=int)
    p.add_argument("--child-out",type=Path)
    a=p.parse_args()
    if a.child is not None:
        if a.index is None or a.child_out is None:raise SystemExit("Missing child args")
        child(a.child,a.index,a.child_out)
    else:
        if a.out is None:raise SystemExit("--out required")
        main(a.out)
