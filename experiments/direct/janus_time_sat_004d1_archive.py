#!/usr/bin/env python3
"""Archive original dual-host TIME-SAT-004D1 artifacts and exact GBD SAT witness.

Must receive ORIGINAL, SHA-verified GitHub Actions ZIPs from run 41329133105;
never replace them with regenerated expected outputs. Re-download exact TLS
GBD source and independently recheck original full CNF against both models.
Preserves all raw bytes; append-only in an isolated research branch.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

from janus_time_sat_004b_acquire import retrieve,unpack_bounded,scan_dimacs
from janus_time_sat_004b_baselines import read_cnf
from janus_time_sat_004d_pilot import FROZEN_SHA
from janus_time_sat_004d1_xor import solve_if_exact_xor,check_original_cnf

RUN=41329133105
RUN_HEAD="3c6af671aefd77ef66f104ab6151ea3972d40523"
ARCHIVES={
    "ubuntu-22.04":(13092711788,"5a59326d3a308b23099e8fd7892da89b712e92173ac5459e940dad3dcd6383d7"),
    "ubuntu-24.04":(13092945914,"4ccb7036b48941db7ca56a8d931373c31f18e7b42a2cee8b0eb4c5dc2bfe8aa1"),
}
ID="01d6fa8efd18ebfecd06af408958477b"
LABEL="lights-out"

def digest(b):return sha256(b).hexdigest()

def archive(z22:Path,z24:Path,output:Path):
    receipts={};models=[]
    for label,original in (("ubuntu-22.04",z22),("ubuntu-24.04",z24)):
        archive_id,original_sha=ARCHIVES[label]
        archive_bytes=original.read_bytes()
        if digest(archive_bytes)!=original_sha:
            raise AssertionError("original GitHub artifact byte sha mismatch: "+label)
        with zipfile.ZipFile(original) as za:
            if set(za.namelist())!={"result.json"}:
                raise AssertionError("unexpected original GitHub artifact members")
            source_data=za.read("result.json")
        j=json.loads(source_data)
        if (j.get("schema")!="JANUS-TIME-SAT-004D1-EXTERNAL-ORIGIN-XOR-PROOF-ONLY-V1"
            or len(j.get("cases",[]))!=2
            or j.get("source_prior_004D0_CI")!=41326432087):
            raise AssertionError("unrecognized original proof-only run")
        target=next((x for x in j["cases"] if x["family"]==LABEL),None)
        control=next((x for x in j["cases"] if x["family"]=="greentao"),None)
        if target is None or control is None or target["gbd_id_NOT_sha256"]!=ID:
            raise AssertionError("original cohort mismatch")
        r=target["xor_certificate"]
        if (r["coverage_status"]!="EXACT_XOR_COVER_PASS"
            or r["verdict"]!="SAT_ORIGINAL_MODEL_VERIFIED"
            or r["group_count"]!=625 or r.get("equation_count")!=625):
            raise AssertionError("not a source-verified complete GF2 SAT receipt")
        if (control["xor_certificate"]["verdict"]!="ABSTAIN_NO_SAT_CLAIM"
            or control["xor_certificate"]["coverage_status"]!="ABSTAIN_NOT_FULL_XOR_COVER"):
            raise AssertionError("Green-Tao source safety regression")
        model=tuple(r["model"])
        if len(model)!=625 or {abs(v) for v in model}!=set(range(1,626)):
            raise AssertionError("original SAT model is not complete")
        models.append(model)
        receipts[label]={
            "github_original_artifact_id":archive_id,
            "github_original_artifact_zip_sha256":original_sha,
            "original_json_sha256":digest(source_data),
            "pure_GF2_and_model_check_seconds":target["structural_GF2_seconds_not_CDCL_comparable"],
            "source_original_download_sha256":target["original_transfer_sha256"],
            "source_decoded_CNF_sha256":target["original_decoded_sha256"],
            "source_GF2_equation_count":r["equation_count"],
            "control_Greentao_abstained":True
        }
    if models[0]!=models[1]:
        raise AssertionError("two independent Ubuntu model assignments disagree")
    fixed=FROZEN_SHA[ID]
    with tempfile.TemporaryDirectory() as temporary:
        tmp=Path(temporary)
        prereg=json.loads(Path("experiments/time_sat_004_external/PREREGISTERED_SATCOMP2026_PILOT_20261101.json").read_text())
        candidate=next(x for x in prereg["candidates"] if x["hash"]==ID)
        raw,meta=retrieve(candidate,tmp)
        if meta["source_sha256"]!=fixed["original"]:
            raise AssertionError("re-downloaded GBD compressed source differs")
        decoded=tmp/"original.cnf"
        actual=unpack_bounded(raw,decoded)
        if actual["uncompressed_sha256"]!=fixed["decoded"]:
            raise AssertionError("re-downloaded GBD CNF differs")
        dim=scan_dimacs(decoded)
        if (dim["n_variables"],dim["n_clauses"],dim["n_literal_occurrences"])!=(625,9216,45312):
            raise AssertionError("source dimensions mismatch")
        rows=read_cnf(decoded,625,9216)
        model=models[0]
        value=sum(1<<(v-1) for v in model if v>0)
        if not check_original_cnf(rows,625,value):
            raise AssertionError("original SAT assignment invalid")
        independent=solve_if_exact_xor(rows,625)
        if (independent["verdict"]!="SAT_ORIGINAL_MODEL_VERIFIED"
            or tuple(independent["model"])!=model
            or independent["equation_count"]!=625):
            raise AssertionError("new exact XOR replay differs from CI")
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(raw,output/"original.download.xz")
        shutil.copyfile(decoded,output/"original.cnf")
    shutil.copyfile(z22,output/"original-github-actions-ubuntu22.zip")
    shutil.copyfile(z24,output/"original-github-actions-ubuntu24.zip")
    (output/"model.json").write_text(json.dumps({
        "original_GBD_id_NOT_SHA256":ID,
        "SAT_model_original_CNF_verified":True,
        "number_of_variables":625,
        "assignment_signed_literals":list(models[0]),
        "external_Witness":"NOT_DONE",
        "source_is_public_unblinded":True,
    },sort_keys=True,indent=2)+"\n")
    manifest={
        "schema":"JANUS-TIME-SAT-004D1-SATCOMP26-LIGHTSOUT-ORIGINAL-XOR-ARCHIVE-V1",
        "status":"EXACT_SOURCE_GF2_SAT_MODEL_VERIFIED_TWO_HOSTS_SPECIALIZED_BASELINES_PENDING",
        "original_run":RUN,"original_run_head_SHA":RUN_HEAD,
        "original_Source_GBD_id_NOT_SHA256":ID,
        "original_SHA256_compressed":fixed["original"],
        "original_SHA256_decoded":fixed["decoded"],
        "source_variables":625,"source_clauses":9216,
        "source_literals":45312,"exact_XOR_equations":625,
        "original_both_hosts_model_identical":True,
        "original_worker_receipts":receipts,
        "independent_original_clause_model_replay":"PASS",
        "same_admin_GitHub_workers_NOT_external_Witness":True,
        "raw_CDCL_004D0_six_second_limit":"ALL_CENSORED_CANNOT_COMPUTE_SPEEDUP_RATIO",
        "specialized_XOR_solver_comparison":"NOT_DONE",
        "production_C023":"UNCHANGED",
        "files_SHA256":{
            p.name:digest(p.read_bytes()) for p in output.iterdir() if p.is_file()
        },
    }
    (output/"manifest.json").write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    print("TIME_SAT_004D1_DURABLE_ARCHIVE_PASS",json.dumps({
        "model":625,"equations":625,"original_source_bytes_sha":fixed["decoded"],
        "original_worker_artifacts":2,
        "files":len(manifest["files_SHA256"])+1
    },sort_keys=True))

if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--zip22",type=Path,required=True)
    cli.add_argument("--zip24",type=Path,required=True)
    cli.add_argument("--out",type=Path,required=True)
    a=cli.parse_args()
    archive(a.zip22,a.zip24,a.out)
